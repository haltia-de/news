"""Exercise the downloader without GTK or third-party dependencies."""
import ast
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import Mock, patch


source = Path(__file__).resolve().parents[1] / "haltia-news"
tree = ast.parse(source.read_text(encoding="utf-8"))
download_node = next(node for node in tree.body
                     if isinstance(node, ast.FunctionDef) and node.name == "download")
namespace = {"time": time}
exec(compile(ast.Module(body=[download_node], type_ignores=[]), str(source), "exec"),
     namespace)
download = namespace["download"]


class DownloadTests(unittest.TestCase):
    def test_complete_response_clears_reader(self):
        response = Mock()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        response.geturl.return_value = "http://localhost/feed.txt"
        response.isclosed.side_effect = [False, True]

        def read(size):
            response.fp = None
            return b"news"

        response.read1.side_effect = read
        opener = Mock()
        opener.open.return_value = response
        with patch("urllib.request.build_opener", return_value=opener):
            raw, final, headers = download("http://localhost/feed.txt", 100, 2)
        self.assertEqual(raw, b"news")
        response.read1.assert_called_once()

    def test_local_http_server(self):
        with tempfile.TemporaryDirectory() as directory:
            # Reserve an available port before starting the stdlib CLI server.
            with socket.socket() as sock:
                sock.bind(("127.0.0.1", 0))
                port = sock.getsockname()[1]
            server = subprocess.Popen(
                [sys.executable, "-m", "http.server", str(port),
                 "--bind", "127.0.0.1", "--directory", directory],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            try:
                deadline = time.monotonic() + 5
                while True:
                    try:
                        with socket.create_connection(("127.0.0.1", port), timeout=0.1):
                            break
                    except OSError:
                        if server.poll() is not None or time.monotonic() >= deadline:
                            self.fail("Local HTTP server did not start")
                        time.sleep(0.02)
                for size, limit in ((0, 100), (23, 100), (150000, 200000),
                                    (150000, 150000), (150000, 70000)):
                    with self.subTest(size=size, limit=limit):
                        body = (b"local news\n" * (size // 11 + 1))[:size]
                        Path(directory, "feed.txt").write_bytes(body)
                        url = "http://127.0.0.1:%d/feed.txt" % port
                        raw, final, headers = download(url, limit, 2)
                        self.assertEqual(raw, body[:limit])
                        self.assertEqual(final, url)
                        self.assertEqual(int(headers["Content-Length"]), size)
            finally:
                server.terminate()
                server.wait(timeout=5)


if __name__ == "__main__":
    unittest.main()
