# Automated Book Publication Workflow

A Python-based system for automated book content extraction, AI-driven rewriting, human-in-the-loop editing, version management, and intelligent retrieval. This project demonstrates an end-to-end workflow for transforming publicly available text (e.g., from Wikisource) into publish-ready content with robust versioning and search capabilities.

---

## 🚀 Features

- **Web Scraping & Screenshots**  
  Uses Playwright to fetch and screenshot chapters from sources like Wikisource.

- **AI-Driven Writing & Review**  
  Integrates LLMs (e.g., Gemini) to "spin" chapters and refine content.

- **Human-in-the-Loop Iterations**  
  Supports multiple rounds of human feedback for writers, reviewers, and editors.

- **Agentic API Architecture**  
  Seamless content flow between AI agents and human participants.

- **Versioning & Consistency**  
  Stores all content versions in ChromaDB and retrieves them using a reinforcement learning (RL) search algorithm.

---

## 🛠️ Core Technologies

- **Python**: Main development language  
- **Playwright**: Web scraping and screenshots  
- **LLM (e.g., Gemini)**: AI writing, reviewing, and editing  
- **ChromaDB**: Versioned storage and vector search  
- **RL Search Algorithm**: Consistent, intelligent retrieval of published content

---

## 📚 Workflow Overview

1. **Scraping**  
   Fetches chapter content and screenshots from a provided URL.

2. **AI Writing & Review**  
   - AI Writer "spins" (rewrites) the chapter.  
   - AI Reviewer suggests improvements.

3. **Human-in-the-Loop**  
   - Human writers, reviewers, and editors can iteratively refine content.

4. **Versioning**  
   - Every iteration is saved to ChromaDB.  
   - RL search ensures retrieval of the most relevant version.

5. **Publishing**  
   - Finalized content can be exported in formats like EPUB or PDF.

---

## ⚡ Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/automated-book-publication.git
cd automated-book-publication
python main.py
