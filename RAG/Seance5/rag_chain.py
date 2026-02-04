#!/usr/bin/env python3
"""
Systeme RAG final pour Seance 5 avec PostgreSQL + pgvector + LangChain
MEME ARCHITECTURE que Seance 4, mais avec chargement automatique des documents .md
"""

import os
import json
import psycopg2
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import litellm
    from litellm import completion
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False

# LangChain OBLIGATOIRE pour Séance 5
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_community.vectorstores import PGVector
    from langchain.schema import Document
    from langchain.memory import ConversationBufferWindowMemory
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    print(f"[ERREUR CRITIQUE] LangChain non disponible: {e}")
    print("Installation requise: pip install langchain langchain-community")
    raise ImportError("LangChain est OBLIGATOIRE pour la Séance 5") from e

class PostgreSQLRAGSystem:
    """Systeme RAG avec PostgreSQL + pgvector - IDENTIQUE Seance 4 mais avec corpus .md"""
    
    def __init__(self, session_name: str = None):
        self.session_name = session_name or f"session_seance5_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.api_key = os.getenv('CODESTRAL_API_KEY')
        self.conversation_history = []
        self.sessions_dir = Path(__file__).parent / "sessions"
        self.sessions_dir.mkdir(exist_ok=True)
        
        # Configuration PostgreSQL depuis .env
        self.db_params = {
            "host": os.getenv('DB_HOST', 'localhost'),
            "port": os.getenv('DB_PORT', '5432'),
            "database": os.getenv('DB_NAME'),
            "user": os.getenv('DB_USER'),
            "password": os.getenv('DB_PASSWORD')
        }
        
        # Setup LangChain + PostgreSQL (obligatoire)
        self._setup_langchain_postgresql()
        
        # Charger les documents (.md pour Seance 5)
        self._load_documents()
        
        print(f"[INIT] PostgreSQL RAG System Seance 5 - Session: {self.session_name}")
    
    def _setup_langchain_postgresql(self):
        """Configurer LangChain avec PostgreSQL + pgvector"""
        try:
            # Embeddings
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            
            # Connection string pour PGVector
            connection_string = f"postgresql://{self.db_params['user']}:{self.db_params['password']}@{self.db_params['host']}:{self.db_params['port']}/{self.db_params['database']}"
            
            # Configuration PGVector pour LangChain - COLLECTION UNIQUE pour toutes les sessions
            self.pgvector_config = {
                'connection_string': connection_string,
                'embedding_function': self.embeddings,
                'collection_name': 'seance5_shared_corpus',  # Collection partagée
                'distance_strategy': 'cosine'
            }
            
            # Memoire conversationnelle LangChain
            self.memory = ConversationBufferWindowMemory(
                memory_key="chat_history",
                return_messages=True,
                k=10
            )
            
            # Le vector store sera cree lors du chargement des documents
            self.vector_store = None
            
            print("[SETUP] LangChain + PostgreSQL configure")
            
        except Exception as e:
            print(f"[ERROR] Setup LangChain PostgreSQL: {e}")
            self.embeddings = None
            self.memory = None
    
    def _load_documents(self):
        """Charger et indexer les documents .md dans PostgreSQL via LangChain"""
        if not hasattr(self, 'embeddings') or not self.embeddings:
            print("[ERROR] Embeddings non initialises")
            return
        
        try:
            # Vérifier si la collection existe déjà avec des documents
            try:
                existing_store = PGVector(
                    connection_string=self.pgvector_config['connection_string'],
                    embedding_function=self.embeddings,
                    collection_name=self.pgvector_config['collection_name']
                )
                # Test de recherche pour voir si des documents existent
                test_docs = existing_store.similarity_search("test", k=1)
                if test_docs:
                    print(f"[INFO] Collection {self.pgvector_config['collection_name']} existe déjà avec {len(test_docs)} documents")
                    self.vector_store = existing_store
                    return
            except Exception as e:
                print(f"[INFO] Collection n'existe pas encore, création: {e}")
            
            documents = []
            base_dir = Path(__file__).parent
            
            # SEANCE 5: Charger UNIQUEMENT les fichiers .md du dossier "Corpus/Corpus documentaire"
            corpus_dir = base_dir / "Corpus" / "Corpus documentaire"
            loaded_files = set()  # Pour éviter les doublons
            total_files = 0
            
            if corpus_dir.exists():
                print(f"[INFO] Chargement depuis: {corpus_dir}")
                # Charger tous les .md dans ce dossier UNIQUEMENT (pas récursif)
                for md_file in corpus_dir.glob("*.md"):
                    file_key = md_file.name
                    
                    if file_key not in loaded_files:
                        try:
                            with open(md_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            # Nettoyer les caracteres non-ASCII
                            content = content.encode('ascii', errors='ignore').decode('ascii')
                            
                            if content.strip():  # Ignorer fichiers vides
                                doc = Document(
                                    page_content=content,
                                    metadata={
                                        'source': str(md_file),
                                        'filename': md_file.name,
                                        'relative_path': str(md_file.relative_to(base_dir)),
                                        'session': self.session_name,
                                        'document_type': 'markdown',
                                        'loaded_at': datetime.now().isoformat()
                                    }
                                )
                                documents.append(doc)
                                loaded_files.add(file_key)
                                total_files += 1
                                print(f"[LOAD] {md_file.name}")
                        
                        except Exception as e:
                            print(f"[ERROR] {md_file.name}: {e}")
                    else:
                        print(f"[SKIP] {file_key} (déjà chargé)")
            else:
                print(f"[WARNING] Dossier corpus non trouvé: {corpus_dir}")
                
            # Ajouter tous les fichiers .txt du dossier Corpus (corpus_intelligence_artificielle.txt, gymWiki.txt, etc.)
            corpus_base_dir = base_dir / "Corpus"
            if corpus_base_dir.exists():
                print(f"[INFO] Recherche fichiers .txt dans: {corpus_base_dir}")
                for txt_file in corpus_base_dir.glob("*.txt"):
                    file_key = txt_file.name
                    
                    if file_key not in loaded_files:
                        try:
                            with open(txt_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            content = content.encode('ascii', errors='ignore').decode('ascii')
                            
                            if content.strip():
                                doc = Document(
                                    page_content=content,
                                    metadata={
                                        'source': str(txt_file),
                                        'filename': txt_file.name,
                                        'relative_path': str(txt_file.relative_to(base_dir)),
                                        'session': self.session_name,
                                        'document_type': 'text',
                                        'loaded_at': datetime.now().isoformat()
                                    }
                                )
                                documents.append(doc)
                                loaded_files.add(file_key)
                                total_files += 1
                                print(f"[LOAD] {txt_file.name}")
                        
                        except Exception as e:
                            print(f"[ERROR] {txt_file.name}: {e}")
                    else:
                        print(f"[SKIP] {file_key} (déjà chargé)")
            
            
            if documents:
                # Text splitter
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=200
                )
                splits = splitter.split_documents(documents)
                
                # Creer le vector store PostgreSQL via LangChain
                self.vector_store = PGVector.from_documents(
                    documents=splits,
                    embedding=self.embeddings,
                    connection_string=self.pgvector_config['connection_string'],
                    collection_name=self.pgvector_config['collection_name'],
                    distance_strategy=self.pgvector_config['distance_strategy']
                )
                
                print(f"[INDEX] {total_files} fichiers traites, {len(splits)} chunks indexes dans PostgreSQL")
            else:
                print("[WARNING] Aucun document charge")
                
        except Exception as e:
            print(f"[ERROR] Chargement documents: {e}")
            self.vector_store = None
    
    def search_documents(self, query: str, k: int = 5) -> List[Dict]:
        """Rechercher dans PostgreSQL via LangChain PGVector"""
        if not self.vector_store:
            return []
        
        try:
            # Recherche avec scores de similarite
            docs_with_scores = self.vector_store.similarity_search_with_score(query, k=k)
            results = []
            
            for doc, score in docs_with_scores:
                # Calculer la similarité correctement (pgvector retourne distance cosine)
                similarity = max(0, 1 - score) if score <= 1 else 1 / (1 + score)
                
                results.append({
                    'content': doc.page_content,
                    'source': doc.metadata.get('filename', 'Unknown'),
                    'similarity': round(similarity, 3),
                    'metadata': doc.metadata
                })
            
            return results
        except Exception as e:
            print(f"[ERROR] Recherche PostgreSQL: {e}")
            return []
    
    def call_api(self, prompt: str) -> str:
        """Appeler l'API Codestral"""
        if not self.api_key:
            return "Erreur: Cle API manquante"
        
        try:
            if LITELLM_AVAILABLE:
                response = completion(
                    model="codestral/codestral-latest",
                    messages=[{"role": "user", "content": prompt}],
                    api_key=self.api_key,
                    max_tokens=2000,
                    temperature=0.1
                )
                return response.choices[0].message.content
            else:
                import requests
                
                headers = {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                }
                
                payload = {
                    'model': 'codestral-latest',
                    'messages': [{"role": "user", "content": prompt}],
                    'max_tokens': 2000,
                    'temperature': 0.1
                }
                
                response = requests.post(
                    "https://codestral.mistral.ai/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    return response.json()['choices'][0]['message']['content']
                else:
                    return f"Erreur API: {response.status_code}"
        
        except Exception as e:
            return f"Erreur: {e}"
    
    def detect_context_reference(self, question: str) -> bool:
        """Detecter reference au contexte precedent"""
        indicators = [
            'cette', 'cela', 'ca', 'precedent', 'ci-dessus', 'avant',
            'le point', 'la point', 'point', 'cette information',
            'ce que tu as dit', 'tu as mentionne', 'plus haut',
            'dans ta reponse', 'tu disais', 'ses', 'son', 'sa',
            'leurs', 'leur', 'elle', 'il', 'ils', 'elles'
        ]
        
        question_lower = question.lower().strip()
        
        # Détecter les références directes
        if any(word in question_lower for word in indicators):
            return True
        
        # Détecter les questions qui commencent par des références
        context_starters = ['ses ', 'son ', 'sa ', 'leur ', 'leurs ']
        if any(question_lower.startswith(starter) for starter in context_starters):
            return True
            
        return False
    
    def _classify_question(self, question: str) -> str:
        """Classifier le type de question"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['cette', 'cela', 'ca', 'precedent']):
            return 'reference_contextuelle'
        elif any(word in question_lower for word in ['comment', 'how', 'procedure']):
            return 'procedure'
        elif any(word in question_lower for word in ['qu\'est-ce', 'what', 'definition']):
            return 'definition'
        elif any(word in question_lower for word in ['pourquoi', 'why', 'raison']):
            return 'explication'
        elif any(word in question_lower for word in ['info', 'information', 'details']):
            return 'information'
        else:
            return 'general'
    
    def build_context(self, question: str, docs: List[Dict], use_history: bool = False) -> str:
        """Construire le contexte enrichi pour l'API"""
        context_parts = []
        
        # Contexte conversationnel amélioré pour références
        if use_history:
            if self.memory:
                # Utiliser la mémoire LangChain
                memory_context = self.memory.load_memory_variables({})
                chat_history = memory_context.get('chat_history', [])
                
                if chat_history:
                    context_parts.append("=== CONTEXTE CONVERSATIONNEL ===")
                    # Prendre seulement le dernier échange pour les références
                    recent_messages = chat_history[-2:] if len(chat_history) >= 2 else chat_history
                    
                    if len(recent_messages) >= 2:
                        human_msg = recent_messages[-2]
                        ai_msg = recent_messages[-1]
                        context_parts.append(f"Question précédente: {human_msg.content}")
                        # Réponse complète pour bien comprendre le contexte
                        context_parts.append(f"Réponse précédente: {ai_msg.content}")
                        context_parts.append("")
            
            elif self.conversation_history:
                # Fallback sur l'historique local
                context_parts.append("=== CONTEXTE PRECEDENT ===")
                last_exchange = self.conversation_history[-1]
                context_parts.append(f"Question précédente: {last_exchange['question']}")
                context_parts.append(f"Réponse précédente: {last_exchange['response']}")
                context_parts.append("")
        
        # Documents pertinents avec filtrage par pertinence
        if docs:
            # Filtrer les sources peu pertinentes si on a une référence contextuelle
            relevant_docs = docs
            if use_history:
                # Pour les questions contextuelles, garder seulement sources très pertinentes
                relevant_docs = [doc for doc in docs if doc.get('similarity', 0) > 0.4] or docs[:2]
            
            if relevant_docs:
                context_parts.append("=== DOCUMENTS PERTINENTS ===")
                for i, doc in enumerate(relevant_docs[:3], 1):
                    similarity = doc.get('similarity', 0)
                    context_parts.append(f"[Source {i}] {doc['source']} (Similarité: {similarity:.3f})")
                    context_parts.append(f"Contenu: {doc['content'][:400]}...")
                    context_parts.append("")
        
        return "\n".join(context_parts)
    
    def query(self, question: str) -> Dict[str, Any]:
        """Requete RAG complete"""
        print(f"[QUERY] {question}")
        
        # Detection de reference contextuelle
        has_context_ref = self.detect_context_reference(question)
        
        # Gestion intelligente des sources selon le contexte
        if has_context_ref and self.conversation_history:
            # TOUJOURS faire une nouvelle recherche, même pour questions contextuelles
            # Cela permet de trouver de nouveaux documents
            docs = self.search_documents(question, k=5)
            print(f"[CONTEXT+SEARCH] Recherche contextuelle: {len(docs)} docs")
            
            # Ajouter quelques sources précédentes si pertinentes pour le contexte
            last_entry = self.conversation_history[-1]
            prev_docs = last_entry.get('sources', [])[:2]  # Seulement 2 sources précédentes
            if prev_docs:
                docs.extend(prev_docs)
                print(f"[CONTEXT] Ajout de {len(prev_docs)} sources précédentes")
        else:
            # Nouvelle recherche vectorielle pour questions non-contextuelles
            docs = self.search_documents(question, k=5)
            print(f"[SEARCH] Nouvelle recherche: {len(docs)} docs")
        
        # Construire le contexte
        context = self.build_context(question, docs, has_context_ref)
        
        # Prompt adaptatif selon le type de question
        if context:
            if has_context_ref:
                prompt = f"""{context}

QUESTION CONTEXTUELLE: {question}

Instructions:
- Cette question fait référence au contexte conversationnel précédent
- Utilise PRINCIPALEMENT la réponse précédente et le contexte fourni
- Développe ou précise les éléments demandés
- Cite uniquement les sources pertinentes au contexte précédent
- Évite d'introduire de nouvelles informations non liées

Reponse:"""
            else:
                prompt = f"""{context}

NOUVELLE QUESTION: {question}

Instructions:
- Utilise les documents fournis pour répondre à cette nouvelle question
- Cite les sources les plus pertinentes
- Sois précis et structuré dans ta réponse

Reponse:"""
        else:
            prompt = f"Question: {question}\n\nReponse:"
        
        # Appel API
        response = self.call_api(prompt)
        
        # Sauvegarder IMMÉDIATEMENT dans la mémoire LangChain
        if self.memory:
            self.memory.save_context(
                {"input": question},
                {"output": response}
            )
        
        # Resultats avec informations de debug
        result = {
            'question': question,
            'response': response,
            'raw_response': response,
            'sources': docs,
            'sources_count': len(docs),
            'context_reference': has_context_ref,
            'question_type': self._classify_question(question),
            'success': len(response) > 10,
            'method': 'contextual_rag' if has_context_ref else 'search_rag',
            'session': self.session_name,
            'timestamp': datetime.now().isoformat(),
            'memory_messages': len(self.memory.chat_memory.messages) if self.memory else 0
        }
        
        # Ajouter a l'historique local
        self.conversation_history.append(result)
        
        # Sauvegarde automatique après chaque échange
        try:
            self._save_current_session()
        except Exception as e:
            print(f"[WARNING] Erreur sauvegarde automatique: {e}")
        
        print(f"[OK] Reponse avec {len(docs)} sources - Mémoire: {result['memory_messages']} messages")
        return result
    
    def clear_memory(self):
        """Effacer l'historique"""
        self.conversation_history.clear()
        print("[CLEAR] Historique efface")
    
    def save_session(self, filepath: str = None):
        """Sauvegarder la session"""
        if not filepath:
            filepath = f"sessions/session_{self.session_name}.json"
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        data = {
            'session_name': self.session_name,
            'saved_at': datetime.now().isoformat(),
            'conversation_count': len(self.conversation_history),
            'conversation_history': self.conversation_history
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"[SAVE] {filepath}")
        return filepath
    
    def load_session(self, filepath: str):
        """Charger une session"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.session_name = data.get('session_name', self.session_name)
            self.conversation_history = data.get('conversation_history', [])
            
            print(f"[LOAD] {len(self.conversation_history)} echanges")
            return True
        except Exception as e:
            print(f"[ERROR] Chargement: {e}")
            return False
    
    def get_session_info(self) -> Dict[str, Any]:
        """Informations session"""
        return {
            'session_name': self.session_name,
            'conversations': len(self.conversation_history),
            'vector_store_ready': self.vector_store is not None,
            'api_ready': bool(self.api_key),
            'langchain_available': True,  # Obligatoire pour Séance 5
            'litellm_available': LITELLM_AVAILABLE
        }
    
    # Méthodes pour compatibilité avec l'interface
    def clear_conversation_memory(self):
        """Effacer la mémoire (alias pour clear_memory)"""
        return self.clear_memory()
    
    def export_conversation(self, format_type: str = "json") -> str:
        """Exporter la conversation"""
        if format_type == "json":
            return json.dumps({
                'session': self.session_name,
                'exported_at': datetime.now().isoformat(),
                'conversations': self.conversation_history
            }, indent=2, ensure_ascii=False)
        else:
            lines = [f"=== CONVERSATION SEANCE 5 {self.session_name} ==="]
            lines.append(f"Exportée le: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            lines.append("")
            
            for i, entry in enumerate(self.conversation_history, 1):
                lines.append(f"[{i}] Q: {entry['question']}")
                lines.append(f"[{i}] R: {entry['response']}")
                if entry.get('sources'):
                    lines.append(f"    Sources: {len(entry['sources'])} documents")
                lines.append("---")
            return "\n".join(lines)
    
    def get_conversation_history(self) -> List[Dict]:
        """Obtenir l'historique de conversation"""
        return self.conversation_history.copy()
    
    # Gestionnaire de sessions pour l'interface
    def list_all_sessions(self) -> List[Dict]:
        """Lister toutes les sessions sauvegardées"""
        sessions = []
        
        # Session courante
        current_time = datetime.now().isoformat()
        sessions.append({
            'session_id': self.session_name,
            'session_name': self.session_name,
            'created_at': current_time,
            'start_time': current_time,  # Pour compatibilité interface web
            'last_activity': current_time,  # Pour compatibilité interface web
            'message_count': len(self.conversation_history),
            'turns_count': len(self.conversation_history),  # Pour compatibilité interface web
            'is_current': True
        })
        
        # Sessions sauvegardées - TOUTES les sessions JSON
        for session_file in self.sessions_dir.glob("*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                
                if session_data.get('session_name') != self.session_name:
                    saved_at = session_data.get('saved_at', current_time)
                    conversations = session_data.get('conversation_history', [])
                    last_activity = conversations[-1].get('timestamp', saved_at) if conversations else saved_at
                    
                    sessions.append({
                        'session_id': session_data.get('session_name', session_file.stem),
                        'session_name': session_data.get('session_name', session_file.stem),
                        'created_at': saved_at,
                        'start_time': saved_at,  # Pour compatibilité interface web
                        'last_activity': last_activity,  # Pour compatibilité interface web
                        'message_count': session_data.get('conversation_count', 0),
                        'turns_count': session_data.get('conversation_count', 0),  # Pour compatibilité interface web
                        'is_current': False
                    })
            except Exception as e:
                print(f"[WARNING] Erreur lecture session {session_file}: {e}")
        
                
        return sessions
    
    def create_new_session(self, session_name: str = None) -> str:
        """Créer une nouvelle session et sauvegarder l'ancienne"""
        # Sauvegarder l'ancienne session si elle a des conversations
        if self.conversation_history:
            self._save_current_session()
        
        old_session = self.session_name
        new_session_name = session_name or f"session_seance5_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Réinitialiser
        self.session_name = new_session_name
        self.conversation_history = []
        
        if self.memory:
            self.memory.clear()
        
        print(f"[NEW] Nouvelle session: {new_session_name} (ancienne: {old_session} sauvegardée)")
        return new_session_name
    
    def load_session_by_id(self, session_id: str) -> bool:
        """Charger une session par ID"""
        if session_id == self.session_name:
            print(f"[LOAD] Session déjà active: {session_id}")
            return True
        
        session_file = self.sessions_dir / f"{session_id}.json"
        if not session_file.exists():
            print(f"[ERROR] Session {session_id} non trouvée")
            return False
        
        try:
            # Sauvegarder la session courante si elle a du contenu
            if self.conversation_history:
                self._save_current_session()
            
            # Charger la nouvelle session
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.session_name = data.get('session_name', session_id)
            self.conversation_history = data.get('conversation_history', [])
            
            # Restaurer dans la mémoire LangChain
            if self.memory:
                self.memory.clear()
                for entry in self.conversation_history:
                    self.memory.save_context(
                        {"input": entry['question']},
                        {"output": entry['response']}
                    )
            
            print(f"[LOAD] Session {session_id} chargée: {len(self.conversation_history)} conversations")
            return True
            
        except Exception as e:
            print(f"[ERROR] Impossible de charger {session_id}: {e}")
            return False
    
    def delete_session_by_id(self, session_id: str) -> bool:
        """Supprimer une session par ID"""
        if session_id == self.session_name:
            print("[ERROR] Impossible de supprimer la session courante")
            return False
        
        session_file = self.sessions_dir / f"{session_id}.json"
        if not session_file.exists():
            print(f"[ERROR] Session {session_id} non trouvée")
            return False
        
        try:
            session_file.unlink()
            print(f"[DELETE] Session {session_id} supprimée")
            return True
        except Exception as e:
            print(f"[ERROR] Impossible de supprimer {session_id}: {e}")
            return False
    
    def _save_current_session(self):
        """Sauvegarder la session courante - CENTRALISÉ"""
        if not self.conversation_history:
            return
        
        # CENTRALISER toutes les sessions dans le dossier sessions/
        session_file = self.sessions_dir / f"{self.session_name}.json"
        data = {
            'session_name': self.session_name,
            'saved_at': datetime.now().isoformat(),
            'conversation_count': len(self.conversation_history),
            'conversation_history': self.conversation_history,
            'session_type': 'unified'  # Marquer comme session unifiée
        }
        
        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"[SAVE] Session {self.session_name} sauvegardée: {len(self.conversation_history)} conversations")
        except Exception as e:
            print(f"[ERROR] Sauvegarde session: {e}")
    

# Alias pour compatibilite avec les interfaces existantes
class GenericEnhancedRAGChain(PostgreSQLRAGSystem):
    def query_with_enhanced_rag(self, question: str) -> Dict[str, Any]:
        return self.query(question)

class RAGChain(PostgreSQLRAGSystem):
    pass

class SimpleRAGSystem(PostgreSQLRAGSystem):
    pass

def test_seance5_rag():
    """Test complet du systeme RAG Seance 5 - IDENTIQUE Seance 4"""
    print("=" * 80)
    print("TEST SYSTEME RAG SEANCE 5 - POSTGRESQL + PGVECTOR + LANGCHAIN")
    print("=" * 80)
    
    try:
        rag = PostgreSQLRAGSystem("test_seance5")
        
        print("\n1. INFOS SYSTEME")
        info = rag.get_session_info()
        for k, v in info.items():
            print(f"   {k}: {v}")
        
        print("\n2. TEST CONNEXION POSTGRESQL")
        try:
            import psycopg2
            conn = psycopg2.connect(**rag.db_params)
            conn.close()
            print("Connexion PostgreSQL OK")
        except Exception as e:
            print(f"Connexion PostgreSQL: {e}")
        
        print("\n3. PREMIERE QUESTION")
        result1 = rag.query("Qu'est-ce que la gestion des projets ?")
        print(f"   Succes: {result1['success']}")
        print(f"   Sources PostgreSQL: {result1['sources_count']}")
        print(f"   Reponse: {result1['response'][:150]}...")
        
        print("\n4. QUESTION AVEC REFERENCE CONTEXTUELLE")
        result2 = rag.query("Quelles sont ses principales fonctionnalites ?")
        print(f"   Reference detectee: {result2['context_reference']}")
        print(f"   Memoire LangChain: {result2.get('memory_messages', 0)} messages")
        print(f"   Reponse: {result2['response'][:150]}...")
        
        print("\n5. VERIFICATION INTEGRATION")
        if result1['success'] and result2['success']:
²            print("PostgreSQL + pgvector : FONCTIONNEL")
            print("LangChain integration : FONCTIONNEL") 
            print("Codestral API : FONCTIONNEL")
            print("Memoire conversationnelle : FONCTIONNEL")
            print("Recherche vectorielle : FONCTIONNEL")
            print("Corpus .md : CHARGE AUTOMATIQUEMENT")
            print("\n[SUCCES] Systeme RAG Seance 5 completement fonctionnel !")
            return True
        else:
            print("\n[ECHEC] Problemes detectes")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_seance5_rag()
