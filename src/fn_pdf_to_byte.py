import base64
import binascii
from typing import Any

def to_pdf_bytes(pdf: Any) -> bytes:
    """
    Accept ONE variable and normalize it into PDF bytes.

    Supported inputs:
    - bytes / bytearray: already PDF bytes
    - str: base64 string OR data URL like "data:application/pdf;base64,...."

    Returns:
    - pdf_bytes (bytes)

    Raises:
    - TypeError / ValueError when input is invalid
    """
    # 1) Already bytes
    if isinstance(pdf, (bytes, bytearray)):
        pdf_bytes = bytes(pdf)

    # 2) Base64 string (or data URL)
    elif isinstance(pdf, str):
        s = pdf.strip()

        # strip data URL prefix if present
        if s.startswith("data:"):
            parts = s.split(",", 1)
            if len(parts) == 2:
                s = parts[1].strip()

        try:
            pdf_bytes = base64.b64decode(s, validate=True)
        except (binascii.Error, ValueError) as e:
            raise ValueError("Invalid base64 PDF string") from e

    else:
        raise TypeError(f"Unsupported input type: {type(pdf).__name__}")

    # Quick validation: PDF header
    if not pdf_bytes.startswith(b"%PDF"):
        raise ValueError("Not a valid PDF (missing %PDF header)")

    return pdf_bytes
