#!/usr/bin/env python3
"""Serve the game over HTTPS, so browsers allow the controller (Gamepad API) on a network address.

Browsers only hand controllers to "secure" pages: https://, or http://localhost. Plain http:// on a LAN
address (http://192.168.0.21:8000) hides them. This serves the repo over https with a self-signed
certificate made on first run (tools/.cert/); accept the browser's warning once.

    python3 tools/serve-https.py              # https://<this machine>:8443
    python3 tools/serve-https.py --port 9443 --bind 192.168.0.21
"""
import argparse, http.server, os, ssl, subprocess, socket

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(here)
ap = argparse.ArgumentParser()
ap.add_argument('--port', type=int, default=8443)
ap.add_argument('--bind', default='0.0.0.0')
args = ap.parse_args()

cert_dir = os.path.join(here, '.cert')
cert, key = os.path.join(cert_dir, 'cert.pem'), os.path.join(cert_dir, 'key.pem')
if not os.path.exists(cert):
    os.makedirs(cert_dir, exist_ok=True)
    host = socket.gethostname()
    ips = subprocess.run(['hostname', '-I'], capture_output=True, text=True).stdout.split() if os.name == 'posix' else []
    san = ','.join([f'DNS:{host}', 'DNS:localhost', 'IP:127.0.0.1'] + [f'IP:{ip}' for ip in ips if ':' not in ip])
    subprocess.run(['openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes', '-days', '825', '-keyout', key, '-out', cert,
                    '-subj', f'/CN={host}', '-addext', f'subjectAltName={san}'], check=True, capture_output=True)

os.chdir(root)
handler = http.server.SimpleHTTPRequestHandler
handler.extensions_map.update({'.js': 'text/javascript', '.wasm': 'application/wasm', '.glb': 'model/gltf-binary'})
httpd = http.server.ThreadingHTTPServer((args.bind, args.port), handler)
ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER); ctx.load_cert_chain(cert, key)
httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)
print(f'Serving {root} at https://{args.bind}:{args.port}/ (self-signed: accept the warning once)')
httpd.serve_forever()
