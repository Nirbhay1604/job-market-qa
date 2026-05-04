import sqlite3
import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer

# Load embedding model
# all-MiniLM-L6-v2: lightweight, fast, good quality
# Downloads ~90MB on first run only
print("Loading embedding model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

def load_jobs():
    """
    Reads cleaned job descriptions from SQLite database.
    Returns list of job dicts with title, company, description.
    """
    conn = sqlite3.connect('processed_jobs.db')
    c = conn.cursor()
    c.execute('SELECT title, company, location, description FROM cleaned_jobs')
    rows = c.fetchall()
    conn.close()

    jobs = []
    for row in rows:
        title, company, location, description = row
        # Combine title + description for richer embedding
        combined = f"Job Title: {title}\nCompany: {company}\nLocation: {location}\nDescription: {description}"
        jobs.append({
            'title': title,
            'company': company,
            'location': location,
            'description': description,
            'combined': combined
        })

    print(f"Loaded {len(jobs)} jobs from database")
    return jobs

def build_index(jobs):
    """
    Converts job text to vectors and builds FAISS index.
    
    Why FAISS:
    - Stores vectors and lets us search by similarity
    - Finding 'nearest neighbor' vectors = finding most relevant jobs
    - Much faster than comparing every vector manually
    
    Why embed combined text:
    - Title + company + description gives more context
    - Better embeddings = better search results
    """
    print("Converting job descriptions to vectors...")
    texts = [job['combined'] for job in jobs]
    
    # Convert text to vectors (embeddings)
    # Each job becomes a 384-dimensional vector
    embeddings = model.encode(texts, show_progress_bar=True)
    embeddings = np.array(embeddings).astype('float32')

    # Build FAISS index
    # IndexFlatL2 = exact search using L2 (euclidean) distance
    # Good for small datasets like ours
    dimension = embeddings.shape[1]  # 384
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    print(f"Built FAISS index with {index.ntotal} vectors")
    return index

def save_index(index, jobs):
    """
    Saves FAISS index and job metadata to disk.
    So we don't rebuild every time app starts.
    """
    faiss.write_index(index, 'jobs.index')
    with open('jobs_metadata.pkl', 'wb') as f:
        pickle.dump(jobs, f)
    print("✅ Saved index to jobs.index")
    print("✅ Saved metadata to jobs_metadata.pkl")

if __name__ == "__main__":
    print("=" * 50)
    print("🔧 BUILDING FAISS INDEX...")
    print("=" * 50)
    
    jobs = load_jobs()
    index = build_index(jobs)
    save_index(index, jobs)
    
    print("\n" + "=" * 50)
    print("✅ Ingestion complete!")
    print("You can now run: streamlit run app.py")
    print("=" * 50)