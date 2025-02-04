from http.server import BaseHTTPRequestHandler
from backend.main import app

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            from fastapi.testclient import TestClient
            client = TestClient(app)
            response = client.get("/api/mirrors")
            
            self.send_response(response.status_code)
            for key, value in response.headers.items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(response.content)
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "detail": str(e)
            }).encode('utf-8'))
