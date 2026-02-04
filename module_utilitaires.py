#!/usr/bin/env python3
"""
Module contenant toutes les procédures et fonctions créées précédemment.
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

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


def afficher_heure():
    """
    Fonction que j'ai créée pour afficher l'heure qu'il est actuellement.
    
    Cette fonction utilise le module datetime pour récupérer
    et afficher l'heure courante au format HH:MM:SS.
    
    Returns:
        str: L'heure actuelle au format HH:MM:SS
    """
    heure_actuelle = datetime.datetime.now()
    return heure_actuelle.strftime('%H:%M:%S')


def taille_fichier(chemin_fichier):
    """
    Fonction que j'ai développée pour donner la taille d'un fichier passé en paramètre.
    
    Args:
        chemin_fichier (str): Le chemin vers le fichier dont on veut connaître la taille
        
    Returns:
        int: La taille du fichier en octets, ou -1 si le fichier n'existe pas
    """
    try:
        if os.path.isfile(chemin_fichier):
            return os.path.getsize(chemin_fichier)
        else:
            return -1
    except Exception:
        return -1


def copier_repertoire(source, destination):
    """
    Fonction que j'ai implémentée pour copier tous les fichiers d'un répertoire et de tous ses sous-répertoires
    dans un autre répertoire.
    
    Args:
        source (str): Le répertoire source à copier
        destination (str): Le répertoire de destination
        
    Returns:
        bool: True si la copie s'est bien déroulée, False sinon
    """
    try:
        if not os.path.exists(source):
            return False
        
        if not os.path.isdir(source):
            return False
        
        os.makedirs(destination, exist_ok=True)
        
        for root, dirs, files in os.walk(source):
            for directory in dirs:
                chemin_source = os.path.join(root, directory)
                chemin_destination = os.path.join(destination, os.path.relpath(chemin_source, source))
                os.makedirs(chemin_destination, exist_ok=True)
            
            for fichier in files:
                chemin_source = os.path.join(root, fichier)
                chemin_destination = os.path.join(destination, os.path.relpath(chemin_source, source))
                shutil.copy2(chemin_source, chemin_destination)
        
        return True
        
    except Exception:
        return False


def creer_csv_fichiers(repertoire, nom_fichier_csv):
    """
    Procédure que j'ai créée pour créer un fichier CSV contenant la liste de tous les fichiers
    d'un répertoire passé en paramètre avec métadonnées.
    
    Args:
        repertoire (str): Le chemin du répertoire à analyser
        nom_fichier_csv (str): Le nom du fichier CSV à créer
        
    Returns:
        bool: True si le CSV a été créé avec succès, False sinon
    """
    try:
        if not os.path.exists(repertoire):
            return False
        
        if not os.path.isdir(repertoire):
            return False
        
        with open(nom_fichier_csv, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['nom_fichier', 'chemin_complet', 'taille_octets', 'date_creation', 'date_modification']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            
            for root, dirs, files in os.walk(repertoire):
                for fichier in files:
                    chemin_complet = os.path.join(root, fichier)
                    
                    stat_info = os.stat(chemin_complet)
                    taille = stat_info.st_size
                    date_creation = datetime.datetime.fromtimestamp(stat_info.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
                    date_modification = datetime.datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    
                    writer.writerow({
                        'nom_fichier': fichier,
                        'chemin_complet': chemin_complet,
                        'taille_octets': taille,
                        'date_creation': date_creation,
                        'date_modification': date_modification
                    })
        
        return True
        
    except Exception:
        return False


def liste_processus():
    """
    Fonction que j'ai développée pour renvoyer un dictionnaire contenant la liste des processus en exécution
    avec en clé l'ID du processus et en valeur le nom du processus.
    
    Returns:
        dict: Dictionnaire avec PID en clé et nom du processus en valeur
    """
    if not PSUTIL_AVAILABLE:
        return {}
    
    try:
        processus = {}
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                processus[proc.info['pid']] = proc.info['name']
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return processus
        
    except Exception:
        return {}


def ping_adresse(adresse, nb_ping=10):
    """
    Fonction que j'ai créée pour exécuter une commande ping sur une adresse et renvoyer le délai moyen.
    
    Args:
        adresse (str): L'adresse à pinger
        nb_ping (int): Le nombre de ping à effectuer (défaut: 10)
        
    Returns:
        str: Le délai moyen si succès, sinon le texte d'erreur
    """
    try:
        commande = ["ping", "-c", str(nb_ping), adresse]
        
        resultat = subprocess.run(commande, capture_output=True, text=True, timeout=30)
        
        if resultat.returncode == 0:
            for ligne in resultat.stdout.split('\n'):
                if 'avg' in ligne or 'moyenne' in ligne:
                    if '/' in ligne:
                        delai_moyen = ligne.split('/')[-2]
                        return f"Délai moyen : {delai_moyen} ms"
            
            return f"Ping réussi vers {adresse} ({nb_ping} paquets)"
        else:
            return f"Ping échoué vers {adresse}"
    
    except subprocess.TimeoutExpired:
        return f"Timeout lors du ping vers {adresse}"
    except Exception as e:
        return f"Erreur ping : {str(e)}"


def compresser_repertoire(repertoire, fichier_zip):
    """
    Procédure que j'ai implémentée pour compresser le contenu d'un répertoire dans un fichier ZIP.
    
    Args:
        repertoire (str): Le chemin complet du répertoire à compresser
        fichier_zip (str): Le nom du fichier ZIP à créer
        
    Returns:
        bool: True si la compression s'est bien déroulée, False sinon
    """
    try:
        if not os.path.exists(repertoire):
            return False
            
        if not os.path.isdir(repertoire):
            return False
        
        with zipfile.ZipFile(fichier_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(repertoire):
                for fichier in files:
                    chemin_fichier = os.path.join(root, fichier)
                    chemin_archive = os.path.relpath(chemin_fichier, repertoire)
                    zipf.write(chemin_fichier, chemin_archive)
        
        return True
        
    except Exception:
        return False


def meteo(commune):
    """
    Fonction que j'ai développée pour renvoyer une chaîne de caractère au format JSON qui contient la
    météo d'une commune passée en paramètre.
    
    Args:
        commune (str): Le nom de la commune
        
    Returns:
        str: Les données météo au format JSON, ou message d'erreur
    """
    if not REQUESTS_AVAILABLE:
        return json.dumps({"erreur": "Le module requests n'est pas installé"})
    
    try:
        url = f"http://wttr.in/{commune}?format=j1"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            donnees = response.json()
            
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
    Procédure que j'ai créée pour découper un fichier de n'importe quel type en plusieurs fichiers.
    Le chemin, le nom du fichier ainsi que le nombre de morceaux sont passés en paramètre.
    
    Args:
        chemin_fichier (str): Le chemin complet vers le fichier à découper
        nb_morceaux (int): Le nombre de morceaux souhaités
        
    Returns:
        bool: True si le découpage s'est bien déroulé, False sinon
    """
    try:
        if not os.path.isfile(chemin_fichier):
            return False
            
        if nb_morceaux <= 0:
            return False
        
        taille_fichier_total = os.path.getsize(chemin_fichier)
        
        if taille_fichier_total == 0:
            return False
            
        taille_morceau = taille_fichier_total // nb_morceaux
        reste = taille_fichier_total % nb_morceaux
        
        chemin_base = os.path.splitext(chemin_fichier)[0]
        extension = os.path.splitext(chemin_fichier)[1]
        
        with open(chemin_fichier, 'rb') as fichier_source:
            for i in range(nb_morceaux):
                if i == nb_morceaux - 1:
                    taille_actuelle = taille_morceau + reste
                else:
                    taille_actuelle = taille_morceau
                
                nom_morceau = f"{chemin_base}_{i+1}{extension}"
                
                with open(nom_morceau, 'wb') as fichier_morceau:
                    data = fichier_source.read(taille_actuelle)
                    fichier_morceau.write(data)
        
        return True
        
    except Exception:
        return False


def reconstituer_fichier(chemin_fichier_base, nb_morceaux):
    """
    Procédure que j'ai implémentée pour reconstituer un fichier à partir de ses morceaux.
    
    Args:
        chemin_fichier_base (str): Le chemin de base du fichier (sans le numéro de morceau)
        nb_morceaux (int): Le nombre de morceaux à reconstituer
        
    Returns:
        bool: True si la reconstitution s'est bien déroulée, False sinon
    """
    try:
        chemin_base = os.path.splitext(chemin_fichier_base)[0]
        extension = os.path.splitext(chemin_fichier_base)[1]
        
        for i in range(1, nb_morceaux + 1):
            nom_morceau = f"{chemin_base}_{i}{extension}"
            if not os.path.isfile(nom_morceau):
                return False
        
        with open(chemin_fichier_base, 'wb') as fichier_final:
            for i in range(1, nb_morceaux + 1):
                nom_morceau = f"{chemin_base}_{i}{extension}"
                
                with open(nom_morceau, 'rb') as fichier_morceau:
                    data = fichier_morceau.read()
                    fichier_final.write(data)
        
        return True
        
    except Exception:
        return False