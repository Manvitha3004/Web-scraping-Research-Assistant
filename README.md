# Autonomous Research Assistant 🔍

**AI-powered web research, scraping, and summarization tool** — Search, scrape, analyze, and summarize web content automatically using completely free APIs.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Configuration](#configuration)
- [Free API Keys](#free-api-keys)
- [Usage](#usage)
- [Docker Deployment](#docker-deployment)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Features in Detail](#features-in-detail)
- [Limitations](#limitations)
- [Known Issues](#known-issues)
- [Future Improvements](#future-improvements)
- [Contributing](#contributing)
- [License](#license)

## Features

✨ **Key Features:**

- 🔍 **Web Search** — DuckDuckGo integration (no API key needed!)
- 📄 **Web Scraping** — Extract content intelligently with BeautifulSoup
- 🤖 **AI Summarization** — Groq API for advanced NLP summaries
- 📊 **Content Analysis** — Extract key points, themes, and statistics
- 💾 **Smart Caching** — 24-hour cache with automatic expiration
- 📱 **Responsive Design** — Terminal-aesthetic dark UI
- ⚡ **Rate Limiting** — Respectful request delays to avoid blocks
- 📋 **Markdown Export** — Copy full reports as formatted markdown
- 🔐 **Search History** — LocalStorage-based recent searches
- 🎨 **Modern UI** — Smooth animations with Vite + React
- 📈 **Progress Tracking** — 4-step visual progress indicator

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React + Vite)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ SearchBar    │  │ Research     │  │ SourceCard   │      │
│  │ Component    │  │ Report       │  │ Component    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────────────────────────────────────────┬┘
                            ↓ HTTP/REST API
┌─────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI + Python)                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │          Research Pipeline Orchestrator             │   │
│  ├─────────────┬─────────────┬──────────────┬─────────┤   │
│  │ SearchSvc   │ ScraperSvc  │ SummarizerSvc│AnalyzerS│   │
│  │ (DuckDuckGo)│(BeautifulSoup)│(Groq API)   │Service  │   │
│  └─────────────┴─────────────┴──────────────┴─────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Caching Layer (SimpleCache + diskcache)            │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
              ┌─────────────────────────────┐
              │  External Free APIs         │
              │ • DuckDuckGo Search API     │
              │ • Groq (llama3-8b-8192)     │
              │ • Web Content (HTTP)        │
              └─────────────────────────────┘
```

## Tech Stack

### Backend
- **Framework**: FastAPI (async web framework)
- **Server**: Uvicorn
- **Search**: `duckduckgo-search` (completely free, no key needed)
- **Scraping**: `requests` + `BeautifulSoup4`
- **AI Summarization**: Groq API (`groq` SDK)
- **NLP Fallback**: `sumy` + NLTK
- **Caching**: `diskcache` and simple JSON file-based cache
- **Rate Limiting**: `slowapi`
- **Data Validation**: Pydantic

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: CSS Variables (custom, no frameworks)
- **State Management**: React Hooks
- **HTTP Client**: Fetch API

## Getting Started

### Prerequisites

- **Node.js** 18+ (for frontend)
- **Python** 3.10+ (for backend)
- **pip** or **conda** (Python package manager)
- **npm** (Node package manager)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create a Python virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**

   **Windows:**
   ```powershell
   venv\Scripts\activate
   ```

   **macOS/Linux:**
   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Copy .env.example and configure:**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your API keys (see [Free API Keys](#free-api-keys) section)

6. **Run the backend server:**
   ```bash
   uvicorn main:app --reload --port 8000
   ```

   The API will be available at `http://localhost:8000`
   - API Docs: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

   The app will be available at `http://localhost:5173`

4. **Build for production:**
   ```bash
   npm run build
   ```

## Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Groq API key (required for AI summarization)
GROQ_API_KEY=your_groq_api_key_here

# HuggingFace API key (optional fallback)
HF_API_KEY=your_huggingface_api_key_here

# Cache directory
CACHE_DIR=./cache

# Maximum sources to retrieve
MAX_SOURCES=10

# Debug mode
DEBUG=true

# Server port
PORT=8000
```

## Free API Keys

### 1. **Groq API** (For AI Summarization)

- Go to: https://groq.com
- Sign up (free)
- Navigate to API Keys
- Copy your key
- Paste in `.env` as `GROQ_API_KEY`
- **Free Tier**: 14,400 requests/day (llama3-8b-8192 model)

### 2. **DuckDuckGo Search** (No Key Needed!)

The `duckduckgo-search` Python library requires **no API key** — it's completely free and anonymous.

### 3. **HuggingFace** (Optional Fallback)

- Go to: https://huggingface.co
- Sign up (free)
- Navigate to Settings → Access Tokens
- Copy your token
- Paste in `.env` as `HF_API_KEY`
- **Free Tier**: Rate-limited inference API

## Usage

1. **Start both backend and frontend** (see Getting Started)
2. **Open browser** to `http://localhost:5173`
3. **Enter a research topic** in the search bar
4. **Wait for the assistant** to:
   - Search for relevant sources (Step 1)
   - Scrape content (Step 2)
   - Analyze findings (Step 3)
   - Generate summary (Step 4)
5. **View the report** with:
   - Comprehensive summary
   - Key bullet points
   - Recurring themes/keywords
   - Source cards with option to expand
   - Report statistics
6. **Copy the report** as Markdown using the "Copy Report" button
7. **View search history** for quick re-running

### Example Research Topics

- "What is artificial intelligence?"
- "Latest renewable energy developments"
- "How does machine learning work?"
- "Impact of climate change on oceans"
- "Future of quantum computing"

## Docker Deployment

Deploy both backend and frontend with Docker Compose:

1. **Create `.env` file** with your API keys
2. **Run Docker Compose:**
   ```bash
   docker-compose up --build
   ```
3. **Access the application:**
   - Frontend: `http://localhost:5173`
   - Backend API: `http://localhost:8000`

### Docker Compose Services

- **Backend**: FastAPI on port 8000
- **Frontend**: React development server on port 5173

## Project Structure

```
Web-scraping-Research-Assistant/
├── backend/
│   ├── main.py                 # FastAPI entry point
│   ├── requirements.txt         # Python dependencies
│   ├── .env.example             # Example environment variables
│   ├── Dockerfile               # Backend Docker image
│   ├── routers/
│   │   └── research.py          # /api/research endpoint
│   ├── services/
│   │   ├── search.py            # DuckDuckGo search
│   │   ├── scraper.py           # Web scraping logic
│   │   ├── summarizer.py        # Groq API integration
│   │   └── analyzer.py          # Content analysis
│   ├── models/
│   │   └── schemas.py           # Pydantic models
│   └── utils/
│       ├── cache.py             # Cache management
│       └── cleaner.py           # Text cleaning utilities
│
├── frontend/
│   ├── src/
│   │   ├── main.jsx             # React entry point
│   │   ├── App.jsx              # Main app component
│   │   ├── components/
│   │   │   ├── SearchBar.jsx
│   │   │   ├── ResearchReport.jsx
│   │   │   ├── SourceCard.jsx
│   │   │   ├── KeyPoints.jsx
│   │   │   ├── ThemesTags.jsx
│   │   │   ├── ProgressLoader.jsx
│   │   │   └── ErrorDisplay.jsx
│   │   ├── hooks/
│   │   │   └── useResearch.js   # API communication hook
│   │   └── styles/
│   │       └── globals.css      # Global styles & theme
│   ├── index.html               # HTML entry point
│   ├── vite.config.js           # Vite configuration
│   ├── package.json             # Node dependencies
│   └── Dockerfile               # Frontend Docker image
│
├── docker-compose.yml           # Multi-container orchestration
├── .gitignore
└── README.md                    # This file
```

## API Endpoints

### POST `/api/research`

Perform a complete research pipeline.

**Request:**
```json
{
  "query": "artificial intelligence",
  "num_sources": 5
}
```

**Response:**
```json
{
  "query": "artificial intelligence",
  "summary": "Comprehensive multi-paragraph summary...",
  "key_points": [
    "AI is transforming industries...",
    "Machine learning is a subset...",
    "..."
  ],
  "themes": ["machine learning", "neural networks", "deep learning", "..."],
  "sources": [
    {
      "title": "Wikipedia - Artificial Intelligence",
      "url": "https://en.wikipedia.org/wiki/Artificial_intelligence",
      "snippet": "Artificial intelligence (AI) is...",
      "scraped_content": "Full extracted text from page..."
    },
    "..."
  ],
  "processing_time": 12.45,
  "cached": false,
  "error": null
}
```

### GET `/api/research/health`

Health check endpoint.

```json
{
  "status": "healthy",
  "services": {
    "search": "ok",
    "scraper": "ok",
    "summarizer": "ok",
    "analyzer": "ok"
  }
}
```

## Features in Detail

### 1. Search Service (DuckDuckGo)
- No API key or authentication needed
- Returns title, URL, and snippet for each result
- Configurable number of results
- Automatic rate limiting (1-2 second delays)
- Retry logic with exponential backoff

### 2. Scraper Service
- Extracts main content from web pages
- Removes navigation, footer, scripts, and ads
- Respects robots.txt
- User-agent rotation (6+ common browser agents)
- Content truncation (3000 chars max per source)
- PDF and non-HTML content filtering
- 10-second timeout per page

### 3. Summarizer Service
- **Primary**: Groq API (llama3-8b-8192 model)
  - Free tier: 14,400 requests/day
  - 3-5 paragraph coherent summaries
  - Context-aware based on original query
- **Fallback 1**: NLTK-based extractive summarization
- **Fallback 2**: First 1500 characters extraction

### 4. Analyzer Service
- Extracts 5-8 key bullet points
- Identifies 3-5 recurring themes/keywords
- Uses TF-IDF + stop word filtering
- Calculates content statistics
- Basic sentiment analysis

### 5. Caching System
- File-based cache with JSON storage
- MD5 hash-based key generation
- 24-hour TTL (configurable)
- Automatic expiration cleanup
- Instant return for cached queries

### 6. Frontend UX
- **Terminal Aesthetic**: Dark theme with cyan/amber accents
- **Responsive Design**: Mobile, tablet, desktop support
- **Animations**:
  - Typing cursor on search placeholder
  - Multi-step progress bar (4 steps)
  - Card fade-in with stagger effect
  - Hover glow effects
- **Search History**: Last 5 searches in localStorage
- **Copy to Clipboard**: Export reports as Markdown
- **Expandable Source Cards**: Show full content on demand

## Limitations

⚠️ **Known Limitations:**

1. **Rate Limiting**
   - DuckDuckGo: May block if requests are too rapid
   - Solution: Automatic 1-2 second delays between requests
   - Groq API: 14,400 requests/day free tier
   - Solution: Caching prevents repeated API calls

2. **Scraping Challenges**
   - JavaScript-rendered content won't be scraped (uses static parsing)
   - Some sites block automated requests
   - Solution: Graceful fallback; skips blocked sites and continues

3. **Content Quality**
   - Relies on robots.txt respect (honored by default)
   - Some sites may have paywalls or require login
   - Solution: Extracts whatever is publicly accessible

4. **Summarization Accuracy**
   - AI summaries are only as good as the source content
   - May miss nuances in highly technical topics
   - Fallback methods are more basic

5. **Caching**
   - Cache is local to the server (not distributed)
   - No cross-instance cache sharing
   - Solution: Use Redis for production deployments

## Known Issues

🐛 **Current Issues:**

1. **PDF Content** — PDFs are currently skipped entirely. Future versions could use `PyPDF2` or `pdfplumber`.

2. **JavaScript-Heavy Sites** — Sites requiring JS rendering (React, Vue, etc.) won't have their content extracted. Consider using Selenium or Playwright for full rendering.

3. **Very Large Pages** — Pages over 30KB are truncated. Consider implementing streaming or pagination.

4. **API Timeouts** — Groq API occasional timeouts during high load. Fallback methods handle this gracefully.

## Future Improvements

🚀 **Planned Enhancements:**

- [ ] **PDF Extraction** — Using `PyPDF2` or `pdfplumber`
- [ ] **JavaScript Rendering** — Selenium/Playwright integration for dynamic sites
- [ ] **Advanced NLP** — spaCy integration for better entity recognition
- [ ] **Custom Summarization Length** — User can choose summary depth (short/medium/long)
- [ ] **Export Formats** — PDF, DOCX, JSON export options
- [ ] **Real-time Streaming** — WebSocket support for live updates during research
- [ ] **Multi-Language Support** — Automatic language detection and translation
- [ ] **Knowledge Graph** — Visualize connections between key concepts
- [ ] **Fact Checking** — Cross-reference claims against known sources
- [ ] **Database Backend** — Replace JSON caching with MongoDB/PostgreSQL
- [ ] **Authentication** — User accounts and personal research history
- [ ] **API Rate Limiting** — Per-IP rate limiting with `slowapi`
- [ ] **Admin Dashboard** — Monitoring, stats, and cache management

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License — See LICENSE file for details.

---

**Made with ❤️ for autonomous research**

**Questions?** Check the [section headers](#table-of-contents) or open an issue!
