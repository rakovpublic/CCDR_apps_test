"""On-disk cached HTTP fetcher with SHA-256 checksums.

Network calls are made at most once per (URL, cache_dir) pair. The cache
is keyed by a hash of the URL; the raw bytes are written next to a
.sha256 sidecar.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from pathlib import Path
from urllib.parse import urlparse

import requests

LOG = logging.getLogger("ccdr.cache")

DEFAULT_CACHE = Path(os.environ.get("CCDR_CACHE", Path(__file__).resolve().parents[3] / "data_cache"))


class DataCache:
    def __init__(self, root: Path | None = None, timeout: float = 30.0):
        self.root = Path(root or DEFAULT_CACHE)
        self.root.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout
        self._index_path = self.root / "_index.json"
        self._index: dict = {}
        if self._index_path.exists():
            try:
                self._index = json.loads(self._index_path.read_text(encoding="utf-8"))
            except Exception:
                self._index = {}

    def _key(self, url: str) -> str:
        return hashlib.sha256(url.encode("utf-8")).hexdigest()[:24]

    def _path(self, url: str) -> Path:
        ext = Path(urlparse(url).path).suffix or ".bin"
        return self.root / f"{self._key(url)}{ext}"

    def get(self, url: str, *, headers: dict | None = None, force: bool = False) -> bytes:
        p = self._path(url)
        if p.exists() and not force:
            data = p.read_bytes()
            return data
        LOG.info("fetching %s", url)
        h = {"User-Agent": "ccdr-tests/0.1 (research harness)"}
        if headers:
            h.update(headers)
        r = requests.get(url, headers=h, timeout=self.timeout)
        r.raise_for_status()
        data = r.content
        p.write_bytes(data)
        checksum = hashlib.sha256(data).hexdigest()
        (p.with_suffix(p.suffix + ".sha256")).write_text(checksum, encoding="utf-8")
        self._index[url] = {"path": str(p.relative_to(self.root)), "sha256": checksum, "n_bytes": len(data)}
        self._index_path.write_text(json.dumps(self._index, indent=2, sort_keys=True), encoding="utf-8")
        return data

    def get_text(self, url: str, encoding: str = "utf-8", **kw) -> str:
        return self.get(url, **kw).decode(encoding, errors="replace")

    def get_json(self, url: str, **kw):
        return json.loads(self.get(url, **kw))

    def checksum(self, url: str) -> str:
        p = self._path(url).with_suffix(self._path(url).suffix + ".sha256")
        return p.read_text().strip() if p.exists() else ""

    def aggregate_checksum(self, urls: list) -> str:
        h = hashlib.sha256()
        for u in sorted(urls):
            h.update(self.checksum(u).encode("ascii"))
        return h.hexdigest()
