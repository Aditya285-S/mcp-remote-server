# remote_mcp_server.py
# from fastapi import FastAPI, Request
# from fastapi.responses import StreamingResponse
from mcp.server.fastmcp import FastMCP
import httpx
import json
from bson import ObjectId

# Fixed configuration
COPILOT_CONFIG = {
    "copilot_id": "6854f4b35bb581fb00e16840",
    "api_key": "VS9U-5NTM-JSHZ-I0AC",
    "base_url": "https://sandbox.karini.ai",
    "thread_id": "68f1efc97c30caba4676f6a0"
}

mcp = FastMCP("Karini Copilot Server", host="0.0.0.0", port=8000)

@mcp.tool()
async def ask_copilot(
    question: str,
    suggest_followup_questions: bool = False,
    files: list[dict] = None
) -> str:
    """
    Ask a question to the Karini copilot.
    
    Args:
        question: The question to ask
        suggest_followup_questions: Whether to get followup question suggestions
        files: Optional list of file objects with documents and metadata
    """
    url = f"{COPILOT_CONFIG['base_url']}/api/copilot/{COPILOT_CONFIG['copilot_id']}"
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": COPILOT_CONFIG['api_key'],
        "x-client-type": "swagger",
    }
    
    payload = {
        "request_id": str(ObjectId()),
        "question": question,
        "suggest_followup_questions": suggest_followup_questions,
        "thread": COPILOT_CONFIG['thread_id'],
    }
    
    if files:
        payload["files"] = {
            "documents": files,
            "metadata": {}
        }
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        async with client.stream("POST", url, headers=headers, json=payload) as response:
            response.raise_for_status()
            
            full_response = ""
            async for chunk in response.aiter_text():
                full_response += chunk
            
            if "#%&response&%#" in full_response:
                response_part = full_response.split("#%&response&%#")[1]
                response_part = json.loads(response_part)
                if "response" in response_part:
                    return response_part.get("response")
                return json.dumps(response_part)
            
            return full_response

if __name__ == "__main__":
    mcp.run(transport="streamable-http")