import io
from pypdf import PdfReader, PdfWriter

def concat_pdf_bytes(*pdfs: bytes) -> bytes:
    writer = PdfWriter()

    for pdf_bytes in pdfs:
        reader = PdfReader(io.BytesIO(pdf_bytes))

        if getattr(reader, "is_encrypted", False):
            try:
                reader.decrypt("")
            except Exception:
                pass

        for page in reader.pages:
            writer.add_page(page)

    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()
