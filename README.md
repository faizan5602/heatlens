# HeatLens Analytics 🌡️

> **Hyperlocal Heat Intelligence Platform** — AI-powered heat exposure analysis and correlation detection for climate-resilient communities.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Node: 16+](https://img.shields.io/badge/Node-16+-green.svg)](https://nodejs.org/)
[![Code style: Black](https://img.shields.io/badge/Code%20style-black-000000.svg)](https://github.com/psf/black)

## Overview

HeatLens is a comprehensive heat analytics platform that combines **real-time heat exposure data** from FortyGuard with **AI-powered insights** from Google Gemini to help communities understand and respond to heat stress patterns.

### Key Features

- 🌍 **Hyperlocal Heat Analysis** – Pinpoint heat exposure by location and district
- 🤖 **AI-Powered Insights** – Natural language interpretation of complex heat patterns
- 📊 **Statistical Analysis** – Correlation detection, anomaly identification, and trend analysis
- 🔄 **Smart Caching** – Efficient API request batching and response caching
- 📈 **Interactive Dashboards** – Real-time visualization of heat metrics and trends
- 🔑 **Multi-Key Support** – Automatic API key rotation for rate-limit handling

## Project Structure

```
heatlens_v1.0/
├── backend/                    # FastAPI backend service
│   ├── api/
│   │   └── routes/            # REST API endpoints
│   │       ├── ai.py          # AI analysis routes
│   │       └── analysis.py    # Heat data analysis routes
│   ├── services/              # External integrations
│   │   ├── gemini.py          # Google Gemini API client
│   │   ├── fortyguard.py      # FortyGuard API client
│   │   └── cache.py           # Response caching layer
│   ├── analytics/             # Core analysis algorithms
│   │   ├── anomalies.py       # Anomaly detection
│   │   ├── correlation.py     # Correlation analysis
│   │   ├── statistics.py      # Statistical measures
│   │   └── scoring.py         # Heat stress scoring
│   ├── models/                # Data models
│   │   ├── requests.py        # Request schemas
│   │   └── responses.py       # Response schemas
│   ├── config.py              # Configuration management
│   └── main.py                # FastAPI application
│
├── frontend/                  # React + TypeScript UI
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── AiAnalystPanel.tsx
│   │   │   ├── AnomalyPanel.tsx
│   │   │   ├── CorrelationMatrix.tsx
│   │   │   ├── HeatTimelineChart.tsx
│   │   │   └── ScoreCard.tsx
│   │   ├── services/
│   │   │   └── api.ts         # API client
│   │   ├── types/
│   │   │   └── heatlens.ts    # TypeScript interfaces
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   └── index.html
│
├── tests/                     # Test suite
│   └── test_analytics.py
│
├── data/                      # Data directory
│   └── cache/                 # API response cache
│
├── docs/
│   ├── SETUP.md              # Setup & installation
│   ├── SECURITY.md           # Security policies
│   └── GITHUB_PUSH_CHECKLIST.md
│
└── Configuration Files
    ├── package.json          # Node.js dependencies
    ├── requirements.txt      # Python dependencies
    ├── tsconfig.json         # TypeScript config
    ├── vite.config.ts        # Vite build config
    ├── tailwind.config.js    # Tailwind CSS
    └── .env.example          # Environment template
```

## Quick Start

### Prerequisites

- **Python** 3.10 or higher
- **Node.js** 16+ and npm
- **API Keys**: FortyGuard and Google Gemini

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/heatlens.git
   cd heatlens_v1.0
   ```

2. **Setup environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API credentials
   ```

3. **Install backend dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Install frontend dependencies**
   ```bash
   npm install
   ```

### Running the Application

**Terminal 1 - Backend:**
```bash
python -m backend.main
```
Backend runs at `http://localhost:8000`
API Docs: `http://localhost:8000/docs`

**Terminal 2 - Frontend:**
```bash
npm run dev
```
Frontend runs at `http://localhost:5173`

## API Configuration

### Getting API Keys

#### FortyGuard API
1. Visit [FortyGuard Dashboard](https://fortyguard.com/dashboard)
2. Navigate to API Settings
3. Create and copy your API key
4. Add to `.env`: `FORTYGUARD_API_KEY=your_key_here`

#### Google Gemini API
1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Click "Get API Key"
3. Create new project key
4. Add to `.env`: `GEMINI_API_KEY=your_key_here`

**For detailed setup instructions, see [SETUP.md](SETUP.md)**

## Development

### Running Tests
```bash
pytest tests/ -v
```

### Building for Production
```bash
# Backend: ready to run with `uvicorn`
# Frontend: 
npm run build
# Output: dist/
```

### Code Quality
```bash
# Python linting (if configured)
pip install pylint black
black backend/

# TypeScript type checking
npx tsc --noEmit
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `FORTYGUARD_API_KEY` | Yes | API key for FortyGuard heat data |
| `GEMINI_API_KEY` | Yes | API key for Google Gemini AI |
| `GEMINI_API_KEYS` | No | Comma-separated keys for rotation |
| `ENVIRONMENT` | No | `development` or `production` |
| `LOG_LEVEL` | No | Logging level (INFO, DEBUG, etc.) |
| `CACHE_TTL_SECONDS` | No | Cache time-to-live (default: 86400) |

See [`.env.example`](.env.example) for all options.

## Security

🔒 **This project prioritizes security:**
- ✅ All API keys are environment-based (never hardcoded)
- ✅ `.env` is excluded from git (see `.gitignore`)
- ✅ Sensitive files are never committed
- ✅ CORS is configured for specific origins only

**For detailed security information, see [SECURITY.md](SECURITY.md)**

## API Endpoints

### Analysis Routes (`/analysis`)
- `POST /analysis/raw` – Raw heat data for location
- `POST /analysis/correlations` – Correlation analysis
- `POST /analysis/anomalies` – Anomaly detection
- `POST /analysis/statistics` – Statistical summary

### AI Routes (`/ai`)
- `POST /ai/interpret` – AI interpretation of results
- `POST /ai/query` – Q&A with AI analyst

### Health
- `GET /health` – Health check endpoint

Full API documentation available at `http://localhost:8000/docs` when running.

## Tech Stack

### Backend
- **FastAPI** – Modern Python web framework
- **Pydantic** – Data validation
- **Google Genai** – AI integration
- **Pandas/NumPy/SciPy** – Data analysis

### Frontend
- **React 18** – UI framework
- **TypeScript** – Type safety
- **Vite** – Build tool
- **Tailwind CSS** – Styling
- **Recharts** – Data visualization
- **Lucide React** – Icons

## Project Status

| Component | Status |
|-----------|--------|
| Core Analytics | ✅ Complete |
| AI Integration | ✅ Complete |
| Frontend Dashboard | ✅ Complete |
| Testing | ✅ Complete |
| Documentation | ✅ Complete |
| Production Ready | ⚠️ Requires API Configuration |

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](.github/CONTRIBUTING.md) for guidelines.

### Development Workflow
1. Create a feature branch: `git checkout -b feature/amazing-feature`
2. Make your changes and commit: `git commit -m 'Add amazing feature'`
3. Push to branch: `git push origin feature/amazing-feature`
4. Open a Pull Request

## Troubleshooting

### Port Already in Use
Modify `PORT` in `.env` to use a different port (e.g., `8001`, `8002`).

### API Key Issues
1. Verify keys are correctly added to `.env`
2. Check for leading/trailing spaces
3. Ensure `.env` is not committed to git

### Module Import Errors
Ensure your virtual environment is activated:
```bash
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

See [SETUP.md](SETUP.md) for more troubleshooting.

## Performance

- **API Caching** – Responses cached for 24 hours (configurable)
- **Async Processing** – FastAPI async request handling
- **Request Batching** – Efficient FortyGuard API usage
- **Key Rotation** – Automatic failover on rate limits

## License

This project is licensed under the **MIT License** – see [LICENSE](LICENSE) file for details.

## Support & Contact

- 📧 **Issues**: Open an issue on GitHub
- 💬 **Discussions**: Start a discussion for questions
- 🐛 **Bugs**: Report via GitHub Issues

## Acknowledgments

- **FortyGuard** – Heat exposure data and analytics
- **Google Gemini** – AI-powered insights
- **Open Source Community** – Dependencies and inspiration

---

**Built for climate-resilient communities** 🌍

Last Updated: August 2026 | Version: 1.0.0
