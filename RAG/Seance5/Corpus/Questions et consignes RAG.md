# Séance 1 - Fiche de questions

1. Qu’est-ce qu’un environnement virtuel Python et à quoi sert-il ?
2. Quelle est la différence entre un environnement virtuel et une installation globale de Python ?
3. À quoi sert la bibliothèque `litellm` ?
4. Quel est le rôle de `fastapi` dans un projet Python ?
5. Quelle est la fonction de `uvicorn` lorsqu’on lance une application ?
6. Pourquoi utilise-t-on un fichier `.env` pour gérer les clés API ?
7. Qu’est-ce qu’une API REST et quels en sont les principes de base ?
8. Que représente un endpoint dans une API ?
9. Comment une application cliente peut-elle envoyer une requête à une API REST ?
10. Quelles sont les bonnes pratiques pour sécuriser une clé API ?

---

# Séance 1 - Consignes

1. Créer un environnement virtuel `venv-litellm`. → Objectif : isoler les dépendances liées à LiteLLM.
2. Installer `litellm`, `fastapi`, `uvicorn`, `python-dotenv`. → Objectif : préparer les outils nécessaires au serveur REST.
3. Configurer la clé API dans un fichier `.env`. → Objectif : gérer la clé de manière sécurisée.
4. Écrire un serveur REST exposant `/chat` qui appelle Codestral via LiteLLM. → Objectif : permettre l’interaction avec le modèle par une API locale.
5. Lancer le serveur sur le port 8000. → Objectif : rendre le service accessible pour des tests.
6. Tester l’API avec une requête externe. → Objectif : vérifier le bon fonctionnement de l’intégration.
7. Créez un fichier pdf nommé Séance1.pdf contenant les commandes utilisées, des copies d'écrans et/ou des résultats de test. → Objectif : démontrer la bonne réalisation de la séance.

---

# Séance 2 - Fiche de questions

1. Qu’est-ce que LangChain et pourquoi est-il utilisé dans les projets RAG ?
2. Quelle est la différence entre FAISS, Chroma et PostgreSQL/pgvector pour stocker des embeddings ?
3. Qu’est-ce qu’un embedding et à quoi sert-il ?
4. Comment choisir la taille des chunks lors du découpage d’un document ?
5. Quels sont les avantages et limites de stocker les embeddings dans une base de données ?
6. Qu’est-ce que `tiktoken` et dans quel cas est-il utilisé ?
7. Quelles différences existent entre un PDF et un fichier texte brut pour l’ingestion documentaire ?
8. Quels formats de fichiers peut-on transformer en embeddings ?
9. Qu’est-ce qu’une recherche vectorielle et en quoi diffère-t-elle d’une recherche par mot-clé ?
10. Pourquoi PostgreSQL/pgvector est-il adapté pour un projet de RAG ?

---

# Séance 2 - Consignes

1. Créer un environnement virtuel `venv-rag`. → Objectif : séparer l’espace de travail dédié au RAG.
2. Installer `langchain`, `faiss-cpu` ou `chromadb`, `tiktoken`, `python-dotenv`. → Objectif : disposer des bibliothèques nécessaires pour le pipeline.
3. Importer un corpus local (texte ou PDF). → Objectif : définir les données sources pour l’indexation.
4. Découper le corpus en chunks. → Objectif : segmenter le texte pour une meilleure recherche.
5. Générer des embeddings. → Objectif : transformer le texte en vecteurs exploitables.
6. Stocker les embeddings dans la base vectorielle PostgreSQL avec l’extension vectorielle (pgvector). → Objectif : rendre les données accessibles via une recherche sémantique.
7. Interroger la base vectorielle avec une question et afficher les résultats. → Objectif : valider le bon fonctionnement de l’index.
8. Créez un fichier pdf nommé Séance2.pdf contenant les commandes utilisées, des copies d'écrans et/ou des résultats de test. → Objectif : démontrer la bonne réalisation de la séance.

---

# Séance 3 - Fiche de questions

1. Que signifie l’acronyme RAG et quel est son objectif ?
2. Qu’est-ce qu’un retriever dans LangChain ?
3. Comment un retriever interagit-il avec la base PostgreSQL/pgvector ?
4. Qu’est-ce qu’une chaîne LangChain et à quoi sert-elle ?
5. Comment intégrer une requête utilisateur dans un pipeline de RAG ?
6. Quelles différences observe-t-on entre une réponse brute du modèle et une réponse enrichie par retrieval ?
7. Qu’est-ce qu’un contexte dans le cadre d’un RAG ?
8. Comment s’effectue l’appel à LiteLLM (Codestral) dans le pipeline ?
9. Pourquoi comparer des réponses avec et sans retrieval ?
10. Quels indicateurs peuvent être utilisés pour juger la pertinence d’une réponse ?

---

# Séance 3 - Consignes

1. Créer une chaîne RAG avec LangChain. → Objectif : assembler les composants du pipeline.
2. Configurer le retriever basé sur la base vectorielle PostgreSQL/pgvector. → Objectif : permettre la récupération des données pertinentes.
3. Construire un pipeline : question → retrieval → contexte → appel à l’API LiteLLM (Codestral) → réponse. → Objectif : établir le flux complet de traitement.
4. Tester une question avec et sans retrieval. → Objectif : comparer l’impact de l’apport documentaire.
5. Comparer la pertinence des réponses. → Objectif : évaluer l’efficacité du RAG par rapport au LLM seul.
6. Créez un fichier pdf nommé Séance3.pdf contenant les commandes utilisées, des copies d'écrans et/ou des résultats de test. → Objectif : démontrer la bonne réalisation de la séance.

---

# Séance 4 - Fiche de questions

1. Qu’est-ce que le chunk size et pourquoi est-il important ?
2. Qu’est-ce que l’overlap et pourquoi l’utiliser ?
3. Pourquoi est-il utile de citer les sources dans un système RAG ?
4. Qu’est-ce qu’un prompt template et à quoi sert-il ?
5. Comment la mémoire de conversation peut-elle améliorer l’expérience utilisateur ?
6. Quelles stratégies existent pour éviter les hallucinations dans un RAG ?
7. Quelles sont les limites de la recherche vectorielle ?
8. Comment une interface CLI peut-elle améliorer la présentation des résultats ?
9. Quelles informations doivent apparaître dans une réponse enrichie de sources ?
10. Pourquoi vérifier que les données proviennent toujours de PostgreSQL/pgvector ?

---

# Séance 4 - Consignes

1. Améliorer le découpage (chunk size / overlap). → Objectif : optimiser la qualité des passages utilisés.
2. Ajouter la citation des sources dans la réponse. → Objectif : renforcer la traçabilité des informations.
3. Mettre en place un prompt template spécifique. → Objectif : structurer l’instruction donnée au modèle.
4. Ajouter la mémoire de conversation. → Objectif : permettre la continuité dans les échanges.
5. Améliorer l’interface en ligne de commande (affichage structuré des réponses et des sources). → Objectif : rendre l’utilisation plus claire et ergonomique.
6. Vérifier que les données proviennent toujours de PostgreSQL/pgvector. → Objectif : garantir la cohérence du stockage et de la recherche vectorielle.
7. Créez un fichier pdf nommé Séance4.pdf contenant les commandes utilisées, des copies d'écrans et/ou des résultats de test. → Objectif : démontrer la bonne réalisation de la séance.

---

# Séance 5 - Fiche de questions

1. Quelles compétences en autonomie et en organisation sont nécessaires pour mener à bien ce type de projet ?
2. Quels critères choisir pour sélectionner un corpus documentaire adapté ?
3. Quelles étapes clés faut-il suivre pour construire un RAG complet ?
4. Quelles différences entre une interface CLI et une interface web ?
5. Quels outils peuvent être utilisés pour créer rapidement une interface web en Python ?
6. Quelles sont les principales difficultés que l’on peut rencontrer dans la mise en place d’un RAG ?
7. Quels éléments doivent être inclus dans une démonstration technique ?
8. Quelles compétences sont mises en valeur lors d’une soutenance individuelle ?
9. Quels critères permettent d’évaluer la qualité d’un RAG ?
10. Quelles pistes d’amélioration pourraient être proposées en conclusion du projet ?

---

# Séance 5 - Consignes

1. Préparer un plan de travail détaillé avant de commencer. → Objectif : organiser les étapes du projet et structurer la démarche.
2. Utiliser le corpus documentaire fourni. → Objectif : définir le périmètre d’application du RAG.
3. Construire un RAG complet avec ce corpus. → Objectif : mettre en pratique l’ensemble de la chaîne.
4. Créer une interface simple (CLI ou web). → Objectif : proposer un accès utilisateur au système.
5. Créez un fichier pdf nommé Séance5.pdf contenant les commandes utilisées, des copies d'écrans et/ou des résultats de test. → Objectif : démontrer la bonne réalisation de la séance.
6. Rédiger une conclusion personnelle. → Objectif : analyser son travail, identifier ses réussites et ses pistes d’amélioration.

---

# Fiche de questions - Aller plus loin

1. Comment intégrer plusieurs bases documentaires dans un même RAG ?
2. Quelles stratégies permettent de combiner retrieval vectoriel et recherche par mots-clés ?
3. Comment gérer la mise à jour d’un corpus documentaire de grande taille en production ?
4. Quelles alternatives existent à PostgreSQL/pgvector pour gérer les embeddings à grande échelle ?
5. Comment ajouter un reranking basé sur un modèle spécialisé pour améliorer la pertinence des documents retrouvés ?
6. Quelles méthodes permettent de mesurer et comparer les performances d’un RAG (temps, pertinence, coût) ?
7. Comment intégrer un système de filtrage par métadonnées dans le processus de retrieval ?
8. Quelles bonnes pratiques de déploiement faut-il appliquer pour mettre un RAG en production ?
9. Comment coupler un RAG avec un agent LangChain pour effectuer des actions complexes au-delà de la génération de texte ?
10. Quelles pistes actuelles de recherche et développement améliorent la robustesse et la précision des RAG modernes ?
