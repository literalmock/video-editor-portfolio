#!/usr/bin/env python3
"""
Smart local server for Framer exports.
Serves extensionless routes (like /about, /projects) as text/html.
"""
import http.server, os, mimetypes, urllib.parse

PORT = 3000
ROOT = os.path.dirname(os.path.abspath(__file__))

MIME = {
    '.html': 'text/html; charset=utf-8',
    '.css':  'text/css',
    '.js':   'application/javascript',
    '.json': 'application/json',
    '.png':  'image/png',
    '.jpg':  'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif':  'image/gif',
    '.svg':  'image/svg+xml',
    '.ico':  'image/x-icon',
    '.woff': 'font/woff',
    '.woff2':'font/woff2',
    '.ttf':  'font/ttf',
    '.mp4':  'video/mp4',
    '.webp': 'image/webp',
}

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse URL
        parsed = urllib.parse.urlparse(self.path)
        url_path = urllib.parse.unquote(parsed.path)

        # Build filesystem path
        fs_path = os.path.normpath(os.path.join(ROOT, url_path.lstrip('/')))

        # Security: don't serve outside ROOT
        if not fs_path.startswith(ROOT):
            self.send_error(403)
            return

        # If directory → try index.html inside it
        if os.path.isdir(fs_path):
            fs_path = os.path.join(fs_path, 'index.html')

        # If file doesn't exist → try adding .html
        if not os.path.isfile(fs_path):
            if os.path.isfile(fs_path + '.html'):
                fs_path = fs_path + '.html'
            else:
                self.send_error(404, f"Not found: {url_path}")
                return

        # Determine MIME type
        _, ext = os.path.splitext(fs_path)
        content_type = MIME.get(ext.lower(), 'text/html; charset=utf-8')

        # Read and serve
        try:
            with open(fs_path, 'rb') as f:
                data = f.read()
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self.send_error(500, str(e))

    def log_message(self, fmt, *args):
        print(f"  {self.address_string()} → {fmt % args}")

if __name__ == '__main__':
    os.chdir(ROOT)
    with http.server.HTTPServer(('', PORT), Handler) as httpd:
        print(f"\n  🚀 http://localhost:{PORT}\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n  Stopped.")
