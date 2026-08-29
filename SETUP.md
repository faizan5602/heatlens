# HeatLens Analytics - Setup Guide

## Prerequisites

- Python 3.10+
- Node.js 16+ and npm
- API Keys for:
  - **Google Gemini API** (for AI analysis)
  - **FortyGuard API** (for heat exposure data)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd heatlens_v1.0
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Configure Environment Variables

Create a `.env` file in the project root (copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` and add your API credentials:

```env
# API Credentials (SERVER SIDE ONLY - NEVER EXPOSE TO FRONTEND)
FORTYGUARD_API_KEY=your_actual_fortyguard_key_here
GEMINI_API_KEY=your_actual_gemini_key_here
GEMINI_API_KEYS=key1,key2  # Optional comma-separated pool for rate limiting
```

#### Run the Backend

```bash
python -m backend.main
```

The API will be available at `http://localhost:8000`  
API Documentation: `http://localhost:8000/docs`

### 3. Frontend Setup

#### Install Dependencies

```bash
cd frontend
npm install
```

#### Run Development Server

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

### 4. Running Tests

```bash
# Python tests
pytest tests/

# Frontend tests
npm run test  # if configured
```

## API Keys

### Google Gemini API

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Click "Get API Key"
3. Create a new API key for this project
4. Add it to `.env` as `GEMINI_API_KEY`

### FortyGuard API

1. Register at [FortyGuard](https://fortyguard.com/)
2. Navigate to API settings
3. Generate an API key
4. Add it to `.env` as `FORTYGUARD_API_KEY`

## Project Structure

```
heatlens_v1.0/
├── backend/                 # FastAPI backend
│   ├── api/                # API routes
│   ├── services/           # External service integrations
│   ├── analytics/          # Heat analytics algorithms
│   ├── models/             # Pydantic models
│   └── config.py           # Configuration
├── frontend/               # React + TypeScript frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API client
│   │   └── types/          # TypeScript types
│   └── index.html
├── tests/                  # Test suite
├── data/                   # Data directory (excluded from git)
├── .env.example           # Environment template
├── .gitignore             # Git ignore rules
├── requirements.txt       # Python dependencies
└── package.json          # Node.js dependencies
```

## Security Notes

- **Never commit `.env` file** – Use `.env.example` as template instead
- **API keys are environment-only** – All keys are loaded from `.env` at runtime
- **Frontend never sees API keys** – Keys are used only server-side in backend
- **Cache directory is excluded** – `data/cache/` is not committed to repository

## Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `ENVIRONMENT` | development or production | No (default: development) |
| `LOG_LEVEL` | Logging level (INFO, DEBUG, etc.) | No (default: INFO) |
| `FORTYGUARD_API_KEY` | FortyGuard service API key | Yes |
| `GEMINI_API_KEY` | Google Gemini API key | Yes |
| `GEMINI_API_KEYS` | Comma-separated Gemini keys for rotation | No |
| `CACHE_DIR` | Cache directory path | No (default: ./data/cache) |
| `CACHE_TTL_SECONDS` | Cache time-to-live | No (default: 86400) |

## Troubleshooting

### Port Already in Use

If port 8000 is already in use, modify `PORT` in `.env`:
```env
PORT=8001
```

### API Key Issues

- Verify your API keys are correctly added to `.env`
- Check that there are no leading/trailing spaces
- Ensure keys are not accidentally committed to git (run `git status`)

### Module Import Errors

Ensure virtual environment is activated:
```bash
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Ensure `.env` file is never committed
4. Submit a pull request

## License

[Add your license here]

## Support

For issues and questions, please open an issue on GitHub.
