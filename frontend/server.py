#!/usr/bin/env python3
"""
Servidor HTTP simples para servir o frontend do Super Trunfo IA.
"""

import http.server
import socketserver
import os
import sys

# Porta do servidor frontend
PORT = 3000

# Diretório público
PUBLIC_DIR = os.path.join(os.path.dirname(__file__), 'public')

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PUBLIC_DIR, **kwargs)
    
    def end_headers(self):
        # Adiciona headers CORS
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def main():
    """Inicia o servidor HTTP."""
    
    if not os.path.exists(PUBLIC_DIR):
        print(f"Erro: Diretório '{PUBLIC_DIR}' não encontrado!")
        sys.exit(1)
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"╔══════════════════════════════════════════════════════════╗")
        print(f"║          Super Trunfo IA - Frontend Server              ║")
        print(f"╚══════════════════════════════════════════════════════════╝")
        print(f"")
        print(f"  🌐 Servidor rodando em: http://localhost:{PORT}")
        print(f"  📁 Servindo arquivos de: {PUBLIC_DIR}")
        print(f"")
        print(f"  ⚠️  Certifique-se de que o backend está rodando em:")
        print(f"     http://localhost:8000")
        print(f"")
        print(f"  Pressione Ctrl+C para parar o servidor")
        print(f"")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n\n✅ Servidor encerrado!")
            sys.exit(0)

if __name__ == "__main__":
    main()
