# Model Card — PawPal+ AI Advisor

**Author:** Alexia Martinez
**Base Model:** Gemini 2.5 Flash (Google)
**Application:** RAG-powered pet care advisor integrated into a Streamlit scheduling app

---

## What the Model Does

The AI advisor takes a natural language question from a pet owner, retrieves relevant content from a local knowledge base, and generates a personalized response using the pet's profile (name, species, breed, age, weight). Every response includes a disclaimer directing users to consult a licensed veterinarian and a confidence score from 1 to 5.

---

## Limitations and Biases

The knowledge base is small and manually written. It covers five topics and does not represent the full range of pet care situations an owner might face. The system currently only handles dogs and cats well — exotic pets like birds or reptiles would receive generic or potentially inaccurate answers. The keyword retrieval method may miss relevant content if the owner phrases their question in an unexpected way. The AI may also present uncertain information with more confidence than is warranted.

---

## Potential Misuse and Prevention

The most significant risk is an owner over-relying on the AI instead of seeking real veterinary care, particularly in an emergency. To reduce this risk, every single response the system generates ends with the disclaimer: "This is general guidance only. Always consult a licensed veterinarian for medical decisions." This is enforced at the prompt level and verified in the evaluation script.

---

## Testing Surprises

The evaluation results were stronger than expected — 6/6 tests passed on the first run with an average confidence score of 4.8/5. The most interesting result was the vomiting question, which received a 4/5 confidence score. This was appropriate because symptom questions involve more uncertainty than factual questions about nutrition or scheduling. It showed that the model was calibrating its confidence reasonably rather than always returning 5/5.

---

## AI Collaboration

**Helpful suggestion:** During this project, the AI was helpful when generating the evaluation test cases and the knowledge base content. Having structured, relevant test questions and well-organized knowledge files saved significant time and made the retrieval layer more reliable from the start.

**Flawed suggestion:** The AI gave incorrect guidance when it came to setting up the API keys. It initially directed me toward a model name and setup process that did not work, which caused errors that required troubleshooting and switching to a different model version. This was a reminder that AI suggestions about external tools and APIs need to be verified independently.