import subprocess
import http.server
import urllib.request
import urllib.error

GATEWAY_URL = "https://syntrix-gateway-541833001986.asia-south1.run.app"

def get_token():
    return subprocess.check_output(["gcloud", "auth", "print-identity-token", f"--audiences={GATEWAY_URL}"]).decode('utf-8').strip()

token = get_token()

class ProxyHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        url = GATEWAY_URL + self.path
        req = urllib.request.Request(url)
        req.add_header('Authorization', f'Bearer {token}')
        
        try:
            with urllib.request.urlopen(req) as response:
                self.send_response(response.status)
                for k, v in response.headers.items():
                    self.send_header(k, v)
                self.end_headers()
                self.wfile.write(response.read())
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            for k, v in e.headers.items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())

print("Starting local proxy at http://localhost:8080 ...")
http.server.HTTPServer(('', 8080), ProxyHTTPRequestHandler).serve_forever()
