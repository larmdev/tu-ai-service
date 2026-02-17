import io
import pdfplumber

def find_first_page_non_empty(
    pdf_bytes: bytes,
    start_page: int = 1,
    min_text_chars: int = 50,
) -> int | None:
    """
    หาเลขหน้า (เริ่มนับที่ 1) ของ "หน้าแรก" ที่มีตัวอักษรจาก extract_text()
    อย่างน้อย min_text_chars ตัว โดยเริ่มตรวจจาก start_page
    ไม่พบคืน None
    """
    if not isinstance(pdf_bytes, (bytes, bytearray, memoryview)):
        raise TypeError(f"pdf_bytes must be bytes-like, got {type(pdf_bytes).__name__}")

    start_page = max(1, int(start_page))

    try:
        with pdfplumber.open(io.BytesIO(bytes(pdf_bytes))) as pdf:
            total = len(pdf.pages)
            for i in range(start_page - 1, total):
                text = (pdf.pages[i].extract_text() or "").strip()
                if len(text) >= min_text_chars:
                    return i + 1
    except Exception as e:
        raise ValueError(f"Cannot read PDF bytes: {e}") from e

    return None
