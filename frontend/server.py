import os, json
from http.server import HTTPServer, SimpleHTTPRequestHandler

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/config.js':
            self.send_response(200)
            self.send_header('Content-Type', 'application/javascript')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            api_base = os.environ.get('API_BASE', 'http://localhost:8000')
            self.wfile.write(f'window.API_BASE = "{api_base}";\n'.encode())
        else:
            super().do_GET()

HTTPServer(('0.0.0.0', 8000), Handler).serve_forever()
