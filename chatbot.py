import gradio as gr
import ollama
import re
import socket
import json
import os
from typing import Dict, List, Tuple, Union
from pathlib import Path
from urllib.parse import quote

class MultimodalChatbot:
    def __init__(self):
        self.model_name = "llama3.1:8b"
        self.history_file = "./history/chat_history5.json"
        Path(self.history_file).touch(exist_ok=True)
        self.conversation_history = self._load_history()

    def _load_history(self) -> List[Dict]:
        try:
            if os.path.getsize(self.history_file) > 0:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Erreur de chargement de l'historique: {str(e)}")
        return []

    def _save_history(self):
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erreur de sauvegarde de l'historique: {str(e)}")

    def generate_response(self, message: str) -> Dict:
        image_response = self._process_image_request(message)
        if image_response:
            self._update_history(message, image_response["content"])
            return image_response
        return self._generate_text_response(message)

    def _generate_text_response(self, message: str) -> Dict:
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=self.conversation_history + [{"role": "user", "content": message}]
            )
            content = response['message']['content']
            self._update_history(message, content)
            return {"type": "text", "content": content}
        except Exception as e:
            error_msg = f"Erreur: {str(e)}"
            self._update_history(message, error_msg)
            return {"type": "error", "content": error_msg}

    def _update_history(self, user_msg: str, assistant_msg: str):
        """Met à jour l'historique et sauvegarde"""
        self.conversation_history.append({"role": "user", "content": user_msg})
        self.conversation_history.append({"role": "assistant", "content": assistant_msg})
        self._save_history()

def find_available_port(start_port: int = 7860, max_attempts: int = 20) -> int:
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    raise OSError(f"Aucun port disponible entre {start_port}-{start_port + max_attempts - 1}")

def create_gradio_interface():
    chatbot = MultimodalChatbot()
    
    with gr.Blocks(theme=gr.themes.Base(), title="Yu- -Ai") as demo:
        gr.Markdown("ChatBot")
        
        chat_interface = gr.Chatbot(
            height=500,
            render_markdown=True,
            type="messages",
            value=chatbot.conversation_history
        )
        
        msg = gr.Textbox(label="Votre message", placeholder="Tapez votre message ici...")
        clear = gr.Button("Effacer l'historique")
        
        def respond(message: str, chat_history: List[Dict]) -> Tuple[str, List[Dict]]:
            response = chatbot.generate_response(message)
            updated_history = chatbot.conversation_history
            if response["type"] == "error":
                gr.Warning(response["content"])
            return "", updated_history
        
        def clear_history():
            chatbot.conversation_history = []
            chatbot._save_history()
            return []
        
        msg.submit(respond, [msg, chat_interface], [msg, chat_interface])
        clear.click(clear_history, None, chat_interface, queue=False)
    
    return demo

if __name__ == "__main__":
    try:
        port = find_available_port()
        print(f"Lancement sur le port {port}")        
        app = create_gradio_interface()
        app.launch(
            server_port=port,
            share=False,
            show_error=True
        )
    except Exception as e:
        print(f"Erreur critique: {str(e)}")