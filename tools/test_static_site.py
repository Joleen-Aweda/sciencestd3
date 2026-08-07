import json
import threading
import urllib.request
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
handler = partial(SimpleHTTPRequestHandler, directory=ROOT)
server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()

try:
    base = f"http://127.0.0.1:{server.server_port}/"
    with urllib.request.urlopen(base + "content/pages.json") as response:
        pages = json.load(response)
    assert [page["page_number"] for page in pages] == list(range(1, len(pages) + 1))
    for number in (1, 58, 59, len(pages)):
        with urllib.request.urlopen(base + pages[number - 1]["href"]) as response:
            html = response.read().decode("utf-8")
        assert response.status == 200
        assert f'content="{number}"' in html
        assert 'id="content"' in html
    with urllib.request.urlopen(base + "index.html") as response:
        landing = response.read().decode("utf-8")
    assert 'url=pg001_sec001.html' in landing
    first_html = urllib.request.urlopen(base + pages[0]["href"]).read().decode("utf-8")
    assert 'id="nav-container"' in first_html
    assert 'assets/base.bundle.local.js' in first_html
    print(f"PASS: native ADT pages 1, 58, 59 and {len(pages)} load with consecutive navigation.")
finally:
    server.shutdown()
    server.server_close()
