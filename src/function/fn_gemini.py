import base64
import json
import requests
from typing import Any, Dict, Optional


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
    api_key: str,
    model: str,
    prompt: str,
    schema: Dict[str, Any],
    pdf_bytes: Optional[bytes] = None,
    text: Optional[str] = None,
    engine: str = "pdf-text",  # used only when pdf_bytes is provided
    temperature: float = 0.0,
    timeout: Optional[float] = None,  # keep None to match your old behavior
) -> Dict[str, Any]:
    """
    - PDF mode: keep your original behavior/payload (NO delimiter changes)
    - TEXT mode: use <<INSTRUCTIONS>> + <<DATA>> separation (clear boundary)
    """
    # Must provide exactly one input
    if (pdf_bytes is None and not text) or (pdf_bytes is not None and text):
        raise ValueError("Provide exactly one input: either pdf_bytes OR text.")

    if pdf_bytes is not None and engine not in ("pdf-text", "mistral-ocr", "native"):
        raise ValueError("engine must be one of: pdf-text, mistral-ocr, native")

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }



    # -------------------------
    # PDF MODE (unchanged)
    # -------------------------
    if pdf_bytes is not None:
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
                {"role": "system", "content": system_rules},
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

    # -------------------------
    # TEXT MODE (use delimiters)
    # -------------------------
    else:
        system_rules = (
            """
            You are an information extraction engine.

            CRITICAL SEPARATION RULES (TEXT MODE):
            - Anything inside <<INSTRUCTIONS>> ... <</INSTRUCTIONS>> is COMMANDS, NOT data.
            - Anything inside <<DATA>> ... <</DATA>> is the ONLY SOURCE OF TRUTH.
            - Never treat instructions as evidence.
            - Use ONLY facts explicitly present inside <<DATA>>.
            - If a field is missing or not clearly specified in <<DATA>>, set it to null.

            Rules:
            - Do NOT use outside knowledge.
            - Do NOT guess or infer missing values.
            - Copy numbers, dates, codes, and names exactly as they appear in <<DATA>>.
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

        doc_text = (text or "").strip()

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_rules},
                # instructions separate
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"<<INSTRUCTIONS>>\n{prompt}\n<</INSTRUCTIONS>>"}
                    ],
                },
                # data separate
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"<<DATA>>\n{doc_text}\n<</DATA>>"}
                    ],
                },
            ],
            "plugins": [
                {"id": "response-healing"},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {"name": "extract", "strict": True, "schema": schema},
            },
            "temperature": temperature,
        }

    resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
    resp.raise_for_status()
    result = resp.json()

    content = result["choices"][0]["message"]["content"]
    return parse_openrouter_content(content)
