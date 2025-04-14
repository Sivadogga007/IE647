# analyze_results.py
import json

def load_dataset(input_file="college_student_dataset.json"):
    with open(input_file, "r") as f:
        dataset = json.load(f)
    return dataset

def load_solution(input_file):
    with open(input_file, "r") as f:
        solution = json.load(f)
    return solution

def satisfaction_score(solution, dataset):
    """
    Compute the raw total satisfaction score.
    Uses exponential scoring:
      - Student: rank 0 -> 100, rank 1 -> 50, rank 2 -> 25, etc.
      - College: similarly for each admitted student.
    """
    # Scoring functions (0-indexed rank: 0 => 100, 1 => 50, ...)
    student_points = lambda r: 100 / (2 ** r)
    college_points = lambda r: 100 / (2 ** r)
    
    total_score = 0

    # Calculate student satisfaction.
    for student, assigned_college in solution.items():
        rank = dataset["student_preferences"][student].index(assigned_college)
        total_score += student_points(rank)

    # Calculate college satisfaction.
    for college in dataset["colleges"]:
        assigned_students = [s for s, c in solution.items() if c == college]
        for student in assigned_students:
            rank = dataset["college_preferences"][college].index(student)
            total_score += college_points(rank)
            
    return total_score

def normalized_satisfaction_score(solution, dataset):
    """
    Normalize the raw satisfaction score to a 0-100 scale.
    
    For each student and each college, the maximum points is 100.
    Since every student is assigned and each assignment contributes:
      - 100 max from the student side and
      - 100 max from the college side,
    the maximum total raw score is 200 * (number of students).
    """
    raw = satisfaction_score(solution, dataset)
    num_students = len(dataset["students"])
    max_possible = 200 * num_students  # Maximum total score if every assignment was perfect.
    normalized = (raw / max_possible) * 100
    return normalized

if __name__ == "__main__":
    # Load the dataset and matching results.
    dataset = load_dataset("college_student_dataset.json")
    greedy_sol = load_solution("result_greedy.json")
    sa_sol = load_solution("result_sa.json")
    ts_sol = load_solution("result_ts.json")
    
    # Compute normalized satisfaction scores.
    greedy_norm = normalized_satisfaction_score(greedy_sol, dataset)
    sa_norm = normalized_satisfaction_score(sa_sol, dataset)
    ts_norm = normalized_satisfaction_score(ts_sol, dataset)
    
    # Print a comparative summary.
    print("--- Normalized Satisfaction Scores (out of 100) ---")
    print(f"Greedy Matching Score: {greedy_norm:.2f}")
    print(f"Simulated Annealing Matching Score: {sa_norm:.2f}")
    print(f"Tabu Search Matching Score: {ts_norm:.2f}")
