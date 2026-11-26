# -*- coding: utf-8 -*-
"""DraveSpellenkast (overgenomen van DraveVlag) - verbinding met de spelserver (eigen draad, berichten via een wachtrij).
Copyright (C) 2026 Dravenlock (Roger & Claudio). GNU GPL v3.0."""
import json
import queue
import threading
import time
import urllib.request


def http_naar_ws(adres):
    adres = adres.strip().rstrip("/")
    if not adres.startswith(("http://", "https://")):
        adres = "http://" + adres
    return adres, adres.replace("https://", "wss://", 1).replace("http://", "ws://", 1)


def nieuwe_kamer(adres, wacht=8):
    http, _ = http_naar_ws(adres)
    # Cloudflare weigert de standaard "Python-urllib"-naam (403), dus we noemen onszelf
    req = urllib.request.Request(http + "/kamer", method="POST", data=b"",
                                 headers={"User-Agent": "DraveSpellenkast (Dravenlock)"})
    with urllib.request.urlopen(req, timeout=wacht) as r:
        return json.loads(r.read().decode("utf-8"))["code"]


class Lijn:
    """Houdt de verbinding open en probeert vanzelf opnieuw als hij wegvalt."""

    def __init__(self, adres, code, hallo, pad="bg/kamer"):
        _, ws = http_naar_ws(adres)
        self.url = "%s/%s/%s/ws" % (ws, pad, code)
        self.hallo = hallo
        self.binnen = queue.Queue()
        self.ws = None
        self.aan = True
        self.verbonden = False
        threading.Thread(target=self._draad, daemon=True).start()

    def _draad(self):
        from websockets.sync.client import connect
        wacht = 1.0
        while self.aan:
            try:
                with connect(self.url, open_timeout=8, close_timeout=2, max_size=2 ** 20) as ws:
                    self.ws = ws
                    ws.send(json.dumps(self.hallo))
                    self.verbonden = True
                    self.binnen.put({"t": "_verbonden"})
                    wacht = 1.0
                    for bericht in ws:
                        try:
                            self.binnen.put(json.loads(bericht))
                        except Exception:
                            pass
            except Exception as e:
                self.binnen.put({"t": "_fout", "fout": str(e)[:120]})
            self.ws = None
            if self.verbonden:
                self.verbonden = False
                self.binnen.put({"t": "_weg"})
            if not self.aan:
                break
            time.sleep(wacht)
            wacht = min(wacht * 2, 10)

    def stuur(self, bericht):
        ws = self.ws
        if ws is None:
            return False
        try:
            ws.send(json.dumps(bericht))
            return True
        except Exception:
            return False

    def haal(self):
        uit = []
        while True:
            try:
                uit.append(self.binnen.get_nowait())
            except queue.Empty:
                return uit

    def stop(self):
        self.aan = False
        try:
            if self.ws:
                self.ws.close()
        except Exception:
            pass
