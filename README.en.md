## tumorDetection

Brain tumor precise segmentation and pre-operative planning system (YOLO11 + radiomics). Backend: Flask + YOLO; Frontend: Vue 3 + TypeScript + Vite.

### Quick Start

1) Backend
- Create and activate Python env
- Install deps: `pip install -r requirements.txt`
- Copy env: `cp backend/.env.example backend/.env` (adjust DB/JWT/model paths)
- Run: `python -m backend.main` (or import `create_app()` for WSGI)

2) Frontend
- `cd frontend && npm install`
- Copy env: `cp .env.example .env` and set `VITE_API_BASE_URL=http://127.0.0.1:8000`
- Dev: `npm run dev`
- Build: `npm run build`

### Structure
- backend/: Flask app factory, blueprints under routes/, YOLO inference under ai/brain_tumor/
- frontend/: Vue 3 + TS, routes in src/router, API clients in src/services, theme tokens in src/styles/theme.css

### Lint & Format
- Frontend: `npm run format`, `npm run lint` (husky/lint-staged enabled)

### Notes
- Default model path: backend/yolov8n.pt (override via .env MODEL_PATH)
- Uploads stored under uploads/medical_images (configurable via UPLOADS_DIR)
