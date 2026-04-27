# PawPal+ Applied AI System

**Author:** Alexia Martinez

PawPal+ is an AI-powered pet care assistant that combines a smart scheduling engine with a Retrieval-Augmented Generation (RAG) advisor. Owners can manage daily care tasks across multiple pets and ask natural language questions to get personalized, knowledge-backed pet care advice.

---

## Base Project

This project extends the original **PawPal+** scheduling app built in Module 2. The original system focused on task management for pet owners — it allowed users to register pets, schedule care tasks with priority and recurrence, detect scheduling conflicts, and view a daily agenda through a Streamlit UI. It had no AI capabilities.

---

## What's New in This Version

The extended system adds a RAG-powered AI advisor built on top of the original scheduling backend:

- A local knowledge base of pet care documents covering nutrition, vet visits, exercise, and symptoms
- A retrieval layer that matches user questions to relevant knowledge chunks before generating a response
- A Gemini-powered response generator that personalizes answers using the pet's profile
- Confidence scoring on every AI response
- An automated evaluation script that tests reliability across 6 fixed questions

---

## System Architecture

The system has five components:

1. **Streamlit UI** — the front end where owners add pets, schedule tasks, and ask questions
2. **Scheduler** — the original core logic handling tasks, recurrence, conflict detection, and filtering
3. **RAG Retriever** — keyword-based retrieval that selects the most relevant knowledge base files for each question
4. **Knowledge Base** — five plain text files covering dog nutrition, cat nutrition, vet visits, exercise needs, and common symptoms
5. **Gemini AI** — generates a personalized, grounded answer using the retrieved context and the pet's profile

User Question
│
▼
Streamlit UI
│
▼
RAG Retriever ──► Knowledge Base (5 .txt files)
│
▼
Gemini API  ◄── Pet Profile (name, species, breed, age, weight)
│
▼
Answer + Confidence Score ──► Streamlit UI

The system architecture diagram is saved in `/assets/architecture.png`.

---

## Setup Instructions

1. Clone the repository:
git clone https://github.com/your-username/applied-ai-system-final.git
cd applied-ai-system-final

2. Install dependencies:
pip install streamlit google-generativeai

3. Set your Gemini API key:
Windows PowerShell
$env:GEMINI_API_KEY="your-key-here"
Mac/Linux
export GEMINI_API_KEY="your-key-here"

4. Run the app:
python -m streamlit run app.py

5. Run the evaluation script:
python eval.py

---

## Sample Interactions

**Question 1**
Input: Can my dog eat grapes?
Pet: Buddy, Golden Retriever, 3 years, 30.5kg

Response: No, Buddy should definitely not eat grapes. Grapes are toxic to dogs and can cause serious health issues including kidney failure, seizures, or even death. Keep them completely away from Buddy. This is general guidance only. Always consult a licensed veterinarian for medical decisions.
Confidence: 5/5

---

**Question 2**
Input: How often should my cat visit the vet?
Pet: Luna, Siamese, 5 years, 4.2kg

Response: For an adult cat like Luna who is 5 years old, it is recommended to visit the vet annually for a wellness exam. Core vaccines and parasite prevention should be kept up to date. This is general guidance only. Always consult a licensed veterinarian for medical decisions.
Confidence: 5/5

---

**Question 3**
Input: My cat has been vomiting twice today, is that ok?
Pet: Luna, Siamese, 5 years, 4.2kg

Response: While vomiting once is usually not an emergency, Luna vomiting twice today warrants attention. If she seems lethargic or has not eaten, contact your vet. This is general guidance only. Always consult a licensed veterinarian for medical decisions.
Confidence: 4/5

---

## Design Decisions

**Why RAG instead of a plain prompt?**
A plain prompt with no context produces generic answers. By retrieving relevant knowledge first, the system grounds every response in specific, curated pet care information rather than relying entirely on what the model already knows. This makes answers more consistent and easier to audit.

**Why a local knowledge base instead of live web search?**
A local knowledge base gives full control over the quality and safety of the information the AI uses. Live web search can return unreliable or harmful sources, which is a serious risk in a health-adjacent application.

**Why keyword-based retrieval instead of embeddings?**
For a knowledge base of five small files, keyword matching is fast, transparent, and requires no additional dependencies. Embedding-based retrieval would be the right upgrade if the knowledge base grew significantly.

---

## Testing Summary

The original test suite covers 25 unit tests across sorting, recurrence, conflict detection, and filtering. All 25 pass.

For the AI layer, the evaluation script (`eval.py`) ran 6 fixed questions through the RAG advisor and logged results to `eval_results.json`. Results: 6/6 tests passed. Confidence scores averaged 4.8/5. The lowest score (4/5) was on the vomiting symptom question, which is expected since symptom-based questions involve more uncertainty than nutrition or scheduling questions. The disclaimer appeared in all 6 responses.

---

## Reflection

This project taught me that building a reliable AI system is not just about getting a response, it is about making sure the response is grounded, testable, and honest about its limits. Adding retrieval changed how the AI behaved in a measurable way. The confidence scoring and evaluation script made it possible to actually verify that, rather than just assume it worked.

---

## Project Structure
- app.py                  # Streamlit UI
- pawpal_system.py        # Core backend logic
- rag_advisor.py          # RAG retrieval and Gemini integration
- eval.py                 # Evaluation script
- eval_results.json       # Logged evaluation - results
- knowledge_base/
- dog_nutrition.txt
- cat_nutrition.txt
- vet_visits.txt
- exercise_needs.txt
- common_symptoms.txt
- tests/
- test_pawpal.py        # 25 automated unit    tests
- assets/
- architecture.png      # System architecture diagram
- model_card.md           # Reflection and ethics