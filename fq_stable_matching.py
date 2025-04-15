import networkx as nx
import matplotlib.pyplot as plt
import json

# Load dataset
with open("admission_dataset.json", "r") as f:
    data = json.load(f)

def derive_college_preferences(data, colleges):
    college_prefs = {}
    for c in colleges:
        students_scores = [(s, data["student_scores"][s].get(c, 0)) for s in data["students"]]
        students_scores.sort(key=lambda x: x[1], reverse=True)
        score_groups = {}
        for s, score in students_scores:
            if score >= data["capacities"][c]["eligibility_score"]:
                if score not in score_groups:
                    score_groups[score] = []
                score_groups[score].append(s)
        pref_list = []
        for score in sorted(score_groups.keys(), reverse=True):
            pref_list.extend(score_groups[score])
        college_prefs[c] = pref_list
    return college_prefs

def create_regular_admission_graph(data):
    G = nx.DiGraph()
    colleges = data["colleges"]
    college_prefs = derive_college_preferences(data, colleges)

    # Nodes: (c, s) for regular seats
    nodes = []
    for s in data["students"]:
        for c in data["student_preferences"][s]:
            if (c in colleges and
                data["student_scores"][s][c] >= data["capacities"][c]["eligibility_score"]):
                nodes.append((c, s))
    G.add_nodes_from(nodes)

    # Edges
    edges = []
    # Student preferences (vertical)
    for s in data["students"]:
        pref_list = [c for c in data["student_preferences"][s] if c in colleges]
        for i in range(len(pref_list) - 1):
            c_higher = pref_list[i]
            c_lower = pref_list[i + 1]
            if ((c_higher, s) in nodes and (c_lower, s) in nodes):
                edges.append(((c_lower, s), (c_higher, s)))
    # College preferences (horizontal)
    for c in colleges:
        pref_list = college_prefs[c]
        score_map = {s: data["student_scores"][s][c] for s in pref_list}
        for i in range(len(pref_list)):
            s_i = pref_list[i]
            for j in range(len(pref_list)):
                s_j = pref_list[j]
                if i != j and (c, s_i) in nodes and (c, s_j) in nodes:
                    if score_map[s_j] >= score_map[s_i]:
                        edges.append(((c, s_i), (c, s_j)))
    G.add_edges_from(edges)
    return G, colleges

def create_bea_admission_graph(data):
    G = nx.DiGraph()
    colleges = [c for c in data["colleges"] if data["capacities"][c]["reserved_quota"] > 0]
    college_prefs = derive_college_preferences(data, colleges)

    # Nodes: (c, s) for reserved seats, BEA-eligible students
    nodes = []
    for s in data["bea_eligible"]:
        for c in data["student_preferences"][s]:
            if (c in colleges and
                data["student_scores"][s][c] >= data["capacities"][c]["eligibility_score"]):
                nodes.append((c, s))
    G.add_nodes_from(nodes)

    # Edges
    edges = []
    # Student preferences
    for s in data["bea_eligible"]:
        pref_list = [c for c in data["student_preferences"][s] if c in colleges]
        for i in range(len(pref_list) - 1):
            c_higher = pref_list[i]
            c_lower = pref_list[i + 1]
            if ((c_higher, s) in nodes and (c_lower, s) in nodes):
                edges.append(((c_lower, s), (c_higher, s)))
    # College preferences
    for c in colleges:
        pref_list = [s for s in college_prefs[c] if s in data["bea_eligible"]]
        score_map = {s: data["student_scores"][s][c] for s in pref_list}
        for i in range(len(pref_list)):
            s_i = pref_list[i]
            for j in range(len(pref_list)):
                s_j = pref_list[j]
                if i != j and (c, s_i) in nodes and (c, s_j) in nodes:
                    if score_map[s_j] >= score_map[s_i]:
                        edges.append(((c, s_i), (c, s_j)))
    G.add_edges_from(edges)
    return G, colleges

def create_unified_admission_graph(data):
    G = nx.DiGraph()
    programs = []
    program_eligibility = {}
    program_to_college = {}
    for c in data["colleges"]:
        programs.append(f"{c}_reg")
        program_eligibility[f"{c}_reg"] = data["capacities"][c]["eligibility_score"]
        program_to_college[f"{c}_reg"] = c
        if data["capacities"][c]["reserved_quota"] > 0:
            programs.append(f"{c}_res")
            program_eligibility[f"{c}_res"] = data["capacities"][c]["eligibility_score"]
            program_to_college[f"{c}_res"] = c
    
    # Derive preferences for programs
    program_prefs = {}
    for c in data["colleges"]:
        students_scores = [(s, data["student_scores"][s].get(c, 0)) for s in data["students"]]
        students_scores.sort(key=lambda x: x[1], reverse=True)
        score_groups = {}
        for s, score in students_scores:
            if score >= data["capacities"][c]["eligibility_score"]:
                if score not in score_groups:
                    score_groups[score] = []
                score_groups[score].append(s)
        pref_list = []
        for score in sorted(score_groups.keys(), reverse=True):
            pref_list.extend(score_groups[score])
        program_prefs[f"{c}_reg"] = pref_list
        if f"{c}_res" in programs:
            bea_pref_list = [s for s in pref_list if s in data["bea_eligible"]]
            program_prefs[f"{c}_res"] = bea_pref_list

    # Nodes: (p, s)
    nodes = []
    for s in data["students"]:
        for p in [p for p in programs if "_reg" in p]:
            c = program_to_college[p]
            if (c in data["student_preferences"][s] and
                data["student_scores"][s][c] >= program_eligibility[p]):
                nodes.append((p, s))
        if s in data["bea_eligible"]:
            for p in [p for p in programs if "_res" in p]:
                c = program_to_college[p]
                if (c in data["student_preferences"][s] and
                    data["student_scores"][s][c] >= program_eligibility[p]):
                    nodes.append((p, s))
    G.add_nodes_from(nodes)

    # Edges
    edges = []
    # Student preferences
    for s in data["students"]:
        pref_list = []
        for c in data["student_preferences"][s]:
            if f"{c}_reg" in programs:
                pref_list.append(f"{c}_reg")
            if s in data["bea_eligible"] and f"{c}_res" in programs:
                pref_list.append(f"{c}_res")
        for i in range(len(pref_list) - 1):
            p_higher = pref_list[i]
            p_lower = pref_list[i + 1]
            if ((p_higher, s) in nodes and (p_lower, s) in nodes):
                edges.append(((p_lower, s), (p_higher, s)))
    # Program preferences
    for p in programs:
        pref_list = program_prefs[p]
        c = program_to_college[p]
        score_map = {s: data["student_scores"][s][c] for s in pref_list}
        for i in range(len(pref_list)):
            s_i = pref_list[i]
            for j in range(len(pref_list)):
                s_j = pref_list[j]
                if i != j and (p, s_i) in nodes and (p, s_j) in nodes:
                    if score_map[s_j] >= score_map[s_i]:
                        edges.append(((p, s_i), (p, s_j)))
    G.add_edges_from(edges)
    return G, programs

def visualize_and_save_graph(G, colleges_or_programs, filename, title):
    plt.figure(figsize=(30, 12))  # Large figure for 1000 students
    # Grid layout: students on x-axis (top), colleges/programs on y-axis (left)
    pos = {}
    for (p, s) in G.nodes():
        x = data["students"].index(s)
        y = -colleges_or_programs.index(p)  # Negative to have C1 at top
        pos[(p, s)] = (x, y)
    
    # Draw graph
    nx.draw(G, pos, with_labels=False, node_size=50, node_color='lightblue',
            font_size=6, font_weight='bold', arrowsize=8)
    
    # Customize axes
    plt.xticks(range(0, len(data["students"]), 50), 
              [data["students"][i] for i in range(0, len(data["students"]), 50)], 
              fontsize=8, rotation=45)
    plt.yticks([-i for i in range(len(colleges_or_programs))], 
              colleges_or_programs, fontsize=8)
    plt.xlabel("Students (a)", fontsize=10)
    plt.ylabel("Colleges/Programs (c)", fontsize=10)
    plt.title(title, fontsize=12)
    
    # Save image
    plt.savefig(filename, format='png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved graph as {filename}")

# Generate and save graphs
G_regular, colleges = create_regular_admission_graph(data)
visualize_and_save_graph(G_regular, colleges, "regular_admission_graph.png", "Regular Admission Graph (Gr)")

G_bea, bea_colleges = create_bea_admission_graph(data)
visualize_and_save_graph(G_bea, bea_colleges, "bea_admission_graph.png", "BEA Admission Graph (Gr)")

G_unified, programs = create_unified_admission_graph(data)
visualize_and_save_graph(G_unified, programs, "unified_admission_graph.png", "Unified Admission Graph")