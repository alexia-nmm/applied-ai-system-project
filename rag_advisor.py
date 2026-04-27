"""
rag_advisor.py
PawPal+ RAG Advisor — retrieves relevant knowledge and generates AI-powered pet care advice.
"""

import os
import google.generativeai as genai

KNOWLEDGE_BASE_DIR = "knowledge_base"

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")


def load_knowledge_base() -> dict[str, str]:
    """Load all .txt files from the knowledge base directory."""
    knowledge = {}
    for filename in os.listdir(KNOWLEDGE_BASE_DIR):
        if filename.endswith(".txt"):
            filepath = os.path.join(KNOWLEDGE_BASE_DIR, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                knowledge[filename] = f.read()
    return knowledge


def retrieve_relevant_chunks(question: str, knowledge: dict[str, str]) -> str:
    """Return the most relevant knowledge base content by keyword matching."""
    question_lower = question.lower()

    keywords = {
        "dog_nutrition.txt":   ["eat", "food", "feed", "nutrition", "diet", "toxic", "grape", "chocolate", "water"],
        "cat_nutrition.txt":   ["cat", "feline", "eat", "food", "feed", "nutrition", "diet", "taurine", "wet food"],
        "vet_visits.txt":      ["vet", "vaccine", "visit", "checkup", "dental", "senior", "appointment", "shot"],
        "exercise_needs.txt":  ["exercise", "walk", "play", "energy", "active", "run", "activity"],
        "common_symptoms.txt": ["vomit", "diarrhea", "letharg", "sick", "symptom", "limp", "cough", "thirst", "litter"],
    }

    matched_chunks = []
    for filename, words in keywords.items():
        if any(word in question_lower for word in words):
            if filename in knowledge:
                matched_chunks.append(knowledge[filename])

    if not matched_chunks:
        matched_chunks = list(knowledge.values())

    return "\n\n".join(matched_chunks)


def ask_pawpal(question: str, pet_name: str, species: str, breed: str, age: int, weight: float) -> dict:
    """
    Retrieve relevant knowledge and generate a personalized AI response.
    Returns a dict with 'answer' and 'confidence' keys.
    """
    knowledge = load_knowledge_base()
    context = retrieve_relevant_chunks(question, knowledge)

    pet_profile = (
        f"Pet name: {pet_name}\n"
        f"Species: {species}\n"
        f"Breed: {breed}\n"
        f"Age: {age} years\n"
        f"Weight: {weight} kg"
    )

    prompt = f"""You are PawPal, a knowledgeable and responsible pet care assistant.
Use the retrieved knowledge below to answer the owner's question about their pet.
Always personalize your answer using the pet's profile.
End every response with this disclaimer: "This is general guidance only. Always consult a licensed veterinarian for medical decisions."
After your answer, on a new line write: Confidence: X/5 where X is how confident you are based on the retrieved knowledge.

Pet Profile:
{pet_profile}

Retrieved Knowledge:
{context}

Owner's Question:
{question}"""

    response = model.generate_content(prompt)
    full_response = response.text

    if "Confidence:" in full_response:
        parts = full_response.rsplit("Confidence:", 1)
        answer = parts[0].strip()
        confidence = "Confidence: " + parts[1].strip()
    else:
        answer = full_response.strip()
        confidence = "Confidence: N/A"

    return {"answer": answer, "confidence": confidence}