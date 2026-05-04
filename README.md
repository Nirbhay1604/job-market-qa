# Job Market Q&A

An AI-powered job market analysis tool that answers natural language questions using real job data. Built with a full RAG (Retrieval-Augmented Generation) pipeline — answers are grounded in actual job listings, not LLM hallucinations.

> **Data source:** 161 remote job listings scraped from [WeWorkRemotely](https://weworkremotely.com). Answers reflect this dataset, not the entire job market.

---

## How It Works

```
User Question
      ↓
Convert to vector embedding (Sentence Transformers)
      ↓
FAISS searches 161 job vectors for closest matches
      ↓
Top 3 most relevant job listings retrieved
      ↓
Llama 3.2 generates answer using only retrieved data
      ↓
Answer streamed token by token to UI
```

This is a RAG (Retrieval-Augmented Generation) system — the LLM only answers from retrieved job data, not from its training knowledge. This prevents hallucination and keeps answers grounded in real market data.

---

## Tech Stack

| Component | Tool | Why |
|---|---|---|
| Embeddings | Sentence Transformers (all-MiniLM-L6-v2) | Lightweight BERT-based model, no API needed |
| Vector Search | FAISS | Fast similarity search across job vectors |
| LLM | Llama 3.2 via Ollama | Free, runs locally, no API costs |
| UI | Streamlit | Fast to build, clean for demos |
| Data Storage | SQLite | Structured storage, not just CSV |

---

## Project Structure

```
job-market-qa/
├── ingest.py              # Builds FAISS index from job descriptions
├── retriever.py           # Semantic search using FAISS
├── answerer.py            # Prompt builder + Ollama LLM integration
├── app.py                 # Streamlit UI
├── processed_jobs.db      # SQLite database of 161 job listings
├── jobs.index             # FAISS vector index
├── jobs_metadata.pkl      # Job metadata for retrieval
└── requirements.txt
```

---

## Setup

### Prerequisites
- Python 3.11+
- [Ollama](https://ollama.com) installed

### 1. Clone the repo
```bash
git clone https://github.com/Nirbhay1604/job-market-qa.git
cd job-market-qa
```

### 2. Create virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Pull Llama 3.2
```bash
ollama pull llama3.2
```

### 5. Run the app
```bash
streamlit run app.py
```

> The database, FAISS index, and metadata are already included in the repo — no need to run ingestion.

---

## Example Questions

- "What skills do Python backend jobs require?"
- "Which companies are hiring for ML roles?"
- "What tools do DevOps engineers need?"
- "What are the most common requirements for remote jobs?"
- "Which roles require TypeScript experience?"

---

## Key Design Decisions

**Why no LangChain?**
Built the RAG pipeline from scratch — embeddings, FAISS search, prompt construction, and LLM calls are all explicit and transparent. Easier to debug, understand, and explain in interviews.

**Why FAISS over a vector database?**
For 161 records, FAISS is faster to set up with zero infrastructure overhead. IndexFlatL2 gives exact search results, appropriate at this scale.

**Why Llama 3.2 locally?**
No API costs, no rate limits, no data leaving the machine. Works on any laptop with 8GB+ RAM.

**Why embed full job listings?**
Each job is embedded as a single unit (title + company + location + description) to preserve context. Splitting into smaller chunks would lose the relationship between role requirements.

---

## Future Improvements

- Add PDF/resume upload — compare your profile against job market
- Expand dataset with more job boards
- Track skill trends over time
- Deploy to Hugging Face Spaces for public access

---

##  Contributing
Fork the repository
Create a feature branch (git checkout -b feature/amazing-feature)
Commit changes (git commit -m 'Add amazing feature')
Push to branch (git push origin feature/amazing-feature)
Open a Pull Request
