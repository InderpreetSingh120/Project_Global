#!/usr/bin/env python
"""
One-time embedding script for Project Global data.
Run locally: python embed_data.py

Optimized for RTX 4060 (8GB VRAM), 16GB RAM, Ryzen 5600X.
"""

import hashlib
import json
from pathlib import Path
from typing import List, Dict, Any, Generator
import pandas as pd
from tqdm import tqdm
import torch

# ─── Config (tuned for RTX 4060 8GB) ────────────────────
EMBED_MODEL = "BAAI/bge-m3"          # Best for mixed text/numeric, 8k context
BATCH_SIZE = 256                      # 4060 8GB handles this easily
USE_FP16 = True                       # Half precision = 2x speed, half VRAM
TORCH_COMPILE = True                  # PyTorch 2.0+ graph optimization
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Only embed the markdown knowledge base (keeps chroma_db/ small for git)
EMBED_ONLY_MD = True

# Used when EMBED_ONLY_MD = False (full local embedding)
MAX_DOCS_PER_SOURCE = {
    "ai_model_arena_rankings_streamlit.csv": 2000,
    "GlobalHappienessIndex.csv": 5000,
    "internet_dataset.csv": 5000,
    "Project_Vision.md": 100,
}

DATA_DIR = Path(__file__).parent / "API" / "data"
CHROMA_DIR = Path(__file__).parent / "API" / "chroma_db"
HASH_FILE = CHROMA_DIR / "file_hashes.json"
COLLECTION_NAME = "project_global"


# ─── Hash Utilities ──────────────────────────────────────

def get_file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def load_hashes() -> Dict[str, str]:
    if HASH_FILE.exists():
        return json.loads(HASH_FILE.read_text())
    return {}


def save_hashes(hashes: Dict[str, str]) -> None:
    CHROMA_DIR.mkdir(exist_ok=True)
    HASH_FILE.write_text(json.dumps(hashes, indent=2))


# ─── Document Processing ─────────────────────────────────

def chunk_markdown(text: str, max_chars: int = 1500, overlap: int = 200) -> List[str]:
    chunks, current = [], ""
    for line in text.split("\n"):
        if len(current) + len(line) > max_chars and current:
            chunks.append(current.strip())
            current = current[-overlap:] + "\n" + line
        else:
            current += "\n" + line
    if current.strip():
        chunks.append(current.strip())
    return chunks


def csv_row_to_text(row: pd.Series, columns: List[str]) -> str:
    parts = [f"{col}: {row[col]}" for col in columns if pd.notna(row[col])]
    return " | ".join(parts)


def iter_documents() -> Generator[Dict[str, Any], None, None]:
    if EMBED_ONLY_MD:
        # Only embed Project_Vision.md (keeps vector DB small for git)
        for md_file in DATA_DIR.glob("*.md"):
            text = md_file.read_text(encoding="utf-8")
            chunks = chunk_markdown(text)
            for i, chunk in enumerate(chunks):
                yield {"id": f"{md_file.stem}_chunk_{i}", "text": chunk,
                       "metadata": {"source_file": md_file.name, "source_type": "markdown", "chunk_index": i,
                                   "title": md_file.stem.replace("_", " ").title()}}
    else:
        # Full embedding (CSV + MD) — run locally, not committed
        for csv_file in DATA_DIR.glob("*.csv"):
            df = pd.read_csv(csv_file)
            df.columns = [c.strip().replace(" ", "_").replace("(", "").replace(")", "").replace("%", "pct") for c in df.columns]
            cols = df.columns.tolist()

            if csv_file.name == "ai_model_arena_rankings_streamlit.csv" and "subset" in df.columns and "leaderboard_publish_date" in df.columns:
                df["leaderboard_publish_date"] = pd.to_datetime(df["leaderboard_publish_date"], errors="coerce")
                df = df.sort_values("leaderboard_publish_date").groupby(["model_name", "subset"], as_index=False).last()

            max_docs = MAX_DOCS_PER_SOURCE.get(csv_file.name, len(df))
            if len(df) > max_docs:
                if csv_file.name == "ai_model_arena_rankings_streamlit.csv" and "subset" in df.columns:
                    per_subset = max_docs // df["subset"].nunique()
                    df = df.groupby("subset", group_keys=False).apply(lambda g: g.sample(min(len(g), per_subset), random_state=42))
                else:
                    df = df.sample(max_docs, random_state=42)
                print(f"  Sampled {csv_file.name}: {len(df):,} rows (limit: {max_docs:,})")

            for idx, row in df.iterrows():
                text = csv_row_to_text(row, cols)
                if not text.strip():
                    continue
                yield {"id": f"{csv_file.stem}_{idx}", "text": text,
                       "metadata": {"source_file": csv_file.name, "source_type": "csv", "row_index": int(idx),
                                   **{k: (v.item() if hasattr(v, "item") else v) for k, v in row.items() if pd.notna(v)}}}

        for md_file in DATA_DIR.glob("*.md"):
            text = md_file.read_text(encoding="utf-8")
            chunks = chunk_markdown(text)
            max_chunks = MAX_DOCS_PER_SOURCE.get(md_file.name, len(chunks))
            for i, chunk in enumerate(chunks[:max_chunks]):
                yield {"id": f"{md_file.stem}_chunk_{i}", "text": chunk,
                       "metadata": {"source_file": md_file.name, "source_type": "markdown", "chunk_index": i,
                                   "title": md_file.stem.replace("_", " ").title()}}


# ─── Main ────────────────────────────────────────────────

def main():
    print(f"Scanning {DATA_DIR}...")
    print(f"Device: {DEVICE.upper()} | Batch: {BATCH_SIZE} | FP16: {USE_FP16} | Compile: {TORCH_COMPILE}")

    current_hashes = {f.name: get_file_hash(f) for f in DATA_DIR.iterdir() if f.is_file()}
    stored_hashes = load_hashes()
    changed_files = {name for name, h in current_hashes.items() if stored_hashes.get(name) != h}

    if not changed_files:
        print("No files changed. Embeddings up to date.")
        return

    print(f"Changed/new files: {changed_files}")

    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(EMBED_MODEL, trust_remote_code=True, device=DEVICE)
    if USE_FP16 and DEVICE == "cuda":
        model.half()
        print("FP16 enabled")
    if TORCH_COMPILE and hasattr(torch, "compile") and DEVICE == "cuda":
        try:
            model = torch.compile(model, mode="max-autotune")
            print("torch.compile enabled")
        except Exception as e:
            print(f"torch.compile failed: {e}")

    import chromadb
    from chromadb.config import Settings
    client = chromadb.PersistentClient(path=str(CHROMA_DIR), settings=Settings(anonymized_telemetry=False))
    collection = client.get_or_create_collection(name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"})

    docs_to_embed = [d for d in iter_documents() if d["metadata"]["source_file"] in changed_files]
    if not docs_to_embed:
        print("No documents to embed from changed files.")
        return

    print(f"Embedding {len(docs_to_embed)} documents...")

    for i in tqdm(range(0, len(docs_to_embed), BATCH_SIZE), desc="Embedding"):
        batch = docs_to_embed[i:i + BATCH_SIZE]
        texts = [d["text"] for d in batch]
        embeddings = model.encode(texts, batch_size=BATCH_SIZE, show_progress_bar=False,
                                  normalize_embeddings=True, convert_to_tensor=True, device=DEVICE)
        embeddings = embeddings.cpu().float().numpy().tolist()
        collection.upsert(ids=[d["id"] for d in batch], embeddings=embeddings,
                          documents=texts, metadatas=[d["metadata"] for d in batch])

    for name in changed_files:
        stored_hashes[name] = current_hashes[name]
    save_hashes(stored_hashes)

    print(f"Done! Collection '{COLLECTION_NAME}' has {collection.count()} documents.")


if __name__ == "__main__":
    main()