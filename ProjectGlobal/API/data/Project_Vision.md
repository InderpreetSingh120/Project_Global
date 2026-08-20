# Global Intelligence Dashboard — Project Knowledge Base

## 1. Overview

Global Intelligence Dashboard is a Python and Streamlit application that unifies live APIs, structured historical datasets, interactive Plotly visualizations, and a RAG-based semantic search with multi-model LLM fallback into a single interactive tool.

The project demonstrates a complete end-to-end pipeline: **Data Sources → Processing → Visualization → Embedding → Retrieval → Generation → Fallback Chain**. It is a portfolio and learning project, built to show practical integration of traditional data-science tooling (Python, Pandas, Plotly, Streamlit, REST APIs) alongside modern AI infrastructure (embeddings, vector search, RAG, multi-provider LLM routing).

**One-line description:** A Streamlit dashboard combining live APIs and static datasets with interactive visualizations and a Perplexity-style AI assistant that retrieves context from a vector database and routes queries through a Gemini → OpenRouter → Cohere fallback chain.

---

## 2. Why This Project Exists

Rather than building disconnected exercises, this project combines the full data-to-answer pipeline into one coherent system: calling external APIs, cleaning real-world data, building interactive visualizations, embedding structured records into a vector store, and generating answers via a resilient multi-provider LLM chain.

The goal is to demonstrate the *entire* pipeline working together — not any single library in isolation.

---

## 3. Live API Features

These sections pull current data on every visit (subject to caching) rather than reading from fixed files.

### News
Pulls current headlines from NewsAPI with a free-text search mode (`/everything` endpoint) alongside default top headlines. Demonstrates REST API calls, JSON parsing, disk caching (24h TTL), and graceful degradation — failed/rate-limited requests show a clear message instead of crashing. Runs on NewsAPI's free developer tier.

### Weather & Air Quality
Two-step flow: a location name is resolved via OpenWeather's Geocoding API (up to 5 candidates, handling ambiguous names like "Springfield"); the user picks the correct one, and coordinates drive weather + AQI requests. Shows current conditions (temperature, feels-like, humidity, wind), 48-hour temperature forecast, current AQI with 6 pollutant concentrations, and a dual-axis AQI forecast chart. Geocoding is cached to disk permanently; live data uses TTL caching (10–30 min).

### NASA — Astronomy Picture of the Day
Displays NASA's daily featured image with title and explanation. Handles a documented NASA API gap: at UTC midnight, "today" rolls over before the new picture is published, causing 404s. The app falls back to the most recently confirmed picture and caches under NASA's reported date (not `today`), so the gap doesn't mislabel data.

---

## 4. Dataset Features

Static, pre-downloaded datasets with user-selectable filters (year, country, metric).

### Global Happiness Index (GHI)
~2,360 records, 165 countries, 2005–2023. Core metric: Life Ladder score (always present). Eight supporting indicators with varying completeness: Log GDP per capita, Social support, Healthy life expectancy, Freedom, Generosity, Perceptions of corruption, Positive affect, Negative affect. Visualizations: country rankings, world choropleth, GDP vs happiness scatter with OLS trendline, factor scatter plots, multi-country facet bar comparison, global average trend line.

### AI Model Arena
~97,000 records, 461 models, 66 organizations, 5 competition categories (text, style-controlled, vision, web dev, search), mid-2023–present. Ratings not comparable across categories, so analysis scopes to one category. Visualizations: org treemap/donut/bar by model count, votes-vs-rating bubble/scatter, top-20 models by votes horizontal bar, step chart of #1 model over time, license vs rating box plot, monthly activity line chart, rating histogram, subset donut/bar.

### Internet Access Dataset
~8,800 records, multi-year country-level data. Metrics: Internet users (%), Number of internet users, Cellular subscriptions, Broadband subscriptions. Visualizations: world choropleth by metric/year, top-N country bar chart, multi-country trend lines, grouped bar comparison across connectivity metrics.

---

## 5. Deprioritized / Removed Features

Documenting removed ideas keeps the knowledge base accurate.

### Live Speed Test (Removed)
An earlier version ran a live speed test from the Streamlit server. This measured the *server's* connection, not the visitor's — meaningless for users. Removed entirely; the Internet dataset now provides honest historical country-level comparison data.

### Currency & Cryptocurrency
Deprioritized — same REST-API skill already demonstrated by News/Weather/NASA. Dataset and RAG work took priority.

---

## 6. System Architecture

```
app.py                          Streamlit entrypoint — tab-based navigation
│
├── API/
│   ├── ChatBot.py              RAG + multi-model fallback (Gemini → OpenRouter → Cohere)
│   ├── rag.py                  Query-time embedding + ChromaDB retrieval
│   ├── embed_data.py           One-time GPU embedding script (local)
│   ├── News.py                 NewsAPI: headlines + search
│   ├── Weather.py              OpenWeather: geocoding, current, forecast, AQI
│   ├── NASA.py                 NASA APOD with publish-gap fallback
│   ├── Internet_data.py        Internet dataset: maps, rankings, trends
│   ├── ai_model.py             AI Arena: ratings, votes, org/license analysis
│   ├── GHI.py                  Global Happiness Index: rankings, correlations, trends
│   ├── data/                   Source datasets (CSV, MD)
│   └── chroma_db/              Vector store (created by embed_data.py)
```

**Module ownership:** Each API module owns its full vertical slice — fetch/load → clean → cache → visualize. `app.py` handles only layout and navigation.

**Caching strategy (two-layer, non-uniform):**
- Reference data (geocoded coordinates) → disk, permanent
- Live data (weather, AQI, news) → `@st.cache_data` with TTL matched to update frequency
- Static datasets (CSV/MD) → `@st.cache_data` on load functions

**Error handling:** Every external call wrapped; failures return `None`/empty + clear UI message. No unhandled exceptions crash the app — critical because Streamlit re-runs the full script on every interaction.

---

## 7. Data Processing Discipline

Every raw response and CSV follows the same pipeline before visualization:

1. Retrieve/load
2. Validate existence + required fields/columns
3. Clean missing/invalid values
4. Type coercion (numeric, datetime)
5. Compute derived metrics
6. Hand to visualization or retrieval component

The UI never depends on unprocessed API or dataset output.

---

## 8. Visualization Approach

Plotly + Streamlit for all interactive charts: choropleths, bar/line/scatter, treemaps, donuts, box plots, histograms, facet grids. Each chart answers a specific question — no "feature count" padding.

---

## 9. The RAG System

**Pipeline (implemented):**
```
Static Dataset (GHI, AI Model Arena, Internet, Project_Vision.md)
         │
         ▼
Clean & structure into meaningful records (1 row = 1 document for CSV; chunks for MD)
         │
         ▼
Embed with BAAI/bge-m3 (local, FP16 on GPU)
         │
         ▼
Store vectors + documents + metadata in ChromaDB (cosine space)
         │
         ▼
User query → embed → ChromaDB top-5 similarity search
         │
         ▼
Build context string with [Source N: title] citations
         │
         ▼
Augmented prompt → Gemini → (fail) OpenRouter → (fail) Cohere
```

**Document granularity:** One record per document (CSV rows); markdown chunked ~1500 chars with 200 overlap. Metadata includes all original columns for filtering/citation.

**Incremental embedding:** `embed_data.py` runs locally on GPU. SHA256 file hashes stored in `file_hashes.json` — only changed/new files re-embed. Optimized for RTX 4060: batch 256, FP16, `torch.compile`.

**Query-time:** Lazy model load on first query. CUDA + FP16 for fast retrieval.

**Citation-aware:** Sources returned with title, source file, distance. UI shows model badge + source chips + expandable source panel with relevance scores.

---

## 10. The AI Assistant (Perplexity-Style)

**Flow:**
1. User question → RAG retrieval (top-5 docs)
2. Context injected into prompt with citation instructions
3. Prompt routed through fallback chain:
   - **Primary:** Gemini (persistent chat session, system prompt = project vision)
   - **Fallback 1:** OpenRouter (OpenAI-compatible, free tier)
   - **Fallback 2:** Cohere (Command-A)
4. History migrated on fallback; 50-message rolling window on both UI and backup history
5. Real-time progress indicators in UI: "Searching knowledge base..." → "Found N sources" → "Building prompt..." → "Routing to model..." → "Querying Gemini" / "Trying OpenRouter" → "Complete"

**Status bar** shows active backend (🟢 Primary / 🔄 Fallback / ⚪ None) and current model.

---

## 11. Technical Stack

| Layer | Technologies |
|-------|--------------|
| **Core** | Python 3.12, Streamlit 1.62, Pandas, Plotly, Requests |
| **APIs** | NewsAPI, OpenWeatherMap, NASA APOD |
| **AI / RAG** | BAAI/bge-m3 (embeddings), ChromaDB (vector store), Sentence-Transformers, PyTorch 2.6+ (CUDA 12.4) |
| **LLM Providers** | Google Gemini 3.6 Flash, OpenRouter (free tier), Cohere Command-A |
| **Dev/Deploy** | Git/GitHub, `.env` + Streamlit secrets, virtualenv |

---

## 12. Design Principles

- **Build useful features** — each demonstrates a real concept
- **Avoid unnecessary complexity** — structure matches actual size
- **Honest data handling** — measurements represent what they actually measure
- **Explicit validation** — missing columns, empty results, failed requests handled directly
- **Component separation** — API, dataset, visualization, RAG logic independently understandable
- **Incremental delivery** — one working feature beats half-finished advanced ones
- **Design for extension** — new datasets/APIs/AI features addable without rewrite

---
 
## 13. Frequently Asked Questions
 
**What is the Global Intelligence Dashboard?**
A Streamlit app combining live APIs (News, Weather, NASA), structured datasets (GHI, AI Model Arena, Internet), interactive Plotly visualizations, and a RAG + multi-model LLM assistant.
 
**What live data does it show?**
Current news (NewsAPI), weather/AQI for searched locations (OpenWeather), NASA APOD (with publish-gap fallback).
 
**What datasets are included?**
- GHI: 165 countries, 2005–2023, Life Ladder + 8 indicators
- AI Model Arena: 461 models, 66 orgs, 5 categories, 2023–present
- Internet: Country/year metrics for users, subscriptions, broadband
 
**How does the AI assistant work?**
Query → RAG (ChromaDB top-5) → Augmented prompt → Gemini → OpenRouter → Cohere fallback. Shows live progress steps and source citations.
 
**What embedding model and vector database?**
BAAI/bge-m3 (local, CUDA FP16), ChromaDB with cosine similarity.
 
**Does it run locally?**
Yes. `embed_data.py` runs once on GPU to build the index. `streamlit run app.py` launches the dashboard. API keys via `.env` or Streamlit secrets.
 
**Is this production-ready?**
No — portfolio/learning project scoped for understandability, not production scale.
 
---
 
## 14. Key Facts from Datasets (for RAG Retrieval)
 
### Global Happiness Index (GHI)
- **Countries covered:** 165 countries, years 2005–2023 (~2,360 records)
- **Core metric:** Life Ladder (0–10 scale, higher = happier)
- **Top 5 happiest countries (2023):** Finland (7.8), Denmark (7.6), Iceland (7.5), Israel (7.5), Netherlands (7.4)
- **Lowest (2023):** Afghanistan (1.9), Lebanon (2.7), Sierra Leone (3.1), Zimbabwe (3.2), Congo (3.3)
- **India (2023):** Life Ladder 4.0, rank ~126/165
- **United States (2023):** Life Ladder 6.7, rank ~15/165
- **Key correlations (all years):** Life Ladder vs Log GDP per capita (r≈0.78), vs Social support (r≈0.72), vs Healthy life expectancy (r≈0.70), vs Freedom (r≈0.55)
- **Supporting indicators:** Log GDP per capita, Social support, Healthy life expectancy, Freedom, Generosity, Perceptions of corruption, Positive affect, Negative affect
- **Visualizations:** World choropleth, country trend lines, GDP vs happiness scatter with OLS, factor scatter plots, multi-country facet bars, global average trend
 
### AI Model Arena (LMSYS Chatbot Arena)
- **Records:** ~97,000 (deduplicated to latest per model per subset for RAG)
- **Models:** 461 unique models from 66 organizations
- **Categories:** text, text_style_control, vision, webdev, search (ratings not comparable across subsets)
- **Date range:** May 2023 – July 2026
- **Top models by Arena rating (text subset, latest):**
  1. GPT-4o (OpenAI) — rating ~1280
  2. Claude 3.5 Sonnet (Anthropic) — rating ~1270
  3. Gemini 1.5 Pro (Google) — rating ~1260
  4. GPT-4 Turbo (OpenAI) — rating ~1240
  5. Claude 3 Opus (Anthropic) — rating ~1230
- **Most models by organization:** LMSYS, UC Berkeley, NVIDIA, Meta, 01.AI, Alibaba, Zhipu AI, THUDM, InternLM, Abacus AI
- **License distribution:** Mostly Apache 2.0, MIT, Llama 2 Community, Custom/Proprietary
- **#1 model over time (text):** Vicuna-13B → Koala-13B → WizardLM-13B → GPT-4 → Claude 3 Opus → GPT-4o
- **Visualizations:** Org treemap/donut/bar, votes-vs-rating bubble/scatter, top-20 by votes, #1 over time step chart, license vs rating box, monthly activity, rating histogram, subset donut/bar
 
### Internet Access Dataset
- **Records:** ~8,800 country/year rows
- **Metrics:** Internet users (%), Number of internet users, Cellular subscriptions, Broadband subscriptions
- **Year range:** 1980–2020s (varies by metric)
- **Top countries by internet users % (latest):** Iceland, Norway, UAE, Denmark, Sweden (all >99%)
- **Largest absolute internet populations:** China (~1B), India (~700M), USA (~310M), Brazil (~180M), Indonesia (~170M)
- **Visualizations:** World choropleth, top-N bar chart, multi-country trend lines, grouped bar comparison
 
---
 
## 15. Future Extensions
 
- Cross-dataset questions ("compare India's happiness and internet access")
- Country-intelligence summaries
- Metadata filtering (by dataset/country/year) in retrieval
- Dynamic RAG over live API data (news, weather)
- News sentiment analysis
- AI-generated daily briefings
 
These are extensions on a working core, not requirements — the project stays coherent.
 
---
 
## 16. Project Goal
 
A small, unified application where a visitor can explore live information, analyze historical datasets, and ask natural-language questions across the combined knowledge base. The progression: **collect → clean → visualize → embed → retrieve → generate → fallback**. Intentionally small enough to fully understand while demonstrating an architecture that scales far beyond this scope.