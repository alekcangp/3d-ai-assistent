import os
from fastapi import FastAPI, Request
from pydantic import BaseModel
# Verifiable IO Intelligence SDK usage for GitHub audit
from iointel import Agent, PersonaConfig
import uvicorn
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from fastmcp import Client
import re
import json
import asyncio
from backend.layout_tables import LAYOUTS, LANG_CHARSETS, fix_keyboard_layout, detect_charset
try:
    from mcp_instructions import get_mcp_instructions, get_mcp_final_instructions
except ImportError:
    # Fallback to default instructions if module not found
    def get_mcp_instructions(mcp_url: str, lang_code: str, tools_context: str) -> str:
        lang_instruction = "RESPOND ONLY IN ENGLISH. Do not use any other languages." if lang_code == "en" else f"RESPOND ONLY IN {lang_code.upper()}. Do not use any other languages."
        return f"""{lang_instruction}

You have access to the following tools:
{tools_context}

CRITICAL INSTRUCTIONS FOR TOOL USAGE:

1. ONLY use tools when the user specifically requests data, information, or functionality that requires external data.

2. Do NOT use tools for: greetings, general conversation, questions about yourself, opinions, explanations, or creative writing.

3. Use tools ONLY for: specific data requests, information retrieval, or functionality that requires external access.

4. When using a tool, respond ONLY with a JSON object in this exact format:
   {{"tool_call": {{"tool": "<tool_name>", "params": {{<params>}}}}}}

5. Ensure ALL required parameters are provided. Do not use 'undefined' or empty values for required parameters.

6. For general conversation, greetings, questions about yourself, or non-data requests, respond naturally without using any tools.

7. If no tool is needed, respond naturally to the user's question.
"""

    def get_mcp_final_instructions(mcp_url: str, lang_code: str) -> str:
        lang_instruction = "RESPOND ONLY IN ENGLISH. Do not use any other languages." if lang_code == "en" else f"RESPOND ONLY IN {lang_code.upper()}. Do not use any other languages."
        return f"""{lang_instruction}

Provide clear, natural language answers to user questions.

RESPONSE FORMAT INSTRUCTIONS:
When providing final answers to users:
- Write in clear, natural language ONLY
- Format your response in Markdown for better readability
- Use **bold** for emphasis, *italic* for subtle emphasis
- Use bullet points (- or *) for lists
- Use numbered lists (1. 2. 3.) for steps or sequences
- Use `code` for technical terms, file names, or commands
- Use ```code blocks``` for longer code examples
- Use > for blockquotes when citing or emphasizing important information
- Do NOT mention which tools were used
- Do NOT show any JSON, arrays, or structured data
- Do NOT include tool call syntax or examples
- Do NOT mention 'thoughts', 'reasoning', or internal processes
- Do NOT show internal tracking data, thought numbers, or metadata
- Do NOT include any JSON objects, even if they appear in tool results
- Focus on answering the user's question directly
- ALWAYS include relevant links from the tool results when available
- Format links as [Description](URL) with descriptive text
- When discussing websites, social media, or resources, ALWAYS include the actual links
- Do not just mention that links exist - actually include them in your response
- Present information clearly and conversationally
- If there was an error, explain what went wrong and suggest alternatives
- NEVER include any JSON, even if it's part of the tool's internal process
- If you see a number that looks like a UNIX timestamp (e.g., 10 or more digits, likely in seconds since 1970), always convert it to a human-readable date in your response
- When users ask about projects, repositories, or documentation, and if the project has DeepWiki documentation available, include the DeepWiki link in format: [DeepWiki Documentation](https://deepwiki.com/owner/repo). Only include this link if you know the project has DeepWiki documentation
"""

# Load environment variables from .env if present
load_dotenv()

app = FastAPI()

# Get frontend URL from environment variable
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL
    ],
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
        # Add timeout for the tools listing
        async with Client(mcp_url, timeout=30) as client:
            tools = await client.list_tools()
            # Show name, description, and parameters for each tool
            tool_descriptions = []
            for tool in tools:
                tool_name = getattr(tool, 'name', str(tool))
                tool_desc = getattr(tool, 'description', '')
                params = getattr(tool, 'parameters', None)
                if not params:
                    params = getattr(tool, 'inputSchema', None)
                desc = f"- **{tool_name}**: {tool_desc}"
                if params and isinstance(params, dict) and 'properties' in params:
                    required_params = params.get('required', [])
                    if required_params:
                        param_lines = []
                        for param_name in required_params:
                            param_info = params['properties'].get(param_name, {})
                            param_type = param_info.get('type', 'unknown')
                            param_desc = param_info.get('description', '')
                            param_lines.append(f"    - {param_name} ({param_type}): {param_desc}")
                        if param_lines:
                            desc += "\n  Required Params:\n" + "\n".join(param_lines)
                tool_descriptions.append(desc)
            # Print the raw tools list/dict as received from the MCP server
            #print(f"[INFO] Raw tools: {tools}")
            return "\n".join(tool_descriptions)
    except Exception as e:
        error_msg = str(e)
        print(f"[DEBUG] Error fetching tools from {mcp_url}: {error_msg}")
        
        # Handle timeout errors specifically
        if "ReadTimeout" in error_msg or "timeout" in error_msg.lower():
            return f"Error: MCP server timeout. The server at {mcp_url} took too long to respond."
        
        # Handle connection errors
        if "connection" in error_msg.lower() or "unreachable" in error_msg.lower():
            return f"Error: Cannot connect to MCP server at {mcp_url}. Please check if the server is running."
        
        return f"Error fetching tools: {error_msg}"

async def call_mcp_tool(mcp_url, tool_name, params):
    if not mcp_url:
        # No MCP server selected, do not call any tool
        return None
    
    # Clean and validate parameters
    cleaned_params = {}
    for key, value in params.items():
        if value is not None and value != "undefined" and value != "":
            cleaned_params[key] = value

    #print(f"[DEBUG] Calling tool {tool_name} with params: {cleaned_params}")
    
    try:
        # Add timeout for the tool call
        async with Client(mcp_url, timeout=30.0) as client:
            return await client.call_tool(tool_name, cleaned_params)
    except Exception as e:
        error_msg = str(e)
        print(f"[DEBUG] Tool call error for {tool_name}: {error_msg}")
        
        # Handle timeout errors specifically
        if "ReadTimeout" in error_msg or "timeout" in error_msg.lower():
            return {
                "error": f"Tool {tool_name} timed out. The MCP server took too long to respond. Please try again or check if the server is available.",
                "details": error_msg
            }
        
        # Provide helpful error message for missing parameters
        if "invalid_type" in error_msg and "Required" in error_msg:
            return {
                "error": f"Tool {tool_name} requires additional parameters. Please provide the missing required parameters.",
                "details": error_msg
            }
        
        return {"error": f"MCP error: {error_msg}"}

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

def clean_html(text):
    """Strip HTML tags and convert special tags to markdown."""
    if not text:
        return text
    
    # Handle newlines first
    text = text.replace('\\n', '\n')
    
    # Handle special formatting
    text = text.replace('<Description>', '**').replace('</Description>', '**')
    text = re.sub(r'<(\/)?(Card|Tabs?|TabItem|CardGrid|LinkCard|Stream|ExternalResources|GlossaryTooltip|ResourcesBySelector)[^>]*>', '', text)
    text = re.sub(r'<\/?(th|td|tr|table|tbody)>', '', text)  # remove table formatting tags
    text = re.sub(r'<DirectoryListing\s*/>', '', text)
    text = re.sub(r':::caution', '> ⚠️ **Caution:**', text)
    text = re.sub(r':::note', '> 💡 **Note:**', text)
    text = re.sub(r':::', '', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'**\1**', text)  # bold
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'[\1](\2)', text)  # markdown links
    
    # Clean up extra whitespace and newlines
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # Remove excessive newlines
    text = re.sub(r' +', ' ', text)  # Remove multiple spaces
    
    return text.strip()

def convert_sformat_to_markdown(sformat_text):
    """Convert structured XML-like blocks to Markdown suitable for chatbot responses."""
    if not sformat_text:
        return sformat_text
    
    # First, try to find structured result blocks
    results = re.findall(r'<result>(.*?)<\/result>', sformat_text, re.DOTALL)
    
    if not results:
        # If no structured blocks found, return the original text
        return sformat_text
    
    markdown_output = []

    for result in results:
        url_match = re.search(r'<url>(.*?)<\/url>', result)
        text_match = re.search(r'<text>(.*?)<\/text>', result, re.DOTALL)

        if not url_match or not text_match:
            # If we can't parse the structure, include the raw result
            cleaned_result = clean_html(result)
            markdown_output.append(f"---\n{cleaned_result}\n")
            continue

        url = url_match.group(1).strip()
        raw_text = text_match.group(1).strip()

        # Convert headings - handle both # and ##### formats
        markdown = re.sub(r'^# ([^\n]+)', r'### \1', raw_text, flags=re.MULTILINE)
        markdown = re.sub(r'^## ([^\n]+)', r'#### \1', markdown, flags=re.MULTILINE)
        markdown = re.sub(r'^##### ([^\n]+)', r'### \1', markdown, flags=re.MULTILINE)
        markdown = re.sub(r'^###### ([^\n]+)', r'#### \1', markdown, flags=re.MULTILINE)
        
        # Clean the HTML and formatting
        markdown = clean_html(markdown)
        
        # Clean up the final markdown
        markdown = re.sub(r'\n\s*\n\s*\n', '\n\n', markdown)  # Remove excessive newlines
        markdown = re.sub(r'^\s+', '', markdown, flags=re.MULTILINE)  # Remove leading spaces
        markdown = re.sub(r'\s+$', '', markdown, flags=re.MULTILINE)  # Remove trailing spaces

        # Format each entry like a chatbot message
        # Extract domain for better link text
        domain_match = re.search(r'https?://([^/]+)', url)
        domain = domain_match.group(1) if domain_match else "Source"
        
        # Create more descriptive link text
        if "github.com" in url:
            link_text = f"GitHub Repository"
        elif "deepwiki.com" in url:
            link_text = f"DeepWiki Documentation"
        elif "developers.cloudflare.com" in url:
            link_text = f"Cloudflare Documentation"
        else:
            link_text = f"{domain} Documentation"
        
        chatbot_block = f"""---\n**{link_text}**: [{url}]({url})\n\n{markdown}\n"""
        markdown_output.append(chatbot_block)

    result_markdown = "\n".join(markdown_output)
    # Replace tabs with spaces to avoid code block rendering
    result_markdown = result_markdown.replace('\t', '    ')
    return result_markdown

def clean_tool_calls_from_response(text):
    """Remove any tool call JSON from the response text."""
    if not text:
        return text
    
    # Remove tool call JSON patterns with various formats
    patterns = [
        r'\{"tool_call":\s*\{[^}]*\}\}',  # {"tool_call": {...}}
        r'{"tool_call":\s*\{[^}]*\}\}',   # {"tool_call": {...}}
        r'or\s*{"tool_call":\s*\{[^}]*\}\}',  # or {"tool_call": {...}}
        r'{"tool_call":\s*\{[^}]*\}\}\s*or\s*{"tool_call":\s*\{[^}]*\}\}',  # Multiple tool calls
        r'To get more specific information.*?\{[^}]*"tool_call"[^}]*\}',  # Tool call with context
        r'you can use the following.*?\{[^}]*"tool_call"[^}]*\}',  # Tool call with context
        r'Thought:\s*.*?```json\s*\{[^}]*\}\s*```',  # Thought section with JSON
        r'Thought:\s*.*?\{[^}]*\}',  # Thought section with JSON
        r'```json\s*\{[^}]*\}\s*```',  # JSON code blocks
        r'\{[^}]*"thought"[^}]*\}',  # JSON with thought field
    ]
    
    cleaned = text
    for pattern in patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.DOTALL)
    
    # Clean up any leftover artifacts
    cleaned = re.sub(r'\s+or\s+$', '', cleaned)
    cleaned = re.sub(r'\s+$', '', cleaned)
    cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned)  # Remove excessive newlines
    cleaned = re.sub(r'Thought:\s*$', '', cleaned)  # Remove trailing "Thought:"
    
    return cleaned.strip()

def ensure_blank_lines_for_markdown(text):
    """Ensure there is a blank line before Markdown elements (headings, lists, blockquotes, code blocks)."""
    import re
    # Blank line before headings
    text = re.sub(r'([^\n])\n(#+ )', r'\1\n\n\2', text)
    # Blank line before unordered lists
    text = re.sub(r'([^\n])\n([-*] )', r'\1\n\n\2', text)
    # Blank line before ordered lists
    text = re.sub(r'([^\n])\n(\d+\. )', r'\1\n\n\2', text)
    # Blank line before blockquotes
    text = re.sub(r'([^\n])\n(> )', r'\1\n\n\2', text)
    # Blank line before code blocks (```) 
    text = re.sub(r'([^\n])\n(```)', r'\1\n\n\2', text)
    return text

def process_response_for_markdown(response_text):
    """Process response text to convert any structured blocks to Markdown."""
    if not response_text:
        return response_text
    # Check if the response contains structured blocks
    if '<result>' in response_text and '</result>' in response_text:
        return convert_sformat_to_markdown(response_text)
    # Check for CallToolResult format
    if 'CallToolResult' in response_text and 'TextContent' in response_text:
        return convert_calltoolresult_to_markdown(response_text)
    # If no structured blocks, ensure blank lines for all Markdown elements and return
    return ensure_blank_lines_for_markdown(response_text)

def convert_calltoolresult_to_markdown(calltoolresult_text):
    """Convert CallToolResult format to Markdown suitable for chatbot responses."""
    if not calltoolresult_text:
        return calltoolresult_text
    
    print(f"[DEBUG] Converting CallToolResult, input length: {len(calltoolresult_text)}")
    print(f"[DEBUG] Input preview: {calltoolresult_text[:200]}...")
    
    # Extract text content from CallToolResult
    text_match = re.search(r"text='([^']*(?:\\'[^']*)*)'", calltoolresult_text, re.DOTALL)
    if not text_match:
        # Try alternative pattern
        text_match = re.search(r'text="([^"]*(?:\\"[^"]*)*)"', calltoolresult_text, re.DOTALL)
    
    if text_match:
        raw_text = text_match.group(1)
        print(f"[DEBUG] Extracted text length: {len(raw_text)}")
        print(f"[DEBUG] Extracted text preview: {raw_text[:200]}...")
        
        # Unescape the text - handle various escape sequences
        raw_text = raw_text.replace("\\'", "'").replace('\\"', '"').replace('\\n', '\n')
        # Handle double backslashes first, then single backslashes
        raw_text = raw_text.replace('\\\\', '\\')  # Handle double backslashes
        raw_text = raw_text.replace('\\#', '#')    # Handle escaped hash symbols
        raw_text = raw_text.replace('\\*', '*')    # Handle escaped asterisks
        raw_text = raw_text.replace('\\[', '[')    # Handle escaped brackets
        raw_text = raw_text.replace('\\]', ']')    # Handle escaped brackets
        raw_text = raw_text.replace('\\`', '`')    # Handle escaped backticks
        raw_text = raw_text.replace('\\_', '_')    # Handle escaped underscores
        
        # Check if the content is JSON/array data
        # More sophisticated check: look for actual JSON structure, not just brackets
        raw_text_stripped = raw_text.strip()
        is_json_array = (raw_text_stripped.startswith('[') and raw_text_stripped.endswith(']') and 
                        ('{' in raw_text_stripped or '"' in raw_text_stripped or 
                         raw_text_stripped.count('[') == 1 and raw_text_stripped.count(']') == 1 and
                         len(raw_text_stripped) > 2))
        
        is_json_object = (raw_text_stripped.startswith('{') and raw_text_stripped.endswith('}') and 
                         ('"' in raw_text_stripped or ':' in raw_text_stripped))
        
        if is_json_array or is_json_object:
            # This is JSON/array data - check size and handle accordingly
            print("[DEBUG] CallToolResult contains JSON/array data")
            
            # Check if the data is too large (more than 8000 characters)
            if len(raw_text) > 3000:
                print(f"[DEBUG] JSON data is too large ({len(raw_text)} chars), summarizing for agent processing")
                # Intelligently summarize the large JSON data
                summarized_text = summarize_large_json(raw_text)
                return summarized_text
            else:
                print("[DEBUG] JSON data size is acceptable, will use agent processing")
                return None
        
        # This is simple string content - convert to Markdown
        print("[DEBUG] CallToolResult contains string data, converting to Markdown")
        
        # Clean and format the text
        markdown = clean_html(raw_text)
        
        # Replace tabs with spaces to avoid code block rendering
        markdown = markdown.replace('\t', '    ')
        
        # Clean up the final markdown
        markdown = re.sub(r'\n\s*\n\s*\n', '\n\n', markdown)  # Remove excessive newlines
        markdown = re.sub(r'^\s+', '', markdown, flags=re.MULTILINE)  # Remove leading spaces
        markdown = re.sub(r'\s+$', '', markdown, flags=re.MULTILINE)  # Remove trailing spaces
        
        print(f"[DEBUG] Final markdown length: {len(markdown)}")
        return markdown
    
    # If we can't extract text, return the original
    print("[DEBUG] Could not extract text from CallToolResult, returning original")
    return calltoolresult_text

def summarize_large_json(json_text):
    """Intelligently summarize large JSON data by extracting key information."""
    try:
        import json
        data = json.loads(json_text)
        
        if isinstance(data, list):
            # For arrays, show first few items and summary
            if len(data) > 10:
                summary = f"Array with {len(data)} items. First 5 items:\n"
                summary += json.dumps(data[:5], indent=2, ensure_ascii=False)
                summary += f"\n\n... and {len(data) - 5} more items"
                return summary
            else:
                return json.dumps(data, indent=2, ensure_ascii=False)
        
        elif isinstance(data, dict):
            # For objects, show key structure and first few values
            keys = list(data.keys())
            if len(keys) > 10:
                summary = f"Object with {len(keys)} keys: {', '.join(keys[:5])}...\n"
                summary += "First few key-value pairs:\n"
                for i, key in enumerate(keys[:5]):
                    summary += f"  {key}: {str(data[key])[:100]}...\n"
                summary += f"\n... and {len(keys) - 5} more keys"
                return summary
            else:
                return json.dumps(data, indent=2, ensure_ascii=False)
        
        else:
            return str(data)
            
    except Exception as e:
        print(f"[DEBUG] Error parsing JSON: {e}")
        # Fallback to simple truncation
        return json_text[:8000] + "\n\n... (data truncated due to parsing error)"

def format_urls_in_text(text):
    """Format long URLs in text to be more readable with descriptive link text."""
    if not text:
        return text
    
    # Common URL patterns to format with proper Markdown links
    url_patterns = [
        (r'https://drive\.google\.com/file/d/([a-zA-Z0-9_-]+)/view', r'[Google Drive Document](https://drive.google.com/file/d/\1/view)'),
        (r'https://bscscan\.com/token/([a-zA-Z0-9]+)', r'[BSCScan Token](https://bscscan.com/token/\1)'),
        (r'https://etherscan\.io/token/([a-zA-Z0-9]+)', r'[Etherscan Token](https://etherscan.io/token/\1)'),
        (r'https://www\.reddit\.com', r'[Reddit](https://www.reddit.com)'),
        (r'https://t\.me/([a-zA-Z0-9_]+)', r'[Telegram Channel](https://t.me/\1)'),
        (r'https://twitter\.com/([a-zA-Z0-9_]+)', r'[Twitter](https://twitter.com/\1)'),
        (r'https://github\.com/([a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+)', r'[GitHub Repository](https://github.com/\1)'),
        (r'https://([a-zA-Z0-9.-]+)\.io', r'[Website](https://\1.io)'),
        (r'https://([a-zA-Z0-9.-]+)\.com', r'[Website](https://\1.com)'),
    ]
    
    formatted_text = text
    
    for pattern, replacement in url_patterns:
        formatted_text = re.sub(pattern, replacement, formatted_text)
    
    return formatted_text

def detect_charset(text: str):
    counts = {lang: sum(c in charset for c in text) for lang, charset in LANG_CHARSETS.items()}
    # Возвращаем язык с максимальным количеством совпадений
    return max(counts, key=counts.get)

def fix_keyboard_layout(text: str, from_lang: str, to_lang: str) -> str:
    layout = LAYOUTS.get((from_lang, to_lang))
    if layout:
        return ''.join(layout.get(c, c) for c in text)
    return text

def summarize_tool_result(result, max_items=3, max_chars=500):
    if isinstance(result, list):
        preview = result[:max_items]
        return f"[{', '.join(map(str, preview))} ...] (showing {min(len(result), max_items)} of {len(result)})"
    elif isinstance(result, dict):
        keys = list(result.keys())
        preview = {k: result[k] for k in keys[:max_items]}
        return f"{{{', '.join(f'{k}: {repr(v)[:60]}' for k, v in preview.items())} ...}} (showing {min(len(keys), max_items)} of {len(keys)} keys)"
    elif isinstance(result, str) and len(result) > max_chars:
        return result[:max_chars] + " ... (truncated)"
    return result

def remove_unwanted_code_indentation(text):
    """Remove leading 4+ spaces from lines not inside code blocks."""
    lines = text.split('\n')
    in_code_block = False
    for i, line in enumerate(lines):
        # Detect start/end of code block
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            continue
        if not in_code_block:
            # Remove leading 4+ spaces (but not if the line is empty)
            lines[i] = re.sub(r'^( {4,})', '', line)
    return '\n'.join(lines)

def auto_wrap_code_blocks(text):
    """Auto-wrap blocks of 2+ consecutive lines starting with 4+ spaces or tabs in triple backticks."""
    import re
    lines = text.split('\n')
    new_lines = []
    in_code = False
    code_block = []
    for line in lines:
        if re.match(r'^( {4,}|\t+)', line):
            code_block.append(line.lstrip())
            in_code = True
        else:
            if in_code and code_block:
                new_lines.append('```css')  # Use 'css' for CSS, or just '```' for generic
                new_lines.extend(code_block)
                new_lines.append('```')
                code_block = []
                in_code = False
            new_lines.append(line)
    # If code block at end
    if code_block:
        new_lines.append('```css')
        new_lines.extend(code_block)
        new_lines.append('```')
    return '\n'.join(new_lines)

def replace_all_tabs(text):
    # Replace both escaped tabs (\\t) and literal tabs (\t) with spaces
    return text.replace('\\t', '    ').replace('\t', '    ')

def clean_markdown_artifacts(text):
    import re
    # Remove lines with unrecognized tags
    text = re.sub(r'^<[^>]+>$', '', text, flags=re.MULTILINE)
    # Remove <Feature ...>, <Details ...>, <Steps>, <ListExamples ...>, <YouTubeVideos ...>, <RelatedProduct ...>
    text = re.sub(r'<(Feature|Details|Steps|ListExamples|YouTubeVideos|RelatedProduct)[^>]*>', '', text, flags=re.MULTILINE)
    # Convert *** to ---
    text = re.sub(r'^\*{3,}$', '---', text, flags=re.MULTILINE)
    # Remove leading 4+ spaces outside code blocks
    lines = text.split('\n')
    in_code = False
    for i, line in enumerate(lines):
        if line.strip().startswith('```'):
            in_code = not in_code
            continue
        if not in_code:
            lines[i] = re.sub(r'^( {4,})', '', line)
    return '\n'.join(lines)

def truncate_json_array(data, max_items=50):
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, list) and len(v) > max_items:
                data[k] = v[:max_items]
            elif isinstance(v, dict):
                data[k] = truncate_json_array(v, max_items)
        return data
    elif isinstance(data, list) and len(data) > max_items:
        return data[:max_items]
    return data

@app.post("/chat")
async def chat(req: ChatRequest):
    #print(f"[DEBUG] Received request with lang: {req.lang}")
    print(f"[DEBUG] Request message: {req.message}")
    
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
    #print("[DEBUG]Received persona traits:", json.dumps(persona.model_dump(), indent=2, ensure_ascii=False))
    model_name = req.model or "meta-llama/Llama-3.3-70B-Instruct"
    mcp_url = req.mcpServer  # None means LLM only

    try:
        tools_context = await asyncio.wait_for(get_mcp_tools(mcp_url), timeout=30)
        print(f"[STATUS] tools got")
        print(f"[DEBUG] Tools context size: {len(str(tools_context))} characters")
        #print(f"[INFO] Tools for LLM:\n{tools_context}")

    except asyncio.TimeoutError:
        tools_context = "Error: MCP server did not respond in time."
        print("[DEBUG] MCP server timeout.")
    except Exception as e:
        error_msg = str(e)
        print(f"[DEBUG] MCP server error: {error_msg}")
        if "ReadTimeout" in error_msg or "timeout" in error_msg.lower():
            tools_context = "Error: MCP server timeout. The server took too long to respond."
        elif "connection" in error_msg.lower():
            tools_context = "Error: Cannot connect to MCP server. Please check if the server is available."
        else:
            tools_context = f"Error: {error_msg}"
   
    if isinstance(tools_context, str) and tools_context.startswith("Error:"):
        # MCP unavailable: skip tool logic, answer as LLM-only
        tools_context = "No tools available"
    
    # Print the length of the tools context if it is a list or dict
    if isinstance(tools_context, (list, dict)):
        print(f"[INFO] Number of tools: {len(tools_context)}")
    
    # Initialize language variables
    lang_code = "en"  # default
    lang_instruction = ""
    
    if req.lang:
        lang_code = req.lang.split('-')[0]
        lang_instruction = f"CRITICAL: You MUST respond in the user's language (code: {lang_code}) ONLY. Do not use any other language."
        #print(f"[DEBUG] Language set to: {lang_code}")
        #print(f"[DEBUG] Language instruction: {lang_instruction}")
    else:
        print("[DEBUG] No language specified in request")
    
    #print(f"[DEBUG] Final lang_code: {lang_code}")
    #print(f"[DEBUG] Final lang_instruction: {lang_instruction}")
    
    # Get MCP-specific instructions
    tool_selection_instructions = get_mcp_instructions(mcp_url, lang_code, tools_context)
    
    # Get MCP-specific final instructions
    final_answer_instructions = get_mcp_final_instructions(mcp_url, lang_code)
    
    # Build conversation prompt from history (only user and assistant messages)
    prompt = ""
    for msg in req.history:
        if msg.role in ["user", "assistant"] and isinstance(msg.content, str) and msg.content.strip():
            role = "User" if msg.role == "user" else "Assistant"
            prompt += f"{role}: {msg.content}\n"
    prompt += f"User: {req.message}\nAssistant:"

    # Print the total length of the full context (instructions + prompt) sent to the LLM
    full_context = str(tool_selection_instructions) + str(prompt)
    print(f"[INFO] Total LLM context length: {len(full_context)} characters")

    agent = Agent(
        name=persona.name,
        instructions=tool_selection_instructions,
        persona=persona,
        model=model_name,
        api_key=os.environ.get("IO_API_KEY")
    )
    #print(f"[DEBUG] Final prompt sent to LLM:\n{tool_selection_instructions}\n---\n{prompt}\n---")
   
    response = await agent.run(prompt)
    print(f"[DEBUG] LLM output after tool call:\n{response}")
   
    # Check if the initial response contains structured <result> blocks
    #if isinstance(response, str) and '<result>' in response and '</result>' in response:
    #    print("[DEBUG] Initial response contains structured result blocks, converting directly to Markdown")
    #    markdown_result = convert_sformat_to_markdown(response)
    #    return {"response": markdown_result}
    
    parsed = None
    if isinstance(response, dict) and "result" in response:
       # print("[DEBUG] Response is dict with 'result' key")
        parsed = extract_first_json(response["result"])
        #print(f"[DEBUG] Parsed from dict result: {parsed}")
      
        if isinstance(parsed, dict) and "tool_call" in parsed:
           # print("[DEBUG] Found tool_call in parsed dict result")
            response = parsed
           
    elif isinstance(response, str):
        print("[DEBUG] Response is string, trying to extract JSON")
        parsed = extract_first_json(response)
       # print(f"[DEBUG] Parsed from string: {parsed}")
       
        if isinstance(parsed, dict) and "tool_call" in parsed:
            #print("[DEBUG] Found tool_call in parsed string")
            response = parsed
           

    
 
    max_tool_loops = 3
    loops = 0
    while isinstance(response, dict) and "tool_call" in response and loops < max_tool_loops:
        print("[STATUS] llm choosed tool")
        tool_name = response["tool_call"].get("tool")
        params = response["tool_call"].get("params", {})
        print(f"[STATUS] calling tool: {tool_name}")
        
        # Check if MCP server is available
        if not mcp_url:
            print("[DEBUG] No MCP server available, cannot call tool")
            return {"response": f"I cannot call the tool '{tool_name}' because no MCP server is configured. Please configure an MCP server to use this functionality."}
        
        # Check if the tool exists in available tools
        if isinstance(tools_context, str) and "Error:" in tools_context:
            print(f"[DEBUG] Tools context has error: {tools_context}")
            return {"response": f"I cannot call the tool '{tool_name}' because there was an error connecting to the MCP server: {tools_context}"}
        
        # Check if the tool name is actually available in the tools context
        if isinstance(tools_context, str) and tool_name not in tools_context:
            print(f"[DEBUG] Tool '{tool_name}' not found in available tools: {tools_context}")
            return {"response": f"I cannot call the tool '{tool_name}' because it's not available. Please ask me about cryptocurrency data using the available tools."}
        
       # print(f"[DEBUG] Tools context available: {len(str(tools_context))} chars")
        
        try:
            tool_result = await asyncio.wait_for(call_mcp_tool(mcp_url, tool_name, params), timeout=60)
        except asyncio.TimeoutError:
            print(f"[DEBUG] Tool call timeout for {tool_name}")
            tool_result = {
                "error": f"Tool {tool_name} timed out. The MCP server took too long to respond.",
                "details": "Timeout after 60 seconds"
            }
        except Exception as e:
            print(f"[DEBUG] Tool call exception for {tool_name}: {e}")
            error_msg = str(e)
            if "Unknown tool" in error_msg:
                tool_result = {"error": f"The tool '{tool_name}' is not available. Please use one of the available tools for cryptocurrency data."}
            else:
                tool_result = {"error": f"Tool call failed: {error_msg}"}
        
        # DEBUG: print raw tool_result
        print(f"[DEBUG] Raw tool_result for {tool_name}: {repr(tool_result)}")

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
        
        # Универсальная обработка результата инструмента
        readable_result = None
        # Попытка извлечь текст из CallToolResult/content/TextContent
        if isinstance(serializable_result, dict) and 'content' in serializable_result:
            content = serializable_result['content']
            if isinstance(content, list) and content:
                text_item = content[0]
                text = getattr(text_item, 'text', None) or (text_item.get('text') if isinstance(text_item, dict) else None)
                if text:
                    try:
                        parsed = json.loads(text)
                        parsed = truncate_json_array(parsed, max_items=10)
                        pretty = json.dumps(parsed, indent=2, ensure_ascii=False)
                        if len(pretty) < 10000:
                            readable_result = pretty
                        else:
                            readable_result = pretty[:10000] + "\n... (truncated)"
                    except Exception:
                        readable_result = text if len(text) < 10000 else text[:10000] + "\n... (truncated)"
        # Если не CallToolResult, но результат простой (dict, list, str)
        if readable_result is None:
            if isinstance(serializable_result, (dict, list)):
                try:
                    result_str = json.dumps(serializable_result, indent=2, ensure_ascii=False)
                except Exception:
                    result_str = str(serializable_result)
                if len(result_str) < 10000:
                    readable_result = result_str
                else:
                    readable_result = result_str[:10000] + "\n... (truncated)"
            elif isinstance(serializable_result, str):
                readable_result = serializable_result if len(serializable_result) < 10000 else serializable_result[:10000] + "\n... (truncated)"
        if not readable_result:
            readable_result = summarize_tool_result(serializable_result)
        print(f"[DEBUG] readable_result for {tool_name}: {repr(readable_result)}")
        summarized_result = readable_result
        summarized_result_str = str(summarized_result)
        # Create a new agent with final answer instructions for processing tool results
        final_answer_agent = Agent(
            name=persona.name,
            instructions=final_answer_instructions,
            persona=persona,
            model=model_name,
        )
        tool_prompt = (
            prompt
            + f"\n[Tool {tool_name} result: {summarized_result_str}]\n"
            + f"CRITICAL: You MUST respond in the user's language (code: {lang_code}) ONLY. Do not use any other language.\n"
            + "Assistant: Based on the tool result above, provide a helpful answer to the user's original question. "
            + "IMPORTANT: If the tool result contains any URLs or links, you MUST include them in your response. "
            + "Format all links as [Description](URL) with descriptive text. "
            + "Do not just mention that links exist - actually include them in your response."
        )
        print(f"[DEBUG] tool_prompt for {tool_name}: {tool_prompt}")
        # Print the total length of the full context (final instructions + tool_prompt) for the final answer
        final_full_context = str(final_answer_instructions) + str(tool_prompt)
        print(f"[INFO] Total FINAL LLM context length: {len(final_full_context)} characters")
        
        response = await final_answer_agent.run(tool_prompt)
        #print(f"[DEBUG] LLM output after tool post-processing:\n{response}")
        
       
        loops += 1
        # Safeguard: if LLM outputs another tool call after tool result, break and return fallback
        if isinstance(response, dict) and "tool_call" in response:
            print("[DEBUG] LLM output another tool call after tool result, breaking")
            return {"response": "I could not generate a natural language answer after using the tool."}
       # print(f"[STATUS] result got for tool: {tool_name}")
    # Ensure response is always a string for the frontend
    if isinstance(response, dict):
        # Check if this is still a tool call that wasn't processed
        if "tool_call" in response:
            print("[DEBUG] Response is still a tool call, this shouldn't happen")
            return {"response": "I encountered an error processing the tool call. Please try again."}
        
        main_message = response.get("result") or response.get("output") or str(response)
        # Process the response for Markdown conversion
        processed_message = process_response_for_markdown(main_message)
        # Replace tabs with spaces as the final step
        if isinstance(processed_message, str):
            #print(f"[DEBUG] Before tab replace: {repr(processed_message[:200])} (length: {len(processed_message)})")
            processed_message = processed_message.replace('\t', ' ').replace('\t', ' ')
            #print(f"[DEBUG] After tab replace: {repr(processed_message[:200])} (length: {len(processed_message)})")
        return {"response": processed_message}
    
    # Process string response for Markdown conversion
    processed_response = process_response_for_markdown(response)
    # Replace tabs with spaces as the final step
    if isinstance(processed_response, str):
        print(f"[DEBUG] Before tab replace: {repr(processed_response[:200])} (length: {len(processed_response)})")
        processed_response = processed_response.replace('\t', ' ').replace('\t', ' ')
        print(f"[DEBUG] After tab replace: {repr(processed_response[:200])} (length: {len(processed_response)})")
    return {"response": processed_response}

@app.get("/models")
def get_models():
    return {"models": AVAILABLE_MODELS}

@app.get("/mcp-tools")
async def get_mcp_tools_endpoint(mcp_url: str):
    """Get available tools from an MCP server"""
    if not mcp_url:
        return {"tools": "No MCP server URL provided"}
    
    try:
        tools_context = await asyncio.wait_for(get_mcp_tools(mcp_url), timeout=30)
        return {"tools": tools_context}
    except asyncio.TimeoutError:
        return {"tools": "Error: MCP server did not respond in time."}
    except Exception as e:
        return {"tools": f"Error fetching tools: {str(e)}"}

@app.post("/fix-layout")
async def fix_layout(request: Request):
    data = await request.json()
    text = data.get("text", "")
    lang = data.get("lang", "en")
    if not text.strip():
        return {"fixed_text": text}

    detected = detect_charset(text)
    if lang != detected and (detected, lang) in LAYOUTS:
        fixed = fix_keyboard_layout(text, detected, lang)
        return {"fixed_text": fixed}
    return {"fixed_text": text}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

# To use, create a .env file in this directory with:
# IO_API_KEY=sk-... 