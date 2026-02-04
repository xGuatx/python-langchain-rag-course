"""
API Flask pour systeme RAG generique - Seance 5
Endpoints pour l'interface web du systeme RAG universel
Compatible avec toute documentation fournie
"""

import os
import sys
import json
from datetime import datetime
from flask import Blueprint, request, jsonify
from typing import Dict, Any, List

# Ajouter le chemin parent pour importer les modules RAG generiques
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

try:
    from rag_chain import RAGChain, PostgreSQLRAGSystem
    print("RAG Chain LangChain charge avec succes")
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    print(f"Erreur d'import: {e}")
    RAGChain = None
    PostgreSQLRAGSystem = None
    LANGCHAIN_AVAILABLE = False

# Blueprint generique pour tout systeme RAG
rag_bp = Blueprint('rag', __name__)

# Instance globale du systeme RAG (initialisee au demarrage)
rag_system = None
indexer_system = None
initialization_error = None

def initialize_rag_system():
    """Initialiser le systeme RAG au demarrage de l'application"""
    global rag_system, initialization_error
    try:
        if LANGCHAIN_AVAILABLE and PostgreSQLRAGSystem:
            print("[STARTUP] Initialisation du systeme RAG Seance 5 avec LangChain + PostgreSQL...")
            rag_system = PostgreSQLRAGSystem("web_session")
            print("[STARTUP] Systeme RAG pret a recevoir des requetes")
        elif RAGChain:
            print("[STARTUP] Fallback sur RAGChain")
            rag_system = RAGChain("web_session")
        else:
            initialization_error = "Aucun systeme RAG disponible"
    except Exception as e:
        initialization_error = f"Erreur lors de l'initialisation du RAG: {e}"
        print(f"[ERROR] {initialization_error}")
        
def get_rag_system():
    """Obtenir l'instance du systeme RAG (deja initialisee)"""
    global rag_system, initialization_error
    if initialization_error:
        print(f"[ERROR] Systeme RAG non disponible: {initialization_error}")
        return None
    return rag_system

# Initialiser le systeme RAG au chargement du module
if LANGCHAIN_AVAILABLE:
    initialize_rag_system()

def get_indexer_system():
    """L'indexeur est integre dans le systeme RAG PostgreSQL"""
    # Pas besoin d'indexeur separe, la recherche se fait via PostgreSQL
    return get_rag_system()

@rag_bp.route('/health', methods=['GET'])
def health_check():
    """Verifier l'etat du systeme"""
    try:
        rag = get_rag_system()
        indexer = get_indexer_system()
        
        status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'components': {
                'rag_system': rag is not None,
                'indexer_system': indexer is not None,
                'database': True  # Simplifie pour la demo
            }
        }
        
        return jsonify(status), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@rag_bp.route('/query', methods=['POST'])
def query_rag():
    """Traiter une requete RAG"""
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({
                'error': 'Question manquante dans la requete',
                'success': False
            }), 400
        
        question = data['question'].strip()
        if not question:
            return jsonify({
                'error': 'Question vide',
                'success': False
            }), 400
        
        # Parametres optionnels
        max_sources = data.get('max_sources', 5)
        include_conversation = data.get('include_conversation', True)
        
        # Obtenir le systeme RAG
        rag = get_rag_system()
        if not rag:
            return jsonify({
                'error': 'Systeme RAG non disponible',
                'success': False
            }), 503
        
        # Traiter la requete avec la nouvelle interface
        try:
            result = rag.query(question)
            print(f"[DEBUG] Résultat RAG keys: {list(result.keys()) if isinstance(result, dict) else type(result)}")
        except Exception as e:
            print(f"[ERROR] Erreur query RAG: {e}")
            return jsonify({
                'error': f'Erreur lors de la requête RAG: {str(e)}',
                'success': False,
                'timestamp': datetime.now().isoformat()
            }), 500
        
        # Formater la reponse pour l'API avec gestion defensive
        try:
            api_response = {
                'success': True,
                'question': question,
                'response': result.get('response', 'Erreur: pas de réponse') if isinstance(result, dict) else str(result),
                'metadata': {
                    'sources_count': len(result.get('sources', [])) if isinstance(result, dict) else 0,
                    'tokens_used': result.get('tokens_used', 0) if isinstance(result, dict) else 0,
                    'model': 'codestral-latest',
                    'timestamp': datetime.now().isoformat(),
                    'method': result.get('method', 'unknown') if isinstance(result, dict) else 'unknown',
                    'context_reference': result.get('context_reference', False) if isinstance(result, dict) else False
                }
            }
            
            # Ajouter les sources si demandees et disponibles
            if data.get('include_sources', True) and isinstance(result, dict):
                sources = result.get('sources', [])
                api_response['sources'] = sources if isinstance(sources, list) else []
        
        except Exception as e:
            print(f"[ERROR] Erreur formatage réponse: {e}")
            return jsonify({
                'error': f'Erreur lors du formatage: {str(e)}',
                'success': False,
                'result_debug': str(result)[:200] if result else 'None',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        return jsonify(api_response), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Erreur lors du traitement: {str(e)}',
            'success': False,
            'timestamp': datetime.now().isoformat()
        }), 500

@rag_bp.route('/search', methods=['POST'])
def search_documents():
    """Rechercher dans la base documentaire"""
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'error': 'Requete de recherche manquante',
                'success': False
            }), 400
        
        query = data['query'].strip()
        if not query:
            return jsonify({
                'error': 'Requete de recherche vide',
                'success': False
            }), 400
        
        limit = data.get('limit', 10)
        
        # Obtenir l'indexeur
        indexer = get_indexer_system()
        if not indexer:
            return jsonify({
                'error': 'Systeme d\'indexation non disponible',
                'success': False
            }), 503
        
        # Effectuer la recherche via PostgreSQL
        if hasattr(indexer, 'search_documents'):
            results = indexer.search_documents(query, k=limit)
            # Adapter le format pour l'API
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'content': result.get('content', ''),
                    'source': result.get('source', 'Unknown'),
                    'similarity': result.get('similarity', 0.0),
                    'metadata': result.get('metadata', {})
                })
            results = formatted_results
        else:
            results = []
        
        return jsonify({
            'success': True,
            'query': query,
            'results': results,
            'count': len(results),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Erreur lors de la recherche: {str(e)}',
            'success': False,
            'timestamp': datetime.now().isoformat()
        }), 500

@rag_bp.route('/conversation/history', methods=['GET'])
def get_conversation_history():
    """Obtenir l'historique de conversation"""
    try:
        rag = get_rag_system()
        if not rag:
            return jsonify({
                'error': 'Systeme RAG non disponible',
                'success': False
            }), 503
        
        # Recuperer l'historique du systeme PostgreSQL
        if hasattr(rag, 'get_conversation_history'):
            history = rag.get_conversation_history()
        elif hasattr(rag, 'conversation_history'):
            history = rag.conversation_history
        else:
            history = []
        
        return jsonify({
            'success': True,
            'history': history,
            'count': len(history),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Erreur lors de la recuperation de l\'historique: {str(e)}',
            'success': False,
            'timestamp': datetime.now().isoformat()
        }), 500

@rag_bp.route('/conversation/clear', methods=['POST'])
def clear_conversation():
    """Effacer l'historique de conversation"""
    try:
        rag = get_rag_system()
        if not rag:
            return jsonify({
                'error': 'Systeme RAG non disponible',
                'success': False
            }), 503
        
        # Effacer la memoire conversationnelle
        if hasattr(rag, 'clear_conversation_memory'):
            rag.clear_conversation_memory()
        elif hasattr(rag, 'clear_memory'):
            rag.clear_memory()
        else:
            # Fallback - reinitialiser la memoire
            if hasattr(rag, 'conversation_history'):
                rag.conversation_history = []
        
        return jsonify({
            'success': True,
            'message': 'Historique de conversation efface',
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Erreur lors de l\'effacement: {str(e)}',
            'success': False,
            'timestamp': datetime.now().isoformat()
        }), 500

@rag_bp.route('/conversation/export', methods=['POST'])
def export_conversation():
    """Exporter la conversation"""
    try:
        rag = get_rag_system()
        if not rag:
            return jsonify({
                'error': 'Systeme RAG non disponible',
                'success': False
            }), 503
        
        if hasattr(rag, 'export_conversation'):
            export_data = rag.export_conversation("text")
            filename = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        else:
            filename = "conversation_export.txt"
            export_data = "Export non disponible"
        
        return jsonify({
            'success': True,
            'message': 'Conversation exportee',
            'filename': filename,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Erreur lors de l\'export: {str(e)}',
            'success': False,
            'timestamp': datetime.now().isoformat()
        }), 500

@rag_bp.route('/conversation/new', methods=['POST'])
def start_new_conversation():
    """Demarrer une nouvelle conversation"""
    try:
        rag = get_rag_system()
        if not rag:
            return jsonify({
                'error': 'Systeme RAG non disponible',
                'success': False
            }), 503
        
        # Demarrer une nouvelle session
        if hasattr(rag, 'create_new_session'):
            old_session_id = rag.session_name
            new_session_id = rag.create_new_session()
            
            return jsonify({
                'success': True,
                'message': 'Nouvelle conversation demarree',
                'old_session_id': old_session_id,
                'new_session_id': new_session_id,
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            # Fallback - effacer l'historique
            if hasattr(rag, 'clear_memory'):
                rag.clear_memory()
            
            return jsonify({
                'success': True,
                'message': 'Nouvelle conversation demarree (historique efface)',
                'timestamp': datetime.now().isoformat()
            }), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Erreur lors du demarrage: {str(e)}',
            'success': False,
            'timestamp': datetime.now().isoformat()
        }), 500

@rag_bp.route('/stats', methods=['GET'])
def get_statistics():
    """Obtenir les statistiques du systeme"""
    try:
        indexer = get_indexer_system()
        rag = get_rag_system()
        
        stats = {
            'timestamp': datetime.now().isoformat(),
            'system_status': {
                'rag_available': rag is not None,
                'indexer_available': indexer is not None
            }
        }
        
        # Statistiques du vector store PostgreSQL
        if indexer and hasattr(indexer, 'get_session_info'):
            try:
                session_info = indexer.get_session_info()
                stats['index'] = {
                    'vector_store_ready': session_info.get('vector_store_ready', False),
                    'api_ready': session_info.get('api_ready', False),
                    'langchain_available': session_info.get('langchain_available', False)
                }
            except Exception as e:
                stats['index'] = {'error': str(e)}
        
        # Statistiques de conversation
        if rag:
            try:
                # Recuperer l'historique du systeme PostgreSQL
                if hasattr(rag, 'get_conversation_history'):
                    history = rag.get_conversation_history()
                elif hasattr(rag, 'conversation_history'):
                    history = rag.conversation_history
                else:
                    history = []
                total_tokens = sum(entry.get('tokens_used', 0) for entry in history)
                stats['conversation'] = {
                    'total_interactions': len(history),
                    'total_tokens_used': total_tokens,
                    'average_tokens_per_interaction': total_tokens / len(history) if history else 0
                }
            except Exception as e:
                stats['conversation'] = {'error': str(e)}
        
        return jsonify({
            'success': True,
            'statistics': stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Erreur lors de la recuperation des statistiques: {str(e)}',
            'success': False,
            'timestamp': datetime.now().isoformat()
        }), 500

@rag_bp.route('/modules', methods=['GET'])
def get_document_modules():
    """Obtenir la liste des modules disponibles dans la documentation"""
    try:
        # Recuperer dynamiquement les modules depuis l'indexeur
        indexer = get_indexer_system()
        if not indexer:
            return jsonify({
                'modules': [],
                'success': False,
                'message': 'Indexeur non disponible'
            }), 503
            
        # Obtenir les modules depuis LangChain PGVector
        try:
            # Requete pour obtenir les sources uniques depuis la table LangChain
            import psycopg2
            conn = psycopg2.connect(
                host="localhost",
                database="rag_database",
                user="postgres",
                password="postgres"
            )
            cursor = conn.cursor()
            
            # Chercher dans les tables LangChain PGVector
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name LIKE 'langchain_pg_%'
            """)
            tables = cursor.fetchall()
            
            modules = []
            if tables:
                # Utiliser la table embedding de LangChain si elle existe
                for table in tables:
                    if 'embedding' in table[0]:
                        try:
                            cursor.execute(f"""
                                SELECT 
                                    cmetadata->>'filename' as filename, 
                                    COUNT(*) as doc_count
                                FROM {table[0]}
                                WHERE cmetadata->>'filename' IS NOT NULL
                                GROUP BY cmetadata->>'filename'
                                ORDER BY doc_count DESC
                                LIMIT 20
                            """)
                            
                            module_data = cursor.fetchall()
                            for filename, count in module_data:
                                if filename:
                                    modules.append({
                                        'id': filename.lower().replace(' ', '_').replace('.', '_'),
                                        'name': filename.replace('.md', '').replace('.txt', ''),
                                        'description': f'Document: {filename}',
                                        'document_count': count
                                    })
                            break
                        except Exception as e:
                            print(f"Erreur requête table {table[0]}: {e}")
                            continue
            
            conn.close()
            
            # Si aucun module trouvé, utiliser fallback
            if not modules:
                modules = [
                    {
                        'id': 'corpus_seance5',
                        'name': 'Corpus Séance 5',
                        'description': 'Documentation du corpus .md de la Séance 5',
                        'document_count': 35
                    }
                ]
                
        except Exception as e:
            print(f"Erreur modules: {e}")
            # Fallback : modules generiques
            modules = [
                {
                    'id': 'documentation',
                    'name': 'Documentation',
                    'description': 'Documentation complete du systeme',
                    'document_count': 0
                }
            ]
        
        return jsonify({
            'success': True,
            'modules': modules,
            'count': len(modules),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Erreur lors de la recuperation des modules: {str(e)}',
            'success': False,
            'timestamp': datetime.now().isoformat()
        }), 500

@rag_bp.route('/questions/examples', methods=['GET'])
def get_example_questions():
    """Obtenir des questions d'exemple"""
    try:
        examples = [
            {
                'category': 'Documentation generale',
                'questions': [
                    'Comment utiliser ce systeme ?',
                    'Quelles sont les fonctionnalites disponibles ?',
                    'Comment configurer les parametres ?'
                ]
            },
            {
                'category': 'Processus et workflows',
                'questions': [
                    'Comment demarrer un processus ?',
                    'Quelles sont les etapes de validation ?',
                    'Comment gerer les alertes ?'
                ]
            },
            {
                'category': 'Administration',
                'questions': [
                    'Comment gerer les utilisateurs ?',
                    'Comment configurer les permissions ?',
                    'Quels sont les parametres systeme ?'
                ]
            }
        ]
        
        return jsonify({
            'success': True,
            'examples': examples,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Erreur lors de la recuperation des exemples: {str(e)}',
            'success': False,
            'timestamp': datetime.now().isoformat()
        }), 500

@rag_bp.route('/conversation/sessions', methods=['GET'])
def get_all_sessions():
    """Obtenir toutes les sessions sauvegardees"""
    try:
        rag = get_rag_system()
        if not rag:
            return jsonify({
                'error': 'Systeme RAG non disponible',
                'success': False
            }), 503
        
        if hasattr(rag, 'list_all_sessions'):
            sessions = rag.list_all_sessions()
        else:
            sessions = []
        
        return jsonify({
            'success': True,
            'sessions': sessions,
            'count': len(sessions),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Erreur lors de la recuperation des sessions: {str(e)}',
            'success': False,
            'timestamp': datetime.now().isoformat()
        }), 500

@rag_bp.route('/conversation/load', methods=['POST'])
def load_session():
    """Charger une session specifique"""
    try:
        data = request.get_json()
        
        if not data or 'session_id' not in data:
            return jsonify({
                'error': 'session_id manquant',
                'success': False
            }), 400
        
        session_id = data['session_id']
        
        rag = get_rag_system()
        if not rag:
            return jsonify({
                'error': 'Systeme RAG non disponible',
                'success': False
            }), 503
        
        if hasattr(rag, 'load_session_by_id'):
            success = rag.load_session_by_id(session_id)
            if success:
                return jsonify({
                    'success': True,
                    'message': f'Session {session_id} chargee',
                    'session_id': session_id,
                    'timestamp': datetime.now().isoformat()
                }), 200
            else:
                return jsonify({
                    'error': f'Session {session_id} non trouvee',
                    'success': False
                }), 404
        else:
            return jsonify({
                'error': 'Gestion de session non disponible',
                'success': False
            }), 503
        
    except Exception as e:
        return jsonify({
            'error': f'Erreur lors du chargement: {str(e)}',
            'success': False,
            'timestamp': datetime.now().isoformat()
        }), 500

@rag_bp.route('/conversation/delete', methods=['POST'])
def delete_session():
    """Supprimer une session"""
    try:
        data = request.get_json()
        
        if not data or 'session_id' not in data:
            return jsonify({
                'error': 'session_id manquant',
                'success': False
            }), 400
        
        session_id = data['session_id']
        
        rag = get_rag_system()
        if not rag:
            return jsonify({
                'error': 'Systeme RAG non disponible',
                'success': False
            }), 503
        
        if hasattr(rag, 'delete_session_by_id'):
            success = rag.delete_session_by_id(session_id)
            if success:
                return jsonify({
                    'success': True,
                    'message': f'Session {session_id} supprimee',
                    'timestamp': datetime.now().isoformat()
                }), 200
            else:
                return jsonify({
                    'error': f'Session {session_id} non trouvee',
                    'success': False
                }), 404
        else:
            return jsonify({
                'error': 'Gestion de session non disponible',
                'success': False
            }), 503
        
    except Exception as e:
        return jsonify({
            'error': f'Erreur lors de la suppression: {str(e)}',
            'success': False,
            'timestamp': datetime.now().isoformat()
        }), 500

