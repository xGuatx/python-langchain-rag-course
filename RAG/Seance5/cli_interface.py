#!/usr/bin/env python3
"""
Interface conversationnelle amelioree pour la Seance 5
Interface CLI et Web - Systeme RAG generique avec corpus .md
"""

import os
import sys
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.syntax import Syntax
    from rich.markdown import Markdown
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("[WARNING] Rich non disponible, utilisation de l'affichage simple")

from rag_chain import RAGChain

class EnhancedConversationInterfaceSeance5:
    """Interface conversationnelle amelioree pour Seance 5"""
    
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.rag_chain = None
        self.session_active = False
        
    def start_interface(self):
        """Demarrer l'interface conversationnelle"""
        self._display_welcome()
        
        try:
            # Initialiser la chaine RAG
            self._initialize_rag_chain()
            
            # Boucle principale de conversation
            self._conversation_loop()
            
        except KeyboardInterrupt:
            self._display_goodbye()
        except Exception as e:
            self._display_error(f"Erreur fatale: {e}")
    
    def _display_welcome(self):
        """Afficher le message de bienvenue"""
        if RICH_AVAILABLE:
            welcome_text = """
# [BOT] Assistant RAG - Seance 5

Bienvenue dans l'interface conversationnelle de la **Seance 5** !

## Systeme RAG generique avec corpus .md

## Fonctionnalites disponibles:
- [SEARCH] **Recherche intelligente** dans la base PostgreSQL/pgvector
- [SOURCES] **Citations de sources** avec tracabilite complete
- [MEMORY] **Memoire conversationnelle** pour la continuite
- [CONTEXT] **Detection automatique** des references contextuelles
- [CHART] **Interface CLI** avec affichage enrichi

## Commandes speciales:
- `!help` - Afficher l'aide complete
- `!session` - Informations sur la session courante
- `!history` - Afficher l'historique des conversations
- `!sessions` - Lister toutes les sessions sauvegardees
- `!load <session_id>` - Charger une session specifique
- `!delete <session_id>` - Supprimer une session
- `!export` - Exporter la conversation
- `!clear` - Effacer la memoire
- `!new` - Demarrer une nouvelle conversation
- `!quit` - Quitter l'interface
            """
            
            self.console.print(Panel(
                Markdown(welcome_text),
                title="[INIT] Seance 5 - RAG Generique",
                border_style="blue"
            ))
        else:
            print("=" * 60)
            print("[BOT] Assistant RAG - Seance 5")
            print("=" * 60)
            print("Bienvenue dans l'interface de la Seance 5 !")
            print("Systeme RAG generique avec corpus .md")
            print("Tapez !help pour voir les commandes disponibles")
            print("=" * 60)
    
    def _initialize_rag_chain(self):
        """Initialiser la chaine RAG avec indicateur de progression"""
        if RICH_AVAILABLE:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Initialisation du systeme RAG generique...", total=None)
                self.rag_chain = RAGChain()
                progress.update(task, description="[OK] Systeme RAG initialise")
        else:
            print("[INIT] Initialisation du systeme RAG generique...")
            self.rag_chain = RAGChain()
            print("[OK] Systeme RAG initialise")
        
        self.session_active = True
    
    def _conversation_loop(self):
        """Boucle principale de conversation"""
        while self.session_active:
            try:
                # Obtenir la question de l'utilisateur
                question = self._get_user_input()
                
                if not question:
                    continue
                
                # Traiter les commandes speciales
                if question.startswith('!'):
                    self._handle_special_command(question)
                    continue
                
                # Traiter la question normale
                self._process_question(question)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                self._display_error(f"Erreur lors du traitement: {e}")
    
    def _get_user_input(self) -> str:
        """Obtenir l'entree utilisateur"""
        if RICH_AVAILABLE:
            return Prompt.ask("\n[bold blue][QUESTION] Votre question[/bold blue]")
        else:
            return input("\n[QUESTION] Votre question: ").strip()
    
    def _process_question(self, question: str):
        """Traiter une question normale"""
        # Afficher l'indicateur de traitement
        if RICH_AVAILABLE:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Traitement de votre question...", total=None)
                
                # Obtenir la reponse RAG
                result = self.rag_chain.query(question)
                
                progress.update(task, description="[OK] Reponse generee")
        else:
            print("[PROCESS] Traitement de votre question...")
            result = self.rag_chain.query(question)
        
        # Afficher la reponse
        self._display_response(result)
    
    def _display_response(self, result: Dict[str, Any]):
        """Afficher la reponse de maniere structuree"""
        if RICH_AVAILABLE:
            self._display_response_rich(result)
        else:
            self._display_response_simple(result)
    
    def _display_response_rich(self, result: Dict[str, Any]):
        """Afficher la reponse avec Rich"""
        # Panel principal avec la reponse
        method_info = f"[{result['method'].upper()}]" if result.get('method') else ""
        context_info = "[CONTEXTUEL]" if result.get('context_reference') else "[NOUVEAU]"
        
        response_panel = Panel(
            result['raw_response'],
            title=f"[BOT] Reponse {method_info} {context_info}",
            border_style="green"
        )
        self.console.print(response_panel)
        
        # Tableau des sources
        if result['sources']:
            sources_table = Table(title="[SOURCES] Sources consultees")
            sources_table.add_column("ID", style="cyan", no_wrap=True)
            sources_table.add_column("Source", style="yellow")
            sources_table.add_column("Similarite", style="magenta")
            sources_table.add_column("Extrait", style="white")
            
            for i, source in enumerate(result['sources']):
                similarity = source.get('similarity', 0)
                content = source['content'][:80] + "..." if len(source['content']) > 80 else source['content']
                filename = source.get('source', 'Unknown')
                
                sources_table.add_row(
                    str(i + 1),
                    filename,
                    f"{similarity:.3f}",
                    content
                )
            
            self.console.print(sources_table)
        
        # Informations de session
        if RICH_AVAILABLE:
            session_info = f"[dim]Session: {result.get('session', 'N/A')} | Memoire: {result.get('memory_messages', 0)} messages | Type: {result.get('question_type', 'N/A')}[/dim]"
            self.console.print(session_info)
    
    def _display_response_simple(self, result: Dict[str, Any]):
        """Afficher la reponse en mode simple"""
        print("\n" + "="*60)
        method = result.get('method', 'rag').upper()
        context = "CONTEXTUEL" if result.get('context_reference') else "NOUVEAU"
        print(f"[BOT] REPONSE [{method}] [{context}]")
        print("="*60)
        print(result['raw_response'])
        
        if result['sources']:
            print(f"\n[SOURCES] SOURCES CONSULTEES ({len(result['sources'])}):")
            print("-"*40)
            for i, source in enumerate(result['sources'], 1):
                similarity = source.get('similarity', 0)
                filename = source.get('source', 'Unknown')
                content = source['content'][:100] + "..."
                print(f"{i}. {filename} (Similarite: {similarity:.3f})")
                print(f"   {content}")
        
        print(f"\n[INFO] Session: {result.get('session', 'N/A')} | Memoire: {result.get('memory_messages', 0)} messages")
    
    def _handle_special_command(self, command: str):
        """Traiter les commandes speciales"""
        command = command.lower().strip()
        
        if command == '!help':
            self._show_help()
        elif command == '!session':
            self._show_session_info()
        elif command == '!history':
            self._show_conversation_history()
        elif command == '!sessions':
            self._show_all_sessions()
        elif command.startswith('!load '):
            session_id = command.split(' ', 1)[1] if len(command.split(' ')) > 1 else None
            if session_id:
                self._load_session(session_id)
            else:
                self._display_error("Usage: !load <session_id>")
        elif command.startswith('!delete '):
            session_id = command.split(' ', 1)[1] if len(command.split(' ')) > 1 else None
            if session_id:
                self._delete_session(session_id)
            else:
                self._display_error("Usage: !delete <session_id>")
        elif command == '!export':
            self._export_conversation()
        elif command == '!clear':
            self._clear_memory()
        elif command in ['!new', '!new_conversation']:
            self._start_new_conversation()
        elif command in ['!quit', '!exit']:
            self._quit_interface()
        else:
            self._display_error(f"Commande inconnue: {command}")
    
    def _show_help(self):
        """Afficher l'aide"""
        if RICH_AVAILABLE:
            help_text = """
# [HELP] Aide - Commandes disponibles

## Questions normales:
Posez vos questions sur le corpus documentaire de la Seance 5.

## Commandes speciales:
- `!help` - Afficher cette aide
- `!session` - Informations sur la session actuelle
- `!history` - Afficher l'historique de la session actuelle
- `!sessions` - Lister toutes les sessions sauvegardees
- `!load <session_id>` - Charger une session specifique
- `!delete <session_id>` - Supprimer une session sauvegardee
- `!export` - Exporter la conversation en JSON ou texte
- `!clear` - Effacer la memoire conversationnelle
- `!new` - Demarrer une nouvelle conversation
- `!quit` - Quitter l'interface

## Fonctionnalites:
- **Detection contextuelle automatique** : Le systeme detecte les references aux echanges precedents
- **Sources multiples** : Recherche dans tous les fichiers .md du corpus
- **Memoire conversationnelle** : Continuity entre les questions
- **Sessions persistantes** : Sauvegarde automatique des conversations
            """
            
            self.console.print(Panel(
                Markdown(help_text),
                title="[HELP] Aide",
                border_style="cyan"
            ))
        else:
            print("\n[HELP] AIDE - Commandes disponibles:")
            print("!help - Afficher cette aide")
            print("!session - Informations sur la session")
            print("!history - Afficher l'historique de la session actuelle")
            print("!sessions - Lister toutes les sessions sauvegardees")
            print("!load <session_id> - Charger une session specifique")
            print("!delete <session_id> - Supprimer une session")
            print("!export - Exporter la conversation")
            print("!clear - Effacer la memoire")
            print("!new - Demarrer une nouvelle conversation")
            print("!quit - Quitter l'interface")
    
    def _show_session_info(self):
        """Afficher les informations de session"""
        session_info = self.rag_chain.get_session_info()
        
        if RICH_AVAILABLE:
            info_table = Table(title="[CHART] Informations de session")
            info_table.add_column("Propriete", style="cyan")
            info_table.add_column("Valeur", style="white")
            
            for key, value in session_info.items():
                if isinstance(value, dict):
                    value = ", ".join([f"{k}: {v}" for k, v in value.items()])
                elif isinstance(value, list):
                    value = ", ".join(map(str, value))
                
                info_table.add_row(key, str(value))
            
            self.console.print(info_table)
        else:
            print("\n[CHART] INFORMATIONS DE SESSION:")
            for key, value in session_info.items():
                print(f"  {key}: {value}")
    
    def _show_conversation_history(self):
        """Afficher l'historique des conversations"""
        if not hasattr(self.rag_chain, 'get_conversation_history'):
            if RICH_AVAILABLE:
                self.console.print("[SEARCH] Aucune session active trouvee")
            else:
                print("[SEARCH] Aucune session active trouvee")
            return
        
        history = self.rag_chain.get_conversation_history()
        if not history:
            if RICH_AVAILABLE:
                self.console.print("[INFO] Aucune conversation dans l'historique")
            else:
                print("[INFO] Aucune conversation dans l'historique")
            return
        
        # Utiliser l'historique du RAG system directement
        if RICH_AVAILABLE:
            history_text = f"**Session ID:** {self.rag_chain.session_name}\n"
            history_text += f"**Conversations:** {len(history)}\n\n"
            
            for i, entry in enumerate(history, 1):
                method = entry.get('method', 'rag').upper()
                context = "CONTEXTUEL" if entry.get('context_reference') else "NOUVEAU"
                
                history_text += f"### [CHAT] Interaction {i} [{method}] [{context}]\n"
                history_text += f"**Question:** {entry['question']}\n\n"
                
                # Tronquer la reponse si trop longue
                response = entry['response']
                if len(response) > 200:
                    response = response[:200] + "..."
                history_text += f"**Reponse:** {response}\n\n"
                
                if entry.get('sources'):
                    history_text += f"**Sources:** {len(entry['sources'])} document(s)\n\n"
                history_text += "---\n\n"
            
            self.console.print(Panel(
                Markdown(history_text),
                title="[SOURCES] Historique de conversation",
                border_style="blue"
            ))
        else:
            print(f"\n[SOURCES] HISTORIQUE DE CONVERSATION")
            print(f"Session ID: {self.rag_chain.session_name}")
            print(f"Nombre d'interactions: {len(history)}")
            print("-" * 60)
            
            for i, entry in enumerate(history, 1):
                method = entry.get('method', 'rag').upper()
                context = "CONTEXTUEL" if entry.get('context_reference') else "NOUVEAU"
                
                print(f"\n[CHAT] Interaction {i} [{method}] [{context}]:")
                print(f"  Question: {entry['question']}")
                
                response = entry['response']
                if len(response) > 150:
                    response = response[:150] + "..."
                print(f"  Reponse: {response}")
                
                if entry.get('sources'):
                    print(f"  Sources: {len(entry['sources'])} document(s)")
    
    def _show_all_sessions(self):
        """Afficher toutes les sessions sauvegardees"""
        if not hasattr(self.rag_chain, 'list_all_sessions'):
            if RICH_AVAILABLE:
                self.console.print("[NOTES] Fonction sessions non disponible")
            else:
                print("[NOTES] Fonction sessions non disponible")
            return
            
        sessions = self.rag_chain.list_all_sessions()
        
        if not sessions:
            if RICH_AVAILABLE:
                self.console.print("[NOTES] Aucune session trouvee")
            else:
                print("[NOTES] Aucune session trouvee")
            return
        
        if RICH_AVAILABLE:
            sessions_table = Table(title="[SAVE] Sessions Seance 5")
            sessions_table.add_column("ID Session", style="cyan")
            sessions_table.add_column("Nom Session", style="green")
            sessions_table.add_column("Messages", style="yellow")
            sessions_table.add_column("Status", style="blue")
            
            for session in sessions:
                status = "[ACTIVE] ACTIVE" if session.get('is_current', False) else "[SAVE] Sauvegardee"
                
                sessions_table.add_row(
                    session['session_id'],
                    session.get('session_name', session['session_id']),
                    str(session.get('message_count', 0)),
                    status
                )
            
            self.console.print(sessions_table)
            self.console.print("\n[INFO] Utilisez [bold]!load <session_id>[/bold] pour charger une session")
            self.console.print("[INFO] Utilisez [bold]!delete <session_id>[/bold] pour supprimer une session")
        else:
            print("\n[SAVE] SESSIONS SEANCE 5:")
            print("-" * 60)
            for i, session in enumerate(sessions, 1):
                status = "[ACTIVE]" if session.get('is_current', False) else "[SAUVEGARDEE]"
                print(f"{i}. {session['session_id']} {status}")
                print(f"   Messages: {session.get('message_count', 0)}")
                print()
            print("[INFO] !load <session_id> pour charger, !delete <session_id> pour supprimer")
    
    def _export_conversation(self):
        """Exporter la conversation"""
        if RICH_AVAILABLE:
            format_choice = Prompt.ask(
                "Format d'export",
                choices=["json", "text"],
                default="text"
            )
        else:
            format_choice = input("Format d'export (json/text): ").strip() or "text"
        
        exported_data = self.rag_chain.export_conversation(format_choice)
        
        # Sauvegarder dans un fichier
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"seance5_export_{timestamp}.{format_choice}"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(exported_data)
        
        if RICH_AVAILABLE:
            self.console.print(f"[OK] Conversation exportee: [bold]{filename}[/bold]")
        else:
            print(f"[OK] Conversation exportee: {filename}")
    
    def _clear_memory(self):
        """Effacer la memoire conversationnelle"""
        if RICH_AVAILABLE:
            confirm = Confirm.ask("Etes-vous sur de vouloir effacer la memoire ?")
        else:
            confirm = input("Effacer la memoire ? (y/N): ").lower().startswith('y')
        
        if confirm:
            self.rag_chain.clear_conversation_memory()
            if RICH_AVAILABLE:
                self.console.print("[DELETE] Memoire conversationnelle effacee")
            else:
                print("[DELETE] Memoire conversationnelle effacee")
    
    def _start_new_conversation(self):
        """Demarrer une nouvelle conversation"""
        if RICH_AVAILABLE:
            confirm = Confirm.ask("Demarrer une nouvelle conversation (l'actuelle sera sauvegardee) ?")
        else:
            confirm = input("Nouvelle conversation ? (y/N): ").lower().startswith('y')
        
        if confirm:
            # Utiliser notre systeme de sessions
            if hasattr(self.rag_chain, 'create_new_session'):
                new_session_id = self.rag_chain.create_new_session()
                
                if RICH_AVAILABLE:
                    self.console.print(f"[NEW] Nouvelle conversation demarree: {new_session_id}")
                else:
                    print(f"[NEW] Nouvelle conversation demarree: {new_session_id}")
            else:
                if RICH_AVAILABLE:
                    self.console.print("[WARNING] Gestionnaire de sessions non disponible")
                else:
                    print("[WARNING] Gestionnaire de sessions non disponible")
    
    def _load_session(self, session_id: str):
        """Charger une session specifique"""
        if RICH_AVAILABLE:
            confirm = Confirm.ask(f"Charger la session {session_id} ? (La session actuelle sera sauvegardee)")
        else:
            confirm = input(f"Charger la session {session_id} ? (y/N): ").lower().startswith('y')
        
        if confirm:
            if hasattr(self.rag_chain, 'load_session_by_id'):
                success = self.rag_chain.load_session_by_id(session_id)
                if success:
                    if RICH_AVAILABLE:
                        self.console.print(f"[OK] Session {session_id} chargee avec succes")
                    else:
                        print(f"[OK] Session {session_id} chargee avec succes")
                else:
                    if RICH_AVAILABLE:
                        self.console.print(f"[ERROR] Impossible de charger la session {session_id}")
                    else:
                        print(f"[ERROR] Impossible de charger la session {session_id}")
            else:
                if RICH_AVAILABLE:
                    self.console.print(f"[INFO] Chargement de session non encore implemente pour {session_id}")
                else:
                    print(f"[INFO] Chargement de session non encore implemente pour {session_id}")
    
    def _delete_session(self, session_id: str):
        """Supprimer une session specifique"""
        if RICH_AVAILABLE:
            confirm = Confirm.ask(f"[WARNING] Supprimer definitivement la session {session_id} ?")
        else:
            confirm = input(f"[WARNING] Supprimer la session {session_id} ? (y/N): ").lower().startswith('y')
        
        if confirm:
            if hasattr(self.rag_chain, 'delete_session_by_id'):
                success = self.rag_chain.delete_session_by_id(session_id)
                if success:
                    if RICH_AVAILABLE:
                        self.console.print(f"[DELETE] Session {session_id} supprimee avec succes")
                    else:
                        print(f"[DELETE] Session {session_id} supprimee avec succes")
                else:
                    if RICH_AVAILABLE:
                        self.console.print(f"[ERROR] Impossible de supprimer la session {session_id}")
                    else:
                        print(f"[ERROR] Impossible de supprimer la session {session_id}")
            else:
                if RICH_AVAILABLE:
                    self.console.print(f"[INFO] Suppression de session non encore implementee pour {session_id}")
                else:
                    print(f"[INFO] Suppression de session non encore implementee pour {session_id}")
    
    def _quit_interface(self):
        """Quitter l'interface"""
        self.session_active = False
        self._display_goodbye()
    
    def _display_goodbye(self):
        """Afficher le message d'au revoir"""
        if RICH_AVAILABLE:
            goodbye_text = """
# [GOODBYE] Au revoir !

Merci d'avoir utilise l'interface RAG generique de la **Seance 5**.

Votre conversation a ete sauvegardee automatiquement.
            """
            
            self.console.print(Panel(
                Markdown(goodbye_text),
                title="[GOODBYE] Session terminee",
                border_style="red"
            ))
        else:
            print("\n[GOODBYE] Au revoir ! Session terminee.")

    def _display_error(self, message: str):
        """Afficher un message d'erreur"""
        if RICH_AVAILABLE:
            self.console.print(f"[bold red][ERROR] {message}[/bold red]")
        else:
            print(f"[ERROR] {message}")

def main():
    """Point d'entree principal"""
    interface = EnhancedConversationInterfaceSeance5()
    interface.start_interface()

if __name__ == "__main__":
    main()