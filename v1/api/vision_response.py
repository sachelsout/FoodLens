import json
import re
from typing import Any, Dict


def _extract_json_text(raw_content: Any) -> str:
    # Support providers that return arrays for multimodal content
    if isinstance(raw_content, list):
        # Concatenate any text segments
        text_parts = []
        for part in raw_content:
            if isinstance(part, dict) and part.get("type") == "text":
                text_parts.append(part.get("text", ""))
            elif isinstance(part, str):
                text_parts.append(part)
        raw_content = "\n".join([t for t in text_parts if t])

    if not isinstance(raw_content, str):
        return ""

    text = raw_content.strip()

    # Strip Markdown fences if present
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, flags=re.IGNORECASE)
    if fence_match:
        return fence_match.group(1).strip()

    # Try to find the first JSON object or array in the text
    obj_match = re.search(r"(\{[\s\S]*\})", text)
    arr_match = re.search(r"(\[[\s\S]*\])", text)
    if obj_match:
        return obj_match.group(1)
    if arr_match:
        return arr_match.group(1)

    return text


def structure_response(llm_result: Dict[str, Any]) -> Dict[str, Any]:
    if not llm_result:
        return {"error": "Empty LLM result"}
    try:
        message = llm_result["choices"][0]["message"]
        content = message.get("content")
        json_text = _extract_json_text(content)
        structured = json.loads(json_text)

        # Basic normalization
        if not isinstance(structured, dict):
            structured = {"categories": structured}
        structured.setdefault("categories", [])
        for category in structured.get("categories", []) or []:
            category.setdefault("name", "")
            category.setdefault("items", [])
            for item in category.get("items", []) or []:
                item.setdefault("name", "")
                item.setdefault("description", "")
                item.setdefault("price", "")
        return structured
    except Exception as e:
        return {"error": f"Failed to parse LLM output: {e}"}
