from http.server import BaseHTTPRequestHandler
from backend.main import app
from fastapi.testclient import TestClient
import json

CHUNK_SIZE = 1024 * 1024  # 1MB chunks

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            client = TestClient(app)
            with client.get(self.path, stream=True) as response:
                self.send_response(response.status_code)
                
                # Set headers for streaming response
                self.send_header('Transfer-Encoding', 'chunked')
                for key, value in response.headers.items():
                    if key.lower() != 'content-length':  # Skip content-length as we're using chunked encoding
                        self.send_header(key, value)
                self.end_headers()
                
                # Stream the response in chunks
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:
                        # Write chunk size in hexadecimal format
                        self.wfile.write(f'{len(chunk):X}\r\n'.encode())
                        self.wfile.write(chunk)
                        self.wfile.write(b'\r\n')
                
                # End chunked response
                self.wfile.write(b'0\r\n\r\n')
                
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
