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
    assert "<iframe" not in landing.lower()
    assert "base.bundle" not in landing
    assert "batchSize = 10" in landing
    print(f"PASS: continuous site serves pages 1, 58, 59 and {len(pages)} with no reader iframe.")
finally:
    server.shutdown()
    server.server_close()
