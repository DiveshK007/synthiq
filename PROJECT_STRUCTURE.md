# SynthIQ Project Structure

Complete overview of the SynthIQ monorepo structure.

## Directory Structure

```
synthiq-1/
├── frontend/              # React + TypeScript + Vite frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── store/         # Zustand state management
│   │   ├── App.tsx        # Main app component
│   │   ├── main.tsx       # Entry point
│   │   └── index.css      # Tailwind styles
│   ├── public/            # Static assets
│   ├── package.json       # Node dependencies
│   ├── tsconfig.json      # TypeScript config
│   ├── vite.config.ts     # Vite config
│   ├── tailwind.config.js # Tailwind config
│   ├── Dockerfile         # Docker config
│   └── nginx.conf         # Nginx config
│
├── orchestrator/          # FastAPI orchestrator service
│   ├── main.py            # Main service file
│   ├── requirements.txt   # Python dependencies
│   ├── Dockerfile         # Docker config
│   └── README.md          # Service docs
│
├── ingestor/              # FastAPI ingestor service
│   ├── main.py            # Main service file
│   ├── requirements.txt   # Python dependencies
│   ├── Dockerfile         # Docker config
│   └── README.md          # Service docs
│
├── summarize/             # FastAPI summarize service
│   ├── main.py            # Main service file
│   ├── requirements.txt   # Python dependencies
│   ├── Dockerfile         # Docker config
│   └── README.md          # Service docs
│
├── viz/                   # FastAPI viz service
│   ├── main.py            # Main service file
│   ├── requirements.txt   # Python dependencies
│   ├── Dockerfile         # Docker config
│   └── README.md          # Service docs
│
├── infra/                 # Infrastructure files
│   ├── docker-compose.yml # Docker Compose config
│   └── README.md          # Infrastructure docs
│
├── docs/                  # Documentation
│   ├── QUICKSTART.md      # Quick start guide
│   └── API.md             # API documentation
│
├── README.md              # Main project README
├── .gitignore             # Git ignore rules
└── .editorconfig          # Editor config
```

## Service Ports

- **Frontend**: 5173 (dev), 80 (Docker)
- **Orchestrator**: 8000
- **Ingestor**: 8001
- **Summarize**: 8002
- **Viz**: 8003

## Technology Stack

### Frontend
- React 18
- TypeScript
- Vite
- Tailwind CSS
- Zustand (state management)
- Framer Motion (animations)
- React Hot Toast (notifications)
- Lucide React (icons)

### Backend
- FastAPI
- Python 3.11+
- Uvicorn (ASGI server)
- Pydantic (data validation)
- httpx (HTTP client)
- BeautifulSoup4 (HTML parsing)

### Infrastructure
- Docker
- Docker Compose
- Nginx (frontend production)

## Key Features

1. **Modular Architecture**: Each service is independent and can be developed/deployed separately
2. **Type Safety**: Full TypeScript support in frontend, type hints in Python backend
3. **Dark/Light Mode**: Theme switching with persistent storage
4. **Responsive Design**: Mobile-friendly UI with Tailwind CSS
5. **Real-time Updates**: Job polling and progress tracking
6. **Docker Support**: Full containerization for easy deployment
7. **API Documentation**: OpenAPI/Swagger docs for all services

## Development Workflow

1. Start backend services (orchestrator, ingestor, summarize, viz)
2. Start frontend development server
3. Create jobs via frontend or API
4. Monitor job progress and view results

## Next Steps

- Add authentication (Supabase/Clerk)
- Integrate real AI models (Gemini/GPT)
- Add persistent storage (SQLite/SQLModel)
- Implement semantic search
- Add CI/CD pipeline
- Deploy to Cloud Run or Hugging Face Spaces

