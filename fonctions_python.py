#!/usr/bin/env python3
"""
Programme Python avec trois fonctions principales
"""

import csv
import datetime
import json
import os
import shutil
import subprocess
import zipfile
from pathlib import Path

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("ATTENTION: Le module requests n'est pas installé. La fonction meteo() ne sera pas disponible.")
    print("Pour l'installer: pip install requests")

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("ATTENTION: Le module psutil n'est pas installé. La fonction liste_processus() ne sera pas disponible.")
    print("Pour l'installer: pip install psutil")


def afficher_heure():
    """
    Fonction qui affiche l'heure qu'il est actuellement.
    
    Cette fonction utilise le module datetime pour récupérer
    et afficher l'heure courante au format HH:MM:SS.
    """
    heure_actuelle = datetime.datetime.now()
    print(f"Il est actuellement : {heure_actuelle.strftime('%H:%M:%S')}")
    return heure_actuelle.strftime('%H:%M:%S')


def taille_fichier(chemin_fichier):
    """
    Fonction qui donne la taille d'un fichier passé en paramètre.
    
    Args:
        chemin_fichier (str): Le chemin vers le fichier dont on veut connaître la taille
        
    Returns:
        int: La taille du fichier en octets, ou -1 si le fichier n'existe pas
    """
    try:
        if os.path.isfile(chemin_fichier):
            taille = os.path.getsize(chemin_fichier)
            print(f"Le fichier '{chemin_fichier}' fait {taille} octets")
            return taille
        else:
            print(f"Erreur : Le fichier '{chemin_fichier}' n'existe pas")
            return -1
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier : {e}")
        return -1


def copier_repertoire(source, destination):
    """
    Fonction qui copie tous les fichiers d'un répertoire et de tous ses sous-répertoires
    dans un autre répertoire.
    
    Args:
        source (str): Le répertoire source à copier
        destination (str): Le répertoire de destination
        
    Returns:
        bool: True si la copie s'est bien déroulée, False sinon
    """
    try:
        # Vérifier que le répertoire source existe
        if not os.path.exists(source):
            print(f"Erreur : Le répertoire source '{source}' n'existe pas")
            return False
            
        if not os.path.isdir(source):
            print(f"Erreur : '{source}' n'est pas un répertoire")
            return False
        
        # Créer le répertoire de destination s'il n'existe pas
        os.makedirs(destination, exist_ok=True)
        
        # Copier récursivement tout le contenu
        for element in os.listdir(source):
            chemin_source = os.path.join(source, element)
            chemin_destination = os.path.join(destination, element)
            
            if os.path.isdir(chemin_source):
                # Si c'est un répertoire, copier récursivement
                shutil.copytree(chemin_source, chemin_destination, dirs_exist_ok=True)
                print(f"Répertoire copié : {chemin_source} -> {chemin_destination}")
            else:
                # Si c'est un fichier, le copier
                shutil.copy2(chemin_source, chemin_destination)
                print(f"Fichier copié : {chemin_source} -> {chemin_destination}")
        
        print(f"Copie terminée avec succès de '{source}' vers '{destination}'")
        return True
        
    except Exception as e:
        print(f"Erreur lors de la copie : {e}")
        return False


def creer_csv_fichiers(repertoire, nom_fichier_csv):
    """
    Procédure qui crée un fichier CSV contenant la liste de tous les fichiers
    d'un répertoire passé en paramètre avec métadonnées.
    
    Args:
        repertoire (str): Le chemin du répertoire à analyser
        nom_fichier_csv (str): Le nom du fichier CSV à créer
        
    Returns:
        bool: True si le CSV a été créé avec succès, False sinon
    """
    try:
        if not os.path.exists(repertoire):
            print(f"Erreur : Le répertoire '{repertoire}' n'existe pas")
            return False
            
        if not os.path.isdir(repertoire):
            print(f"Erreur : '{repertoire}' n'est pas un répertoire")
            return False
        
        with open(nom_fichier_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(['Nom_fichier', 'Chemin_complet', 'Date_creation', 'Date_modification', 'Taille_octets'])
            
            for root, dirs, files in os.walk(repertoire):
                for fichier in files:
                    chemin_complet = os.path.join(root, fichier)
                    try:
                        stats = os.stat(chemin_complet)
                        date_creation = datetime.datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
                        date_modification = datetime.datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                        taille = stats.st_size
                        
                        writer.writerow([fichier, chemin_complet, date_creation, date_modification, taille])
                    except Exception as e:
                        print(f"Erreur lors de l'analyse du fichier {chemin_complet}: {e}")
                        continue
        
        print(f"Fichier CSV créé avec succès : {nom_fichier_csv}")
        return True
        
    except Exception as e:
        print(f"Erreur lors de la création du CSV : {e}")
        return False


def liste_processus():
    """
    Fonction qui renvoie un dictionnaire contenant la liste des processus en exécution
    avec en clé l'ID du processus et en valeur le nom du processus.
    
    Returns:
        dict: Dictionnaire {pid: nom_processus}
    """
    if not PSUTIL_AVAILABLE:
        print("Erreur : Le module psutil n'est pas installé. Impossible de lister les processus.")
        return {}
    
    try:
        processus = {}
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                processus[proc.info['pid']] = proc.info['name']
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        print(f"Nombre de processus trouvés : {len(processus)}")
        return processus
        
    except Exception as e:
        print(f"Erreur lors de la récupération des processus : {e}")
        return {}


def ping_adresse(adresse, nb_ping=10):
    """
    Fonction qui exécute une commande ping sur une adresse et renvoie le délai moyen.
    
    Args:
        adresse (str): L'adresse à pinger
        nb_ping (int): Le nombre de ping à effectuer (défaut: 10)
        
    Returns:
        str: Le délai moyen si succès, sinon le texte d'erreur
    """
    try:
        # Commande ping selon l'OS
        commande = ['ping', '-c', str(nb_ping), adresse]
        if os.name == 'nt':  # Windows
            commande = ['ping', '-n', str(nb_ping), adresse]
        
        resultat = subprocess.run(commande, capture_output=True, text=True, timeout=30)
        
        if resultat.returncode == 0:
            # Analyser la sortie pour extraire le délai moyen
            lignes = resultat.stdout.split('\n')
            for ligne in lignes:
                if 'avg' in ligne.lower() or 'moyenne' in ligne.lower():
                    # Extraction du délai moyen selon le format
                    if 'avg' in ligne.lower():
                        # Format Linux: rtt min/avg/max/mdev = 12.345/23.456/34.567/8.901 ms
                        parties = ligne.split('=')[1].strip().split('/')
                        delai_moyen = parties[1]
                        return f"Délai moyen : {delai_moyen} ms"
                    elif 'moyenne' in ligne.lower():
                        # Format Windows
                        return ligne.strip()
            
            # Si pas de ligne avec avg/moyenne trouvée, retourner un message générique
            return f"Ping réussi vers {adresse} ({nb_ping} paquets)"
        else:
            return f"Erreur ping : {resultat.stderr.strip()}"
            
    except subprocess.TimeoutExpired:
        return f"Timeout : Le ping vers {adresse} a pris trop de temps"
    except Exception as e:
        return f"Erreur lors du ping : {str(e)}"


def compresser_repertoire(repertoire, fichier_zip):
    """
    Procédure qui compresse le contenu d'un répertoire dans un fichier ZIP.
    
    Args:
        repertoire (str): Le chemin complet du répertoire à compresser
        fichier_zip (str): Le nom du fichier ZIP à créer
        
    Returns:
        bool: True si la compression s'est bien déroulée, False sinon
    """
    try:
        if not os.path.exists(repertoire):
            print(f"Erreur : Le répertoire '{repertoire}' n'existe pas")
            return False
            
        if not os.path.isdir(repertoire):
            print(f"Erreur : '{repertoire}' n'est pas un répertoire")
            return False
        
        with zipfile.ZipFile(fichier_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(repertoire):
                for fichier in files:
                    chemin_fichier = os.path.join(root, fichier)
                    # Calculer le chemin relatif pour l'archive
                    chemin_archive = os.path.relpath(chemin_fichier, repertoire)
                    zipf.write(chemin_fichier, chemin_archive)
                    print(f"Ajouté à l'archive : {chemin_archive}")
        
        print(f"Compression terminée avec succès : {fichier_zip}")
        return True
        
    except Exception as e:
        print(f"Erreur lors de la compression : {e}")
        return False


def meteo(commune):
    """
    Fonction qui renvoie une chaîne de caractère au format JSON qui contient la
    météo d'une commune passée en paramètre.
    
    Args:
        commune (str): Le nom de la commune
        
    Returns:
        str: Les données météo au format JSON, ou message d'erreur
    """
    if not REQUESTS_AVAILABLE:
        return json.dumps({"erreur": "Le module requests n'est pas installé"})
    
    try:
        # J'utilise l'API gratuite OpenWeatherMap (nécessite une clé API gratuite)
        # Pour cet exemple, j'utilise wttr.in qui ne nécessite pas de clé
        url = f"http://wttr.in/{commune}?format=j1"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            donnees = response.json()
            
            # Je structure les données météo importantes
            meteo_info = {
                "commune": commune,
                "temperature_celsius": donnees["current_condition"][0]["temp_C"],
                "description": donnees["current_condition"][0]["weatherDesc"][0]["value"],
                "humidite": donnees["current_condition"][0]["humidity"],
                "vitesse_vent_kmh": donnees["current_condition"][0]["windspeedKmph"],
                "pression": donnees["current_condition"][0]["pressure"],
                "visibilite_km": donnees["current_condition"][0]["visibility"]
            }
            
            return json.dumps(meteo_info, ensure_ascii=False, indent=2)
            
        else:
            return json.dumps({"erreur": f"Impossible de récupérer la météo pour {commune}"})
            
    except Exception as e:
        return json.dumps({"erreur": f"Erreur lors de la récupération météo : {str(e)}"})


def decouper_fichier(chemin_fichier, nb_morceaux):
    """
    Procédure qui découpe un fichier de n'importe quel type en plusieurs fichiers.
    Le chemin, le nom du fichier ainsi que le nombre de morceaux sont passés en paramètre.
    
    Args:
        chemin_fichier (str): Le chemin complet vers le fichier à découper
        nb_morceaux (int): Le nombre de morceaux souhaités
        
    Returns:
        bool: True si le découpage s'est bien déroulé, False sinon
    """
    try:
        if not os.path.isfile(chemin_fichier):
            print(f"Erreur : Le fichier '{chemin_fichier}' n'existe pas")
            return False
            
        if nb_morceaux <= 0:
            print("Erreur : Le nombre de morceaux doit être supérieur à 0")
            return False
        
        taille_fichier_total = os.path.getsize(chemin_fichier)
        
        if taille_fichier_total == 0:
            print("Erreur : Le fichier est vide")
            return False
            
        # Je calcule la taille de chaque morceau
        taille_morceau = taille_fichier_total // nb_morceaux
        reste = taille_fichier_total % nb_morceaux
        
        # Je récupère le nom de base du fichier sans extension
        chemin_base = os.path.splitext(chemin_fichier)[0]
        extension = os.path.splitext(chemin_fichier)[1]
        
        with open(chemin_fichier, 'rb') as fichier_source:
            for i in range(nb_morceaux):
                # Je détermine la taille de ce morceau
                if i == nb_morceaux - 1:  # Dernier morceau
                    taille_actuelle = taille_morceau + reste
                else:
                    taille_actuelle = taille_morceau
                
                # Je crée le nom du fichier morceau
                nom_morceau = f"{chemin_base}_{i+1}{extension}"
                
                # Je lis et écris ce morceau
                with open(nom_morceau, 'wb') as fichier_morceau:
                    data = fichier_source.read(taille_actuelle)
                    fichier_morceau.write(data)
                
                print(f"Morceau créé : {nom_morceau} ({taille_actuelle} octets)")
        
        print(f"Découpage terminé avec succès : {nb_morceaux} morceaux créés")
        return True
        
    except Exception as e:
        print(f"Erreur lors du découpage : {e}")
        return False


def reconstituer_fichier(chemin_fichier_base, nb_morceaux):
    """
    Procédure qui reconstitue un fichier à partir de ses morceaux.
    
    Args:
        chemin_fichier_base (str): Le chemin de base du fichier (sans le numéro de morceau)
        nb_morceaux (int): Le nombre de morceaux à reconstituer
        
    Returns:
        bool: True si la reconstitution s'est bien déroulée, False sinon
    """
    try:
        # Je récupère le nom de base et l'extension
        chemin_base = os.path.splitext(chemin_fichier_base)[0]
        extension = os.path.splitext(chemin_fichier_base)[1]
        
        # Je vérifie que tous les morceaux existent
        for i in range(1, nb_morceaux + 1):
            nom_morceau = f"{chemin_base}_{i}{extension}"
            if not os.path.isfile(nom_morceau):
                print(f"Erreur : Le morceau '{nom_morceau}' n'existe pas")
                return False
        
        # Je reconstitue le fichier
        with open(chemin_fichier_base, 'wb') as fichier_final:
            for i in range(1, nb_morceaux + 1):
                nom_morceau = f"{chemin_base}_{i}{extension}"
                
                with open(nom_morceau, 'rb') as fichier_morceau:
                    data = fichier_morceau.read()
                    fichier_final.write(data)
                
                print(f"Morceau ajouté : {nom_morceau}")
        
        print(f"Reconstitution terminée avec succès : {chemin_fichier_base}")
        return True
        
    except Exception as e:
        print(f"Erreur lors de la reconstitution : {e}")
        return False


if __name__ == "__main__":
    print("=== Test des fonctions Python ===\n")
    
    # Test de la fonction afficher_heure
    print("1. Test de la fonction afficher_heure :")
    afficher_heure()
    print()
    
    # Test de la fonction taille_fichier
    print("2. Test de la fonction taille_fichier :")
    taille_fichier(__file__)  # Taille du fichier actuel
    taille_fichier("fichier_inexistant.txt")  # Test avec un fichier inexistant
    print()
    
    # Test de la fonction copier_repertoire
    print("3. Test de la fonction copier_repertoire :")
    # Créer un répertoire de test avec quelques fichiers
    test_dir = "test_source"
    dest_dir = "test_destination"
    
    # Nettoyer les répertoires de test s'ils existent
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)
    
    # Créer une structure de test
    os.makedirs(os.path.join(test_dir, "sous_repertoire"), exist_ok=True)
    
    # Créer quelques fichiers de test
    with open(os.path.join(test_dir, "fichier1.txt"), "w") as f:
        f.write("Contenu du fichier 1")
    
    with open(os.path.join(test_dir, "sous_repertoire", "fichier2.txt"), "w") as f:
        f.write("Contenu du fichier 2 dans le sous-répertoire")
    
    # Tester la copie
    copier_repertoire(test_dir, dest_dir)
    print()
    
    # Test de la fonction creer_csv_fichiers
    print("4. Test de la fonction creer_csv_fichiers :")
    creer_csv_fichiers(test_dir, "liste_fichiers.csv")
    print()
    
    # Test de la fonction liste_processus
    print("5. Test de la fonction liste_processus :")
    processus = liste_processus()
    if processus:
        print(f"Nombre de processus trouvés : {len(processus)}")
        print("Exemples de processus (5 premiers) :")
        for i, (pid, nom) in enumerate(list(processus.items())[:5]):
            print(f"  PID {pid}: {nom}")
    print()
    
    # Test de la fonction ping_adresse
    print("6. Test de la fonction ping_adresse :")
    resultat_ping = ping_adresse("8.8.8.8", 4)
    print(f"Résultat ping : {resultat_ping}")
    print()
    
    # Test de la fonction compresser_repertoire
    print("7. Test de la fonction compresser_repertoire :")
    compresser_repertoire(test_dir, "archive_test.zip")
    print()
    
    # Test de la fonction meteo
    print("8. Test de la fonction meteo :")
    if REQUESTS_AVAILABLE:
        meteo_paris = meteo("Paris")
        print("Météo de Paris :")
        print(meteo_paris)
    else:
        print("Module requests non disponible pour tester la météo")
    print()
    
    # Test des fonctions de découpage/reconstitution
    print("9. Test des fonctions de découpage et reconstitution :")
    fichier_test = "test_decoupage.txt"
    
    # Créer un fichier de test
    with open(fichier_test, "w") as f:
        f.write("Ceci est un fichier de test pour le découpage.\n" * 100)
    
    print(f"Fichier créé : {fichier_test}")
    
    # Découper le fichier
    if decouper_fichier(fichier_test, 3):
        print("Découpage réussi")
        
        # Supprimer le fichier original
        os.remove(fichier_test)
        
        # Reconstituer le fichier
        if reconstituer_fichier(fichier_test, 3):
            print("Reconstitution réussie")
            
            # Nettoyer les morceaux
            for i in range(1, 4):
                nom_morceau = f"test_decoupage_{i}.txt"
                if os.path.exists(nom_morceau):
                    os.remove(nom_morceau)
        else:
            print("Erreur lors de la reconstitution")
    else:
        print("Erreur lors du découpage")
    
    # Nettoyer le fichier de test
    if os.path.exists(fichier_test):
        os.remove(fichier_test)