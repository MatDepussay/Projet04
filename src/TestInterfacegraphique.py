import tkinter as tk
from tkinter import ttk
from affichage import afficherCarte
from data import ListeLiaison, calculerFlotMaximal, liaison_existe, optimiser_liaisons, optimiser_liaisons_pour_approvisionnement
from data import liaison as Liaison
import copy


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion des Liaisons")
        self.liaisons_actuelles = copy.deepcopy(ListeLiaison)

        # Layout
        self.create_widgets()

    def create_widgets(self):
        # Menu principal
        self.menu_frame = tk.Frame(self.root)
        self.menu_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        tk.Label(self.menu_frame, text="=== MENU ===", font=("Arial", 14)).pack(pady=5)
        tk.Button(self.menu_frame, text="Afficher la carte actuelle", command=self.afficher_carte).pack(fill=tk.X, pady=5)
        tk.Button(self.menu_frame, text="Travaux", command=self.travaux).pack(fill=tk.X, pady=5)
        tk.Button(self.menu_frame, text="Approvisionnement des villes", command=self.approvisionnement).pack(fill=tk.X, pady=5)
        tk.Button(self.menu_frame, text="Quitter", command=self.root.quit).pack(fill=tk.X, pady=5)

        # Zone de texte pour les logs
        self.log_frame = tk.Frame(self.root)
        self.log_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.log_text = tk.Text(self.log_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = ttk.Scrollbar(self.log_frame, command=self.log_text.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=self.scrollbar.set)
        self.canvas_frame = tk.Frame(self.root, bg="white")
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def afficher_carte(self):
        result, index_noeuds = calculerFlotMaximal(self.liaisons_actuelles)
        afficherCarte(result=result, index_noeuds=index_noeuds, liaisons=self.liaisons_actuelles, frame=self.canvas_frame)

        self.log("Carte actuelle affichée.")

    def travaux(self):
        liaisons_a_optimiser = []

        def ajouter_liaison():
            u = sommet_depart.get().strip().upper()
            v = sommet_arrivee.get().strip().upper()

            if not liaison_existe(u, v, self.liaisons_actuelles):
                self.log(f"❌ La liaison ({u}, {v}) n’existe pas.")
                return

            liaisons_a_optimiser.append((u, v))
            self.log(f"➕ Liaison ajoutée : {u} ➝ {v}")

        def lancer_optimisation():
            config_finale, travaux = optimiser_liaisons(self.liaisons_actuelles, liaisons_a_optimiser)
            for i, (liaison, cap, flot) in enumerate(travaux):
                u, v = liaison
                self.log(f"🔧 Travaux #{i+1} : Liaison {u} ➝ {v}")
                self.log(f"   ↪ Capacité choisie : {cap} unités")
                self.log(f"   🚀 Nouveau flot maximal : {flot} unités\n")

            result, index_noeuds = calculerFlotMaximal(config_finale)
            afficherCarte(result=result, index_noeuds=index_noeuds, liaisons=self.liaisons_actuelles, frame=self.canvas_frame)

            self.log("Carte finale affichée après travaux.")

        # Fenêtre pour les travaux
        travaux_window = tk.Toplevel(self.root)
        travaux_window.title("Travaux")

        tk.Label(travaux_window, text="Sommet de départ :").pack(pady=5)
        sommet_depart = tk.Entry(travaux_window)
        sommet_depart.pack(pady=5)

        tk.Label(travaux_window, text="Sommet d’arrivée :").pack(pady=5)
        sommet_arrivee = tk.Entry(travaux_window)
        sommet_arrivee.pack(pady=5)

        tk.Button(travaux_window, text="Ajouter liaison", command=ajouter_liaison).pack(pady=5)
        tk.Button(travaux_window, text="Lancer optimisation", command=lancer_optimisation).pack(pady=5)

    def approvisionnement(self):
        liaisons_possibles = [(l.depart, l.arrivee) for l in ListeLiaison][:20]

        config_finale, travaux = optimiser_liaisons_pour_approvisionnement(
            ListeLiaison, liaisons_possibles, objectif_flot=50
        )

        self.log(f"✅ Objectif atteint avec {len(travaux)} travaux :")
        for (u, v), cap, flot in travaux:
            self.log(f"🔧 {u} → {v} capacité {cap} => flot = {flot} u")

        result, index_noeuds = calculerFlotMaximal(config_finale)
        afficherCarte(result=result, index_noeuds=index_noeuds, liaisons=self.liaisons_actuelles, frame=self.canvas_frame)

        self.log("Carte affichée après approvisionnement.")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
