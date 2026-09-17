import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import docx

logger = logging.getLogger(__name__)

class DocumentProcessingInterface(ABC):
    @abstractmethod
    def extract_text_and_chunk(
        self,
        file_path: str,
        document_id: str,
        filename: str,
        chunk_size: int = 800,
        chunk_overlap: int = 100
    ) -> List[Dict[str, Any]]:
        """Extract text from document and return chunk dictionary list."""
        pass


class LocalDocumentProcessor(DocumentProcessingInterface):
    """Local implementation of document processing using python-docx."""

    def extract_text_and_chunk(
        self,
        file_path: str,
        document_id: str,
        filename: str,
        chunk_size: int = 800,
        chunk_overlap: int = 100
    ) -> List[Dict[str, Any]]:
        logger.info(f"Extracting text from DOCX file: {file_path}")
        
        try:
            doc = docx.Document(file_path)
        except Exception as e:
            logger.error(f"Error reading docx file {file_path}: {str(e)}")
            raise ValueError(f"Failed to read DOCX file: {str(e)}")

        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text and p.text.strip()]
        full_text = "\n\n".join(paragraphs)

        if not full_text:
            logger.warning(f"No text extracted from document_id {document_id} ({filename})")
            return []

        # Word-based chunking logic
        words = full_text.split()
        chunks = []
        start = 0
        chunk_index = 0

        while start < len(words):
            end = start + chunk_size
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)

            chunks.append({
                "chunk_id": f"{document_id}_{chunk_index}",
                "document_id": document_id,
                "filename": filename,
                "chunk_index": chunk_index,
                "text": chunk_text
            })

            chunk_index += 1
            start += (chunk_size - chunk_overlap)
            if start >= len(words) or end >= len(words):
                break

        logger.info(f"Generated {len(chunks)} chunks for document_id {document_id}")
        return chunks


def get_document_processor() -> DocumentProcessingInterface:
    return LocalDocumentProcessor()
