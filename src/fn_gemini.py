import base64
import json
import requests
from typing import Any, Dict


def extract_json_object(text: str) -> str | None:
    """Very small JSON 'healing': strip ``` fences and grab the outer {...}."""
    if not text:
        return None
    t = text.strip()
    t = t.replace("```json", "").replace("```", "").strip()

    start = t.find("{")
    end = t.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    return t[start : end + 1]


def parse_openrouter_content(content: Any) -> Dict[str, Any]:
    """Parse OpenRouter message.content into dict; fallback to {'_raw': ...}."""
    # Some providers might return list-of-parts; join text parts
    if isinstance(content, dict):
        return content
    
    if isinstance(content, list):
        text = "\n".join(
            p.get("text", "")
            for p in content
            if isinstance(p, dict) and p.get("type") == "text"
        ).strip()
    else:
        text = str(content or "").strip()

    if not text:
        return {}

    # 1) strict JSON
    try:
        obj = json.loads(text)
        return obj if isinstance(obj, dict) else {"_raw": text}
    except json.JSONDecodeError:
        pass

    # 2) heal
    candidate = extract_json_object(text)
    if candidate:
        try:
            obj = json.loads(candidate)
            return obj if isinstance(obj, dict) else {"_raw": text}
        except json.JSONDecodeError:
            pass

    return {"_raw": text}


def call_openrouter_pdf(
    *,
    api_key: str,
    model: str,
    prompt: str,
    schema: Dict[str, Any],
    pdf_bytes: bytes,
    engine: str = "pdf-text",  # "pdf-text" (FREE) | "mistral-ocr" (paid) | "native"
    temperature: float = 0.0,
) -> Dict[str, Any]:
    """
    Always-on:
      - response-healing plugin
      - response_format json_schema (strict)
    """
    if engine not in ("pdf-text", "mistral-ocr", "native"):
        raise ValueError("engine must be one of: pdf-text, mistral-ocr, native")

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json", "Accept": "application/json"}

    # PDF bytes -> base64 data URL
    b64 = base64.b64encode(pdf_bytes).decode("utf-8")
    data_url = f"data:application/pdf;base64,{b64}"


    system_rules = (
        """
        You are an information extraction engine.

        Rules:
        - Use ONLY information that is explicitly present in the provided document (PDF/TXT).
        - Do NOT use outside knowledge.
        - Do NOT guess or infer missing values.
        - If a field is missing or not clearly specified, set it to null.
        - Copy numbers, dates, codes, and names exactly as they appear.
        - If you are uncertain, do not guess; use null.
        - responde same language as appear.

        Whitespace / spacing normalization:
        - You MAY fix whitespace artifacts caused by PDF/text extraction, such as:
        - random extra spaces inside a word,
        - broken words split by spaces,
        - repeated spaces,
        - stray newlines or tabs.
        - Normalize whitespace to a standard form:
        - collapse multiple spaces to a single space,
        - remove leading/trailing spaces,
        - remove stray line breaks if they break a sentence or a field value.

        Do NOT change spelling, characters, punctuation, or meaning—ONLY fix whitespace artifacts.

        Output must strictly follow the JSON schema. No extra keys, no free text.
        """
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_rules},   # ✅ ใส่ rules แยก
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "file", "file": {"filename": "document.pdf", "file_data": data_url}},
                ],
            },
        ],
        "plugins": [
            {"id": "file-parser", "pdf": {"engine": engine}},
            {"id": "response-healing"},
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {"name": "extract", "strict": True, "schema": schema},
        },
        "temperature": temperature,
    }


    resp = requests.post(url, headers=headers, json=payload)  # no timeout
    resp.raise_for_status()
    result = resp.json()

    content = result["choices"][0]["message"]["content"]
    return parse_openrouter_content(content)
