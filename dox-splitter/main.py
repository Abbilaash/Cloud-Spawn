#!/usr/bin/env python3
import os
import glob
import time
import sys
import logging
from typing import List, Dict, Any

# Formicx Agent SDK
from formicx import Agent

# Text processing & Machine Learning libraries (Pure scikit-learn + docx/pypdf)
import docx
import pypdf
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import AgglomerativeClustering

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("docx-splitter")

# Ensure Backend path is in sys.path so 'app' package can be imported
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from app.core.logger_handler import system_log_handler
    if system_log_handler not in logger.handlers:
        logger.addHandler(system_log_handler)
except Exception as e:
    logger.warning(f"Could not load system_log_handler: {e}")



class DocumentSplitterAgent(Agent):
    """Formicx Agent that performs dynamic text extraction and similarity clustering on DOCX and PDF files."""

    def on_start(self):
        logger.info(f"[{self.name}] Document Splitter Agent started with ID: {self.id}")
        logger.info(f"[{self.name}] Text vectorizer and clustering engine ready.")
        sys.stdout.flush()

    def _extract_text_from_docx(self, file_path: str) -> str:
        try:
            doc = docx.Document(file_path)
            paragraphs = [p.text.strip() for p in doc.paragraphs if p.text and p.text.strip()]
            return " ".join(paragraphs)
        except Exception as e:
            logger.error(f"Error reading DOCX file {file_path}: {str(e)}")
            return ""

    def _extract_text_from_pdf(self, file_path: str) -> str:
        page_texts = []
        # 1. Attempt pypdf with strict=False
        try:
            reader = pypdf.PdfReader(file_path, strict=False)
            for page in reader.pages:
                try:
                    text = page.extract_text()
                    if text and text.strip():
                        page_texts.append(text.strip())
                except Exception as pe:
                    logger.warning(f"Notice extracting PDF page text from '{file_path}': {str(pe)}")
            if page_texts:
                return " ".join(page_texts)
        except Exception as e:
            logger.warning(f"pypdf reader notice for PDF file '{file_path}': {str(e)}")

        # 2. Binary stream fallback with strict=False
        try:
            with open(file_path, "rb") as f:
                reader = pypdf.PdfReader(f, strict=False)
                for page in reader.pages:
                    try:
                        text = page.extract_text()
                        if text and text.strip():
                            page_texts.append(text.strip())
                    except Exception:
                        pass
            return " ".join(page_texts)
        except Exception as e2:
            logger.error(f"Error reading PDF file {file_path}: {str(e2)}")
            return ""

    def process_document_clustering(
        self,
        folder_path: str,
        distance_threshold: float = 0.6
    ) -> Dict[str, Any]:
        """Reads documents from folder, extracts text, computes TF-IDF vector embeddings, and dynamically clusters documents."""
        start_time = time.time()

        if not os.path.exists(folder_path):
            return {
                "status": "error",
                "message": f"Specified folder path '{folder_path}' does not exist."
            }

        # Discover DOCX and PDF files
        files = [
            f for f in glob.glob(os.path.join(folder_path, "*"))
            if f.lower().endswith((".docx", ".pdf")) and not os.path.basename(f).startswith("~$")
        ]

        total_discovered = len(files)
        if total_discovered == 0:
            return {
                "status": "error",
                "message": f"No .docx or .pdf files found in '{folder_path}'."
            }

        logger.info(f"Found {total_discovered} documents in '{folder_path}'. Extracting text...")

        valid_files: List[str] = []
        texts: List[str] = []

        for file_path in files:
            filename = os.path.basename(file_path)
            if file_path.lower().endswith(".docx"):
                text = self._extract_text_from_docx(file_path)
            elif file_path.lower().endswith(".pdf"):
                text = self._extract_text_from_pdf(file_path)
            else:
                text = ""

            if text and text.strip():
                valid_files.append(filename)
                texts.append(text.strip())
            else:
                logger.warning(f"Skipping empty or unreadable file: {filename}")

        if not texts:
            return {
                "status": "error",
                "message": "All discovered files were empty or unreadable."
            }

        # Edge Case: 1 Document
        if len(texts) == 1:
            processing_time = round(time.time() - start_time, 2)
            return {
                "status": "success",
                "agent_name": self.name,
                "total_documents": 1,
                "cluster_count": 1,
                "distance_threshold": distance_threshold,
                "processing_time_seconds": processing_time,
                "clusters": [
                    {
                        "cluster_id": 0,
                        "size": 1,
                        "documents": [valid_files[0]]
                    }
                ]
            }

        # 1. Generate TF-IDF Document Feature Vector Matrix (Shape: N x Vocabulary)
        logger.info(f"Generating TF-IDF vector representations for {len(texts)} documents...")
        vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        embeddings = vectorizer.fit_transform(texts).toarray()

        # 2. Dynamic Agglomerative Clustering
        logger.info(f"Clustering with distance_threshold={distance_threshold}...")
        clustering_model = AgglomerativeClustering(
            n_clusters=None,
            distance_threshold=distance_threshold,
            metric="cosine",
            linkage="average"
        )
        cluster_labels = clustering_model.fit_predict(embeddings)

        # 3. Group documents into clusters
        clusters_map: Dict[int, List[str]] = {}
        for filename, label in zip(valid_files, cluster_labels):
            label_int = int(label)
            if label_int not in clusters_map:
                clusters_map[label_int] = []
            clusters_map[label_int].append(filename)

        structured_clusters = []
        for cluster_id, doc_list in sorted(clusters_map.items()):
            structured_clusters.append({
                "cluster_id": cluster_id,
                "size": len(doc_list),
                "documents": doc_list
            })

        processing_time = round(time.time() - start_time, 2)
        logger.info(f"Clustering complete. Formed {len(structured_clusters)} dynamic clusters in {processing_time}s.")

        return {
            "status": "success",
            "agent_name": self.name,
            "total_documents": len(valid_files),
            "cluster_count": len(structured_clusters),
            "distance_threshold": distance_threshold,
            "processing_time_seconds": processing_time,
            "clusters": structured_clusters
        }

    def on_message(self, message):
        """Formicx IPC message handler."""
        payload = message.payload or {}
        logger.info(f"[{self.name}] Received message from '{message.sender}' (ID={message.message_id})")

        action = payload.get("action", "cluster_documents")
        folder_path = payload.get("folder_path", "./documents")
        threshold = float(payload.get("distance_threshold", 0.6))

        if action in ["cluster_documents", "split_documents"]:
            result = self.process_document_clustering(
                folder_path=folder_path,
                distance_threshold=threshold
            )
            self.reply(message, payload=result)
            logger.info(f"[{self.name}] Sent response payload back to '{message.sender}'.")
        else:
            self.reply(message, payload={
                "status": "error",
                "message": f"Unsupported action: '{action}'."
            })

    def on_stop(self):
        logger.info(f"[{self.name}] Document Splitter Agent stopping cleanly.")


if __name__ == "__main__":
    DocumentSplitterAgent().run()
