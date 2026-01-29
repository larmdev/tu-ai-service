import requests

def load_pdf_from_url(pdf_url: str) -> bytes:
    resp = requests.get(pdf_url, timeout=30)
    resp.raise_for_status()

    content = resp.content
    if not content.startswith(b"%PDF-"):
        raise ValueError("URL does not point to a valid PDF")

    return content
