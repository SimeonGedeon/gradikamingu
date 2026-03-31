import tkinter as tk
from tkinter import PhotoImage, messagebox
import json



# ============================================================
# Sujet : Coloration automatique de la carte de la RDC
# Methode : Algorithme de Welsh-Powell (version 1)
# Logique : while externe (couleurs) + for interne (sommets)
# ============================================================

# Chargement du graphe depuis un fichier JSON
try:
    with open("rdc_graph.json", "r", encoding="utf-8") as f:
        # Graphe d'entree : chaque cle represente une province et la liste associee
        RAW_GRAPH = json.load(f)
except FileNotFoundError:
    print("Fichier JSON introuvable !")
    RAW_GRAPH = {}

# Coordonnees d'affichage des sommets sur le canevas
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


# Parametres de reference pour l'affichage
REFERENCE_IMAGE_SIZE = 612
REFERENCE_IMAGE_LEFT = 79
REFERENCE_IMAGE_TOP = 4
CANVAS_WIDTH = 620
CANVAS_HEIGHT = 620
DISPLAY_MAX_SIZE = 720
BACKGROUND_SOURCE_SIZE = 1024
BACKGROUND_CONTENT_LEFT = 64
BACKGROUND_CONTENT_TOP = 84
BACKGROUND_CONTENT_WIDTH = 831
BACKGROUND_CONTENT_HEIGHT = 851


# Palette de couleurs
COLOR_PALETTE = [
    "#ef476f",  # rose
    "#118ab2",  # bleu
    "#06d6a0",  # vert
    "#ffd166",  # jaune
    "#8338ec",  # violet
    "#fb5607",  # orange
    "#3a86ff",  # bleu clair
    "#8ac926",  # vert clair
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
    """
    Normalise le graphe : supprime les doublons, garantit la reciprocite.
    """
    graph = {node: set(neighbors) for node, neighbors in raw_graph.items()}

    for node in list(graph):
        graph.setdefault(node, set())
        graph[node].discard(node)
        for neighbor in list(graph[node]):
            graph.setdefault(neighbor, set()).add(node)

    return {node: sorted(neighbors) for node, neighbors in graph.items()}


def calculer_degres(graph):
    """
    Calcule le degre de chaque sommet.
    """
    return {v: len(voisins) for v, voisins in graph.items()}


def trier_par_degre_decroissant(graph, degres):
    """
    Trie les sommets par ordre decroissant de degre.
    """
    return sorted(graph.keys(), key=lambda v: (-degres[v], v))


def welsh_powell_v1(graph, verbose=False):
    """
    Algorithme de Welsh-Powell - Version 1 (logique du pseudo-code)

    Logique :
        - Calcul des degres
        - Tri des sommets par degre decroissant
        - Initialisation : tous les sommets non colories (0)
        - k = 1 (premiere couleur)
        - Tant qu'il existe un sommet non colorie :
            - Parcourir tous les sommets tries
            - Si un sommet n'est pas colorie ET aucun voisin n'a la couleur k
              alors lui attribuer la couleur k
            - Incrementer k

    Retourne:
        tuple -- (dictionnaire des couleurs, nombre de couleurs utilisees)
    """
    # Etape 1 : Calcul des degres
    degres = calculer_degres(graph)

    # Etape 2 : Tri des sommets
    sommets_tries = trier_par_degre_decroissant(graph, degres)

    if verbose:
        print("\n=== TRI DES SOMMETS ===")
        for i, v in enumerate(sommets_tries, 1):
            print(f"{i}. {v} (degre: {degres[v]})")

    # Etape 3 : Initialisation
    couleurs = {v: 0 for v in graph}  # 0 = non colorie
    k = 1  # Premiere couleur

    # Etape 4 : Boucle principale (while externe)
    while any(couleur == 0 for couleur in couleurs.values()):
        if verbose:
            print(f"\n--- Couleur {k} ---")

        nb_colories = 0

        # Boucle interne : parcours de tous les sommets
        for sommet in sommets_tries:
            if couleurs[sommet] == 0:  # Si non colorie
                # Verifier les voisins
                conflit = False
                for voisin in graph[sommet]:
                    if couleurs[voisin] == k:
                        conflit = True
                        if verbose:
                            print(f"  {sommet} -> conflit avec {voisin} (deja couleur {k})")
                        break

                if not conflit:
                    couleurs[sommet] = k
                    nb_colories += 1
                    if verbose:
                        print(f"  ✓ {sommet} -> couleur {k}")

        if verbose:
            print(f"  → {nb_colories} sommet(s) colorie(s) avec la couleur {k}")

        k += 1

    return couleurs, k - 1


def verifier_coloration(graph, couleurs):
    """
    Verifie qu'aucune arete ne relie deux sommets de meme couleur.
    """
    conflits = []
    for node, neighbors in graph.items():
        for neighbor in neighbors:
            if node < neighbor and couleurs[node] == couleurs[neighbor]:
                conflits.append((node, neighbor))
    return conflits


class MapColoringApp:
    """Interface graphique pour la coloration de la carte de la RDC."""

    def __init__(self, root):
        self.root = root

        # Preparation des donnees
        self.graph = normalize_graph(RAW_GRAPH)

        # Calcul initial de la coloration (version 1)
        self.color_map, self.color_count = welsh_powell_v1(self.graph)

        # Variables d'affichage
        self.original_image = None
        self.image = None
        self.display_positions = dict(POSITIONS)
        self.node_radius = 24

        # Configuration de la fenetre
        self.root.title("Coloration automatique de la RDC - Welsh-Powell (Version 1)")
        self.root.geometry("1040x820")
        self.root.minsize(920, 720)
        self.root.configure(bg="#f4f7fb")

        # Titre
        self.title_label = tk.Label(
            root,
            text="Coloration automatique de la carte de la RDC",
            font=("Arial", 18, "bold"),
            bg="#f4f7fb",
            fg="#1f2937",
        )
        self.title_label.pack(pady=(12, 6))

        # Sous-titre avec la version de l'algorithme
        self.subtitle_label = tk.Label(
            root,
            text="Algorithme de Welsh-Powell (Version 1 : while externe + for interne)",
            font=("Arial", 11),
            bg="#f4f7fb",
            fg="#475569",
        )
        self.subtitle_label.pack()

        # Zone centrale
        self.main_frame = tk.Frame(root, bg="#f4f7fb")
        self.main_frame.pack(fill="both", expand=True, padx=14, pady=14)

        # Zone gauche : canevas
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
            self.canvas_frame, orient="vertical", command=self.canvas.yview
        )
        self.canvas_scroll_x = tk.Scrollbar(
            self.canvas_frame, orient="horizontal", command=self.canvas.xview
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

        # Panneau lateral
        self.sidebar = tk.Frame(self.main_frame, bg="white", bd=1, relief="solid")
        self.sidebar.pack(side="right", fill="y", padx=(14, 0))

        # Section Resume
        self.summary_label = tk.Label(
            self.sidebar,
            text="Resume",
            font=("Arial", 14, "bold"),
            bg="white",
            anchor="w",
        )
        self.summary_label.pack(fill="x", padx=14, pady=(14, 8))

        self.stats_text = tk.Label(
            self.sidebar,
            justify="left",
            anchor="nw",
            bg="white",
            fg="#334155",
            font=("Arial", 10),
        )
        self.stats_text.pack(fill="x", padx=14)

        # Section Liste des couleurs
        self.list_label = tk.Label(
            self.sidebar,
            text="Attribution des couleurs",
            font=("Arial", 12, "bold"),
            bg="white",
            anchor="w",
        )
        self.list_label.pack(fill="x", padx=14, pady=(18, 8))

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

        # Barre des boutons
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

        # Premier affichage
        self.draw_graph()
        self.refresh_sidebar()

    def load_background(self):
        """Charge l'image de fond si disponible."""
        try:
            self.original_image = PhotoImage(file="rdc.png")
            self.image = self.original_image
            image_width = self.image.width()
            image_height = self.image.height()

            self.canvas.create_image(0, 0, image=self.image, anchor="nw")

            # Ajuster les positions des sommets
            content_left = round(BACKGROUND_CONTENT_LEFT * image_width / BACKGROUND_SOURCE_SIZE)
            content_top = round(BACKGROUND_CONTENT_TOP * image_height / BACKGROUND_SOURCE_SIZE)
            content_width = round(BACKGROUND_CONTENT_WIDTH * image_width / BACKGROUND_SOURCE_SIZE)
            content_height = round(BACKGROUND_CONTENT_HEIGHT * image_height / BACKGROUND_SOURCE_SIZE)

            self.display_positions = self.scale_positions(
                content_left, content_top, content_width, content_height
            )

            scale_factor = min(image_width / REFERENCE_IMAGE_SIZE, image_height / REFERENCE_IMAGE_SIZE)
            self.node_radius = max(18, round(18 * scale_factor))
        except tk.TclError:
            self.display_positions = dict(POSITIONS)
            self.node_radius = 24
            self.canvas.create_text(
                20, 30,
                text="Image 'rdc.png' introuvable : affichage du graphe sans fond de carte.",
                fill="#64748b", font=("Arial", 10, "italic"), anchor="nw"
            )

    def scale_positions(self, left, top, image_width, image_height):
        """Adapte les positions des sommets a la taille de l'image."""
        scaled = {}
        for province, (x, y) in POSITIONS.items():
            rel_x = (x - REFERENCE_IMAGE_LEFT) / REFERENCE_IMAGE_SIZE
            rel_y = (y - REFERENCE_IMAGE_TOP) / REFERENCE_IMAGE_SIZE
            scaled[province] = (
                round(left + rel_x * image_width),
                round(top + rel_y * image_height),
            )
        return scaled

    def draw_graph(self):
        """Dessine le graphe colorie."""
        self.canvas.delete("all")
        self.load_background()

        drawn_edges = set()
        for node, neighbors in self.graph.items():
            for neighbor in neighbors:
                edge = tuple(sorted((node, neighbor)))
                if edge in drawn_edges:
                    continue
                drawn_edges.add(edge)
                x1, y1 = self.display_positions[node]
                x2, y2 = self.display_positions[neighbor]
                self.canvas.create_line(x1, y1, x2, y2, fill="#94a3b8", width=2)

        for node, (x, y) in self.display_positions.items():
            color_idx = self.color_map[node]
            fill_color = COLOR_PALETTE[color_idx % len(COLOR_PALETTE)]
            tag = f"province::{node}"

            self.canvas.create_oval(
                x - self.node_radius, y - self.node_radius,
                x + self.node_radius, y + self.node_radius,
                fill=fill_color, outline="#0f172a", width=2,
                tags=(tag, "province")
            )
            self.canvas.create_text(
                x, y, text=str(color_idx + 1),
                font=("Arial", 12, "bold"), fill="white",
                tags=(tag, "province")
            )
            self.canvas.create_text(
                x, y + self.node_radius + 12, text=node,
                font=("Arial", 8, "bold"), fill="#0f172a",
                tags=(tag, "province")
            )
            self.canvas.tag_bind(
                tag, "<Button-1>",
                lambda event, p=node: self.on_province_click(p)
            )

        self.canvas.update_idletasks()
        bbox = self.canvas.bbox("all")
        if bbox:
            self.canvas.configure(scrollregion=(bbox[0]-20, bbox[1]-20, bbox[2]+20, bbox[3]+20))

    def refresh_sidebar(self):
        """Met a jour le panneau lateral."""
        color_count = len(set(self.color_map.values()))
        conflicts = verifier_coloration(self.graph, self.color_map)

        stats = [
            f"Nombre de provinces : {len(self.graph)}",
            f"Nombre de couleurs utilisees : {color_count}",
            f"Conflits detectes : {len(conflicts)}",
            "",
            "Legende :",
        ]
        for cid in sorted(set(self.color_map.values())):
            stats.append(f"Couleur {cid + 1} -> {COLOR_NAMES[cid % len(COLOR_NAMES)]}")
        self.stats_text.config(text="\n".join(stats))

        lines = []
        degres = calculer_degres(self.graph)
        sommets_tries = trier_par_degre_decroissant(self.graph, degres)
        for node in sommets_tries:
            lines.append(f"{node:<16} : couleur {self.color_map[node] + 1} | degre {degres[node]}")

        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert("1.0", "\n".join(lines))
        self.result_text.configure(state="disabled")

    def recolor(self):
        """Recalcule la coloration avec la version 1."""
        self.color_map, self.color_count = welsh_powell_v1(self.graph)
        self.draw_graph()
        self.refresh_sidebar()

    def on_province_click(self, province):
        """Affiche les informations d'une province."""
        neighbors = ", ".join(self.graph[province])
        color_idx = self.color_map[province]
        color_name = COLOR_NAMES[color_idx % len(COLOR_NAMES)]

        window = tk.Toplevel(self.root)
        window.title(f"Province : {province}")
        window.configure(bg="white")

        message = (
            f"Province : {province}\n"
            f"Couleur : {color_idx + 1} ({color_name})\n"
            f"Degre : {len(self.graph[province])}\n"
            f"Voisines : {neighbors}"
        )
        tk.Label(window, text=message, justify="left", bg="white",
                 font=("Arial", 11), padx=18, pady=18).pack()

    def show_results_window(self):
        """Affiche les resultats complets."""
        window = tk.Toplevel(self.root)
        window.title("Resultats de la coloration")
        window.geometry("430x520")
        window.configure(bg="white")

        text = tk.Text(window, wrap="word", font=("Consolas", 10), bg="white")
        text.pack(fill="both", expand=True, padx=14, pady=14)

        lines = ["Coloration des provinces de la RDC (Welsh-Powell - Version 1)", ""]
        degres = calculer_degres(self.graph)
        sommets_tries = trier_par_degre_decroissant(self.graph, degres)
        for node in sommets_tries:
            cid = self.color_map[node]
            lines.append(f"{node:<16} -> couleur {cid + 1} - {COLOR_NAMES[cid % len(COLOR_NAMES)]}")

        text.insert("1.0", "\n".join(lines))
        text.configure(state="disabled")

    def show_validation(self):
        """Verifie et affiche le resultat de la validation."""
        conflicts = verifier_coloration(self.graph, self.color_map)
        if conflicts:
            msg = "Coloration invalide.\n\n" + "\n".join(f"{c[0]} - {c[1]}" for c in conflicts)
        else:
            msg = (f"Coloration valide.\n\n"
                   f"Aucune province voisine ne partage la meme couleur.\n"
                   f"Nombre de couleurs utilisees : {len(set(self.color_map.values()))}")
        messagebox.showinfo("Verification", msg)


def main():
    """Point d'entree du programme."""
    root = tk.Tk()
    app = MapColoringApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()