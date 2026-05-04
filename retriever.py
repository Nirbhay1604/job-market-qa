import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def load_index():
    index = faiss.read_index('jobs.index')
    with open('jobs_metadata.pkl', 'rb') as f:
        jobs = pickle.load(f)
    return index, jobs

def retrieve(query, top_k=5):
    """
    Finds top_k most relevant jobs for a given query.
    Returns FULL descriptions for better answers.
    """
    index, jobs = load_index()

    query_vector = model.encode([query])
    query_vector = np.array(query_vector).astype('float32')

    distances, indices = index.search(query_vector, top_k)

    results = []
    for i, idx in enumerate(indices[0]):
        if idx == -1:
            continue
        job = jobs[idx]
        results.append({
            'title': job['title'],
            'company': job['company'],
            'location': job['location'],
            'description': job.get('description', 'No description available.'),
            'relevance_score': float(distances[0][i])
        })

    return results

if __name__ == "__main__":
    print("=" * 50)
    print("🔍 TESTING RETRIEVER...")
    print("=" * 50)

    query = "What skills are needed for Python backend jobs?"
    print(f"\nQuery: {query}")
    results = retrieve(query)
    for i, job in enumerate(results, 1):
        print(f"\n{i}. {job['title']} @ {job['company']}")
        print(f"   Description length: {len(job['description'])} chars")

    print("\n✅ Retriever working!")