import os
import time
from typing import Any, Callable, Dict, List, Literal, Optional

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

# OpenRouter uses the OpenAI SDK framework to connect
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import cohere
except ImportError:
    cohere = None

# ─────────────────────────────────────────────
# RAG Integration
# ─────────────────────────────────────────────
try:
    from .rag import build_context
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    def build_context(query: str, n_results: int = 5) -> str:
        return ""

# ─────────────────────────────────────────────
# Configuration & Environment Setup
# ─────────────────────────────────────────────

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_THIS_DIR)

PROJECT_INFO_PATH = os.path.join(
    _PROJECT_ROOT,
    "api",
    "data",
    "Project_Vision.md"
)

load_dotenv()

# ── API Keys ──

GEMINI_API_KEY = (
    os.getenv("GEMINI_API_KEY")
    or st.secrets.get("GEMINI_API_KEY")
)

OPENROUTER_API_KEY = (
    os.getenv("OPENROUTER_API_KEY")
    or st.secrets.get("OPENROUTER_API_KEY")
)

COHERE_API_KEY = (
    os.getenv("COHERE_API_KEY")
    or st.secrets.get("COHERE_API_KEY")
)


# ── Models ──

GEMINI_MODEL = "gemini-3.6-flash"
OPENROUTER_MODEL = "openrouter/free"
COHERE_MODEL = "command-a-03-2025"


# ── Timeout Settings ──

PROVIDER_TIMEOUT = 15
MAX_CHAIN_TIME = 45


# ─────────────────────────────────────────────
# Initialize SDK Clients
# ─────────────────────────────────────────────

_client = (
    genai.Client(
        api_key=GEMINI_API_KEY,
        http_options=types.HttpOptions(
            timeout=PROVIDER_TIMEOUT * 1000
        )
    )
    if GEMINI_API_KEY
    else None
)

# OpenRouter initialization using the OpenAI client
_openrouter_client = (
    OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        timeout=PROVIDER_TIMEOUT
    )
    if (OpenAI and OPENROUTER_API_KEY)
    else None
)

_cohere_client = (
    cohere.ClientV2(
        api_key=COHERE_API_KEY,
        timeout=PROVIDER_TIMEOUT
    )
    if (cohere and COHERE_API_KEY)
    else None
)


ANY_BACKEND_CONFIGURED = any([
    _client is not None,
    _openrouter_client is not None,
    _cohere_client is not None,
])


Backend = Literal[
    "gemini",
    "openrouter",
    "cohere",
    "none"
]


# ─────────────────────────────────────────────
# Project Information
# ─────────────────────────────────────────────

def load_project_info() -> str:

    candidates = [
        PROJECT_INFO_PATH,
        os.path.join(_THIS_DIR, "data", "Project_Vision.md")
    ]

    for path in candidates:

        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()

        except FileNotFoundError:
            continue

    return (
        "You are a helpful assistant for this "
        "Streamlit dashboard project."
    )


# ─────────────────────────────────────────────
# Message Types
# ─────────────────────────────────────────────

class Message(Dict):
    role: str
    content: str
    model: Optional[str] = None
    sources: Optional[List[Dict[str, Any]]] = None


# ─────────────────────────────────────────────
# Chatbot Core
# ─────────────────────────────────────────────

class Chatbot:

    def __init__(self, model_name: str = GEMINI_MODEL, max_history: int = 50):

        self.model_name = model_name
        self.max_history = max_history

        self.chat_session = None
        self.using_fallback = False

        self.backup_history: List[Dict[str, str]] = []
        self.ui_history: List[Message] = []

        self.last_used_model: str = "Ready"
        self.active_backend: Backend = "none"

        self.last_event: str = "Initialized"
        self.last_error: Optional[str] = None

    # ─────────────────────────────────────────
    # Session Management
    # ─────────────────────────────────────────

    def start_new_chat(self) -> str:

        self.using_fallback = False
        self.chat_session = None

        self.backup_history = []
        self.ui_history = []

        self.last_used_model = "Ready"
        self.active_backend = "none"

        self.last_event = "Initialized"
        self.last_error = None

        # No providers configured
        if not ANY_BACKEND_CONFIGURED:
            self.using_fallback = True
            self.last_event = "No AI backend configured."
            self.last_error = "No valid API keys were found."
            return "No AI backend configured."

        # ── Try Gemini ──

        if _client is not None:

            try:

                self.chat_session = _client.chats.create(
                    model=self.model_name,
                    config=types.GenerateContentConfig(
                        system_instruction=load_project_info()
                    ),
                    history=[]
                )

                self.active_backend = "gemini"
                self.last_used_model = f"Gemini ({self.model_name})"
                self.last_event = "Gemini session started successfully."
                return "Chat session initialized."

            except Exception as e:
                self.using_fallback = True
                self.last_error = f"Gemini initialization failed: {e}"
                self.last_event = "Gemini unavailable; fallback chain ready."

        # Gemini unavailable
        self.using_fallback = True
        self.last_event = "Using backup AI providers."
        return "Chat session initialized in fallback mode."

    # ─────────────────────────────────────────
    # Main Entry Point — Perplexity-style Flow
    # ─────────────────────────────────────────
    # 1. Query RAG for relevant context
    # 2. Build augmented prompt with context
    # 3. Send through fallback chain: Gemini → OpenRouter → Cohere

    def send_message(
        self,
        user_input: str,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> str:

        def _progress(msg: str):
            if progress_callback:
                progress_callback(msg)

        # Add user message to UI history
        self._append_ui_message("user", user_input, "User")

        if not ANY_BACKEND_CONFIGURED:
            return self._respond_system(
                "⚠️ No AI backend is configured.\n\nPlease add at least one API key."
            )

        # ── Step 1: Retrieve context from RAG ──

        _progress("🔍 Searching knowledge base...")
        rag_context = ""
        sources = []

        if RAG_AVAILABLE:
            try:
                rag_context = build_context(user_input, n_results=5)
                if rag_context:
                    from .rag import query_similar
                    results = query_similar(user_input, n_results=5)
                    sources = [
                        {"title": self._make_source_title(r["metadata"]),
                         "source": r["metadata"].get("source_file", "Unknown"),
                         "distance": r["distance"]}
                        for r in results
                    ]
                    _progress(f"📚 Found {len(sources)} relevant sources")
                else:
                    _progress("📭 No relevant context found")
            except Exception as e:
                self.last_error = f"RAG retrieval failed: {e}"
                _progress("⚠️ RAG search failed, continuing without context")

        # ── Step 2: Build augmented prompt ──

        _progress("📝 Building prompt with context...")
        augmented_prompt = self._build_augmented_prompt(user_input, rag_context)

        # ── Step 3: Route through fallback chain ──

        _progress("🤖 Routing to model...")
        if self.using_fallback or self.chat_session is None:
            reply = self._send_via_fallbacks(augmented_prompt, progress_callback=_progress)
        else:
            reply = self._send_via_gemini(augmented_prompt, progress_callback=_progress)

        # ── Step 4: Record response with sources ──

        _progress("✅ Complete")
        self._append_ui_message("assistant", reply, self.last_used_model, sources)
        return reply

    # ─────────────────────────────────────────
    # Prompt Building
    # ─────────────────────────────────────────

    def _build_augmented_prompt(self, user_input: str, rag_context: str) -> str:
        """Build prompt with RAG context injected."""
        if not rag_context:
            return user_input

        return f"""Context from knowledge base:
{rag_context}

---
User question: {user_input}

Instructions: Answer using the context above when relevant. If the context doesn't contain the answer, say so and use your general knowledge. Cite sources when using context."""

    # ─────────────────────────────────────────
    # Provider: Gemini
    # ─────────────────────────────────────────

    def _send_via_gemini(
        self,
        prompt: str,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> str:

        def _p(msg: str):
            if progress_callback:
                progress_callback(msg)

        _p("💎 Querying Gemini...")
        try:
            response = self.chat_session.send_message(prompt)
            reply_text = (response.text or "").strip()

            if not reply_text:
                raise RuntimeError("Gemini returned an empty response.")

            self.active_backend = "gemini"
            self.last_used_model = f"Gemini ({self.model_name})"
            self.last_event = "Successfully replied via Gemini."
            self.last_error = None

            return reply_text

        except Exception as e:
            self.using_fallback = True
            self.last_error = f"Gemini generation failed: {e}"
            self.last_event = "Gemini failed; routing to fallback chain."
            _p("🔄 Gemini failed, trying fallbacks...")
            return self._send_via_fallbacks(prompt, carry_over_gemini_history=True, progress_callback=progress_callback)

    # ─────────────────────────────────────────
    # Fallback Chain: OpenRouter → Cohere
    # ─────────────────────────────────────────

    def _send_via_fallbacks(
        self,
        prompt: str,
        carry_over_gemini_history: bool = False,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> str:

        def _p(msg: str):
            if progress_callback:
                progress_callback(msg)

        start_time = time.time()

        # Carry Gemini conversation over
        if carry_over_gemini_history and not self.backup_history:
            self._migrate_gemini_history()

        self._append_backup_message("user", prompt)

        system_prompt = load_project_info()
        messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt}
        ] + self.backup_history

        errors = []

        # ── 1. OpenRouter ──

        if _openrouter_client:
            if self._chain_expired(start_time):
                errors.append("OpenRouter skipped: fallback chain timeout.")
            else:
                try:
                    _p("🔄 Trying OpenRouter...")
                    self.active_backend = "openrouter"
                    completion = _openrouter_client.chat.completions.create(
                        model=OPENROUTER_MODEL,
                        messages=messages,
                        temperature=0.7,
                        timeout=PROVIDER_TIMEOUT
                    )
                    reply_text = (completion.choices[0].message.content or "").strip()
                    if not reply_text:
                        raise RuntimeError("OpenRouter returned an empty response.")
                    self._record_success(reply_text, f"OpenRouter ({OPENROUTER_MODEL})")
                    return reply_text
                except Exception as e:
                    errors.append(f"OpenRouter Error: {e}")
                    _p("⚠️ OpenRouter failed, trying Cohere...")

        # ── 2. Cohere ──

        if _cohere_client:
            if self._chain_expired(start_time):
                errors.append("Cohere skipped: fallback chain timeout.")
            else:
                try:
                    _p("🔄 Trying Cohere...")
                    res = _cohere_client.chat(
                        model=COHERE_MODEL,
                        messages=messages
                    )
                    reply_text = ""
                    msg_obj = getattr(res, "message", None)
                    if msg_obj:
                        content_list = getattr(msg_obj, "content", None)
                        if content_list and isinstance(content_list, list):
                            for item in content_list:
                                text = getattr(item, "text", "")
                                if text:
                                    reply_text += text
                    reply_text = reply_text.strip()
                    if not reply_text:
                        raise RuntimeError("Cohere returned an empty response.")
                    self._record_success(reply_text, f"Cohere ({COHERE_MODEL})")
                    return reply_text
                except Exception as e:
                    errors.append(f"Cohere Error: {e}")
                    _p("❌ All fallbacks failed")

        # ── Total Failure ──

        self.active_backend = "none"
        error_msg = "⚠️ All configured AI models failed.\n\n" + "\n".join(errors)
        self._record_failure(error_msg)
        return error_msg

    # ─────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────

    def _chain_expired(self, start_time: float) -> bool:
        return (time.time() - start_time) >= MAX_CHAIN_TIME

    def _make_source_title(self, metadata: Dict[str, Any]) -> str:
        """Build a readable title from RAG metadata."""
        if metadata.get("title"):
            return metadata["title"]
        if metadata.get("source_type") == "csv":
            parts = [str(metadata[k]) for k in ("Country name", "Entity", "model_name") if metadata.get(k)]
            if metadata.get("year"):
                parts.append(f"Year {metadata['year']}")
            if parts:
                return " — ".join(parts)
        return metadata.get("source_file", "Source")

    def _append_ui_message(
        self,
        role: str,
        content: str,
        model: str,
        sources: Optional[List[Dict[str, Any]]] = None
    ):
        msg: Message = {"role": role, "content": content, "model": model}
        if sources:
            msg["sources"] = sources
        self.ui_history.append(msg)
        self._trim_history()

    def _append_backup_message(self, role: str, content: str):
        self.backup_history.append({"role": role, "content": content})
        self._trim_history()

    def _record_success(self, reply_text: str, model_label: str):
        self._append_backup_message("assistant", reply_text)
        self.last_used_model = model_label
        self.last_event = f"Successfully replied via {model_label}."
        self.last_error = None

    def _record_failure(self, error_msg: str):
        self._append_backup_message("assistant", error_msg)
        self._append_ui_message("assistant", error_msg, "Error")
        self.last_used_model = "Error"
        self.last_error = error_msg
        self.last_event = "Complete fallback chain failure."

    def _trim_history(self):
        if len(self.ui_history) > self.max_history:
            self.ui_history = self.ui_history[-self.max_history:]
        if len(self.backup_history) > self.max_history:
            self.backup_history = self.backup_history[-self.max_history:]

    def _migrate_gemini_history(self):
        if self.chat_session is None:
            return
        try:
            for content in self.chat_session.get_history(curated=True):
                text = "".join(p.text for p in (content.parts or []) if p.text)
                if text:
                    role = "assistant" if content.role == "model" else "user"
                    self.backup_history.append({"role": role, "content": text})
        except Exception as e:
            self.last_error = f"Could not migrate Gemini history: {e}"

    def _respond_system(self, text: str) -> str:
        self._append_ui_message("assistant", text, "System")
        self.last_error = "No valid API keys found."
        return text

    # ─────────────────────────────────────────
    # Public API
    # ─────────────────────────────────────────

    def get_display_history(self) -> List[Message]:
        return self.ui_history

    def clear_history(self):
        self.chat_session = None
        self.using_fallback = False
        self.backup_history = []
        self.ui_history = []
        self.last_used_model = "Ready"
        self.active_backend = "none"
        self.last_error = None
        self.last_event = "History cleared."