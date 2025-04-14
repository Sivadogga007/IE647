# solve_methods.py
import json
import random
import math

def load_dataset(input_file="college_student_dataset.json"):
    with open(input_file, "r") as f:
        dataset = json.load(f)
    return dataset

def greedy_matching(dataset):
    # Use a copy of the capacities so the original dataset remains unchanged.
    capacities = dataset["capacities"].copy()
    assignment = {}  # Mapping: student -> college

    for student in dataset["students"]:
        # Choose the highest-ranked college (by student's preference) with available capacity.
        for college in dataset["student_preferences"][student]:
            if capacities[college] > 0:
                assignment[student] = college
                capacities[college] -= 1
                break
    return assignment

def objective(solution, dataset):
    # A simple internal objective: the sum of the index (0-indexed dissatisfaction) over student preferences.
    total = 0
    for student, college in solution.items():
        rank = dataset["student_preferences"][student].index(college)
        total += rank
    return total

def get_neighbor(solution):
    new_solution = solution.copy()
    s1, s2 = random.sample(list(new_solution.keys()), 2)
    new_solution[s1], new_solution[s2] = new_solution[s2], new_solution[s1]
    return new_solution

def get_neighbor_with_move(solution):
    new_solution = solution.copy()
    s1, s2 = random.sample(list(new_solution.keys()), 2)
    new_solution[s1], new_solution[s2] = new_solution[s2], new_solution[s1]
    move = (s1, s2)
    return new_solution, move

def simulated_annealing(dataset, initial_solution, iterations=1000, initial_temp=100, cooling_rate=0.95):
    current_solution = initial_solution
    current_cost = objective(current_solution, dataset)
    temperature = initial_temp
    best_solution = current_solution
    best_cost = current_cost

    for i in range(iterations):
        neighbor = get_neighbor(current_solution)
        neighbor_cost = objective(neighbor, dataset)
        delta = neighbor_cost - current_cost
        # Accept if improving or with some probability to escape local optima.
        if delta < 0 or random.random() < math.exp(-delta / temperature):
            current_solution = neighbor
            current_cost = neighbor_cost
        if current_cost < best_cost:
            best_solution = current_solution
            best_cost = current_cost
        temperature *= cooling_rate
    return best_solution

def tabu_search(dataset, initial_solution, iterations=100, tabu_list_max_size=10):
    current_solution = initial_solution
    current_cost = objective(current_solution, dataset)
    best_solution = current_solution
    best_cost = current_cost
    tabu_list = []

    for i in range(iterations):
        neighbor, move = get_neighbor_with_move(current_solution)
        if move in tabu_list:
            continue
        neighbor_cost = objective(neighbor, dataset)
        if neighbor_cost < current_cost:
            current_solution = neighbor
            current_cost = neighbor_cost
            if current_cost < best_cost:
                best_solution = current_solution
                best_cost = current_cost
        tabu_list.append(move)
        if len(tabu_list) > tabu_list_max_size:
            tabu_list.pop(0)
    return best_solution

def save_solution(solution, output_file):
    with open(output_file, "w") as f:
        json.dump(solution, f, indent=4)
    print("Solution saved to", output_file)

if __name__ == "__main__":
    random.seed(42)  # For reproducibility
    dataset = load_dataset("college_student_dataset.json")
    
    # Greedy Matching
    greedy_sol = greedy_matching(dataset)
    save_solution(greedy_sol, "result_greedy.json")

    # Simulated Annealing Matching (starting from the Greedy solution)
    sa_sol = simulated_annealing(dataset, greedy_sol, iterations=1000, initial_temp=100, cooling_rate=0.95)
    save_solution(sa_sol, "result_sa.json")

    # Tabu Search Matching (starting from the Greedy solution)
    ts_sol = tabu_search(dataset, greedy_sol, iterations=100, tabu_list_max_size=10)
    save_solution(ts_sol, "result_ts.json")
