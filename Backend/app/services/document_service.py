import logging
import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import docx
import pypdf

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
        """Extract text from document (DOCX or PDF) and return chunk dictionary list."""
        pass


class LocalDocumentProcessor(DocumentProcessingInterface):
    """Local implementation of document processing supporting DOCX and PDF files."""

    def _extract_text_from_docx(self, file_path: str) -> str:
        try:
            doc = docx.Document(file_path)
            paragraphs = [p.text.strip() for p in doc.paragraphs if p.text and p.text.strip()]
            return "\n\n".join(paragraphs)
        except Exception as e:
            logger.error(f"Error reading DOCX file {file_path}: {str(e)}")
            raise ValueError(f"Failed to read DOCX file: {str(e)}")

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
                    logger.warning(f"Notice reading page in PDF '{file_path}': {str(pe)}")
            if page_texts:
                return "\n\n".join(page_texts)
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
                return "\n\n".join(page_texts)
        except Exception as e2:
            logger.error(f"Error reading PDF file {file_path}: {str(e2)}")
            return ""

    def extract_text_and_chunk(
        self,
        file_path: str,
        document_id: str,
        filename: str,
        chunk_size: int = 800,
        chunk_overlap: int = 100
    ) -> List[Dict[str, Any]]:
        logger.info(f"Extracting text from file: {file_path} ({filename})")
        
        ext = os.path.splitext(filename)[1].lower()

        if ext == ".docx":
            full_text = self._extract_text_from_docx(file_path)
        elif ext == ".pdf":
            full_text = self._extract_text_from_pdf(file_path)
        else:
            raise ValueError(f"Unsupported file format '{ext}'. Only .docx and .pdf files are supported.")

        if not full_text or not full_text.strip():
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

        logger.info(f"Generated {len(chunks)} chunks for document_id {document_id} ({filename})")
        return chunks


def get_document_processor() -> DocumentProcessingInterface:
    return LocalDocumentProcessor()
