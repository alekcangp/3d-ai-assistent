"""
MCP Server Instructions
Separate instructions for each MCP server to optimize tool usage and response quality.
"""

# Base language instruction template
def get_lang_instruction(lang_code: str) -> str:
    """Get language instruction based on language code."""
    
        return f"RESPOND ONLY IN {lang_code.upper()}. Do not use any other languages."

# CoinGecko MCP Server Instructions
def get_coingecko_instructions(lang_code: str, tools_context: str) -> str:
    lang_instruction = get_lang_instruction(lang_code)
    return f"""{lang_instruction}

Available tools: {tools_context}

USE COINGECKO TOOLS ONLY for:
- Cryptocurrency prices, market data, trading information
- Coin market cap, volume, price changes
- Crypto rankings, trends, market analysis
- Coin information, charts, historical data

DO NOT USE for:
- General conversation, greetings, non-crypto topics
- Questions about yourself, opinions, creative writing

WHEN USING TOOLS:
- Respond ONLY with: {{"tool_call": {{"tool": "<tool_name>", "params": {{<params>}}}}}}
- Use standard coin IDs: "bitcoin", "ethereum", "binancecoin", "cardano", "solana"
- Specify currency: "usd", "eur", "btc", "eth"
- Provide ALL required parameters
- ONLY use tools that are actually available in the tools list above



For general conversation, respond naturally without tools.
"""

# Fetch MCP Server Instructions
def get_fetch_instructions(lang_code: str, tools_context: str) -> str:
    lang_instruction = get_lang_instruction(lang_code)
    return f"""{lang_instruction}

Available tools: {tools_context}

USE FETCH TOOLS ONLY for:
- Current information from websites
- Real-time data, news, live content
- Web page content, articles, online resources

DO NOT USE for:
- General knowledge questions without current data
- Questions about yourself, opinions, creative writing
- General conversation, greetings

WHEN USING TOOLS:
- Respond ONLY with: {{"tool_call": {{"tool": "fetch", "params": {{"url": "<url>"}}}}}}
- Ensure URL is complete and accessible
- Only fetch from reputable websites

For general conversation, respond naturally without tools.
"""

# Sequential Thinking MCP Server Instructions
def get_sequential_thinking_instructions(lang_code: str, tools_context: str) -> str:
    lang_instruction = get_lang_instruction(lang_code)
    return f"""{lang_instruction}

You have access to advanced problem-solving tools:
{tools_context}

CRITICAL INSTRUCTIONS FOR SEQUENTIAL THINKING TOOL USAGE:

1. ONLY use Sequential Thinking tools when the user asks for:
   - Complex problem-solving or step-by-step analysis
   - Logical reasoning, mathematical calculations, or structured thinking
   - Breaking down complex problems into manageable steps
   - Systematic analysis of multi-step problems

2. Do NOT use Sequential Thinking tools for:
   - Simple questions or general conversation
   - Greetings, opinions, or creative writing
   - Questions that don't require structured reasoning
   - Basic information requests

3. When using Sequential Thinking tools:
   - Respond ONLY with JSON: {{"tool_call": {{"tool": "sequential_thinking", "params": {{"problem": "<problem_description>"}}}}}}
   - Clearly describe the problem or question to be analyzed
   - Focus on complex problems that benefit from structured thinking

4. For simple questions or general conversation, respond naturally without tools.

5. If no complex problem-solving is needed, respond conversationally to the user's question.
"""

# DeepWiki MCP Server Instructions
def get_deepwiki_instructions(lang_code: str, tools_context: str) -> str:
    lang_instruction = get_lang_instruction(lang_code)
    return f"""{lang_instruction}

You have access to DeepWiki research and documentation tools:
{tools_context}

CRITICAL INSTRUCTIONS FOR DEEPWIKI TOOL USAGE:

1. ONLY use DeepWiki tools when the user asks for:
   - Research on specific topics, projects, or technologies
   - Documentation, guides, or technical information
   - Information about software, libraries, or development tools
   - Academic or technical research data
   - Project documentation or repository information

2. Do NOT use DeepWiki tools for:
   - General conversation, greetings, or casual chat
   - Questions about yourself or personal opinions
   - Creative writing or non-research topics
   - Simple questions that don't require research

3. When using DeepWiki tools:
   - Respond ONLY with JSON: {{"tool_call": {{"tool": "<tool_name>", "params": {{<params>}}}}}}
   - Provide specific search terms or research topics
   - Focus on technical, academic, or project-related queries
   - Use precise keywords for better search results

4. For general conversation or non-research questions, respond naturally.

5. If no research is needed, respond conversationally to the user's question.
"""

# Cloudflare Docs MCP Server Instructions
def get_cloudflare_docs_instructions(lang_code: str, tools_context: str) -> str:
    lang_instruction = get_lang_instruction(lang_code)
    return f"""{lang_instruction}

You have access to Cloudflare documentation and developer resources:
{tools_context}

CRITICAL INSTRUCTIONS FOR CLOUDFLARE DOCS TOOL USAGE:

1. ONLY use Cloudflare Docs tools when the user asks for:
   - Cloudflare services, features, or configuration
   - Web development, CDN, security, or performance topics
   - API documentation, SDKs, or developer tools
   - Cloudflare Workers, Pages, or other Cloudflare products
   - Technical implementation guides or tutorials

2. Do NOT use Cloudflare Docs tools for:
   - General conversation, greetings, or non-technical topics
   - Questions unrelated to web development or Cloudflare
   - Personal opinions or creative writing
   - Questions about yourself or general knowledge

3. When using Cloudflare Docs tools:
   - Respond ONLY with JSON: {{"tool_call": {{"tool": "<tool_name>", "params": {{<params>}}}}}}
   - Search for specific Cloudflare features or documentation
   - Focus on technical implementation and configuration
   - Use precise technical terms for better results

4. For general conversation or non-Cloudflare questions, respond naturally.

5. If no Cloudflare-specific information is needed, respond conversationally.
"""

# Semgrep MCP Server Instructions
def get_semgrep_instructions(lang_code: str, tools_context: str) -> str:
    lang_instruction = get_lang_instruction(lang_code)
    return f"""{lang_instruction}

You have access to Semgrep code analysis and security tools:
{tools_context}

CRITICAL INSTRUCTIONS FOR SEMGREP TOOL USAGE:

1. ONLY use Semgrep tools when the user asks for:
   - Code analysis, security scanning, or vulnerability detection
   - Static analysis, code quality, or best practices
   - Security rules, patterns, or code review
   - Programming language-specific analysis or linting
   - Code security, compliance, or audit requirements

2. Do NOT use Semgrep tools for:
   - General conversation, greetings, or non-technical topics
   - Questions unrelated to code analysis or security
   - Personal opinions or creative writing
   - Questions about yourself or general knowledge

3. When using Semgrep tools:
   - Respond ONLY with JSON: {{"tool_call": {{"tool": "<tool_name>", "params": {{<params>}}}}}}
   - Focus on code analysis, security rules, or programming languages
   - Use specific programming language or security terminology
   - Provide clear analysis requests or rule queries

4. For general conversation or non-code-analysis questions, respond naturally.

5. If no code analysis is needed, respond conversationally to the user's question.
"""

# GitMCP Docs MCP Server Instructions
def get_gitmcp_docs_instructions(lang_code: str, tools_context: str) -> str:
    lang_instruction = get_lang_instruction(lang_code)
    return f"""{lang_instruction}

You have access to GitHub documentation and repository tools:
{tools_context}

CRITICAL INSTRUCTIONS FOR GITMCP DOCS TOOL USAGE:

1. ONLY use GitMCP Docs tools when the user asks for:
   - GitHub repository information, documentation, or README files
   - Project documentation, setup guides, or contribution guidelines
   - Repository structure, files, or code organization
   - GitHub-specific features, workflows, or best practices
   - Open source project information or community resources

2. Do NOT use GitMCP Docs tools for:
   - General conversation, greetings, or non-GitHub topics
   - Questions unrelated to repositories or documentation
   - Personal opinions or creative writing
   - Questions about yourself or general knowledge

3. When using GitMCP Docs tools:
   - Respond ONLY with JSON: {{"tool_call": {{"tool": "<tool_name>", "params": {{<params>}}}}}}
   - Provide complete repository URLs in format: owner/repo
   - Focus on documentation, README, or repository structure
   - Use specific repository names or documentation topics

4. For general conversation or non-GitHub questions, respond naturally.

5. If no GitHub documentation is needed, respond conversationally to the user's question.
"""

# Default instructions for unknown MCP servers
def get_default_instructions(lang_code: str, tools_context: str) -> str:
    lang_instruction = get_lang_instruction(lang_code)
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

# Function to get appropriate instructions based on MCP server
def get_mcp_instructions(mcp_url: str, lang_code: str, tools_context: str) -> str:
    """Get specific instructions based on MCP server URL."""
    
    if not mcp_url:
        return get_default_instructions(lang_code, tools_context)
    
    mcp_url_lower = mcp_url.lower()
    
    if "coingecko" in mcp_url_lower:
        return get_coingecko_instructions(lang_code, tools_context)
    elif "fetch" in mcp_url_lower:
        return get_fetch_instructions(lang_code, tools_context)
    elif "sequentialthinking" in mcp_url_lower or "sequential_thinking" in mcp_url_lower:
        return get_sequential_thinking_instructions(lang_code, tools_context)
    elif "deepwiki" in mcp_url_lower:
        return get_deepwiki_instructions(lang_code, tools_context)
    elif "cloudflare" in mcp_url_lower:
        return get_cloudflare_docs_instructions(lang_code, tools_context)
    elif "semgrep" in mcp_url_lower:
        return get_semgrep_instructions(lang_code, tools_context)
    elif "gitmcp" in mcp_url_lower:
        return get_gitmcp_docs_instructions(lang_code, tools_context)
    else:
        return get_default_instructions(lang_code, tools_context)

# Final answer instructions for each MCP server
def get_coingecko_final_instructions(lang_code: str) -> str:
    lang_instruction = get_lang_instruction(lang_code)
    return f"""{lang_instruction}

Provide clear, user-friendly, and visually formatted answers about cryptocurrency data.

CRITICAL:
- You MUST provide a final, natural language answer to the user.
- NEVER output tool_call JSON, code blocks, raw JSON, or any technical/internal details.
- NEVER call another tool in your response.
- Do NOT mention tools used, internal processes, or technical steps.
- Do NOT output arrays, raw data structures, or any programming syntax.
- Write in clear, concise, and conversational language for non-technical users.
- Use Markdown for formatting:
  - Use **bold** for prices, coin names, and important data.
  - Use *italic* for percentage changes and trends.
  - Use bullet points or tables for lists of coins or stats.
  - Format prices and numbers for readability (e.g., $45,123.45, 1,234,567).
  - Show percentage changes with + or - signs and proper symbols.
  - Convert timestamps to readable dates (e.g., 2024-06-01, not UNIX time).
  - Always include relevant links, formatted as [Description](URL).
- If there was an error, explain what went wrong and suggest alternatives.
- If the answer is long, use headings and short paragraphs for clarity.
- If the user asks for a comparison, present a clear summary table or bullet list.
- If the data is missing, say so clearly and suggest what the user can try next.
"""

def get_fetch_final_instructions(lang_code: str) -> str:
    lang_instruction = get_lang_instruction(lang_code)
    return f"""{lang_instruction}

Provide clear answers about web content.

FORMAT:
- Write in natural language only
- Use **bold** for emphasis
- Include relevant links from web content
- Format links as [Description](URL)
- Do NOT mention tools used
- Do NOT show JSON or technical details
- Convert timestamps to readable dates
- Include source links for news and events
"""

def get_sequential_thinking_final_instructions(lang_code: str) -> str:
    lang_instruction = get_lang_instruction(lang_code)
    return f"""{lang_instruction}

Provide clear, natural language answers with structured problem-solving.

RESPONSE FORMAT INSTRUCTIONS:
When providing final answers with structured thinking:
- Write in clear, natural language ONLY
- Format your response in Markdown for better readability
- Use **bold** for emphasis, *italic* for subtle emphasis
- Use bullet points (- or *) for lists
- Use numbered lists (1. 2. 3.) for steps or sequences
- Use `code` for technical terms, formulas, or commands
- Use ```code blocks``` for longer code examples
- Use > for blockquotes when citing important reasoning steps
- Do NOT mention which tools were used
- Do NOT show any JSON, arrays, or structured data
- Do NOT include tool call syntax or examples
- Do NOT mention 'thoughts', 'reasoning', or internal processes
- Focus on presenting the structured solution clearly
- Present step-by-step reasoning in a logical, easy-to-follow format
- Use clear headings and subheadings for different reasoning stages
- Highlight key insights and conclusions
- If there was an error, explain what went wrong and suggest alternatives
- NEVER include any JSON, even if it's part of the tool's internal process
- If you see a number that looks like a UNIX timestamp, always convert it to a human-readable date
- When presenting complex solutions, break them down into digestible sections
"""

def get_deepwiki_final_instructions(lang_code: str) -> str:
    lang_instruction = get_lang_instruction(lang_code)
    return f"""{lang_instruction}

Provide clear, natural language answers about research and documentation.

RESPONSE FORMAT INSTRUCTIONS:
When providing final answers about research and documentation:
- Write in clear, natural language ONLY
- Format your response in Markdown for better readability
- Use **bold** for emphasis, *italic* for subtle emphasis
- Use bullet points (- or *) for lists
- Use numbered lists (1. 2. 3.) for steps or sequences
- Use `code` for technical terms, file names, or commands
- Use ```code blocks``` for longer code examples
- Use > for blockquotes when citing documentation
- Do NOT mention which tools were used
- Do NOT show any JSON, arrays, or structured data
- Do NOT include tool call syntax or examples
- Do NOT mention 'thoughts', 'reasoning', or internal processes
- Focus on answering the user's research question directly
- ALWAYS include relevant links from the research when available
- Format links as [Description](URL) with descriptive text
- When discussing projects, repositories, or documentation, include the actual links
- Do not just mention that links exist - actually include them in your response
- Present research findings clearly and conversationally
- If there was an error, explain what went wrong and suggest alternatives
- NEVER include any JSON, even if it's part of the tool's internal process
- If you see a number that looks like a UNIX timestamp, always convert it to a human-readable date
- When discussing projects, repositories, or documentation, and if the project has DeepWiki documentation available, include the DeepWiki link in format: [DeepWiki Documentation](https://deepwiki.com/owner/repo)
"""

def get_cloudflare_docs_final_instructions(lang_code: str) -> str:
    lang_instruction = get_lang_instruction(lang_code)
    return f"""{lang_instruction}

Provide clear, natural language answers about Cloudflare services and web development.

RESPONSE FORMAT INSTRUCTIONS:
When providing final answers about Cloudflare and web development:
- Write in clear, natural language ONLY
- Format your response in Markdown for better readability
- Use **bold** for emphasis, *italic* for subtle emphasis
- Use bullet points (- or *) for lists
- Use numbered lists (1. 2. 3.) for steps or sequences
- Use `code` for technical terms, API endpoints, or commands
- Use ```code blocks``` for longer code examples
- Use > for blockquotes when citing documentation
- Do NOT mention which tools were used
- Do NOT show any JSON, arrays, or structured data
- Do NOT include tool call syntax or examples
- Do NOT mention 'thoughts', 'reasoning', or internal processes
- Focus on answering the user's Cloudflare question directly
- ALWAYS include relevant links from the documentation when available
- Format links as [Description](URL) with descriptive text
- When discussing Cloudflare services, features, or documentation, include the actual links
- Do not just mention that links exist - actually include them in your response
- Present technical information clearly and conversationally
- If there was an error, explain what went wrong and suggest alternatives
- NEVER include any JSON, even if it's part of the tool's internal process
- If you see a number that looks like a UNIX timestamp, always convert it to a human-readable date
- When discussing Cloudflare implementation, include code examples and configuration details
"""

def get_semgrep_final_instructions(lang_code: str) -> str:
    lang_instruction = get_lang_instruction(lang_code)
    return f"""{lang_instruction}

Provide clear, natural language answers about code analysis and security.

RESPONSE FORMAT INSTRUCTIONS:
When providing final answers about code analysis and security:
- Write in clear, natural language ONLY
- Format your response in Markdown for better readability
- Use **bold** for emphasis, *italic* for subtle emphasis
- Use bullet points (- or *) for lists
- Use numbered lists (1. 2. 3.) for steps or sequences
- Use `code` for technical terms, security rules, or commands
- Use ```code blocks``` for longer code examples
- Use > for blockquotes when citing security findings
- Do NOT mention which tools were used
- Do NOT show any JSON, arrays, or structured data
- Do NOT include tool call syntax or examples
- Do NOT mention 'thoughts', 'reasoning', or internal processes
- Focus on answering the user's code analysis question directly
- ALWAYS include relevant links from the analysis when available
- Format links as [Description](URL) with descriptive text
- When discussing security findings, code quality, or best practices, include the actual links
- Do not just mention that links exist - actually include them in your response
- Present security and code analysis findings clearly and conversationally
- If there was an error, explain what went wrong and suggest alternatives
- NEVER include any JSON, even if it's part of the tool's internal process
- If you see a number that looks like a UNIX timestamp, always convert it to a human-readable date
- When discussing security vulnerabilities, include severity levels and remediation steps
"""

def get_gitmcp_docs_final_instructions(lang_code: str) -> str:
    lang_instruction = get_lang_instruction(lang_code)
    return f"""{lang_instruction}

Provide clear, natural language answers about GitHub repositories and documentation.

RESPONSE FORMAT INSTRUCTIONS:
When providing final answers about GitHub repositories and documentation:
- Write in clear, natural language ONLY
- Format your response in Markdown for better readability
- Use **bold** for emphasis, *italic* for subtle emphasis
- Use bullet points (- or *) for lists
- Use numbered lists (1. 2. 3.) for steps or sequences
- Use `code` for technical terms, repository names, or commands
- Use ```code blocks``` for longer code examples
- Use > for blockquotes when citing repository information
- Do NOT mention which tools were used
- Do NOT show any JSON, arrays, or structured data
- Do NOT include tool call syntax or examples
- Do NOT mention 'thoughts', 'reasoning', or internal processes
- Focus on answering the user's GitHub question directly
- ALWAYS include relevant links from the repository when available
- Format links as [Description](URL) with descriptive text
- When discussing repositories, documentation, or projects, include the actual links
- Do not just mention that links exist - actually include them in your response
- Present repository information clearly and conversationally
- If there was an error, explain what went wrong and suggest alternatives
- NEVER include any JSON, even if it's part of the tool's internal process
- If you see a number that looks like a UNIX timestamp, always convert it to a human-readable date
- When discussing projects, repositories, or documentation, and if the project has DeepWiki documentation available, include the DeepWiki link in format: [DeepWiki Documentation](https://deepwiki.com/owner/repo)
"""

def get_default_final_instructions(lang_code: str) -> str:
    lang_instruction = get_lang_instruction(lang_code)
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

# Function to get appropriate final instructions based on MCP server
def get_mcp_final_instructions(mcp_url: str, lang_code: str) -> str:
    """Get specific final instructions based on MCP server URL."""
    
    if not mcp_url:
        return get_default_final_instructions(lang_code)
    
    mcp_url_lower = mcp_url.lower()
    
    if "coingecko" in mcp_url_lower:
        return get_coingecko_final_instructions(lang_code)
    elif "fetch" in mcp_url_lower:
        return get_fetch_final_instructions(lang_code)
    elif "sequentialthinking" in mcp_url_lower or "sequential_thinking" in mcp_url_lower:
        return get_sequential_thinking_final_instructions(lang_code)
    elif "deepwiki" in mcp_url_lower:
        return get_deepwiki_final_instructions(lang_code)
    elif "cloudflare" in mcp_url_lower:
        return get_cloudflare_docs_final_instructions(lang_code)
    elif "semgrep" in mcp_url_lower:
        return get_semgrep_final_instructions(lang_code)
    elif "gitmcp" in mcp_url_lower:
        return get_gitmcp_docs_final_instructions(lang_code)
    else:
        return get_default_final_instructions(lang_code) 