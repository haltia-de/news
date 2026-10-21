"""Bad dates and picture bombs, without GTK windows or network."""
import ast
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import os
from pathlib import Path
import resource
import struct
import time
from types import SimpleNamespace
import unittest
import zlib


source = Path(__file__).resolve().parents[1] / "haltia-news"
tree = ast.parse(source.read_text(encoding="utf-8"))
NAMES = {"PER_FEED", "SHOW", "PAGE_MAX", "parse_when", "showable", "entry_when",
         "entry_image", "one_feed", "headlines", "picture"}
nodes = [node for node in tree.body
         if (isinstance(node, ast.FunctionDef) and node.name in NAMES)
         or (isinstance(node, ast.Assign) and len(node.targets) == 1
             and getattr(node.targets[0], "id", None) in NAMES)]


def load(**extra):
    namespace = {"datetime": datetime, "timezone": timezone,
                 "parsedate_to_datetime": parsedate_to_datetime}
    namespace.update(extra)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(source), "exec"), namespace)
    return namespace


def entry(title, **dates):
    return dict(title=title, link="https://example.org/" + title, summary="text", **dates)


FEEDS = {
    "https://good.example/feed": [
        entry("good", published_parsed=(2026, 10, 20, 9, 0, 0, 0, 293, 0))],
    "https://bad.example/feed": [
        entry("zero-parsed", published_parsed=(0, 0, 0, 0, 0, 0, 0, 0, 0)),
        entry("zero-text", published="0000-00-00T00:00:00Z"),
        entry("far", published_parsed=(9999, 12, 31, 23, 59, 59, 4, 365, 0)),
        entry("far-text", published="9999-12-31T23:59:59Z"),
        "not an entry",
    ],
    "https://broken.example/feed": None,  # entries that cannot be read at all
}


class DateTests(unittest.TestCase):
    def setUp(self):
        # Year 9999 overflows only east of UTC.
        self.tz = os.environ.get("TZ")
        os.environ["TZ"] = "Europe/Moscow"
        time.tzset()
        self.ns = load(get=lambda url, timeout=10: (url, url, ""),
                       parse_feed=lambda raw: SimpleNamespace(entries=FEEDS[raw]))

    def tearDown(self):
        if self.tz is None:
            os.environ.pop("TZ", None)
        else:
            os.environ["TZ"] = self.tz
        time.tzset()

    def test_bad_feed_beside_good_one(self):
        feeds = [(url.split("/")[2], url, "") for url in FEEDS]
        items = self.ns["headlines"](feeds)
        titles = [item[2] for item in items]
        self.assertEqual(titles[0], "good")
        self.assertEqual(set(titles),
                         {"good", "zero-parsed", "zero-text", "far", "far-text"})
        for stamp, *_rest in items[1:]:
            self.assertIsNone(stamp)
        self.assertEqual(items[0][0], datetime(2026, 10, 20, 9, tzinfo=timezone.utc))

    def test_year_9999_is_dropped(self):
        when = self.ns["entry_when"](entry("far", published_parsed=(9999, 12, 31, 23, 0, 0)))
        self.assertIsNone(when)
        when = self.ns["entry_when"](entry("near", published="2026-10-22T10:00:00+03:00"))
        self.assertEqual(when.astimezone().hour, 10)


def png(width, height):
    """A 1-bit grey PNG of zeros, compressed row by row."""
    def chunk(kind, data):
        return (struct.pack(">I", len(data)) + kind + data
                + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF))

    packer = zlib.compressobj(9)
    row = bytes(1 + (width + 7) // 8)
    idat = b"".join(packer.compress(row) for _ in range(height)) + packer.flush()
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 1, 0, 0, 0, 0))
            + chunk(b"IDAT", idat) + chunk(b"IEND", b""))


try:
    import gi
    gi.require_version("GdkPixbuf", "2.0")
    from gi.repository import GdkPixbuf
except (ImportError, ValueError):
    GdkPixbuf = None


@unittest.skipIf(GdkPixbuf is None, "GdkPixbuf is not available")
class PictureTests(unittest.TestCase):
    def picture(self, data):
        ns = load(GdkPixbuf=GdkPixbuf,
                  download=lambda url, limit, timeout: (data, url, {}))
        return ns["picture"]("https://example.org/picture.png")

    def test_png_bomb_refused_before_decoding(self):
        data = png(16000, 16000)
        self.assertLess(len(data), 3 * 1024 * 1024)
        before = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        self.assertIsNone(self.picture(data))
        grown = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss - before
        self.assertLess(grown, 100 * 1024)  # KiB: the full image is 768 MB

    def test_normal_png_scaled(self):
        pix = self.picture(png(1800, 600))
        self.assertEqual((pix.get_width(), pix.get_height()), (900, 300))


if __name__ == "__main__":
    unittest.main()
