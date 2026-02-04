#!/usr/bin/env python3
"""
Interface Graphique PyQt6 pour les fonctions utilitaires
"""

import sys
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QLabel, QLineEdit, QTextEdit, 
                             QSpinBox, QGroupBox, QFileDialog, QMessageBox, QTabWidget)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

# J'importe mes fonctions utilitaires
from fonctions_python import liste_processus, ping_adresse, compresser_repertoire, meteo, decouper_fichier, reconstituer_fichier


class WorkerThread(QThread):
    """
    Thread worker que j'ai créé pour exécuter les tâches longues sans bloquer l'interface
    """
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, function, *args):
        super().__init__()
        self.function = function
        self.args = args
    
    def run(self):
        try:
            result = self.function(*self.args)
            self.finished.emit(str(result))
        except Exception as e:
            self.error.emit(f"Erreur : {str(e)}")


class InterfaceGraphique(QMainWindow):
    """
    Interface graphique principale que j'ai développée pour utiliser mes fonctions
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interface Graphique - Fonctions Utilitaires")
        self.setGeometry(100, 100, 800, 600)
        
        # Je crée le widget central avec des onglets
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Je crée la mise en page principale
        layout = QVBoxLayout(self.central_widget)
        
        # Je crée le widget à onglets
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # J'initialise les onglets
        self.init_processus_tab()
        self.init_ping_tab()
        self.init_compression_tab()
        self.init_meteo_tab()
        self.init_decoupage_tab()
        
        # Zone de résultats commune
        self.result_area = QTextEdit()
        self.result_area.setFont(QFont("Consolas", 10))
        self.result_area.setMaximumHeight(150)
        layout.addWidget(QLabel("Résultats :"))
        layout.addWidget(self.result_area)
        
    def init_processus_tab(self):
        """J'initialise l'onglet pour la liste des processus"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Groupe principal
        group = QGroupBox("5. Liste des processus système")
        group_layout = QVBoxLayout(group)
        
        # Description
        desc = QLabel("Cette fonction me permet d'obtenir la liste de tous les processus en cours d'exécution.")
        desc.setWordWrap(True)
        group_layout.addWidget(desc)
        
        # Bouton d'exécution
        btn = QPushButton("Obtenir la liste des processus")
        btn.clicked.connect(self.executer_liste_processus)
        group_layout.addWidget(btn)
        
        layout.addWidget(group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Processus")
    
    def init_ping_tab(self):
        """J'initialise l'onglet pour le ping"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Groupe principal
        group = QGroupBox("6. Test de connexion réseau (Ping)")
        group_layout = QVBoxLayout(group)
        
        # Description
        desc = QLabel("Cette fonction me permet de tester une connexion réseau vers une adresse.")
        desc.setWordWrap(True)
        group_layout.addWidget(desc)
        
        # Champ adresse
        adresse_layout = QHBoxLayout()
        adresse_layout.addWidget(QLabel("Adresse à tester :"))
        self.ping_adresse = QLineEdit("8.8.8.8")
        adresse_layout.addWidget(self.ping_adresse)
        group_layout.addLayout(adresse_layout)
        
        # Nombre de pings
        nb_layout = QHBoxLayout()
        nb_layout.addWidget(QLabel("Nombre de pings :"))
        self.ping_nombre = QSpinBox()
        self.ping_nombre.setRange(1, 20)
        self.ping_nombre.setValue(4)
        nb_layout.addWidget(self.ping_nombre)
        nb_layout.addStretch()
        group_layout.addLayout(nb_layout)
        
        # Bouton d'exécution
        btn = QPushButton("Effectuer le ping")
        btn.clicked.connect(self.executer_ping)
        group_layout.addWidget(btn)
        
        layout.addWidget(group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Ping")
    
    def init_compression_tab(self):
        """J'initialise l'onglet pour la compression"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Groupe principal
        group = QGroupBox("7. Compression de répertoire")
        group_layout = QVBoxLayout(group)
        
        # Description
        desc = QLabel("Cette fonction me permet de compresser un répertoire en fichier ZIP.")
        desc.setWordWrap(True)
        group_layout.addWidget(desc)
        
        # Répertoire source
        rep_layout = QHBoxLayout()
        rep_layout.addWidget(QLabel("Répertoire à compresser :"))
        self.compress_repertoire = QLineEdit()
        btn_browse_rep = QPushButton("Parcourir...")
        btn_browse_rep.clicked.connect(self.browse_repertoire)
        rep_layout.addWidget(self.compress_repertoire)
        rep_layout.addWidget(btn_browse_rep)
        group_layout.addLayout(rep_layout)
        
        # Fichier ZIP de destination
        zip_layout = QHBoxLayout()
        zip_layout.addWidget(QLabel("Fichier ZIP de sortie :"))
        self.compress_zip = QLineEdit("archive.zip")
        btn_browse_zip = QPushButton("Parcourir...")
        btn_browse_zip.clicked.connect(self.browse_zip_save)
        zip_layout.addWidget(self.compress_zip)
        zip_layout.addWidget(btn_browse_zip)
        group_layout.addLayout(zip_layout)
        
        # Bouton d'exécution
        btn = QPushButton("Compresser le répertoire")
        btn.clicked.connect(self.executer_compression)
        group_layout.addWidget(btn)
        
        layout.addWidget(group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Compression")
    
    def init_meteo_tab(self):
        """J'initialise l'onglet pour la météo"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Groupe principal
        group = QGroupBox("8. Données météorologiques")
        group_layout = QVBoxLayout(group)
        
        # Description
        desc = QLabel("Cette fonction me permet d'obtenir les données météo d'une ville au format JSON.")
        desc.setWordWrap(True)
        group_layout.addWidget(desc)
        
        # Champ ville
        ville_layout = QHBoxLayout()
        ville_layout.addWidget(QLabel("Nom de la ville :"))
        self.meteo_ville = QLineEdit("Paris")
        ville_layout.addWidget(self.meteo_ville)
        ville_layout.addStretch()
        group_layout.addLayout(ville_layout)
        
        # Bouton d'exécution
        btn = QPushButton("Obtenir la météo")
        btn.clicked.connect(self.executer_meteo)
        group_layout.addWidget(btn)
        
        layout.addWidget(group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Météo")
    
    def init_decoupage_tab(self):
        """J'initialise l'onglet pour le découpage/reconstitution de fichiers"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Groupe découpage
        group_dec = QGroupBox("9. Découpage de fichier")
        group_dec_layout = QVBoxLayout(group_dec)
        
        # Description découpage
        desc_dec = QLabel("Cette fonction me permet de découper un fichier en plusieurs morceaux.")
        desc_dec.setWordWrap(True)
        group_dec_layout.addWidget(desc_dec)
        
        # Fichier à découper
        fichier_layout = QHBoxLayout()
        fichier_layout.addWidget(QLabel("Fichier à découper :"))
        self.decoup_fichier = QLineEdit()
        btn_browse_fichier = QPushButton("Parcourir...")
        btn_browse_fichier.clicked.connect(self.browse_fichier)
        fichier_layout.addWidget(self.decoup_fichier)
        fichier_layout.addWidget(btn_browse_fichier)
        group_dec_layout.addLayout(fichier_layout)
        
        # Nombre de morceaux
        morceaux_layout = QHBoxLayout()
        morceaux_layout.addWidget(QLabel("Nombre de morceaux :"))
        self.decoup_nombre = QSpinBox()
        self.decoup_nombre.setRange(2, 50)
        self.decoup_nombre.setValue(3)
        morceaux_layout.addWidget(self.decoup_nombre)
        morceaux_layout.addStretch()
        group_dec_layout.addLayout(morceaux_layout)
        
        # Bouton découpage
        btn_decoup = QPushButton("Découper le fichier")
        btn_decoup.clicked.connect(self.executer_decoupage)
        group_dec_layout.addWidget(btn_decoup)
        
        layout.addWidget(group_dec)
        
        # Groupe reconstitution
        group_rec = QGroupBox("Reconstitution de fichier")
        group_rec_layout = QVBoxLayout(group_rec)
        
        # Description reconstitution
        desc_rec = QLabel("Cette fonction me permet de reconstituer un fichier à partir de ses morceaux.")
        desc_rec.setWordWrap(True)
        group_rec_layout.addWidget(desc_rec)
        
        # Fichier de base
        base_layout = QHBoxLayout()
        base_layout.addWidget(QLabel("Fichier de base :"))
        self.recon_fichier = QLineEdit()
        btn_browse_base = QPushButton("Parcourir...")
        btn_browse_base.clicked.connect(self.browse_fichier_base)
        base_layout.addWidget(self.recon_fichier)
        base_layout.addWidget(btn_browse_base)
        group_rec_layout.addLayout(base_layout)
        
        # Nombre de morceaux pour reconstitution
        morceaux_rec_layout = QHBoxLayout()
        morceaux_rec_layout.addWidget(QLabel("Nombre de morceaux :"))
        self.recon_nombre = QSpinBox()
        self.recon_nombre.setRange(2, 50)
        self.recon_nombre.setValue(3)
        morceaux_rec_layout.addWidget(self.recon_nombre)
        morceaux_rec_layout.addStretch()
        group_rec_layout.addLayout(morceaux_rec_layout)
        
        # Bouton reconstitution
        btn_recon = QPushButton("Reconstituer le fichier")
        btn_recon.clicked.connect(self.executer_reconstitution)
        group_rec_layout.addWidget(btn_recon)
        
        layout.addWidget(group_rec)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Découpage/Reconstitution")
    
    def browse_repertoire(self):
        """Je permets de parcourir pour sélectionner un répertoire"""
        repertoire = QFileDialog.getExistingDirectory(self, "Sélectionner un répertoire")
        if repertoire:
            self.compress_repertoire.setText(repertoire)
    
    def browse_zip_save(self):
        """Je permets de choisir l'emplacement du fichier ZIP"""
        fichier, _ = QFileDialog.getSaveFileName(self, "Enregistrer le fichier ZIP", 
                                                "archive.zip", "Fichiers ZIP (*.zip)")
        if fichier:
            self.compress_zip.setText(fichier)
    
    def browse_fichier(self):
        """Je permets de sélectionner un fichier à découper"""
        fichier, _ = QFileDialog.getOpenFileName(self, "Sélectionner un fichier")
        if fichier:
            self.decoup_fichier.setText(fichier)
    
    def browse_fichier_base(self):
        """Je permets de sélectionner le fichier de base pour reconstitution"""
        fichier, _ = QFileDialog.getOpenFileName(self, "Sélectionner le fichier de base")
        if fichier:
            self.recon_fichier.setText(fichier)
    
    def executer_liste_processus(self):
        """J'exécute la fonction liste des processus"""
        self.result_area.clear()
        self.result_area.append("Récupération de la liste des processus...")
        
        # Je crée un thread pour ne pas bloquer l'interface
        self.worker = WorkerThread(self.obtenir_processus_formatte)
        self.worker.finished.connect(self.afficher_resultat)
        self.worker.error.connect(self.afficher_erreur)
        self.worker.start()
    
    def obtenir_processus_formatte(self):
        """J'obtiens la liste des processus formatée"""
        processus = liste_processus()
        if processus:
            result = f"Liste des processus ({len(processus)} processus trouvés):\n\n"
            for pid, nom in list(processus.items())[:20]:  # Je limite à 20 pour l'affichage
                result += f"PID {pid}: {nom}\n"
            if len(processus) > 20:
                result += f"\n... et {len(processus) - 20} autres processus"
            return result
        else:
            return "Aucun processus trouvé ou erreur lors de la récupération."
    
    def executer_ping(self):
        """J'exécute la fonction ping"""
        adresse = self.ping_adresse.text().strip()
        nombre = self.ping_nombre.value()
        
        if not adresse:
            QMessageBox.warning(self, "Erreur", "Veuillez saisir une adresse.")
            return
        
        self.result_area.clear()
        self.result_area.append(f"Test de ping vers {adresse} ({nombre} paquets)...")
        
        # Je crée un thread pour ne pas bloquer l'interface
        self.worker = WorkerThread(ping_adresse, adresse, nombre)
        self.worker.finished.connect(self.afficher_resultat)
        self.worker.error.connect(self.afficher_erreur)
        self.worker.start()
    
    def executer_compression(self):
        """J'exécute la fonction de compression"""
        repertoire = self.compress_repertoire.text().strip()
        fichier_zip = self.compress_zip.text().strip()
        
        if not repertoire or not fichier_zip:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs.")
            return
        
        self.result_area.clear()
        self.result_area.append(f"Compression de '{repertoire}' vers '{fichier_zip}'...")
        
        # Je crée un thread pour ne pas bloquer l'interface
        self.worker = WorkerThread(self.compresser_avec_message, repertoire, fichier_zip)
        self.worker.finished.connect(self.afficher_resultat)
        self.worker.error.connect(self.afficher_erreur)
        self.worker.start()
    
    def compresser_avec_message(self, repertoire, fichier_zip):
        """J'exécute la compression avec un message de retour"""
        resultat = compresser_repertoire(repertoire, fichier_zip)
        if resultat:
            return f"Compression réussie !\nFichier créé : {fichier_zip}"
        else:
            return "Erreur lors de la compression."
    
    def executer_meteo(self):
        """J'exécute la fonction météo"""
        ville = self.meteo_ville.text().strip()
        
        if not ville:
            QMessageBox.warning(self, "Erreur", "Veuillez saisir le nom d'une ville.")
            return
        
        self.result_area.clear()
        self.result_area.append(f"Récupération de la météo pour {ville}...")
        
        # Je crée un thread pour ne pas bloquer l'interface
        self.worker = WorkerThread(self.obtenir_meteo_formatee, ville)
        self.worker.finished.connect(self.afficher_resultat)
        self.worker.error.connect(self.afficher_erreur)
        self.worker.start()
    
    def obtenir_meteo_formatee(self, ville):
        """J'obtiens la météo formatée pour l'affichage"""
        meteo_json = meteo(ville)
        try:
            # Je parse le JSON pour un affichage plus lisible
            data = json.loads(meteo_json)
            if "erreur" in data:
                return f"Erreur : {data['erreur']}"
            else:
                result = f"Météo pour {data['commune']} :\n\n"
                result += f"Température : {data['temperature_celsius']}°C\n"
                result += f"Description : {data['description']}\n"
                result += f"Humidité : {data['humidite']}%\n"
                result += f"Vent : {data['vitesse_vent_kmh']} km/h\n"
                result += f"Pression : {data['pression']} hPa\n"
                result += f"Visibilité : {data['visibilite_km']} km\n"
                result += f"\nDonnées JSON complètes :\n{meteo_json}"
                return result
        except:
            return f"Données météo brutes :\n{meteo_json}"
    
    def executer_decoupage(self):
        """J'exécute la fonction de découpage"""
        fichier = self.decoup_fichier.text().strip()
        nombre = self.decoup_nombre.value()
        
        if not fichier:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un fichier.")
            return
        
        self.result_area.clear()
        self.result_area.append(f"Découpage de '{fichier}' en {nombre} morceaux...")
        
        # Je crée un thread pour ne pas bloquer l'interface
        self.worker = WorkerThread(self.decouper_avec_message, fichier, nombre)
        self.worker.finished.connect(self.afficher_resultat)
        self.worker.error.connect(self.afficher_erreur)
        self.worker.start()
    
    def decouper_avec_message(self, fichier, nombre):
        """J'exécute le découpage avec un message de retour"""
        resultat = decouper_fichier(fichier, nombre)
        if resultat:
            return f"Découpage réussi !\nLe fichier '{fichier}' a été découpé en {nombre} morceaux."
        else:
            return "Erreur lors du découpage."
    
    def executer_reconstitution(self):
        """J'exécute la fonction de reconstitution"""
        fichier = self.recon_fichier.text().strip()
        nombre = self.recon_nombre.value()
        
        if not fichier:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un fichier de base.")
            return
        
        self.result_area.clear()
        self.result_area.append(f"Reconstitution de '{fichier}' à partir de {nombre} morceaux...")
        
        # Je crée un thread pour ne pas bloquer l'interface
        self.worker = WorkerThread(self.reconstituer_avec_message, fichier, nombre)
        self.worker.finished.connect(self.afficher_resultat)
        self.worker.error.connect(self.afficher_erreur)
        self.worker.start()
    
    def reconstituer_avec_message(self, fichier, nombre):
        """J'exécute la reconstitution avec un message de retour"""
        resultat = reconstituer_fichier(fichier, nombre)
        if resultat:
            return f"Reconstitution réussie !\nLe fichier '{fichier}' a été reconstitué à partir de {nombre} morceaux."
        else:
            return "Erreur lors de la reconstitution. Vérifiez que tous les morceaux existent."
    
    def afficher_resultat(self, resultat):
        """J'affiche le résultat dans la zone de texte"""
        self.result_area.clear()
        self.result_area.append(resultat)
    
    def afficher_erreur(self, erreur):
        """J'affiche l'erreur dans la zone de texte"""
        self.result_area.clear()
        self.result_area.append(f"ERREUR : {erreur}")


def main():
    """Fonction principale pour lancer l'interface graphique"""
    app = QApplication(sys.argv)
    
    # Je configure le style de l'application
    app.setStyle('Fusion')
    
    # Je crée et affiche la fenêtre principale
    fenetre = InterfaceGraphique()
    fenetre.show()
    
    # Je lance la boucle d'événements
    sys.exit(app.exec())


if __name__ == "__main__":
    main()