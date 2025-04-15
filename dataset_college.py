import random
import json

def generate_admission_dataset(num_students=10, num_colleges=5, seed=42):
    random.seed(seed)  # For reproducibility
    
    # Students: a1, a2, ..., aN
    students = [f"a{i+1}" for i in range(num_students)]
    
    # Colleges: C1, C2, ..., CM
    colleges = [f"C{i+1}" for i in range(num_colleges)]
    
    # Score components: Math, Language, Grades
    score_components = ["Math", "Language", "Grades"]
    
    # Generate raw scores for each student (50-100 per component)
    raw_scores = {}
    for s in students:
        raw_scores[s] = {comp: random.randint(50, 100) for comp in score_components}
    
    # College weights and capacities
    capacities = {}
    college_weights = {}
    for c in colleges:
        # Random weights summing to 1
        w1 = random.uniform(0.2, 0.5)
        w2 = random.uniform(0.2, 0.5)
        w3 = 1.0 - w1 - w2
        if w3 < 0.2:
            w3 = 0.2
            w1 = w1 * 0.8 / (w1 + w2)
            w2 = w2 * 0.8 / (w1 + w2)
        college_weights[c] = {
            "Math": round(w1, 2),
            "Language": round(w2, 2),
            "Grades": round(w3, 2)
        }
        
        # Capacities
        regular_quota = random.randint(50, 100)  # ~1000 students / 15 colleges
        reserved_quota = random.randint(0, 10)   # Fewer reserved seats
        eligibility_score = random.randint(60, 80)
        capacities[c] = {
            "regular_quota": regular_quota,
            "reserved_quota": reserved_quota,
            "eligibility_score": eligibility_score
        }
    
    # Compute weighted scores
    student_scores = {}
    for s in students:
        scores = {}
        for c in colleges:
            score = sum(
                college_weights[c][comp] * raw_scores[s][comp]
                for comp in score_components
            )
            # Round to nearest integer for ties
            scores[c] = round(score)
        student_scores[s] = scores
    
    # Student preferences: strict total order
    student_preferences = {}
    for s in students:
        # Shuffle colleges for a random permutation
        pref = colleges.copy()
        random.shuffle(pref)
        student_preferences[s] = pref
    
    # BEA eligibility: ~30% of students
    bea_eligible = random.sample(students, k=max(1, num_students // 3))
    
    # Dataset
    dataset = {
        "students": students,
        "colleges": colleges,
        "capacities": capacities,
        "score_components": score_components,
        "college_weights": college_weights,
        "raw_scores": raw_scores,
        "student_scores": student_scores,
        "student_preferences": student_preferences,
        "bea_eligible": bea_eligible
    }
    
    return dataset

# Generate and save dataset
if __name__ == "__main__":
    dataset = generate_admission_dataset()
    with open("admission_dataset.json", "w") as f:
        json.dump(dataset, f, indent=2)
    print("Dataset saved as admission_dataset.json")