# 3D AI Assistant

A modern web application featuring a 3D animated AI avatar with real-time facial animation, voice controls, and intelligent chat interface. Built with Vue 3, TypeScript, Three.js, and a Python backend (FastAPI, FastMCP) with IOIntel integration.

[Demo Video](https://www.loom.com/share/6a1ef2da181e4bbd83caabafde5251af?sid=87ef211c-b55b-45a1-88cb-c1a77db1da71)

## 🌟 Features

### 🤖 AI Avatar & Animation
- **3D Avatar Rendering**: High-quality 3D avatar using Three.js with realistic facial features
- **Real-time Facial Animation**: Dynamic mouth movements synchronized with speech synthesis
- **Micro-expressions**: Subtle facial animations for more natural interaction
- **Responsive Animations**: Speaking, listening, and idle states with smooth transitions

### 🎤 Voice Interaction
- **Speech-to-Text (STT)**: Real-time voice input with language detection
- **Text-to-Speech (TTS)**: Natural voice output with multiple language support
- **Voice Controls**: Start/stop listening, interrupt speech, voice commands
- **Multi-language Support**: Russian, English, and other languages with automatic detection

### 💬 Intelligent Chat Interface
- **AI-powered Responses**: Integration with multiple LLM models (DeepSeek, Llama, Qwen, etc.)
- **Personality Customization**: Adjustable AI personality traits (friendliness, creativity, formality, etc.)
- **Markdown Rendering**: Rich text formatting with code blocks, lists, and links
- **Message History**: Persistent chat history with local storage
- **Copy Functionality**: Easy copying of user messages with visual feedback
- **Keyboard Layout Correction:** Instantly fix keyboard layout mistakes in your chat input with a single click.

### 🔧 Advanced Features
- **MCP Server Integration**: Connect to external tools and data sources
- **Model Selection**: Choose from 20+ available AI models
- **Language Selection**: Support for multiple languages with system detection
- **Dark/Light Theme**: Toggle between themes with persistent settings
- **Responsive Design**: Works on desktop and mobile devices

### 🛠 Technical Features
- **Real-time Processing**: Instant response generation and voice synthesis
- **Error Handling**: Graceful error handling with user-friendly messages
- **Performance Optimized**: Efficient rendering and minimal resource usage
- **Cross-platform**: Works on all modern browsers


## 🏗 Architecture

### Frontend (Vue 3 + TypeScript)
- **Vue 3 Composition API**: Modern reactive framework
- **Three.js**: 3D graphics and animation
- **TypeScript**: Type-safe development
- **Vite**: Fast development and build tooling
- **GSAP**: Smooth animations and transitions

### Backend (Python + FastAPI)
- **FastAPI**: High-performance async web framework
- **IOIntel**: Advanced AI model integration for inference, providing access to multiple LLM models through a unified API
- **FastMCP**: Model Context Protocol client for external tool integration
- **MCP (Model Context Protocol)**: External tool integration
- **CORS Support**: Cross-origin resource sharing

### IO Intelligence Integration
This project uses the **IO Intelligence SDK** (`iointel`) to access multiple AI models through a unified API. The integration includes:

- **Direct SDK Usage**: `from iointel import Agent, PersonaConfig`
- **API Key Configuration**: `IO_API_KEY` environment variable
- **Model Selection**: Support for 20+ IO models including:
  - `deepseek-ai/DeepSeek-R1-0528` - Advanced reasoning and programming
  - `meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8` - Multimodal capabilities
  - `Qwen/Qwen3-235B-A22B-FP8` - Large-scale language model
  - `google/gemma-3-27b-it` - Google's open model
  - And 15+ more models...

The backend makes direct calls to IO Intelligence endpoints through the SDK for real-time AI inference.

### Code Example: IO Intelligence Integration

```python
# Import IO Intelligence SDK
from iointel import Agent, PersonaConfig

# Configure AI agent with IO model
agent = Agent(
    name=persona.name,
    instructions=tool_selection_instructions,
    persona=persona,
    model=model_name,  # e.g., "deepseek-ai/DeepSeek-R1-0528"
    api_key=os.environ.get("IO_API_KEY")
)

# Run inference with IO Intelligence
response = await agent.run(prompt)
```


### AI Models Supported
- **DeepSeek-R1**: Advanced reasoning and programming
- **Llama-4-Maverick**: Multimodal capabilities
- **Qwen3-235B**: Large-scale language model
- **Gemma-3-27b**: Google's open model
- **And 15+ more models**...

## 🚀 Quick Start

### Prerequisites
- **Node.js** (v16+ recommended)
- **npm** or **yarn**
- **Python 3.8+**


### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd 3d-ai-assistant
```

2. **Install frontend dependencies**
```bash
npm install
```

3. **Install backend dependencies**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys
```

### Development

1. **Start the backend server**
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2. **Start the frontend development server**
```bash
npm run dev
```

3. **Open your browser**
Navigate to `http://localhost:5173`

## 🎯 Usage

### Interaction
1. **Type or speak** your message to the AI
2. **Adjust AI personality** traits for different interaction styles
3. **Select AI models** based on your needs
4. **Select MCP Server**: Connect to external data sources and tools
4. **Use voice controls** for hands-free interaction
5. **Language Switching**: Change interface and AI language
6. **Theme Toggle**: Switch between light and dark modes


## 🚀 Deployment

### Render.com (Recommended)

1. **Push your code to GitHub**
2. **Go to [render.com](https://render.com/)** and sign in
3. **Click "New +" → "Blueprint"** and select your repository
4. **Render will auto-detect** the `render.yaml` configuration
5. **Set environment variables** in the Render dashboard
6. **Deploy!**

The blueprint will create:
- **Frontend Service**: Static site deployment
- **Backend Service**: Python API deployment

**⚠️ Important Note:** The backend is deployed on Render's free tier, which means it will sleep after 15 minutes of inactivity. The first request after inactivity may take 30-60 seconds to wake up the service.

### Environment Variables

**Backend (.env)**
```env
# IO Intelligence API Key - Required for AI model access
IO_API_KEY=your_iointel_api_key_here

# Frontend URL for CORS configuration
FRONTEND_URL=https://your-frontend.onrender.com
```

**Frontend (Render Environment)**
```env
VITE_BACKEND_URL=https://your-backend.onrender.com
```

## 🔧 Configuration

### AI Model Selection
Choose from available models in the settings panel:
- **DeepSeek-R1**: Best for reasoning and programming
- **Llama-4-Maverick**: Excellent for multimodal tasks
- **Qwen3-235B**: Strong general performance
- **Gemma-3-27b**: Good balance of speed and quality
- and more...

### Personality Customization
Adjust AI personality traits:
- **Friendliness**: How warm and approachable the AI is
- **Creativity**: How imaginative and original responses are
- **Formality**: How formal or casual the language is
- **Empathy**: How understanding and supportive the AI is
- **Humor**: How playful and witty responses are

### MCP Server Integration
Connect to external tools:
- **Fetch**: Web content retrieval
- **Sequential Thinking**: Advanced problem-solving
- **DeepWiki**: Documentation access
- **Cloudflare Docs**: Developer resources
- **Semgrep**: Code analysis tools

## 🛰️ MCP Servers
This project supports integration with **MCP (Model Context Protocol) servers** to enable external tool usage and advanced data retrieval. MCP servers allow the AI assistant to access external APIs, perform web searches, fetch documentation, and more, by calling tools defined on the MCP server.

### How MCP Servers Are Used
- When you select or specify an MCP server in the app, the backend will connect to that server to list available tools and call them as needed.
- If no MCP server is specified, the assistant will use LLM-only mode (no external tools).

### Example Public MCP Servers
- You can use your own MCP server or connect to public ones (if available). Example:
  - `https://mcp.api.coingecko.com/sse` (for CoinGeko tools)
  - `https://mcp.deepwiki.com/mcp` (for DeepWiki documentation)
  - (Replace with your own or other public MCP endpoints as needed)

### Adding/Changing MCP Servers
- In the app UI, go to the settings or server selection panel and enter the MCP server URL.
- The backend will fetch available tools from the specified server and make them available for tool calls.


## 🛠 Development

### Project Structure
```
3d-ai-assistant/
├── src/
│   ├── components/          # Vue components
│   ├── composables/         # Vue composables
│   ├── constants/           # App constants
│   └── types/              # TypeScript types
├── backend/
│   ├── main.py             # FastAPI application
│   └── requirements.txt    # Python dependencies
├── public/                 # Static assets
└── package.json           # Frontend dependencies
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[IOIntel](https://iointel.ai)** for advanced AI model integration
- **[MCP Protocol](https://modelcontextprotocol.io)** for external tool integration


