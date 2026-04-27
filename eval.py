"""
eval.py
PawPal+ Evaluation Script — tests AI reliability across fixed questions and logs results.
"""

import os
import json
from datetime import datetime
from rag_advisor import ask_pawpal

# Fixed test cases: (question, pet_name, species, breed, age, weight)
TEST_CASES = [
    ("Can my dog eat grapes?",                          "Buddy", "dog", "Golden Retriever", 3, 30.5),
    ("How often should my cat visit the vet?",          "Luna",  "cat", "Siamese",          5,  4.2),
    ("How much exercise does my dog need daily?",       "Buddy", "dog", "Golden Retriever", 3, 30.5),
    ("My cat has been vomiting twice today, is that ok?","Luna", "cat", "Siamese",          5,  4.2),
    ("What should I feed my dog?",                      "Buddy", "dog", "Golden Retriever", 3, 30.5),
    ("My dog is limping, what should I do?",            "Buddy", "dog", "Golden Retriever", 3, 30.5),
]

def run_evaluation():
    results = []
    passed = 0

    print("Running PawPal AI Evaluation...\n")
    print("=" * 60)

    for i, (question, pet_name, species, breed, age, weight) in enumerate(TEST_CASES, 1):
        print(f"Test {i}: {question}")

        result = ask_pawpal(
            question=question,
            pet_name=pet_name,
            species=species,
            breed=breed,
            age=age,
            weight=weight,
        )

        answer = result["answer"]
        confidence = result["confidence"]

        # Basic pass check: answer is non-empty and contains the disclaimer
        passed_check = (
            len(answer) > 50 and
            "consult a licensed veterinarian" in answer.lower()
        )

        status = "PASS" if passed_check else "FAIL"
        if passed_check:
            passed += 1

        print(f"Status:     {status}")
        print(f"Confidence: {confidence}")
        print(f"Answer preview: {answer[:120]}...")
        print("-" * 60)

        results.append({
            "test": i,
            "question": question,
            "pet": pet_name,
            "status": status,
            "confidence": confidence,
            "answer_preview": answer[:120],
        })

    print(f"\nResults: {passed}/{len(TEST_CASES)} tests passed")
    print(f"Average confidence scores logged to eval_results.json")

    # Save full results to file
    log = {
        "run_at": datetime.now().isoformat(),
        "passed": passed,
        "total": len(TEST_CASES),
        "results": results,
    }

    with open("eval_results.json", "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)

    print("Evaluation complete.")

if __name__ == "__main__":
    run_evaluation()