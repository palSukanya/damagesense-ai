# DamageSense AI

> AI-powered vehicle damage detection and assessment system. Upload a vehicle photo and get instant damage analysis — severity scores, repair cost estimates, and insurance recommendations.

---

## Tech Stack

- **Backend**: FastAPI + YOLOv8 + SQLite
- **Frontend**: React + Tailwind CSS + Axios

---

## Project Structure

```
damagesense-ai/
├── app/
│   ├── main.py              # FastAPI app & all routes
│   ├── config.py            # Settings & paths
│   ├── database/            # SQLAlchemy models & DB init
│   ├── models/              # YOLO model loader & severity logic
│   ├── services/            # Detection, history, quality services
│   └── utils/               # Image helpers & damage map overlay
├── frontend/
│   ├── src/
│   │   ├── components/      # HeroSection, ImageUploader, AnalysisResults
│   │   ├── pages/           # AnalyzePage
│   │   ├── services/api.js  # Axios client → http://127.0.0.1:8000
│   │   └── App.js
│   └── .env                 # REACT_APP_API_URL=http://127.0.0.1:8000
├── models/                  # Place best.pt (trained YOLO model) here
├── uploads/                 # Auto-created: raw/ and annotated/ images
├── damagesense.db           # SQLite database (auto-created)
└── requirements.txt
```

---

## Setup & Running

### Prerequisites

- [Conda](https://docs.conda.io/en/latest/miniconda.html)
- [Node.js](https://nodejs.org/) (v16+)
- Trained YOLO model file: place `best.pt` inside the `models/` folder

### 1. Backend

```bash
conda activate damagesense
uvicorn app.main:app --reload
```

Backend runs at: http://127.0.0.1:8000  
API docs (Swagger): http://127.0.0.1:8000/docs

### 2. Frontend

```bash
cd frontend
# First time only:
npm install
# Start:
npm start
```

Frontend runs at: http://localhost:3000

> The frontend connects to the backend via the `.env` file:  
> `REACT_APP_API_URL=http://127.0.0.1:8000`

---

## Key API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/analyze` | Analyze vehicle damage from image |
| `POST` | `/api/v1/quality-check` | Check image quality before analysis |
| `GET` | `/api/v1/history/{vehicle_id}` | Get inspection history for a vehicle |
| `GET` | `/api/v1/stats` | System-wide statistics |
| `GET` | `/health` | Health check |

---

## Notes

- The app uses `yolov8n-seg.pt` as a fallback if `models/best.pt` is not found
- Uploaded images are stored in `uploads/raw/` and annotated results in `uploads/annotated/`
- Cost estimates are in INR (₹); auto-approval threshold is ₹50,000