from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

from db_search import search_urn
from report_generator import generate_html


class App(BaseHTTPRequestHandler):

    def do_GET(self):

        parsed = urlparse(self.path)

        # ---------------- HOME PAGE ----------------
        if parsed.path == "/":

            with open("templates/index.html", "r") as f:
                html = f.read()

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode())
            return

        # ---------------- STATIC CSS ----------------
        if parsed.path == "/static/style.css":

            with open("static/style.css", "r") as f:
                css = f.read()

            self.send_response(200)
            self.send_header("Content-type", "text/css")
            self.end_headers()
            self.wfile.write(css.encode())
            return

        # ---------------- SEARCH ROUTE ----------------

        if parsed.path == "/search":

            params = parse_qs(parsed.query)
            urn = params.get("urn", [""])[0].strip()

            # ---------------- VALIDATIONS ----------------
            if not urn:
                html = "<h2 style='color:red;text-align:center;'>URN cannot be empty</h2>"

            elif len(urn) < 18:
                html = "<h2 style='color:red;text-align:center;'>URN must be at least 18 characters</h2>"

            elif len(urn) > 25:
                html = "<h2 style='color:red;text-align:center;'>URN cannot be greater than 25 characters</h2>"

            elif not (urn.startswith("SB") or urn.startswith("EIS")):
                html = "<h2 style='color:red;text-align:center;'>URN must start with SB or EIS</h2>"

            else:
                print(f"[INFO] Searching URN: {urn}")

                results = search_urn(urn)
                html = generate_html(urn, results)

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode())

            return
        # ---------------- 404 ----------------
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"Not Found")


# ---------------- SERVER START ----------------
server = HTTPServer(("0.0.0.0", 8080), App)

print("Server Running on http://localhost:8080")

server.serve_forever()