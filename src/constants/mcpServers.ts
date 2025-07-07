export const mcpServers = [
  {
    name: 'Only LLM knowledge',
    value: null,
    description: 'Use only the LLM\'s internal knowledge. No real-time data.'
  },
  {
    name: 'CoinGecko',
    value: 'https://mcp.api.coingecko.com/sse',
    description: 'CoinGecko is a cryptocurrency data platform.'
  },
  {
    name: 'Fetch',
    value: 'https://remote.mcpservers.org/fetch/mcp',
    description: 'An MCP server that provides web content fetching capabilities. This server enables LLMs to retrieve and process content from web pages, converting HTML to markdown for easier consumption.'
  },
  {
    name: 'Sequential Thinking',
    value: 'https://remote.mcpservers.org/sequentialthinking/mcp',
    description: 'An MCP server implementation that provides a tool for dynamic and reflective problem-solving through a structured thinking process.'
  },
  {
    name: 'DeepWiki',
    value: 'https://mcp.deepwiki.com/mcp',
    description: 'DeepWiki MCP: General-purpose tool server for research, data, and more.'
  },
  {
    name: 'Cloudflare Docs',
    value: 'https://docs.mcp.cloudflare.com/sse',
    description: 'Cloudflare Docs MCP: Access documentation and developer resources via Model Context Protocol (SSE endpoint).'
  },
  /*
  {
    name: 'Hugging Face',
    value: 'https://hf.co/mcp',
    description: 'Hugging Face MCP: Access Hugging Face tools and models via Model Context Protocol (SSE endpoint).'
  },
  */
  {
    name: 'Semgrep',
    value: 'https://mcp.semgrep.ai/sse',
    description: 'Semgrep MCP: Access code analysis and security tools via Model Context Protocol (SSE endpoint).'
  },
  /*
  {
    name: 'LLM Text',
    value: 'https://mcp.llmtxt.dev/sse',
    description: 'LLM Text MCP: Access data analysis and text processing tools via Model Context Protocol (SSE endpoint).'
  },
  */
  {
    name: 'GitMCP Docs',
    value: 'https://gitmcp.io/docs',
    description: 'GitMCP Docs: Chat with all GitHub documentation online via Model Context Protocol (SSE endpoint). See: https://gitmcp.io/docs'
  },
  /*
  {
    name: 'EdgeOne Pages',
    value: 'https://remote.mcpservers.org/edgeone-pages/mcp',
    description: 'EdgeOne Pages MCP: Access EdgeOne Pages tools and integrations via Model Context Protocol (SSE endpoint).'
  }
    */
]; 

export function getDefaultMcpServers() {
  return [
    {
      name: 'Only LLM knowledge',
      value: null,
      description: "Use only the LLM's internal knowledge. No real-time data."
    },
    {
      name: 'CoinGecko',
      value: 'https://mcp.api.coingecko.com/sse',
      description: 'CoinGecko is a cryptocurrency data platform.'
    },
    {
      name: 'Fetch',
      value: 'https://remote.mcpservers.org/fetch/mcp',
      description: 'An MCP server that provides web content fetching capabilities. This server enables LLMs to retrieve and process content from web pages, converting HTML to markdown for easier consumption.'
    },
    {
      name: 'Sequential Thinking',
      value: 'https://remote.mcpservers.org/sequentialthinking/mcp',
      description: 'An MCP server implementation that provides a tool for dynamic and reflective problem-solving through a structured thinking process.'
    },
    {
      name: 'DeepWiki',
      value: 'https://mcp.deepwiki.com/mcp',
      description: 'DeepWiki MCP: General-purpose tool server for research, data, and more.'
    },
    {
      name: 'Cloudflare Docs',
      value: 'https://docs.mcp.cloudflare.com/sse',
      description: 'Cloudflare Docs MCP: Access documentation and developer resources via Model Context Protocol (SSE endpoint).'
    },
    {
      name: 'Semgrep',
      value: 'https://mcp.semgrep.ai/sse',
      description: 'Semgrep MCP: Access code analysis and security tools via Model Context Protocol (SSE endpoint).'
    },
    {
      name: 'GitMCP Docs',
      value: 'https://gitmcp.io/docs',
      description: 'GitMCP Docs: Chat with all GitHub documentation online via Model Context Protocol (SSE endpoint). See: https://gitmcp.io/docs'
    }
  ];
} 