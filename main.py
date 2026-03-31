import tkinter as tk
from tkinter import PhotoImage


# ============================================================
# Sujet : Coloration automatique de la carte de la RDC
# Methode : algorithme de Welsh-Powell
# Bibliotheques utilisees : tkinter uniquement (bibliotheque standard)
# ============================================================


# Graphe d'entree : chaque cle represente une province et la liste associee
# contient les provinces voisines. Cette structure sera nettoyee ensuite pour
# obtenir un graphe non oriente sans doublons.
RAW_GRAPH = {
    "Kinshasa": ["Kongo Central"],

    "Kongo Central": ["Kinshasa", "Kwango", "Kwilu"],

    "Kwango": ["Kongo Central", "Kwilu", "Mai-Ndombe"],

    "Kwilu": ["Kongo Central", "Kwango", "Mai-Ndombe", "Kasai"],

    "Mai-Ndombe": ["Kwango", "Kwilu", "Kasai", "Sankuru", "Tshuapa", "Equateur"],

    "Equateur": ["Mai-Ndombe", "Tshuapa", "Mongala", "Nord-Ubangi", "Sud-Ubangi"],

    "Mongala": ["Equateur", "Nord-Ubangi", "Tshopo"],

    "Nord-Ubangi": ["Equateur", "Mongala", "Sud-Ubangi", "Bas-Uele"],

    "Sud-Ubangi": ["Equateur", "Nord-Ubangi"],

    "Tshuapa": ["Equateur", "Mai-Ndombe", "Sankuru", "Tshopo"],

    "Tshopo": ["Tshuapa", "Mongala", "Bas-Uele", "Haut-Uele", "Ituri", "Maniema", "Sankuru"],

    "Bas-Uele": ["Nord-Ubangi", "Tshopo", "Haut-Uele"],

    "Haut-Uele": ["Bas-Uele", "Tshopo", "Ituri"],

    "Ituri": ["Haut-Uele", "Tshopo", "Nord-Kivu"],

    "Nord-Kivu": ["Ituri", "Maniema", "Sud-Kivu"],

    "Sud-Kivu": ["Nord-Kivu", "Maniema", "Tanganyika"],

    "Maniema": ["Tshopo", "Nord-Kivu", "Sud-Kivu", "Tanganyika", "Sankuru", "Lomami"],

    "Tanganyika": ["Sud-Kivu", "Maniema", "Haut-Lomami", "Lualaba", "Haut-Katanga"],

    "Haut-Lomami": ["Tanganyika", "Lualaba", "Haut-Katanga", "Lomami"],

    "Lualaba": ["Tanganyika", "Haut-Lomami", "Haut-Katanga", "Kasai-Central"],

    "Haut-Katanga": ["Tanganyika", "Haut-Lomami", "Lualaba"],

    "Sankuru": ["Mai-Ndombe", "Tshuapa", "Tshopo", "Maniema", "Lomami", "Kasai-Oriental", "Kasai-Central"],

    "Lomami": ["Sankuru", "Maniema", "Haut-Lomami", "Kasai-Oriental", "Kasai-Central"],

    "Kasai": ["Kwilu", "Mai-Ndombe", "Kasai-Central"],

    "Kasai-Central": ["Kasai", "Sankuru", "Lomami", "Kasai-Oriental", "Lualaba"],

    "Kasai-Oriental": ["Kasai-Central", "Sankuru", "Lomami"]
}



# Coordonnees d'affichage des sommets sur le canevas Tkinter.
# Chaque province est associee a une position (x, y) calibree sur
# l'ancienne image de reference (612 x 612 pixels), centree dans un
# canevas 770 x 620. Ces coordonnees seront redimensionnees ensuite
# pour suivre automatiquement la nouvelle carte.
POSITIONS = {
    "Kinshasa": (140, 385),
    "Kongo Central": (110, 430),
    "Kwango": (205, 430),
    "Kwilu": (250, 370),
    "Mai-Ndombe": (245, 285),
    "Equateur": (300, 185),
    "Mongala": (365, 115),
    "Nord-Ubangi": (280, 80),
    "Sud-Ubangi": (215, 130),
    "Tshuapa": (370, 220),
    "Tshopo": (505, 210),
    "Bas-Uele": (515, 80),
    "Haut-Uele": (585, 105),
    "Ituri": (655, 140),
    "Nord-Kivu": (670, 220),
    "Sud-Kivu": (675, 295),
    "Maniema": (565, 305),
    "Tanganyika": (590, 410),
    "Haut-Lomami": (495, 470),
    "Lualaba": (420, 455),
    "Haut-Katanga": (560, 540),
    "Sankuru": (380, 350),
    "Lomami": (425, 410),
    "Kasai": (270, 455),
    "Kasai-Central": (335, 445),
    "Kasai-Oriental": (385, 470),
}


# Parametres de reference utilises pour redimensionner les sommets
# lorsque l'image de fond change de taille.
REFERENCE_IMAGE_SIZE = 612
REFERENCE_IMAGE_LEFT = 79
REFERENCE_IMAGE_TOP = 4
CANVAS_WIDTH = 620
CANVAS_HEIGHT = 620

# Avec tkinter standard, la reduction d'une image PNG par zoom/subsample
# degrade fortement les traits fins de la carte. On privilegie donc
# un affichage a la taille native quand l'image le permet.
DISPLAY_MAX_SIZE = 720

# La nouvelle image rdc.png contient des marges blanches importantes.
# La carte utile a ete mesuree approximativement dans un cadre 1024 x 1024 :
# x = 64..894 et y = 84..934. On s'en sert pour mieux caler les sommets.
BACKGROUND_SOURCE_SIZE = 1024
BACKGROUND_CONTENT_LEFT = 64
BACKGROUND_CONTENT_TOP = 84
BACKGROUND_CONTENT_WIDTH = 831
BACKGROUND_CONTENT_HEIGHT = 851


# Palette de couleurs utilisee pour colorier les sommets du graphe.
# Elle est suffisamment large pour le resultat produit par l'heuristique.
COLOR_PALETTE = [
    "#ef476f",
    "#118ab2",
    "#06d6a0",
    "#ffd166",
    "#8338ec",
    "#fb5607",
    "#3a86ff",
    "#8ac926",
]

COLOR_NAMES = [
    "rose",
    "bleu",
    "vert",
    "jaune",
    "violet",
    "orange",
    "bleu clair",
    "vert clair",
]


def normalize_graph(raw_graph):
    graph = {node: set(neighbors) for node, neighbors in raw_graph.items()}

    # Boucle critique : on force la reciprocite des aretes.
    # Si A cite B comme voisin, alors B doit aussi citer A.
    for node in list(graph):
        graph.setdefault(node, set())
        graph[node].discard(node)
        for neighbor in list(graph[node]):
            graph.setdefault(neighbor, set()).add(node)

    return {node: sorted(neighbors) for node, neighbors in graph.items()}


def sort_nodes(graph):
    return sorted(graph, key=lambda node: (-len(graph[node]), node))


def welsh_powell(graph):
    sorted_nodes = sort_nodes(graph)
    color_map = {}
    current_color = 0

    # Boucle principale : on cree les couleurs une par une.
    for node in sorted_nodes:
        if node in color_map:
            continue

        # Le sommet courant lance une nouvelle classe de couleur.
        color_map[node] = current_color

        # Boucle critique : on tente de reutiliser la meme couleur
        # pour tous les autres sommets compatibles.
        for other in sorted_nodes:
            if other in color_map:
                continue

            has_conflict = any(
                color_map.get(neighbor) == current_color for neighbor in graph[other]
            )
            if not has_conflict:
                color_map[other] = current_color

        current_color += 1

    return color_map


def validate_coloring(graph, color_map):
    conflicts = []

    # On parcourt chaque arete une seule fois grace au test node < neighbor.
    for node, neighbors in graph.items():
        for neighbor in neighbors:
            if node < neighbor and color_map[node] == color_map[neighbor]:
                conflicts.append((node, neighbor))
    return conflicts


def resize_photo_to_max_size(image, target_max_size):
    """
    Redimensionne une PhotoImage vers une taille maximale cible.
    """
    current_max = max(image.width(), image.height())
    if current_max <= target_max_size:
        return image

    scale = target_max_size / current_max
    best_num = 1
    best_den = 1
    best_error = abs(1 - scale)

    # Recherche d'une approximation rationnelle num/den du facteur de reduction.
    # Cela permet d'utiliser exclusivement zoom/subsample de tkinter.
    for den in range(1, 33):
        num = max(1, round(scale * den))
        approx = num / den
        error = abs(approx - scale)
        if error < best_error:
            best_num = num
            best_den = den
            best_error = error

    resized = image.subsample(best_den, best_den) if best_den > 1 else image
    if best_num > 1:
        resized = resized.zoom(best_num, best_num)
    return resized


class MapColoringApp:
    """Interface graphique de visualisation de la coloration de la RDC."""

    def __init__(self, root):
        # Fenetre principale transmise par le programme principal.
        self.root = root

        # Preparation des donnees :
        # 1. nettoyage du graphe,
        # 2. calcul initial de la coloration,
        # 3. variable de stockage de l'image de fond.
        self.graph = normalize_graph(RAW_GRAPH)
        self.color_map = welsh_powell(self.graph)
        self.original_image = None
        self.image = None
        self.display_positions = dict(POSITIONS)
        self.node_radius = 24

        # Configuration generale de la fenetre.
        self.root.title("Coloration automatique de la RDC - Welsh-Powell")
        self.root.geometry("1040x820")
        self.root.minsize(920, 720)
        self.root.configure(bg="#f4f7fb")

        # Titre principal du projet.
        self.title_label = tk.Label(
            root,
            text="Coloration automatique de la carte de la RDC",
            font=("Arial", 18, "bold"),
            bg="#f4f7fb",
            fg="#1f2937",
        )
        self.title_label.pack(pady=(12, 6))

        # Sous-titre rappelant l'algorithme employe.
        self.subtitle_label = tk.Label(
            root,
            text="Algorithme de Welsh-Powell applique aux 26 provinces",
            font=("Arial", 11),
            bg="#f4f7fb",
            fg="#475569",
        )
        self.subtitle_label.pack()

        # Zone centrale contenant le dessin du graphe et le panneau lateral.
        self.main_frame = tk.Frame(root, bg="#f4f7fb")
        self.main_frame.pack(fill="both", expand=True, padx=14, pady=14)

        # Zone gauche : canevas scrollable pour parcourir la carte.
        self.canvas_frame = tk.Frame(self.main_frame, bg="#f4f7fb")
        self.canvas_frame.pack(side="left", fill="both", expand=True)

        self.canvas = tk.Canvas(
            self.canvas_frame,
            width=CANVAS_WIDTH,
            height=CANVAS_HEIGHT,
            bg="#eaf4ff",
            highlightthickness=1,
            highlightbackground="#bfd3ea",
        )
        self.canvas_scroll_y = tk.Scrollbar(
            self.canvas_frame,
            orient="vertical",
            command=self.canvas.yview,
        )
        self.canvas_scroll_x = tk.Scrollbar(
            self.canvas_frame,
            orient="horizontal",
            command=self.canvas.xview,
        )
        self.canvas.configure(
            yscrollcommand=self.canvas_scroll_y.set,
            xscrollcommand=self.canvas_scroll_x.set,
        )

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas_scroll_y.grid(row=0, column=1, sticky="ns")
        self.canvas_scroll_x.grid(row=1, column=0, sticky="ew")
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)

        # Panneau lateral : resume, statistiques et liste des provinces.
        self.sidebar = tk.Frame(self.main_frame, bg="white", bd=1, relief="solid")
        self.sidebar.pack(side="right", fill="y", padx=(14, 0))

        self.summary_label = tk.Label(
            self.sidebar,
            text="Resume",
            font=("Arial", 14, "bold"),
            bg="white",
            anchor="w",
        )
        self.summary_label.pack(fill="x", padx=14, pady=(14, 8))

        # Cette etiquette affiche les informations globales :
        # nombre de provinces, nombre de couleurs et nombre de conflits.
        self.stats_text = tk.Label(
            self.sidebar,
            justify="left",
            anchor="nw",
            bg="white",
            fg="#334155",
            font=("Arial", 10),
        )
        self.stats_text.pack(fill="x", padx=14)

        self.list_label = tk.Label(
            self.sidebar,
            text="Attribution des couleurs",
            font=("Arial", 12, "bold"),
            bg="white",
            anchor="w",
        )
        self.list_label.pack(fill="x", padx=14, pady=(18, 8))

        # Zone texte contenant la liste detaillee des couleurs attribuees.
        self.result_text = tk.Text(
            self.sidebar,
            width=28,
            height=18,
            wrap="word",
            font=("Consolas", 10),
            bg="#fcfdff",
            fg="#1e293b",
        )
        self.result_text.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        self.result_text.configure(state="disabled")

        # Barre des actions utilisateur.
        self.button_frame = tk.Frame(root, bg="#f4f7fb")
        self.button_frame.pack(pady=(0, 14))

        tk.Button(
            self.button_frame,
            text="Recalculer la coloration",
            command=self.recolor,
            bg="#22c55e",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=14,
            pady=8,
        ).pack(side="left", padx=8)

        tk.Button(
            self.button_frame,
            text="Afficher les resultats",
            command=self.show_results_window,
            bg="#2563eb",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=14,
            pady=8,
        ).pack(side="left", padx=8)

        tk.Button(
            self.button_frame,
            text="Verifier la coloration",
            command=self.show_validation,
            bg="#f59e0b",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=14,
            pady=8,
        ).pack(side="left", padx=8)

        # Premier affichage a l'ouverture de l'application.
        self.draw_graph()
        self.refresh_sidebar()

    def load_background(self):
        """Charge l'image de fond si le fichier rdc.png est disponible."""
        try:
            self.original_image = PhotoImage(file="rdc.png")
            self.image = resize_photo_to_max_size(self.original_image, DISPLAY_MAX_SIZE)

            image_width = self.image.width()
            image_height = self.image.height()
            left = 0
            top = 0

            self.canvas.create_image(
                left,
                top,
                image=self.image,
                anchor="nw",
            )

            # On projette les sommets sur la zone utile de la carte,
            # et non sur tout le cadre blanc de l'image.
            content_left = left + round(BACKGROUND_CONTENT_LEFT * image_width / BACKGROUND_SOURCE_SIZE)
            content_top = top + round(BACKGROUND_CONTENT_TOP * image_height / BACKGROUND_SOURCE_SIZE)
            content_width = round(BACKGROUND_CONTENT_WIDTH * image_width / BACKGROUND_SOURCE_SIZE)
            content_height = round(BACKGROUND_CONTENT_HEIGHT * image_height / BACKGROUND_SOURCE_SIZE)

            self.display_positions = self.scale_positions(
                content_left,
                content_top,
                content_width,
                content_height,
            )

            scale_factor = min(
                image_width / REFERENCE_IMAGE_SIZE,
                image_height / REFERENCE_IMAGE_SIZE,
            )
            self.node_radius = max(18, round(18 * scale_factor))
        except tk.TclError:
            self.display_positions = dict(POSITIONS)
            self.node_radius = 24
            self.canvas.create_text(
                20,
                30,
                text="Image 'rdc.png' introuvable : affichage du graphe sans fond de carte.",
                fill="#64748b",
                font=("Arial", 10, "italic"),
                anchor="nw",
            )

    def scale_positions(self, left, top, image_width, image_height):
        """
        Adapte les positions des sommets a la taille effectivement affichee.

        Entree :
            left, top (int) : coin superieur gauche de l'image dans le canevas.
            image_width, image_height (int) : dimensions de l'image affichee.

        Sortie :
            dict[str, tuple[int, int]] : nouvelles positions des provinces.
        """
        scaled_positions = {}
        for province, (x, y) in POSITIONS.items():
            relative_x = (x - REFERENCE_IMAGE_LEFT) / REFERENCE_IMAGE_SIZE
            relative_y = (y - REFERENCE_IMAGE_TOP) / REFERENCE_IMAGE_SIZE
            scaled_positions[province] = (
                round(left + relative_x * image_width),
                round(top + relative_y * image_height),
            )
        return scaled_positions

    def draw_graph(self):
        """
        Dessine le graphe colorie.

        Sortie :
            aucune valeur retournee ; la methode met a jour le canevas.
        """
        self.canvas.delete("all")
        self.load_background()

        drawn_edges = set()

        # Premiere passe : dessin des aretes entre provinces voisines.
        for node, neighbors in self.graph.items():
            for neighbor in neighbors:
                edge = tuple(sorted((node, neighbor)))
                if edge in drawn_edges:
                    continue
                drawn_edges.add(edge)

                x1, y1 = self.display_positions[node]
                x2, y2 = self.display_positions[neighbor]
                self.canvas.create_line(x1, y1, x2, y2, fill="#94a3b8", width=2)

        # Deuxieme passe : dessin des sommets et ajout du clic utilisateur.
        for node, (x, y) in self.display_positions.items():
            color_index = self.color_map[node]
            fill_color = COLOR_PALETTE[color_index % len(COLOR_PALETTE)]
            province_tag = f"province::{node}"

            self.canvas.create_oval(
                x - self.node_radius,
                y - self.node_radius,
                x + self.node_radius,
                y + self.node_radius,
                fill=fill_color,
                outline="#0f172a",
                width=2,
                tags=(province_tag, "province"),
            )
            self.canvas.create_text(
                x,
                y,
                text=str(color_index + 1),
                font=("Arial", 12, "bold"),
                fill="white",
                tags=(province_tag, "province"),
            )
            self.canvas.create_text(
                x,
                y + self.node_radius + 12,
                text=node,
                font=("Arial", 8, "bold"),
                fill="#0f172a",
                tags=(province_tag, "province"),
            )

            self.canvas.tag_bind(
                province_tag,
                "<Button-1>",
                lambda event, province=node: self.on_province_click(province),
            )

        # La zone scrollable suit la taille reelle de l'image et des etiquettes.
        self.canvas.update_idletasks()
        bbox = self.canvas.bbox("all")
        if bbox is not None:
            padding = 20
            self.canvas.configure(
                scrollregion=(
                    bbox[0] - padding,
                    bbox[1] - padding,
                    bbox[2] + padding,
                    bbox[3] + padding,
                )
            )

    def refresh_sidebar(self):
        """Met a jour le panneau lateral avec le resume et les resultats."""
        # Nombre de couleurs effectivement utilisees par l'algorithme.
        color_count = len(set(self.color_map.values()))

        # Verification de la validite de la solution calculee.
        conflicts = validate_coloring(self.graph, self.color_map)

        stats = [
            f"Nombre de provinces : {len(self.graph)}",
            f"Nombre de couleurs utilisees : {color_count}",
            f"Conflits detectes : {len(conflicts)}",
            "",
            "Legende :",
        ]

        # Construction de la legende couleur par couleur.
        for color_id in sorted(set(self.color_map.values())):
            stats.append(
                f"Couleur {color_id + 1} -> {COLOR_NAMES[color_id % len(COLOR_NAMES)]}"
            )

        self.stats_text.config(text="\n".join(stats))

        lines = []

        # On reutilise le tri par degre pour afficher d'abord les provinces
        # les plus contraintes dans la coloration.
        for node in sort_nodes(self.graph):
            lines.append(
                f"{node:<16} : couleur {self.color_map[node] + 1} | degre {len(self.graph[node])}"
            )

        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert("1.0", "\n".join(lines))
        self.result_text.configure(state="disabled")

    def recolor(self):
        """
        Recalcule la coloration du graphe puis redessine l'interface.

        Sortie :
            aucune ; met a jour self.color_map et l'affichage.
        """
        self.color_map = welsh_powell(self.graph)
        self.draw_graph()
        self.refresh_sidebar()

    def on_province_click(self, province):
        """
        Affiche les informations detaillees d'une province selectionnee.

        Entree :
            province (str) : nom de la province cliquee.
        """
        # Recuperation des informations utiles a afficher.
        neighbors = ", ".join(self.graph[province])
        fill_color = COLOR_PALETTE[self.color_map[province] % len(COLOR_PALETTE)]

        # Fenetre secondaire d'information.
        window = tk.Toplevel(self.root)
        window.title(f"Province : {province}")
        window.configure(bg="white")

        message = (
            f"Province : {province}\n"
            f"Couleur attribuee : {self.color_map[province] + 1} ({fill_color})\n"
            f"Degre : {len(self.graph[province])}\n"
            f"Voisines : {neighbors}"
        )

        tk.Label(
            window,
            text=message,
            justify="left",
            bg="white",
            fg="#1f2937",
            font=("Arial", 11),
            padx=18,
            pady=18,
        ).pack()

    def show_results_window(self):
        """Ouvre une fenetre contenant la liste complete des couleurs attribuees."""
        window = tk.Toplevel(self.root)
        window.title("Resultats de la coloration")
        window.geometry("430x520")
        window.configure(bg="white")

        text = tk.Text(window, wrap="word", font=("Consolas", 10), bg="white")
        text.pack(fill="both", expand=True, padx=14, pady=14)

        # Preparation du contenu textuel a afficher dans la fenetre.
        lines = [
            "Coloration des provinces de la RDC par Welsh-Powell",
            "",
        ]
        for province in sort_nodes(self.graph):
            color_id = self.color_map[province]
            lines.append(
                f"{province:<16} -> couleur {color_id + 1} - {COLOR_NAMES[color_id % len(COLOR_NAMES)]}"
            )

        text.insert("1.0", "\n".join(lines))
        text.configure(state="disabled")

    def show_validation(self):
        """Affiche si la coloration respecte la contrainte de non-conflit."""
        conflicts = validate_coloring(self.graph, self.color_map)

        # Selon le resultat de la verification, on affiche soit les conflits,
        # soit un message de confirmation.
        if conflicts:
            message = "Coloration invalide.\n\n" + "\n".join(
                f"{left} - {right}" for left, right in conflicts
            )
        else:
            message = (
                "Coloration valide.\n\n"
                f"Aucune province voisine ne partage la meme couleur.\n"
                f"Nombre de couleurs utilisees : {len(set(self.color_map.values()))}"
            )

        window = tk.Toplevel(self.root)
        window.title("Verification")
        window.configure(bg="white")

        tk.Label(
            window,
            text=message,
            justify="left",
            bg="white",
            fg="#1f2937",
            font=("Arial", 11),
            padx=18,
            pady=18,
        ).pack()


def main():
    """Point d'entree du programme."""
    # Creation de la fenetre principale puis lancement de l'application.
    root = tk.Tk()
    MapColoringApp(root)

    # Boucle d'evenements Tkinter : le programme reste actif
    # tant que la fenetre n'est pas fermee.
    root.mainloop()


if __name__ == "__main__":
    main()
