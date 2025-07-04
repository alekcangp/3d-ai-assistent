# 3D AI Assistant

A modern web application featuring a 3D animated AI avatar with real-time facial animation, voice controls, and chat interface. Built with Vue 3, TypeScript, Three.js, and a Python backend (FastAPI).

## Features
- 3D avatar rendered with Three.js
- Realistic facial animation and micro-expressions
- Voice input and output controls
- Customizable avatar appearance
- Chat interface with AI responses
- Python backend for AI and data processing

## Installation

### Prerequisites
- Node.js (v16+ recommended)
- npm
- Python 3.8+

### Frontend Setup
```bash
npm install
```

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Development

### Start Frontend (Vite)
```bash
npm run dev
```

### Start Backend (FastAPI)
```bash
cd backend
uvicorn main:app --reload
```

## Build
To build the frontend for production:
```bash
npm run build
```


## License
MIT License

---

## 🚀 Deploy to Render (Monorepo: Frontend + Backend)

1. **Push your code to GitHub.**
2. **Go to [render.com](https://render.com/)** and sign in.
3. **Click "New +" → "Blueprint"** and select your repo.
4. Render will auto-detect the `render.yaml` and set up two services:
   - **vite-frontend** (static site)
   - **fastapi-backend** (Python API)
5. **Set environment variables** for the backend in the Render dashboard (copy from `backend/.env.example`).
6. **Deploy!**
7. **Frontend will be live at:** `https://your-frontend.onrender.com`
   **Backend will be live at:** `https://your-backend.onrender.com`

### Environment Variables
- Copy `backend/.env.example` to `backend/.env` and fill in your secrets.
- Add these in the Render dashboard for the backend service.

### CORS
- The backend allows CORS from all origins by default. For production, restrict to your frontend domain.

---
