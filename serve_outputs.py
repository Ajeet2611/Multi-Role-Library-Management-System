"""
Simple HTTP server to preview and download generated documents
(Presentation .pptx and Documentation .docx) from the output folder.
Runs on 0.0.0.0:5000 so Replit preview can access it.
"""

import http.server
import socketserver
import os
from urllib.parse import quote

PORT = 5000
OUTPUT_DIR = "output"


HTML_TEMPLATE = """<!doctype html>
<html lang="hi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Library Management System — Generated Documents</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, "Segoe UI", "Nirmala UI", Roboto, sans-serif;
    background: linear-gradient(135deg, #0B1F3A 0%, #1F4E79 100%);
    min-height: 100vh; padding: 40px 20px; color: #1f1f1f;
  }}
  .wrap {{ max-width: 880px; margin: 0 auto; }}
  header {{
    text-align: center; color: #fff; margin-bottom: 32px;
  }}
  header h1 {{ font-size: 32px; margin-bottom: 8px; letter-spacing: .5px; }}
  header p {{ font-size: 14px; opacity: .85; }}
  .gold-bar {{
    width: 80px; height: 3px; background: #B8860B;
    margin: 14px auto; border-radius: 2px;
  }}
  .card {{
    background: #fff; border-radius: 14px; padding: 28px;
    margin-bottom: 18px; box-shadow: 0 8px 24px rgba(0,0,0,.18);
    display: flex; align-items: center; gap: 20px;
    transition: transform .18s ease;
  }}
  .card:hover {{ transform: translateY(-3px); }}
  .icon {{
    width: 64px; height: 64px; border-radius: 12px;
    display: grid; place-items: center; font-size: 28px;
    flex-shrink: 0; color: #fff;
  }}
  .icon.docx {{ background: #2B579A; }}
  .icon.pptx {{ background: #D24726; }}
  .meta {{ flex: 1; }}
  .meta h2 {{
    font-size: 18px; color: #0B1F3A; margin-bottom: 4px; font-weight: 700;
  }}
  .meta p {{ font-size: 13px; color: #555; margin-bottom: 6px; }}
  .meta .size {{
    display: inline-block; background: #f3f4f6; padding: 3px 10px;
    border-radius: 20px; font-size: 12px; color: #444;
  }}
  .btn {{
    padding: 11px 22px; border-radius: 8px; text-decoration: none;
    background: #B8860B; color: #fff; font-weight: 600; font-size: 14px;
    transition: background .15s ease;
  }}
  .btn:hover {{ background: #9a720a; }}
  .empty {{
    background: #fff; padding: 40px; border-radius: 12px;
    text-align: center; color: #666;
  }}
  footer {{
    text-align: center; color: #cfd6e0; margin-top: 30px;
    font-size: 12px;
  }}
</style>
</head>
<body>
  <div class="wrap">
    <header>
      <h1>📚 Library Management System</h1>
      <div class="gold-bar"></div>
      <p>Generated Documents — Presentation & Documentation</p>
    </header>
    {cards}
    <footer>© Ajeet Prasad · 2026 · Generated from Replit Environment</footer>
  </div>
</body>
</html>
"""


class IndexedHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            return self._render_index()
        # Serve files from output/ directly
        if self.path.startswith("/files/"):
            filename = self.path.replace("/files/", "", 1)
            file_path = os.path.join(OUTPUT_DIR, filename)
            if os.path.isfile(file_path):
                self.send_response(200)
                if filename.endswith(".docx"):
                    ct = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                elif filename.endswith(".pptx"):
                    ct = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
                else:
                    ct = "application/octet-stream"
                self.send_header("Content-Type", ct)
                self.send_header("Content-Disposition",
                                 f'attachment; filename="{filename}"')
                self.send_header("Content-Length", str(os.path.getsize(file_path)))
                self.end_headers()
                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())
                return
            self.send_error(404)
            return
        self.send_error(404)

    def _render_index(self):
        cards = []
        if os.path.isdir(OUTPUT_DIR):
            files = sorted(os.listdir(OUTPUT_DIR))
            for fname in files:
                fpath = os.path.join(OUTPUT_DIR, fname)
                if not os.path.isfile(fpath):
                    continue
                size_kb = os.path.getsize(fpath) / 1024
                size_str = f"{size_kb:.1f} KB" if size_kb < 1024 \
                    else f"{size_kb/1024:.2f} MB"
                if fname.endswith(".docx"):
                    icon, icon_cls = "📄", "docx"
                    title = "Comprehensive Documentation Report"
                    desc = "90+ pages — पूरा technical documentation Hinglish में, " \
                           "16 chapters, diagrams, screenshots placeholders"
                elif fname.endswith(".pptx"):
                    icon, icon_cls = "📊", "pptx"
                    title = "Project Presentation"
                    desc = "12 slides — Hinglish presentation, navy + gold theme, " \
                           "with speaker notes और animation suggestions"
                else:
                    icon, icon_cls = "📁", "docx"
                    title = fname
                    desc = ""

                cards.append(f"""
                <div class="card">
                  <div class="icon {icon_cls}">{icon}</div>
                  <div class="meta">
                    <h2>{title}</h2>
                    <p>{desc}</p>
                    <span class="size">{fname} · {size_str}</span>
                  </div>
                  <a href="/files/{quote(fname)}" class="btn">Download</a>
                </div>
                """)
        if not cards:
            cards = ['<div class="empty">No generated documents yet. '
                     'Run the generator scripts to create them.</div>']

        html = HTML_TEMPLATE.format(cards="\n".join(cards))
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def log_message(self, format, *args):
        # Quieter logs
        print(f"[server] {self.address_string()} - {format % args}")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    handler = IndexedHandler
    with socketserver.TCPServer(("0.0.0.0", PORT), handler) as httpd:
        print(f"Serving on http://0.0.0.0:{PORT}")
        print(f"Output directory: {os.path.abspath(OUTPUT_DIR)}")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
