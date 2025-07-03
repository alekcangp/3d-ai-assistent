# Vue 3 + TypeScript + Vite

This template should help get you started developing with Vue 3 and TypeScript in Vite. The template uses Vue 3 `<script setup>` SFCs, check out the [script setup docs](https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup) to learn more.

Learn more about the recommended Project Setup and IDE Support in the [Vue Docs TypeScript Guide](https://vuejs.org/guide/typescript/overview.html#project-setup).

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
