import os
import uuid
from datetime import datetime
from playwright.sync_api import sync_playwright
import chromadb
import google.generativeai as genai

# --- Gemini API Setup ---
GEMINI_API_KEY = "AIzaSyB-_GbtFXVlW8jSFM-FDD_Qai4A9_VpWMY"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# --- Configuration ---
URL = "https://en.wikisource.org/wiki/The_Gates_of_Morning/Book_1/Chapter_1"
SCREENSHOT_PATH = "chapter1_screenshot.png"
CONTENT_PATH = "chapter1_content.txt"
CHROMA_DB_DIR = "chroma_db"
COLLECTION_NAME = "book_chapters"
VERSIONS_PARENT_DIR = "versions"

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

# --- Web Scraping & Screenshot ---
def scrape_and_screenshot(url, screenshot_path, content_path):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        page.screenshot(path=screenshot_path, full_page=True)
        body = page.query_selector("body")
        text = body.inner_text() if body else ""
        with open(content_path, "w", encoding="utf-8") as f:
            f.write(text)
        browser.close()
    print(f"Screenshot saved to {screenshot_path}")
    print(f"Content saved to {content_path}")

# --- Gemini AI Writer ---
def ai_writer(text):
    prompt = f"Rewrite the following chapter in a new style, preserving the meaning and structure:\n\n{text[:3000]}"
    response = model.generate_content(prompt)
    return response.text if hasattr(response, "text") else str(response)

# --- Gemini AI Reviewer ---
def ai_reviewer(text):
    prompt = f"Review the following rewritten chapter and provide suggestions for improvement:\n\n{text[:3000]}"
    response = model.generate_content(prompt)
    return response.text if hasattr(response, "text") else str(response)

# --- Human-in-the-Loop ---
def human_in_the_loop(text, role):
    print(f"\n--- {role} Iteration ---")
    print(f"Current Text:\n{text[:500]} ... [truncated]\n")
    user_input = input("Edit text? (y/n): ")
    if user_input.lower() == 'y':
        print("Enter your edits (end input with a single line containing only 'END'):")
        lines = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)
        return "\n".join(lines)
    return text

# --- ChromaDB Versioning ---
def get_chroma_client():
    return chromadb.PersistentClient(path=CHROMA_DB_DIR)

def save_version(client, content, metadata):
    collection = client.get_or_create_collection(COLLECTION_NAME)
    doc_id = str(uuid.uuid4())
    collection.add(
        documents=[content],
        metadatas=[metadata],
        ids=[doc_id]
    )
    print(f"Version saved with ID: {doc_id}")
    return doc_id

# --- RL Search Algorithm (Simplified) ---
def rl_search(client, query, n_results=1):
    collection = client.get_collection(COLLECTION_NAME)
    results = collection.query(query_texts=[query], n_results=n_results)
    docs = results['documents'][0]
    ids = results['ids'][0]
    print(f"Retrieved version(s): {ids}")
    return docs

# --- Save version to txt file in subdirectory ---
def save_version_txt(version_dir, filename, content):
    ensure_dir(version_dir)
    filepath = os.path.join(version_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Saved {filename} to {version_dir}")

# --- Main Workflow ---
def main():
    # Step 1: Scrape and screenshot
    scrape_and_screenshot(URL, SCREENSHOT_PATH, CONTENT_PATH)

    # Step 2: Load content
    with open(CONTENT_PATH, "r", encoding="utf-8") as f:
        raw_text = f.read()

    # Create unique subdirectory for this run
    run_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    version_dir = os.path.join(VERSIONS_PARENT_DIR, run_id)
    ensure_dir(version_dir)

    # Step 3: AI Writer
    ai_written = ai_writer(raw_text)
    save_version_txt(version_dir, "writer.txt", ai_written)
    ai_written = human_in_the_loop(ai_written, "Writer")
    save_version_txt(version_dir, "writer_edited.txt", ai_written)

    # Step 4: AI Reviewer
    ai_review = ai_reviewer(ai_written)
    save_version_txt(version_dir, "reviewer_feedback.txt", ai_review)
    print(f"\n[AI Reviewer Feedback]:\n{ai_review}\n")
    ai_reviewed = human_in_the_loop(ai_written, "Reviewer")
    save_version_txt(version_dir, "reviewer_edited.txt", ai_reviewed)

    # Step 5: Editor (Human-in-the-loop, can iterate as needed)
    finalized = human_in_the_loop(ai_reviewed, "Editor")
    save_version_txt(version_dir, "final.txt", finalized)

    # Step 6: Save version to ChromaDB
    client_db = get_chroma_client()
    metadata = {
        "timestamp": datetime.now().isoformat(),
        "source_url": URL,
        "role": "final_version"
    }
    save_version(client_db, finalized, metadata)

    # Step 7: RL Search for retrieval
    query = input("Enter search query to retrieve version: ")
    results = rl_search(client_db, query)
    print(f"\n--- Retrieved Content ---\n{results[0][:1000]} ... [truncated]")

if __name__ == "__main__":
    main()
