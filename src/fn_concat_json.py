import json
from typing import Any, Dict, Mapping, Union

JsonObj = Union[Mapping[str, Any], str]

def _as_obj(x: JsonObj) -> Dict[str, Any]:
    """รับ dict หรือ JSON string ที่เป็น object แล้วคืนเป็น dict"""
    if isinstance(x, str):
        parsed = json.loads(x)
        if not isinstance(parsed, dict):
            raise ValueError("JSON string ต้องเป็น object เช่น {...} ไม่ใช่ list/primitive")
        return parsed
    return dict(x)

def merge_json_concat(*objs: JsonObj, **kwargs: Any) -> Dict[str, Any]:
    """
    รวม JSON/object หลายอันเป็นอันเดียว:
    - ถ้าคีย์ชนกันและทั้งคู่เป็น list -> concat (ต่อกัน)
    - ถ้าคีย์ชนกันและทั้งคู่เป็น dict -> merge แบบ recursive
    - อื่น ๆ -> ตัวหลังทับตัวก่อน
    """
    def deep_merge(a: Dict[str, Any], b: Mapping[str, Any]) -> None:
        for k, v in b.items():
            if k not in a:
                a[k] = v
                continue

            av = a[k]
            if isinstance(av, dict) and isinstance(v, dict):
                deep_merge(av, v)
            elif isinstance(av, list) and isinstance(v, list):
                av.extend(v)  # concat list
            else:
                a[k] = v      # override

    out: Dict[str, Any] = {}
    for o in objs:
        deep_merge(out, _as_obj(o))
    if kwargs:
        deep_merge(out, kwargs)
    return out

a = {"model": "google/gemini-2.5-flash", "plugins": [{"id": "file-parser"}]}
b = {"temperature": 0, "plugins": [{"id": "another-plugin"}]}
c = '{"messages":[{"role":"user","content":"hi"}]}'


payload = merge_json_concat(a, b, c)

print(json.dumps(payload, ensure_ascii=False, indent=2))