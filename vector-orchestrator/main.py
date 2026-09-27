#!/usr/bin/env python3
import os
import sys
import json
import time
import logging
from typing import List, Dict, Any, Optional

# Formicx Agent SDK
from formicx import Agent

# FAISS and NumPy
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    faiss = None

import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("vector-orchestrator")

# Add Backend to python path if available
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    from app.core.logger_handler import system_log_handler
    if system_log_handler not in logger.handlers:
        logger.addHandler(system_log_handler)
except Exception:
    pass


class VectorOrchestratorAgent(Agent):
    """Formicx Orchestrator Agent that collects partition FAISS indices and metadata maps
    from serverless Lambda worker instances, consolidates them into a single orchestrated FAISS vector DB,
    and removes individual partition files so ONLY the master index & metadata remain stored.
    """

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.jobs: Dict[str, Dict[str, Any]] = {}

    def on_start(self):
        logger.info(f"[{self.name}] Vector Orchestrator Agent started with ID: {self.id}")
        logger.info(f"[{self.name}] Single FAISS vector index & metadata orchestration engine active.")
        sys.stdout.flush()

    def register_job(self, job_id: str, total_clusters: int, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """Registers a multi-cluster vectorization job to track incoming Lambda outputs."""
        if not output_dir:
            output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../data/vector_db/{job_id}"))

        os.makedirs(output_dir, exist_ok=True)

        self.jobs[job_id] = {
            "job_id": job_id,
            "total_clusters": total_clusters,
            "output_dir": output_dir,
            "received_clusters": {},  # cluster_id -> { index_file_path, metadata_file_path, total_chunks }
            "status": "in_progress",
            "created_at": time.time(),
            "master_index_path": None,
            "master_metadata_path": None
        }

        logger.info(f"[{self.name}] Registered new job '{job_id}' expecting {total_clusters} cluster partition(s).")
        return {
            "status": "success",
            "job_id": job_id,
            "total_clusters": total_clusters,
            "output_dir": output_dir
        }

    def submit_cluster_output(
        self,
        job_id: str,
        cluster_id: int,
        index_file_path: str,
        metadata_file_path: str,
        total_chunks: int = 0
    ) -> Dict[str, Any]:
        """Receives partition FAISS output from a Lambda worker for a registered job."""
        if job_id not in self.jobs:
            # Auto-register if not explicitly registered beforehand
            self.register_job(job_id=job_id, total_clusters=cluster_id + 1)

        job = self.jobs[job_id]
        job["received_clusters"][str(cluster_id)] = {
            "cluster_id": cluster_id,
            "index_file_path": index_file_path,
            "metadata_file_path": metadata_file_path,
            "total_chunks": total_chunks,
            "received_at": time.time()
        }

        received_count = len(job["received_clusters"])
        total_expected = job["total_clusters"]

        logger.info(
            f"[{self.name}] Job '{job_id}': Received cluster_id={cluster_id} partition output "
            f"({received_count}/{total_expected} total received)."
        )

        # If all expected cluster outputs have arrived, trigger automatic merge
        auto_merged = False
        merge_result = None
        if received_count >= total_expected:
            logger.info(f"[{self.name}] Job '{job_id}': All {total_expected} partition outputs received. Merging single master FAISS index...")
            merge_result = self.merge_job_indices(job_id)
            auto_merged = True

        return {
            "status": "success",
            "job_id": job_id,
            "cluster_id": cluster_id,
            "received_count": received_count,
            "total_expected": total_expected,
            "auto_merged": auto_merged,
            "merge_result": merge_result
        }

    def merge_job_indices(self, job_id: str) -> Dict[str, Any]:
        """Consolidates all collected partition FAISS index files & metadata maps into a single master FAISS DB
        and purges individual partition files so ONLY the orchestrated single output is stored.
        """
        if not FAISS_AVAILABLE:
            error_msg = "faiss package is not installed. Unable to merge vector index files."
            logger.error(f"[{self.name}] {error_msg}")
            return {"status": "error", "message": error_msg}

        if job_id not in self.jobs:
            return {"status": "error", "message": f"Job '{job_id}' not found."}

        job = self.jobs[job_id]

        # If job is already completed and master index exists, return existing result idempotently
        if job.get("status") == "completed" and job.get("master_index_path") and os.path.exists(job.get("master_index_path")):
            logger.info(f"[{self.name}] Job '{job_id}' is already completed. Returning master index: {job.get('master_index_path')}")
            return {
                "status": "success",
                "job_id": job_id,
                "total_vectors": job.get("total_vectors", 0),
                "dimension": 384,
                "master_index_path": job.get("master_index_path"),
                "master_metadata_path": job.get("master_metadata_path"),
                "cleaned_partition_files": 0
            }

        received = job["received_clusters"]

        if not received:
            return {"status": "error", "message": f"No partition outputs collected for job '{job_id}'."}

        output_dir = job["output_dir"]
        os.makedirs(output_dir, exist_ok=True)

        master_index = None
        master_metadata: List[Dict[str, Any]] = []
        dimension = 384
        global_vector_id = 0

        # Sort clusters by cluster_id key
        sorted_clusters = sorted(received.values(), key=lambda c: int(c["cluster_id"]))

        for partition in sorted_clusters:
            idx_path = partition["index_file_path"]
            meta_path = partition["metadata_file_path"]

            if not os.path.exists(idx_path):
                logger.warning(f"[{self.name}] Index file missing for cluster {partition['cluster_id']}: {idx_path}")
                continue

            if not os.path.exists(meta_path):
                logger.warning(f"[{self.name}] Metadata file missing for cluster {partition['cluster_id']}: {meta_path}")
                continue

            try:
                # 1. Read partition FAISS index
                part_index = faiss.read_index(idx_path)
                dimension = part_index.d

                if master_index is None:
                    master_index = faiss.IndexFlatIP(dimension)

                # Reconstruct/merge vectors into master index
                vectors = part_index.reconstruct_n(0, part_index.ntotal)
                master_index.add(vectors)

                # 2. Read partition metadata JSON
                with open(meta_path, "r", encoding="utf-8") as f:
                    part_meta = json.load(f)

                if isinstance(part_meta, list):
                    chunks = part_meta
                elif isinstance(part_meta, dict):
                    chunks = part_meta.get("chunks", part_meta.get("items", []))
                else:
                    chunks = []
                for chunk in chunks:
                    chunk["vector_id"] = global_vector_id
                    chunk["job_id"] = job_id
                    master_metadata.append(chunk)
                    global_vector_id += 1

                logger.info(
                    f"[{self.name}] Merged cluster {partition['cluster_id']} "
                    f"({part_index.ntotal} vectors). Running total: {master_index.ntotal} vectors."
                )

            except Exception as err:
                logger.error(f"[{self.name}] Error merging cluster {partition['cluster_id']} files: {str(err)}", exc_info=True)

        if master_index is None or master_index.ntotal == 0:
            return {"status": "error", "message": "Failed to create master index (0 valid vectors extracted)."}

        # 3. Save single master FAISS index & metadata files
        master_idx_path = os.path.join(output_dir, "master_index.faiss")
        master_meta_path = os.path.join(output_dir, "master_metadata.json")

        faiss.write_index(master_index, master_idx_path)

        master_payload = {
            "job_id": job_id,
            "total_vectors": master_index.ntotal,
            "dimension": dimension,
            "total_clusters": len(received),
            "updated_at": time.time(),
            "chunks": master_metadata
        }

        with open(master_meta_path, "w", encoding="utf-8") as f:
            json.dump(master_payload, f, indent=2)

        # 4. Cleanup individual cluster partition files so ONLY the orchestrated single output remains
        cleaned_files = 0
        for partition in sorted_clusters:
            idx_p = partition.get("index_file_path")
            meta_p = partition.get("metadata_file_path")
            if idx_p and os.path.exists(idx_p) and os.path.abspath(idx_p) != os.path.abspath(master_idx_path):
                try:
                    os.remove(idx_p)
                    cleaned_files += 1
                except Exception as err:
                    logger.warning(f"[{self.name}] Could not remove partition index file '{idx_p}': {err}")

            if meta_p and os.path.exists(meta_p) and os.path.abspath(meta_p) != os.path.abspath(master_meta_path):
                try:
                    os.remove(meta_p)
                    cleaned_files += 1
                except Exception as err:
                    logger.warning(f"[{self.name}] Could not remove partition metadata file '{meta_p}': {err}")

        logger.info(
            f"[{self.name}] Cleaned up {cleaned_files} temporary cluster partition file(s). "
            f"Retained ONLY single orchestrated FAISS index at '{master_idx_path}' and metadata at '{master_meta_path}'."
        )

        # Update job status state
        job["status"] = "completed"
        job["master_index_path"] = master_idx_path
        job["master_metadata_path"] = master_meta_path
        job["total_vectors"] = master_index.ntotal

        logger.info(
            f"[{self.name}] Successfully orchestrated single master FAISS DB for job '{job_id}' "
            f"({master_index.ntotal} total vectors saved to {master_idx_path})."
        )

        return {
            "status": "success",
            "job_id": job_id,
            "total_vectors": master_index.ntotal,
            "dimension": dimension,
            "master_index_path": master_idx_path,
            "master_metadata_path": master_meta_path,
            "cleaned_partition_files": cleaned_files
        }

    def orchestrate_clusters(
        self,
        job_id: str,
        cluster_outputs: List[Dict[str, Any]],
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """High-level Formicx orchestration method that registers, collects all partition outputs from Lambda workers,
        merges them into a single consolidated FAISS vector index & metadata file, cleans up all individual partition files,
        and returns the single orchestrated output details.
        """
        total_clusters = len(cluster_outputs)
        self.register_job(job_id=job_id, total_clusters=total_clusters, output_dir=output_dir)

        last_res = None
        for partition in cluster_outputs:
            c_id = partition.get("cluster_id", 0)
            idx_path = partition.get("index_file_path")
            meta_path = partition.get("metadata_file_path")
            chunks_cnt = partition.get("total_chunks", 0)

            if idx_path and meta_path:
                last_res = self.submit_cluster_output(
                    job_id=job_id,
                    cluster_id=c_id,
                    index_file_path=idx_path,
                    metadata_file_path=meta_path,
                    total_chunks=chunks_cnt
                )

        if last_res and last_res.get("auto_merged") and last_res.get("merge_result"):
            return last_res.get("merge_result")

        return self.merge_job_indices(job_id)


    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Returns the current aggregation state for a given job."""
        if job_id not in self.jobs:
            return {"status": "not_found", "message": f"Job '{job_id}' is not registered."}

        job = self.jobs[job_id]
        return {
            "status": "success",
            "job_id": job_id,
            "job_status": job["status"],
            "received_clusters_count": len(job["received_clusters"]),
            "total_expected_clusters": job["total_clusters"],
            "master_index_path": job["master_index_path"],
            "master_metadata_path": job["master_metadata_path"]
        }

    def on_message(self, message):
        """Formicx IPC message handler."""
        payload = message.payload or {}
        logger.info(f"[{self.name}] Received Formicx message from '{message.sender}' (ID={message.message_id})")

        action = payload.get("action")
        job_id = payload.get("job_id")

        if action == "orchestrate_clusters":
            cluster_outputs = payload.get("cluster_outputs", [])
            output_dir = payload.get("output_dir")
            res = self.orchestrate_clusters(job_id=job_id, cluster_outputs=cluster_outputs, output_dir=output_dir)
            self.reply(message, payload=res)

        elif action == "register_job":
            total_clusters = int(payload.get("total_clusters", 1))
            output_dir = payload.get("output_dir")
            res = self.register_job(job_id=job_id, total_clusters=total_clusters, output_dir=output_dir)
            self.reply(message, payload=res)

        elif action in ["submit_cluster_output", "cluster_output"]:
            cluster_id = int(payload.get("cluster_id", 0))
            index_path = payload.get("index_file_path")
            meta_path = payload.get("metadata_file_path")
            chunks_cnt = int(payload.get("total_chunks", 0))

            res = self.submit_cluster_output(
                job_id=job_id,
                cluster_id=cluster_id,
                index_file_path=index_path,
                metadata_file_path=meta_path,
                total_chunks=chunks_cnt
            )
            self.reply(message, payload=res)

        elif action in ["merge_job_clusters", "merge_job_indices"]:
            res = self.merge_job_indices(job_id=job_id)
            self.reply(message, payload=res)

        elif action == "get_job_status":
            res = self.get_job_status(job_id=job_id)
            self.reply(message, payload=res)

        else:
            self.reply(message, payload={
                "status": "error",
                "message": f"Unsupported action '{action}'."
            })

    def on_stop(self):
        logger.info(f"[{self.name}] Vector Orchestrator Agent stopping cleanly.")


if __name__ == "__main__":
    VectorOrchestratorAgent().run()

