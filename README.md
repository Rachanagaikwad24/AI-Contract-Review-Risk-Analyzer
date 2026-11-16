# ⚖️ AI Contract Review & Risk Analyzer

> **An advanced AI-powered platform for intelligent contract analysis, risk detection, and obligation extraction — built with Streamlit, LangChain, and local LLMs.**

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Running the App](#-running-the-app)
- [How to Use](#-how-to-use)
- [Project Structure](#-project-structure)
- [Running Tests](#-running-tests)
- [LLM Provider Options](#-llm-provider-options)
- [Exporting Reports](#-exporting-reports)
- [Disclaimer](#-disclaimer)

---

## 🌟 Overview

**AI Contract Review & Risk Analyzer** is a privacy-first, AI-powered legal tech tool that helps users understand contracts without needing a lawyer for every review. Upload a contract in PDF, DOCX, or TXT format and get:

- A **risk assessment** with severity scoring
- A breakdown of all **contractual obligations**
- **Clause-by-clause extraction** with category labels
- **Source-grounded evidence** for every AI finding
- A **chat interface** to ask natural language questions about the contract
- Downloadable **PDF and JSON reports**

The tool runs **100% locally** using [Ollama](https://ollama.com) by default, keeping your sensitive contract data private. It can also be configured to use **OpenAI** as a cloud LLM provider.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 📄 **Multi-format Upload** | Supports PDF, DOCX, and TXT files up to 20 MB |
| 🔴 **Risk Analysis** | Identifies high/medium/low risks with explanations |
| 📌 **Clause Extraction** | Classifies 20+ clause types (Payment, Termination, GDPR, etc.) |
| ✅ **Obligation Tracking** | Extracts all party obligations with deadlines |
| 🔍 **Evidence View** | Links every AI finding to original contract text |
| 💬 **Ask AI** | Chat with the contract using RAG (Retrieval-Augmented Generation) |
| 📊 **Dashboard** | Visual risk summary and contract metadata |
| 📥 **Export** | Download full PDF report or raw JSON analysis |
| 🔒 **Privacy-First** | Runs fully offline with Ollama — no data sent to the cloud |

---

## 🏗️ Architecture

```
+-----------------------------------------------------+
|                  Streamlit Frontend                  |
|  Dashboard | Clauses | Risks | Obligations | Chat   |
+--------------------+--------------------------------+
                     |
+--------------------v--------------------------------+
|                  src/ Backend Modules               |
|                                                     |
|  DocumentParser --> Chunker --> VectorStore (FAISS) |
|       |                               |             |
|  ContractAnalyzer <--- Retriever <----+             |
|       |                                             |
|  RiskAnalyzer | ClauseClassifier | Summarizer       |
|  ObligationExtractor | ReportGenerator              |
|       |                                             |
|  LLM Client (Ollama / OpenAI)                       |
+-----------------------------------------------------+
```

---

## 🛠️ Prerequisites

Before you begin, make sure the following are installed on your system:

### Required

| Tool | Version | Download |
|---|---|---|
| **Python** | 3.10 or higher | [python.org](https://www.python.org/downloads/) |
| **pip** | Latest | Comes with Python |
| **Git** | Any | [git-scm.com](https://git-scm.com) |

### For Local LLM (Recommended)

| Tool | Notes |
|---|---|
| **Ollama** | Local LLM runtime — [ollama.com](https://ollama.com) |
| **qwen2.5:1.5b** | Default model (or any Ollama-compatible model) |

### For OCR Support (Optional)

| Tool | Notes |
|---|---|
| **Tesseract OCR** | Required only for scanned image-based PDFs. [Install guide](https://github.com/tesseract-ocr/tesseract) |

> **Note:** Tesseract is not required for regular text-based PDFs and DOCX files.

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/ai-contract-reviewer.git
cd ai-contract-reviewer
```

### 2. Create a Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

> This may take a few minutes as it downloads ML libraries (sentence-transformers, faiss-cpu, etc.)

### 4. Set Up Ollama (Local LLM)

```bash
# 1. Install Ollama from https://ollama.com

# 2. Pull the default model
ollama pull qwen2.5:1.5b

# 3. Start the Ollama server (keep this terminal open)
ollama serve
```

---

## ⚙️ Configuration

Copy the example environment file and edit it:

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Open `.env` and configure the settings:

```dotenv
# AI Provider: "ollama" (local) or "openai" (cloud)
LLM_PROVIDER=ollama

# Ollama settings (used when LLM_PROVIDER=ollama)
OLLAMA_MODEL=qwen2.5:1.5b
OLLAMA_BASE_URL=http://localhost:11434

# OpenAI settings (used when LLM_PROVIDER=openai)
# OPENAI_API_KEY=sk-...

# Embedding model for semantic search
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Number of context chunks retrieved per query
TOP_K_RESULTS=5

# Storage paths
DATABASE_PATH=data/contracts.db
VECTORSTORE_PATH=vectorstore

# Maximum allowed file size in MB
MAX_FILE_SIZE_MB=20
```

---

## ▶️ Running the App

Make sure your virtual environment is active and Ollama is running, then:

```bash
streamlit run app.py
```

The app will open in your browser at:

```
http://localhost:8501
```

---

## 📖 How to Use

### Step 1 — Upload a Contract
- Go to the **Dashboard** tab in the left sidebar
- Click **Browse files** or drag-and-drop your contract (PDF, DOCX, or TXT)
- Click **🚀 Analyze Contract**

### Step 2 — Wait for Analysis
The app will automatically:
1. Parse and extract text from the document
2. Split it into semantic chunks
3. Build a FAISS vector index for retrieval
4. Run AI analysis for risks, clauses, and obligations

### Step 3 — Explore the Results

Navigate through the sidebar views:

| View | What You Will See |
|---|---|
| **📊 Dashboard** | Overall risk score, contract type, party names, key dates |
| **📋 Contract Analysis** | Detailed metadata — parties, effective dates, contract value |
| **📌 Clauses** | All extracted clauses grouped by category |
| **🔴 Risk Analysis** | Risks ranked by severity (High / Medium / Low) with explanations |
| **✅ Obligations** | All obligations extracted with responsible party |
| **🔍 Evidence** | Source passages from the contract backing each AI finding |
| **💬 Ask Contract** | Free-form chat — ask anything about the contract in plain English |

### Step 4 — Export Results
In the sidebar under **📥 EXPORT**:
- **📄 PDF Report** — A formatted, downloadable report
- **📊 JSON Data** — Raw structured analysis (for integration with other tools)

---

## 📁 Project Structure

```
ai-contract-reviewer/
│
├── app.py                      # Main Streamlit application entry point
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
├── .gitignore
├── LICENSE
│
├── src/                        # Core backend modules
│   ├── config.py               # Environment & app configuration
│   ├── contract_analyzer.py    # Orchestrates the full analysis pipeline
│   ├── document_parser.py      # PDF, DOCX, TXT text extraction
│   ├── chunker.py              # Text chunking for vector indexing
│   ├── vector_store.py         # FAISS vector store management
│   ├── embeddings.py           # Sentence-transformer embeddings
│   ├── retriever.py            # Semantic search / RAG retriever
│   ├── llm_client.py           # LLM abstraction (Ollama / OpenAI)
│   ├── risk_analyzer.py        # Risk detection and scoring
│   ├── clause_classifier.py    # Clause type classification
│   ├── obligation_extractor.py # Obligation extraction
│   ├── summarizer.py           # Contract summarization
│   ├── prompts.py              # LLM prompt templates
│   ├── report_generator.py     # PDF report generation (ReportLab)
│   ├── database.py             # SQLite contract history database
│   ├── text_processor.py       # Text cleaning utilities
│   └── logger.py               # Application logging
│
├── ui/                         # Streamlit UI view components
│   ├── styles.py               # Theme, CSS, and reusable UI helpers
│   ├── dashboard.py            # Dashboard overview view
│   ├── contract_analysis.py    # Contract metadata view
│   ├── clause_view.py          # Clause extraction view
│   ├── risk_view.py            # Risk analysis view
│   ├── obligation_view.py      # Obligations view
│   ├── evidence_view.py        # Evidence / source text view
│   └── chat_view.py            # AI chat interface view
│
├── tests/                      # Unit tests
│   ├── test_chunker.py
│   ├── test_parser.py
│   ├── test_risk_analyzer.py
│   ├── test_vector_store.py
│   ├── test_database.py
│   ├── test_llm_client.py
│   └── test_completion_contracts.py
│
├── sample_contracts/           # Demo contract files for testing
│   └── demo_contract.txt       # Ready-to-use sample contract
│
├── data/                       # Runtime data (auto-created on first run)
│   ├── uploads/                # Uploaded contract files
│   ├── processed/              # Processed documents
│   └── reports/                # Generated PDF reports
│
└── vectorstore/                # FAISS index files (auto-created)
```

---

## 🧪 Running Tests

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run a specific test file
pytest tests/test_parser.py -v

# Run with coverage report
pytest tests/ --cov=src
```

---

## 🤖 LLM Provider Options

### Option A — Ollama (Default, Local & Private)

Best for privacy-sensitive contracts. Runs 100% on your machine.

```bash
# Install Ollama from https://ollama.com, then:
ollama pull qwen2.5:1.5b    # Lightweight default (recommended)
ollama pull llama3.2         # More capable alternative
ollama serve
```

`.env` settings:
```dotenv
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5:1.5b
OLLAMA_BASE_URL=http://localhost:11434
```

### Option B — OpenAI (Cloud)

Best for higher accuracy without local GPU requirements.

`.env` settings:
```dotenv
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-api-key-here
```

> ⚠️ **Warning:** When using OpenAI, contract text is sent to OpenAI servers.
> Do not use this for confidential contracts unless permitted by your organization.

---

## 📥 Exporting Reports

After analysis, the **📥 EXPORT** panel appears in the sidebar:

- **📄 PDF Report** — A clean, formatted report with risk summary, obligations, and clause breakdown. Saved to `data/reports/`.
- **📊 JSON Data** — The full raw analysis object. Useful for building integrations or storing results in your own systems.

---

## ⚠️ Disclaimer

> This tool provides AI-assisted contract analysis for **informational and review purposes only**.
> It does **not** provide legal advice or constitute a final legal opinion.
> All identified risks, obligations, and interpretations should be reviewed by a **qualified legal professional** before any decisions are made.

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">

Built with Streamlit · LangChain · Ollama · FAISS · ReportLab

</div>
