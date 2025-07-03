import os
from fastapi import FastAPI
from pydantic import BaseModel
from iointel import Agent, PersonaConfig
import uvicorn
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from fastmcp import Client
import asyncio
import logging
import json
import re

# Load environment variables from .env if present
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PersonaTraits(BaseModel):
    name: str
    age: int
    role: str
    style: str
    bio: str
    emotional_stability: float
    friendliness: float
    creativity: float
    curiosity: float
    formality: float
    empathy: float
    humor: float
    domain_knowledge: list[str] = []
    quirks: str = ""
    lore: str = ""
    personality: str = ""
    conversation_style: str = ""
    description: str = ""
    model: str = None

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    traits: PersonaTraits
    history: list[Message] = []
    model: Optional[str] = None
    mcpServer: Optional[str] = None
    lang: Optional[str] = None

class SafeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        return str(obj)

# Hardcoded list of available models and descriptions
AVAILABLE_MODELS = [
    {"id": "deepseek-ai/DeepSeek-R1-0528", "name": "DeepSeek-R1-0528", "description": "DeepSeek R1 v0528: Top-tier reasoning, math, programming, and logic. Nears OpenAI o3 and Gemini 2.5 Pro."},
    {"id": "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8", "name": "Llama-4-Maverick-17B-128E-Instruct-FP8", "description": "Llama 4 Maverick 17B: Best multimodal, beats GPT-4o/Gemini 2.0 Flash, rivals DeepSeek v3 in reasoning/coding."},
    {"id": "Qwen/Qwen3-235B-A22B-FP8", "name": "Qwen3-235B-A22B-FP8", "description": "Qwen3 235B: Advanced reasoning, instruction-following, agent capabilities, and multilingual support."},
    {"id": "google/gemma-3-27b-it", "name": "Gemma-3-27b-it", "description": "Gemma 3 27B: Multimodal, text/image input, open weights, instruction-tuned."},
    {"id": "meta-llama/Llama-3.3-70B-Instruct", "name": "Llama-3.3-70B-Instruct", "description": "Llama 3.3 70B: SFT and RLHF tuned, optimized transformer, helpful and safe."},
    {"id": "mistralai/Devstral-Small-2505", "name": "Devstral-Small-2505", "description": "Devstral Small: SWE-bench #1, excels at codebase exploration and software engineering agents."},
    {"id": "mistralai/Magistral-Small-2506", "name": "Magistral-Small-2506", "description": "Magistral Small: Long reasoning chains, highly multilingual."},
    {"id": "deepseek-ai/DeepSeek-R1", "name": "DeepSeek-R1", "description": "DeepSeek R1: First-gen reasoning, RL-trained, strong in math/code/reasoning."},
    {"id": "deepseek-ai/DeepSeek-R1-Distill-Llama-70B", "name": "DeepSeek-R1-Distill-Llama-70B", "description": "DeepSeek-R1-Distill Llama 70B: Fine-tuned Llama 3.3 70B, improved configs/tokenizers."},
    {"id": "netease-youdao/Confucius-o1-14B", "name": "Confucius-o1-14B", "description": "Confucius-o1-14B: o1-like reasoning, lightweight, based on Qwen2.5-14B-Instruct."},
    {"id": "nvidia/AceMath-7B-Instruct", "name": "AceMath-7B-Instruct", "description": "AceMath 7B: Excels at English math problems with Chain-of-Thought reasoning."},
    {"id": "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B", "name": "DeepSeek-R1-Distill-Qwen-32B", "description": "DeepSeek-R1-Distill Qwen-32B: Fine-tuned Qwen-32, improved configs/tokenizers."},
    {"id": "mistralai/Mistral-Large-Instruct-2411", "name": "Mistral-Large-Instruct-2411", "description": "Mistral Large 123B: State-of-the-art reasoning, coding, long context, function calling."},
    {"id": "microsoft/phi-4", "name": "phi-4", "description": "Phi-4 14B: SLM excelling at complex reasoning, math, and language processing."},
    {"id": "bespokelabs/Bespoke-Stratos-32B", "name": "Bespoke-Stratos-32B", "description": "Bespoke-Stratos-32B: Fine-tuned Qwen2.5-32B-Instruct, distilled from DeepSeek-R1."},
    {"id": "THUDM/glm-4-9b-chat", "name": "glm-4-9b-chat", "description": "GLM-4-9B: Open-source, latest pre-trained model in the GLM-4 series."},
    {"id": "CohereForAI/aya-expanse-32b", "name": "aya-expanse-32b", "description": "Aya Expanse 32B: Advanced multilingual open-weight research model."},
    {"id": "openbmb/MiniCPM3-4B", "name": "MiniCPM3-4B", "description": "MiniCPM3-4B: 32k context, LLMxMapReduce, infinite context handling."},
    {"id": "mistralai/Ministral-8B-Instruct-2410", "name": "Ministral-8B-Instruct-2410", "description": "Ministral 8B: Instruct fine-tuned, outperforms similar size models."},
    {"id": "ibm-granite/granite-3.1-8b-instruct", "name": "granite-3.1-8b-instruct", "description": "Granite-3.1-8B-Instruct: Long-context, open-source, instruction-tuned."},
]

async def get_mcp_tools(mcp_url):
    if not mcp_url:
        return "No tools available"
    try:
        async with Client(mcp_url) as client:
            tools = await client.list_tools()
            # Show name, description, and parameters for each tool
            tool_descriptions = []
            for tool in tools:
                desc = f"- {getattr(tool, 'name', str(tool))}: {getattr(tool, 'description', '')}"
                params = getattr(tool, 'parameters', None)
                if params:
                    desc += f"\n    Parameters: {json.dumps(params, ensure_ascii=False)}"
                tool_descriptions.append(desc)
            return "\n".join(tool_descriptions)
    except Exception as e:
        return f"Error fetching tools: {e}"

async def call_mcp_tool(mcp_url, tool_name, params):
    if not mcp_url:
        # No MCP server selected, do not call any tool
        return None
    try:
        async with Client(mcp_url) as client:
            return await client.call_tool(tool_name, params)
    except Exception as e:
        return {"error": str(e)}

def extract_first_json(text):
    # Try direct JSON parse first
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass
    # Fallback: extract first {...} block
    match = re.search(r'({.*})', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass
    return None

@app.post("/chat")
async def chat(req: ChatRequest):
    print("[DEBUG] /chat endpoint called")
    persona = PersonaConfig(
        name=req.traits.name,
        age=req.traits.age,
        role=req.traits.role,
        style=req.traits.style,
        bio=req.traits.bio,
        emotional_stability=req.traits.emotional_stability,
        friendliness=req.traits.friendliness,
        creativity=req.traits.creativity,
        curiosity=req.traits.curiosity,
        formality=req.traits.formality,
        empathy=req.traits.empathy,
        humor=req.traits.humor,
        domain_knowledge=req.traits.domain_knowledge,
        quirks=req.traits.quirks,
        lore=req.traits.lore,
        personality=req.traits.personality,
        conversation_style=req.traits.conversation_style,
        description=req.traits.description,
    )
    print("[DEBUG]Received persona traits:", json.dumps(persona.dict(), indent=2, ensure_ascii=False))
    model_name = req.model or "meta-llama/Llama-3.3-70B-Instruct"
    mcp_url = req.mcpServer  # None means LLM only
    tools_context = await get_mcp_tools(mcp_url)
    print(f"[DEBUG] tools_context for LLM:\n{tools_context}")
    lang_instruction = ""
    if req.lang:
        lang_instruction = f"Always answer in the language: {req.lang}."
    instructions = (
        #f"You are {persona.name}, {persona.role}. Respond in a {persona.style} style. "
        f"{lang_instruction}\n"
        f"You have access to the following tools (with parameters):\n{tools_context}\n"
        "If you need to use a tool, respond ONLY with a JSON object in the following format:\n"
        '{"tool_call": {"tool": "<tool_name>", "params": {<params>}}}'
        "\nIf no tool is relevant, answer the user's question using your own knowledge as usual. Otherwise, respond with a natural language answer."
    )
    print(f"[DEBUG] LLM instructions:\n{instructions}")
    agent = Agent(
        name=persona.name,
        instructions=instructions,
        persona=persona,
        model=model_name,
        api_key=os.environ.get("IO_API_KEY")
    )
    # Build conversation prompt from history
    prompt = ""
    for msg in req.history:
        role = "User" if msg.role == "user" else "Assistant"
        prompt += f"{role}: {msg.content}\n"
    prompt += f"User: {req.message}\nAssistant:"
    response = await agent.run(prompt)
    print(f"[DEBUG] Initial LLM response: {response}")
    parsed = None
    if isinstance(response, dict) and "result" in response:
        parsed = extract_first_json(response["result"])
        print(f"[DEBUG] extract_first_json parsed: {parsed}")
        if isinstance(parsed, dict) and "tool_call" in parsed:
            response = parsed
            print("[DEBUG] Parsed tool_call from string result.")
    elif isinstance(response, str):
        parsed = extract_first_json(response)
        print(f"[DEBUG] extract_first_json parsed: {parsed}")
        if isinstance(parsed, dict) and "tool_call" in parsed:
            response = parsed
            print("[DEBUG] Parsed tool_call from string response.")

    print(f"[DEBUG] After parsing, response is: {response}")
    print(f"[DEBUG] Entering tool call loop with response: {response}")
    max_tool_loops = 3
    loops = 0
    while isinstance(response, dict) and "tool_call" in response and loops < max_tool_loops:
        tool_name = response["tool_call"].get("tool")
        params = response["tool_call"].get("params", {})
        tool_result = await call_mcp_tool(mcp_url, tool_name, params)
        print(f"[DEBUG] Tool result for {tool_name}: {tool_result}")
        # Convert CallToolResult to a serializable dict or string
        if hasattr(tool_result, 'output'):
            serializable_result = tool_result.output
        elif hasattr(tool_result, 'result'):
            serializable_result = tool_result.result
        else:
            try:
                serializable_result = tool_result.__dict__
            except Exception:
                serializable_result = str(tool_result)
        tool_result_str = json.dumps(serializable_result, indent=2, ensure_ascii=False, cls=SafeJSONEncoder)
        tool_prompt = (
            prompt
            + f"\n[Tool {tool_name} result: {tool_result_str}]\n"
            + "Assistant: Here is the result from the tool above. Now, answer the user's original question in clear, natural language, as if you are speaking to a human. Do NOT output any JSON or tool call. ONLY provide a helpful, conversational answer. If you cannot answer, say you do not have enough information."
        )
        print(f"[DEBUG] Tool prompt sent to LLM: {tool_prompt}")
        response = await agent.run(tool_prompt)
        print(f"[DEBUG] LLM response after tool result: {response}")
        loops += 1
        # Safeguard: if LLM outputs another tool call after tool result, break and return fallback
        if isinstance(response, dict) and "tool_call" in response:
            return {"response": "Sorry, I could not generate a natural language answer after using the tool."}
    # Ensure response is always a string for the frontend
    if isinstance(response, dict):
        main_message = response.get("result") or response.get("output") or str(response)
        return {"response": main_message}
    return {"response": response}

@app.get("/models")
def get_models():
    return {"models": AVAILABLE_MODELS}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

# To use, create a .env file in this directory with:
# IO_API_KEY=sk-... 