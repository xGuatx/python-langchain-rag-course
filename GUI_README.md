# Interface Graphique PyQt6 - Guide d'utilisation

**Fichier :** `interface_graphique.py`

## Description

J'ai créé une interface graphique moderne avec PyQt6 qui permet d'utiliser facilement toutes mes fonctions utilitaires (exercices 5 à 9) de manière interactive et conviviale.

## Fonctionnalités de l'interface

### Architecture de l'interface

J'ai organisé l'interface en **5 onglets** distincts pour une navigation claire :

#### 1. **Onglet "Processus"** (Exercice 5)
- **Fonction :** `liste_processus()`
- **Interface :** Bouton simple pour obtenir la liste
- **Résultat :** Affichage des 20 premiers processus avec PID et nom

#### 2. **Onglet "Ping"** (Exercice 6)
- **Fonction :** `ping_adresse(adresse, nb_ping)`
- **Champs de saisie :**
  - Adresse à tester (défaut: 8.8.8.8)
  - Nombre de pings (1-20, défaut: 4)
- **Résultat :** Délai moyen ou message d'erreur

#### 3. **Onglet "Compression"** (Exercice 7)
- **Fonction :** `compresser_repertoire(repertoire, fichier_zip)`
- **Champs de saisie :**
  - Répertoire source (avec bouton "Parcourir...")
  - Fichier ZIP de destination (avec bouton "Parcourir...")
- **Résultat :** Confirmation de création du fichier ZIP

#### 4. **Onglet "Météo"** (Exercice 8)
- **Fonction :** `meteo(commune)`
- **Champs de saisie :**
  - Nom de la ville (défaut: Paris)
- **Résultat :** Données météo formatées + JSON complet

#### 5. **Onglet "Découpage/Reconstitution"** (Exercice 9)
- **Fonctions :** `decouper_fichier()` et `reconstituer_fichier()`
- **Deux sections distinctes :**
  
  **Section Découpage :**
  - Fichier à découper (avec bouton "Parcourir...")
  - Nombre de morceaux (2-50, défaut: 3)
  
  **Section Reconstitution :**
  - Fichier de base (avec bouton "Parcourir...")
  - Nombre de morceaux à reconstituer (2-50, défaut: 3)

### Zone de résultats commune

J'ai ajouté une **zone de résultats** en bas de l'interface qui :
- Affiche les résultats de toutes les opérations
- Utilise une police monospace (Consolas) pour un meilleur affichage
- Se met à jour en temps réel
- Affiche les messages d'erreur si nécessaire

## Fonctionnalités techniques

### Multithreading
J'ai implémenté un système de **threads** pour :
- Éviter le blocage de l'interface pendant les opérations longues
- Permettre l'annulation des opérations en cours
- Maintenir la réactivité de l'interface utilisateur

### Gestion des erreurs
- Validation des champs de saisie
- Messages d'erreur explicites dans les boîtes de dialogue
- Affichage des erreurs dans la zone de résultats

### Interface utilisateur
- **Style moderne** : Utilisation du style 'Fusion'
- **Navigation par onglets** : Organisation claire par fonction
- **Boutons "Parcourir"** : Sélection facile des fichiers et dossiers
- **Champs pré-remplis** : Valeurs par défaut pratiques
- **Responsive** : Interface qui s'adapte au contenu

## Installation et utilisation

### Prérequis
```bash
# J'installe les dépendances
pip install PyQt6>=6.4.0 psutil>=7.0.0 requests>=2.25.0
```

### Lancement de l'interface
```bash
# Avec l'environnement virtuel
source venv/bin/activate
python interface_graphique.py

# Ou directement
python3 interface_graphique.py
```

### Utilisation

1. **Je lance l'application** et la fenêtre s'ouvre
2. **Je navigue entre les onglets** selon la fonction souhaitée
3. **Je remplis les champs** nécessaires pour chaque fonction
4. **Je clique sur le bouton d'exécution**
5. **Je consulte les résultats** dans la zone en bas de l'écran

## Détails techniques de l'implémentation

### Architecture du code

```python
class InterfaceGraphique(QMainWindow):
    """Interface principale que j'ai développée"""
    
    def __init__(self):
        # J'initialise la fenêtre et les onglets
    
    def init_processus_tab(self):
        # J'initialise l'onglet processus
    
    # ... autres méthodes d'initialisation des onglets
    
    def executer_liste_processus(self):
        # J'exécute la fonction dans un thread séparé
```

### WorkerThread
J'ai créé une classe `WorkerThread` qui hérite de `QThread` pour :
- Exécuter les fonctions longues en arrière-plan
- Émettre des signaux pour communiquer avec l'interface principale
- Éviter le gel de l'interface utilisateur

### Gestion des fichiers
- **QFileDialog** pour la sélection de fichiers et dossiers
- **Validation automatique** des chemins sélectionnés
- **Gestion des extensions** (ZIP pour la compression)

## Exemple d'utilisation complète

1. **Test de ping :**
   - Je vais sur l'onglet "Ping"
   - Je saisis "google.com" dans le champ adresse
   - Je règle sur 5 pings
   - Je clique "Effectuer le ping"
   - Le résultat s'affiche avec le délai moyen

2. **Compression d'un dossier :**
   - Je vais sur l'onglet "Compression"
   - Je clique "Parcourir..." pour sélectionner mon dossier
   - Je choisis l'emplacement du ZIP de sortie
   - Je clique "Compresser le répertoire"
   - La confirmation s'affiche une fois terminé

## Avantages de cette interface

- **Simplicité d'usage** : Pas besoin de connaître les paramètres des fonctions
- **Feedback visuel** : Résultats immédiats et formatés
- **Robustesse** : Gestion complète des erreurs
- **Performance** : Opérations en arrière-plan sans blocage
- **Intuitivité** : Interface claire avec boutons "Parcourir"

Cette interface transforme mes fonctions en ligne de commande en application graphique moderne et accessible à tous les utilisateurs.
