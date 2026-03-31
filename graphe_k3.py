import tkinter as tk


# ============================================
# Validation de l'algorithme de Welsh-Powell
# Cas de test : graphe complet K4
# ============================================

# Graphe complet K4 : chaque sommet est voisin de tous les autres
RAW_GRAPH = {
    "A": ["B", "C", "D"],
    "B": ["A", "C", "D"],
    "C": ["A", "B", "D"],
    "D": ["A", "B", "C"],
}

# Positions fixes des sommets sur le canevas
POSITIONS = {
    "A": (220, 70),
    "B": (90, 200),
    "C": (350, 200),
    "D": (220, 330),
}

# Palette de couleurs
COLOR_PALETTE = ["#ef476f", "#118ab2", "#06d6a0", "#ffd166", "#8338ec"]


def normalize_graph(raw_graph):
    graph = {node: set(neighbors) for node, neighbors in raw_graph.items()}

    # Assure la symetrie des aretes
    for node in list(graph):
        graph.setdefault(node, set())
        graph[node].discard(node)
        for neighbor in list(graph[node]):
            graph.setdefault(neighbor, set()).add(node)

    return {node: sorted(neighbors) for node, neighbors in graph.items()}


def sort_nodes(graph):
    # Tri par degre decroissant, puis ordre alphabetique
    return sorted(graph, key=lambda node: (-len(graph[node]), node))


def welsh_powell(graph):
    sorted_nodes = sort_nodes(graph)
    color_map = {}
    current_color = 0

    for node in sorted_nodes:
        if node in color_map:
            continue

        color_map[node] = current_color

        for other in sorted_nodes:
            if other in color_map:
                continue

            has_conflict = any(
                color_map.get(neighbor) == current_color
                for neighbor in graph[other]
            )

            if not has_conflict:
                color_map[other] = current_color

        current_color += 1

    return color_map


def validate_coloring(graph, color_map):
    for node, neighbors in graph.items():
        for neighbor in neighbors:
            if node < neighbor and color_map[node] == color_map[neighbor]:
                return False
    return True


def draw_graph(canvas, graph, color_map):
    canvas.delete("all")

    # Dessin des aretes
    drawn_edges = set()
    for node, neighbors in graph.items():
        for neighbor in neighbors:
            edge = tuple(sorted((node, neighbor)))
            if edge in drawn_edges:
                continue
            drawn_edges.add(edge)

            x1, y1 = POSITIONS[node]
            x2, y2 = POSITIONS[neighbor]
            canvas.create_line(x1, y1, x2, y2, fill="#64748b", width=2)

    # Dessin des sommets
    radius = 28
    for node, (x, y) in POSITIONS.items():
        color_index = color_map[node]
        fill_color = COLOR_PALETTE[color_index % len(COLOR_PALETTE)]

        canvas.create_oval(
            x - radius, y - radius,
            x + radius, y + radius,
            fill=fill_color,
            outline="black",
            width=2
        )

        canvas.create_text(
            x, y,
            text=node,
            font=("Arial", 14, "bold"),
            fill="white"
        )

        canvas.create_text(
            x, y + 45,
            text=f"Couleur {color_index + 1}",
            font=("Arial", 10, "bold"),
            fill="#0f172a"
        )


def main():
    graph = normalize_graph(RAW_GRAPH)
    color_map = welsh_powell(graph)
    is_valid = validate_coloring(graph, color_map)
    nb_colors = len(set(color_map.values()))

    root = tk.Tk()
    root.title("Validation Welsh-Powell - Graphe complet K4")
    root.geometry("520x500")
    root.configure(bg="white")

    title = tk.Label(
        root,
        text="Validation de l'algorithme de Welsh-Powell",
        font=("Arial", 15, "bold"),
        bg="white",
        fg="#111827"
    )
    title.pack(pady=(12, 4))

    subtitle = tk.Label(
        root,
        text="Cas de test : graphe complet K4",
        font=("Arial", 11),
        bg="white",
        fg="#374151"
    )
    subtitle.pack()

    canvas = tk.Canvas(root, width=440, height=360, bg="#f8fafc", highlightthickness=1)
    canvas.pack(pady=12)

    draw_graph(canvas, graph, color_map)

    result_text = (
        f"Nombre de sommets : {len(graph)}\n"
        f"Nombre de couleurs obtenues : {nb_colors}\n"
        f"Coloration valide : {'Oui' if is_valid else 'Non'}"
    )

    result_label = tk.Label(
        root,
        text=result_text,
        font=("Arial", 11),
        bg="white",
        fg="#1f2937",
        justify="left"
    )
    result_label.pack(pady=(4, 10))

    root.mainloop()


if __name__ == "__main__":
    main()