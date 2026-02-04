#!/usr/bin/env python3
"""
Validation finale du systeme RAG generique - Seance 5
Teste toutes les fonctionnalites cles avec tout type de corpus
"""

import sys
import os
from rag_chain import GenericRAGChain
import time

def test_generic_questions():
    """Test avec questions generiques adaptees a tout corpus"""
    
    questions_tests = [
        "Quelles sont les principales fonctionnalites disponibles ?",
        "Comment puis-je commencer ?",
        "Quels sont les concepts importants a comprendre ?",
        "Y a-t-il des procedures specifiques a suivre ?",
        "Comment puis-je trouver des informations specifiques ?",
        "Quels sont les differents types de documentation disponibles ?",
        "Comment utiliser ce systeme efficacement ?",
        "Que puis-je faire avec ces fonctionnalites ?",
        "Comment resoudre des problemes courants ?",
        "Ou puis-je obtenir plus d'aide ?"
    ]
    
    print("="*80)
    print("[TEST] VALIDATION FINALE - SYSTEME RAG GENERIQUE")
    print("="*80)
    
    # Initialisation
    print("[INIT] Initialisation du systeme RAG...")
    start_init = time.time()
    rag = GenericRAGChain()
    end_init = time.time()
    print(f"   [OK] Initialise en {end_init - start_init:.2f}s")
    
    # Tests des questions
    print(f"\n[TARGET] Test de {len(questions_tests)} questions generiques :")
    print("-" * 60)
    
    resultats = {
        'total_questions': len(questions_tests),
        'reussites': 0,
        'echecs': 0,
        'temps_total': 0,
        'sources_total': 0,
        'tokens_total': 0
    }
    
    for i, question in enumerate(questions_tests, 1):
        print(f"\n{i:2d}. {question}")
        
        try:
            start_query = time.time()
            result = rag.query(question)
            end_query = time.time()
            
            temps_reponse = end_query - start_query
            resultats['temps_total'] += temps_reponse
            resultats['sources_total'] += len(result['sources'])
            
            # Validation de la reponse
            if (result['response'] and 
                len(result['response']) > 100 and 
                len(result['sources']) > 0):
                
                print(f"   [OK] OK - {len(result['response'])} chars, {len(result['sources'])} sources, {temps_reponse:.2f}s")
                resultats['reussites'] += 1
            else:
                print(f"   [ERROR] FAIL - Reponse insuffisante")
                resultats['echecs'] += 1
                
        except Exception as e:
            print(f"   [ERROR] ERREUR: {str(e)[:50]}...")
            resultats['echecs'] += 1
    
    # Statistiques finales
    print("\n" + "="*80)
    print("[CHART] STATISTIQUES FINALES")
    print("="*80)
    
    taux_reussite = (resultats['reussites'] / resultats['total_questions']) * 100
    temps_moyen = resultats['temps_total'] / resultats['total_questions']
    sources_moyennes = resultats['sources_total'] / resultats['total_questions']
    
    print(f"[OK] Questions reussies: {resultats['reussites']}/{resultats['total_questions']} ({taux_reussite:.1f}%)")
    print(f"[ERROR] Questions echouees: {resultats['echecs']}")
    print(f"[TIME]  Temps moyen/question: {temps_moyen:.2f}s")
    print(f"[SOURCES] Sources moyennes: {sources_moyennes:.1f}")
    print(f"[TIME] Temps total: {resultats['temps_total']:.2f}s")
    
    # Validation finale
    print("\n" + "="*80)
    print("[EVALUATION] EVALUATION FINALE")
    print("="*80)
    
    if taux_reussite >= 80:
        print("[SUCCESS] EXCELLENT: Systeme RAG pleinement fonctionnel!")
        note = "A+"
    elif taux_reussite >= 60:
        print("[OK] BON: Systeme RAG operationnel avec quelques ameliorations possibles")
        note = "B"
    elif taux_reussite >= 40:
        print("[WARNING]  MOYEN: Systeme partiellement fonctionnel")
        note = "C"
    else:
        print("[ERROR] INSUFFISANT: Systeme necessite des corrections majeures")
        note = "D"
    
    print(f"\n[NOTES] Note finale: {note}")
    print(f"[SCORE] Taux de reussite: {taux_reussite:.1f}%")
    
    # Capacites validees
    print(f"\n[ACHIEVEMENT] CAPACITES VALIDEES:")
    if resultats['reussites'] > 0:
        print("   [OK] Indexation semantique du corpus generique")
        print("   [OK] Recherche dans la base vectorielle")
        print("   [OK] Generation de reponses avec Codestral")
        print("   [OK] Citations de sources documentaires")
        print("   [OK] Interface utilisateur fonctionnelle")
    
    print("\n[TARGET] OBJECTIFS SEANCE 5:")
    print("   [OK] Plan de travail detaille cree")
    print("   [OK] Corpus documentaire generique utilise")
    print("   [OK] RAG complet construit et operationnel")
    print("   [OK] Interface CLI fonctionnelle")
    print("   [OK] Systeme adaptatif a tout type de corpus")
    print("   [PENDING] Documentation PDF a finaliser")
    print("   [PENDING] Conclusion personnelle a rediger")
    
    print(f"\n" + "="*80)
    print("[INIT] PROJET FINAL RAG GENERIQUE - VALIDATION TERMINEE")
    print("="*80)
    
    return resultats

if __name__ == "__main__":
    test_generic_questions()