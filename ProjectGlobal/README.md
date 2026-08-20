# Project Global — Global Intelligence Dashboard

A Streamlit application combining live APIs, structured datasets, interactive visualizations, and RAG-based semantic search with multi-model LLM fallback.

## Features

| Tab | Description |
|-----|-------------|
| **Home** | Project overview, architecture, tech stack |
| **Assistant** | Perplexity-style chat: RAG retrieval → Gemini → OpenRouter → Cohere fallback |
| **News** | Live headlines + search via NewsAPI |
| **Weather & AQI** | Location search → current conditions → 5-day forecast → air quality + forecast |
| **NASA** | Astronomy Picture of the Day (with publish-gap fallback) |
| **Internet** | Global internet metrics: usage %, subscriptions, broadband (world map, rankings, trends) |
| **AI Models** | LMSYS Chatbot Arena leaderboard: ratings, votes, org analysis, license comparison |
| **GHI** | World Happiness Report data: rankings, GDP vs happiness, factor analysis, trends |

## Architecture

```
app.py                 Streamlit entrypoint, tab navigation
API/
├── ChatBot.py         RAG + multi-model fallback (Gemini → OpenRouter → Cohere)
├── rag.py             Query-time embedding + ChromaDB retrieval
├── embed_data.py      One-time local embedding script (run on GPU)
├── News.py            NewsAPI: headlines + search
├── Weather.py         OpenWeather: geocoding, current, forecast, AQI
├── NASA.py            NASA APOD with fallback
├── Internet_data.py   Internet dataset: maps, rankings, trends
├── ai_model.py        AI Arena: ratings, votes, org/license analysis
├── GHI.py             Global Happiness Index: rankings, correlations, trends
├── data/              CSV/MD datasets (source files)
└── chroma_db/         Vector store (created by embed_data.py)
```

## Quick Start

### 1. Install dependencies
```bash
pip install -r Requirements.txt
```

### 2. Configure API keys
Create `.env` in project root:
```env
GEMINI_API_KEY=your_key
OPENROUTER_API_KEY=your_key
COHERE_API_KEY=your_key
WEATHER_KEY=your_openweather_key
NASA_KEY=your_nasa_key
NEWS_KEY=your_newsapi_key
```
Or use Streamlit secrets (`.streamlit/secrets.toml`).

### 3. Build vector index (run once locally on GPU)
```bash
python embed_data.py
```
- Uses **BAAI/bge-m3** with FP16 on CUDA (optimized for RTX 4060)
- Only re-embeds changed files (hash-based incremental)
- Stores vectors in `API/chroma_db/`

### 4. Run
```bash
streamlit run app.py
```

## RAG Pipeline

```
User Query → embed_text() → ChromaDB similarity search → top-5 docs
    → build_context() → augmented prompt → Gemini
    → (fail) → OpenRouter → (fail) → Cohere
```

## Hardware Notes

- `embed_data.py` optimized for **RTX 4060 8GB**: batch=256, FP16, torch.compile
- Query-time embedding in `rag.py` also uses CUDA+FP16
- First run downloads ~500MB model weights

## Data Sources

- **News**: NewsAPI (free tier)
- **Weather/AQI**: OpenWeatherMap
- **NASA APOD**: NASA Open API
- **Internet**: Kaggle Internet Dataset
- **AI Models**: LMSYS Chatbot Arena (Kaggle)
- **GHI**: World Happiness Report style dataset

## Project Structure

```
ProjectGlobal/
├── app.py                      # Main Streamlit app
├── embed_data.py               # Local GPU embedding script
├── Requirements.txt            # Dependencies
├── .env                        # API keys (gitignored)
├── .streamlit/
│   └── config.toml             # Streamlit theme config
├── API/
│   ├── __init__.py
│   ├── ChatBot.py              # RAG + multi-model chat
│   ├── rag.py                  # Retrieval interface
│   ├── News.py
│   ├── Weather.py
│   ├── NASA.py
│   ├── Internet_data.py
│   ├── ai_model.py
│   ├── GHI.py
│   ├── data/                   # Source datasets
│   │   ├── Project_Vision.md
│   │   ├── GlobalHappienessIndex.csv
│   │   ├── ai_model_arena_rankings_streamlit.csv
│   │   └── internet_dataset.csv
│   ├── chroma_db/              # Vector store (gitignored)
│   └── cache/                  # API response caches (gitignored)
└── README.md
```

## License

MIT