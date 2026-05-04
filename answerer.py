import requests
import json
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2"

# Words that mean "I'm done, stop talking"
STOP_WORDS = [
    'ok', 'okay', 'thanks', 'thank you', 'thx', 'ty', 'got it',
    'nice', 'cool', 'awesome', 'great', 'perfect', 'alright', 'alr',
    'sure', 'yep', 'yeah', 'yes', 'no', 'nope', 'bye', 'goodbye',
    'i see', 'i understand', 'understood', 'makes sense', 'clear',
    'gotcha', 'fair enough', 'sounds good', 'appreciate it'
]

def is_closing_message(text):
    """Check if user is just acknowledging, not asking a real question"""
    text = text.strip().lower()
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    return text in STOP_WORDS or len(text.split()) <= 2 and any(word in text for word in STOP_WORDS)

def build_prompt(query, retrieved_jobs, conversation_history=None):
    # If user just said thanks/ok, give short polite reply
    if is_closing_message(query):
        return "__CLOSING__", "You're welcome! Feel free to ask if you have more questions about the job market."
    
    # Build context from jobs
    context = ""
    for i, job in enumerate(retrieved_jobs, 1):
        desc = job.get('description', '')
        if len(desc) < 50:
            desc = f"{job.get('title', '')} at {job.get('company', '')}. Remote position."
        
        context += f"""
Job {i}: {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')}
Location: {job.get('location', 'Remote')}
Description: {desc[:1000]}
---"""

    prompt = f"""You are a helpful job market analyst. Answer the user's question using the job listings below.

JOB LISTINGS:
{context}

USER QUESTION: {query}

INSTRUCTIONS:
- Answer based ONLY on the job listings above
- Be helpful and detailed — explain things clearly for someone new to the field
- Mention specific skills, tools, and technologies found in the job data
- Quote from the descriptions when relevant
- If the data doesn't fully answer the question, say what you found and what might be missing
- IMPORTANT: After you finish answering, STOP. Do NOT add extra topics or ask follow-up questions
- Do NOT say things like "Additionally, you might want to learn..." or "Speaking of which..."
- Stay focused on what the user asked

ANSWER:"""

    return prompt, None

def post_process_answer(answer):
    """Remove hallucinated follow-ups that appear after the real answer"""
    # Phrases that indicate the LLM started rambling about new topics
    ramble_starters = [
        "Additionally,",
        "Moreover,",
        "Furthermore,",
        "In addition,",
        "Also,",
        "You might also want to consider",
        "If you're interested in",
        "Speaking of",
        "On a related note",
        "It's worth mentioning",
        "Don't forget about",
        "Another thing to consider",
        "By the way,",
        "While we're at it,",
        "If you want to expand your skills,",
        "To further enhance your profile,",
    ]
    
    # Cut off at first ramble phrase (but not if it's near the start)
    for phrase in ramble_starters:
        idx = answer.find(phrase)
        if idx > 150:  # Only cut if it's clearly an add-on, not the main answer
            answer = answer[:idx].strip()
            break
    
    # Remove trailing offers to help more
    answer = re.sub(r'\s*Would you like me to.*$', '', answer, flags=re.IGNORECASE)
    answer = re.sub(r'\s*Let me know if you.*$', '', answer, flags=re.IGNORECASE)
    answer = re.sub(r'\s*Feel free to ask.*$', '', answer, flags=re.IGNORECASE)
    answer = re.sub(r'\s*I hope this (helps|was helpful).*$', '', answer, flags=re.IGNORECASE)
    answer = re.sub(r'\s*Do you want me to.*$', '', answer, flags=re.IGNORECASE)
    answer = re.sub(r'\s*If you have any (other |more )?questions.*$', '', answer, flags=re.IGNORECASE)
    
    return answer.strip()

def get_answer(query, retrieved_jobs, conversation_history=None):
    prompt, closing_response = build_prompt(query, retrieved_jobs, conversation_history)
    
    # Return short closing response immediately
    if closing_response:
        return closing_response
    
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": 0.4,
                    "top_p": 0.9,
                    "num_predict": 500,
                }
            },
            stream=True,
            timeout=120
        )
        response.raise_for_status()

        full_answer = ""
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                token = data.get("response", "")
                full_answer += token
                if data.get("done"):
                    break

        # Clean up any hallucinated rambling at the end
        full_answer = post_process_answer(full_answer)
        
        return full_answer.strip()

    except requests.exceptions.ConnectionError:
        return "❌ Ollama is not running. Open CMD and run: ollama serve"
    except Exception as e:
        return f"❌ Error: {str(e)}"

if __name__ == "__main__":
    from retriever import retrieve

    print("=" * 50)
    print("🤖 TESTING ANSWERER...")
    print("=" * 50)

    query = "What skills are needed for backend engineering jobs?"
    print(f"\nQuery: {query}")
    jobs = retrieve(query)
    answer = get_answer(query, jobs)
    print(f"\n💬 Answer:\n{answer}")

    print("\n" + "="*50)
    query2 = "ok thanks"
    print(f"Query: {query2}")
    answer2 = get_answer(query2, jobs)
    print(f"💬 Answer: {answer2}")

    print("\n✅ Done!")