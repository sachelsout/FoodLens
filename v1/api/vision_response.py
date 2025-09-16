import json

def structure_response(llm_result: dict) -> dict:
    if not llm_result:
        return {"error": "Empty LLM result"}
    try:
        content = llm_result["choices"][0]["message"]["content"]
        structured = json.loads(content)
        return structured
    except Exception as e:
        return {"error": f"Failed to parse LLM output: {e}"}
