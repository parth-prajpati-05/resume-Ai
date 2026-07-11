"""
OCR Engine using Tesseract + pytesseract
Handles scanned PDF/image resumes
"""

import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import io
import os
from pathlib import Path
from typing import Optional
from loguru import logger


class OCREngine:
    """
    Extracts text from scanned images and PDFs using Tesseract OCR.
    Supports: PNG, JPG, JPEG, TIFF, and scanned PDFs.
    """

    def __init__(self, tesseract_cmd: Optional[str] = None):
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        elif os.name == "nt":
            # Windows default Tesseract path
            default_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            if os.path.exists(default_path):
                pytesseract.pytesseract.tesseract_cmd = default_path

    def extract_from_image(self, image_path: str) -> str:
        """Extract text from an image file."""
        try:
            img = Image.open(image_path)
            # Enhance image for better OCR
            img = img.convert("L")  # Grayscale
            text = pytesseract.image_to_string(img, config="--psm 6 --oem 3")
            logger.info(f"✅ OCR extracted {len(text)} chars from image")
            return text.strip()
        except Exception as e:
            logger.error(f"❌ OCR failed for image {image_path}: {e}")
            return ""

    def extract_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF, using OCR for scanned pages."""
        try:
            doc = fitz.open(pdf_path)
            full_text = ""

            for page_num, page in enumerate(doc):
                # Try native text extraction first
                text = page.get_text("text")
                
                if len(text.strip()) < 50:
                    # Page appears scanned — use OCR
                    logger.info(f"Page {page_num + 1} needs OCR")
                    pix = page.get_pixmap(dpi=300)
                    img_data = pix.tobytes("png")
                    img = Image.open(io.BytesIO(img_data)).convert("L")
                    text = pytesseract.image_to_string(img, config="--psm 6 --oem 3")

                full_text += text + "\n"

            doc.close()
            logger.info(f"✅ PDF text extracted: {len(full_text)} chars")
            return full_text.strip()
        except Exception as e:
            logger.error(f"❌ PDF OCR failed: {e}")
            return ""

    def extract_text(self, file_path: str) -> str:
        """Auto-detect file type and extract text."""
        ext = Path(file_path).suffix.lower()
        
        if ext in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
            return self.extract_from_image(file_path)
        elif ext == ".pdf":
            return self.extract_from_pdf(file_path)
        else:
            logger.warning(f"⚠️ Unsupported OCR file type: {ext}")
            return ""
