#!/usr/bin/env python3
"""Renderer de console pour une cartouche. Copie-le et adapte-le : les zones et
les jauges doivent parler la langue de TA cartouche, pas celle de l'exemple.

    python3 console.py etat.json

Il ne sait rien du jeu. Il prend un état, il rend un cadre de largeur fixe.
Aucune couleur, aucun ANSI : la sortie est destinée à être recopiée telle
quelle dans un bloc de code.
"""
import json, os, sys, textwrap, unicodedata

STYLE = {
    "width": 80, "pad": 2,
    "tl": "┌", "tr": "┐", "bl": "└", "br": "┘",
    "h": "─", "v": "│", "ml": "├", "mr": "┤",
    "bar_full": "█", "bar_empty": "░", "bar_width": 12,
    "rail": False,          # True = pas de bordure droite (rail ouvert)
    "art_align": "center",  # center | left
}


def w(s):
    """Largeur d'affichage réelle (les glyphes larges comptent double)."""
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)


def clip(s, n):
    while w(s) > n:
        s = s[:-1]
    return s


class Frame:
    def __init__(self, st):
        self.s = st
        self.inner = st["width"] - 2 if not st["rail"] else st["width"] - 1
        self.text = self.inner - 2 * st["pad"]
        self.out = []

    def rule(self, left, right, title=None):
        s, fill = self.s, self.s["h"]
        bar = fill * self.inner
        if title:
            t = clip(str(title), self.text)
            head = fill * s["pad"] + " " + t + " "
            bar = head + fill * (self.inner - w(head))
        self.out.append(left + bar + (right if not s["rail"] else ""))

    def line(self, s=""):
        st = self.s
        body = " " * st["pad"] + clip(s, self.text)
        if st["rail"]:
            self.out.append((st["v"] + body).rstrip())
        else:
            self.out.append(st["v"] + body + " " * (self.inner - w(body)) + st["v"])

    def prose(self, txt):
        for para in str(txt).split("\n"):
            if not para.strip():
                self.line()
                continue
            for ln in textwrap.wrap(para, self.text) or [""]:
                self.line(ln)

    def art(self, lines):
        block = [clip(l.rstrip("\n"), self.text) for l in lines]
        while block and not block[0].strip():
            block.pop(0)
        while block and not block[-1].strip():
            block.pop()
        if self.s["art_align"] == "center" and block:
            off = max(0, (self.text - max(w(l) for l in block)) // 2)
            block = [" " * off + l for l in block]
        for l in block:
            self.line(l)

    def bar(self, cur, mx):
        n = self.s["bar_width"]
        k = 0 if mx <= 0 else max(0, min(n, round(n * cur / mx)))
        return self.s["bar_full"] * k + self.s["bar_empty"] * (n - k)

    def gauges(self, rows):
        pads = [r for r in rows if "bar" in r]
        lw = max((w(r.get("label", "")) for r in pads), default=0)
        for r in rows:
            if "bar" in r:
                cur, mx = r["bar"]
                s = f"{r.get('label',''):<{lw}}  {self.bar(cur, mx)} {cur}/{mx}"
                if r.get("right"):
                    s += "  " + r["right"]
            else:
                s = r.get("text", "")
            self.line(s)


def render(state):
    st = dict(STYLE, **state.get("style", {}))
    f = Frame(st)
    f.rule(st["tl"], st["tr"], state.get("title"))
    for zone in state.get("zones", []):
        kind = zone.get("kind")
        if kind == "rule":
            f.rule(st["ml"], st["mr"], zone.get("title"))
            continue
        if kind == "blank":
            f.line()
            continue
        f.line()
        if kind == "prose":
            f.prose(zone.get("text", ""))
        elif kind == "art":
            src = zone.get("file")
            if src and os.path.exists(src):
                lines = open(src).read().split("\n")
            else:
                lines = zone.get("lines", [])   # repli : une vue manquante ne
            f.art(lines)                        # casse pas le beat en cours
        elif kind == "gauges":
            f.gauges(zone.get("rows", []))
        elif kind == "raw":
            for l in zone.get("lines", []):
                f.line(l)
        f.line()
    f.rule(st["bl"], st["br"])
    return "\n".join(f.out)


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else None
    print(render(json.load(open(src) if src else sys.stdin)))
