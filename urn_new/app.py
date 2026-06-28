from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from pathlib import Path

from db_search import search_urn
from report_generator import generate_html


class App(BaseHTTPRequestHandler):

    def do_GET(self):

        parsed = urlparse(self.path)

        # ---------------- HOME PAGE ----------------
        if parsed.path == "/":

            with open("templates/index.html", "r", encoding="utf-8") as f:
                content = f.read()

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
            return

        # ---------------- STATIC FILES ----------------
        if parsed.path.startswith("/static/"):

            file_path = Path(parsed.path.lstrip("/"))

            if not file_path.exists():
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Static file not found")
                return

            if file_path.suffix == ".css":
                content_type = "text/css"

            elif file_path.suffix == ".js":
                content_type = "application/javascript"

            else:
                content_type = "text/plain"

            self.send_response(200)
            self.send_header("Content-type", content_type)
            self.end_headers()

            with open(file_path, "rb") as f:
                self.wfile.write(f.read())

            return

        # ---------------- SEARCH ----------------
        if parsed.path == "/search":

            params = parse_qs(parsed.query)

            urn = params.get("urn", [""])[0].strip().upper()

            if not urn:

                html = """
                <h2 style="text-align:center;color:red;">
                    URN cannot be empty
                </h2>
                """

            elif len(urn) < 18:

                html = """
                <h2 style="text-align:center;color:red;">
                    URN must be at least 18 characters
                </h2>
                """

            elif len(urn) > 25:

                html = """
                <h2 style="text-align:center;color:red;">
                    URN cannot be greater than 25 characters
                </h2>
                """

            elif not (urn.startswith("SB") or urn.startswith("EIS")):

                html = """
                <h2 style="text-align:center;color:red;">
                    URN must start with SB or EIS
                </h2>
                """

            else:

                print(f"[INFO] Searching URN : {urn}")

                results = search_urn(urn)

                html = generate_html(urn, results)

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
            return

        # ---------------- 404 ----------------
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"404 - Page Not Found")


if __name__ == "__main__":

    server = HTTPServer(("0.0.0.0", 8080), App)

    print("======================================")
    print(" RRN Finder Started")
    print(" URL : http://localhost:8080")
    print("======================================")

    server.serve_forever()