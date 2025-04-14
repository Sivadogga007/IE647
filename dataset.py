# dataset_generator.py
import json
import random

def generate_dataset(num_students=10, num_colleges=3, output_file="college_student_dataset.json"):
    random.seed(42)  # For reproducibility

    # Generate student and college IDs
    students = [f"S{i+1}" for i in range(num_students)]
    colleges = [f"C{i+1}" for i in range(num_colleges)]

    # Generate random capacities for colleges (each between 2 and 5)
    capacities = {c: random.randint(2, 5) for c in colleges}
    total_capacity = sum(capacities.values())
    # Ensure total capacity is at least equal to the number of students.
    if total_capacity < num_students:
        capacities[colleges[0]] += (num_students - total_capacity)

    # Generate student preferences: each student gets a random ordering of all colleges.
    student_prefs = {}
    for s in students:
        prefs = colleges.copy()
        random.shuffle(prefs)
        student_prefs[s] = prefs

    # Generate college preferences: each college gets a random ordering of all students.
    college_prefs = {}
    for c in colleges:
        prefs = students.copy()
        random.shuffle(prefs)
        college_prefs[c] = prefs

    # Bundle the dataset in a dictionary.
    dataset = {
        "students": students,
        "colleges": colleges,
        "capacities": capacities,
        "student_preferences": student_prefs,
        "college_preferences": college_prefs
    }

    # Save the dataset to a JSON file.
    with open(output_file, "w") as f:
        json.dump(dataset, f, indent=4)
    print("Dataset generated and saved to", output_file)

if __name__ == "__main__":
    generate_dataset(100,7)
