#!/usr/bin/env python3
"""Synthé de bruitages pour une cartouche. Copie-le et ajoute tes propres cues :
un jeu a besoin de ses sons à lui, pas de ceux de l'exemple.

    python3 son.py impact          # joue et rend la main TOUT DE SUITE
    python3 son.py impact --in 2   # pareil, mais déclenché dans 2 secondes
    python3 son.py menace --loop   # nappe de fond, en boucle, détachée
    python3 son.py --stop          # coupe la boucle
    python3 son.py --demo          # audition de tous les cues, avec les noms
    python3 son.py impact -o x.wav # écrit le wav sans jouer

Pur stdlib : ni numpy, ni sox, ni banque de sons. Une seconde de son coûte
quelques millisecondes à synthétiser.
"""
import array, math, os, random, subprocess, sys, tempfile, wave

SR = 22050
PID = os.path.join(tempfile.gettempdir(), "cartouche-son-loop.pid")

# --- oscillateurs ----------------------------------------------------------
# freq est soit un nombre, soit une fonction de u (0→1 sur la durée) : c'est ce
# qui donne les glissandos, et un glissando s'entend là où un bip ne s'entend pas.

def osc(shape, freq, dur, detune=0.0):
    n = int(SR * dur)
    out = [0.0] * n
    phase = 0.0
    for i in range(n):
        u = i / max(1, n - 1)
        f = freq(u) if callable(freq) else freq
        f *= (1.0 + detune)
        phase += 2 * math.pi * f / SR
        p = phase % (2 * math.pi)
        if shape == "sine":
            v = math.sin(p)
        elif shape == "square":
            v = 1.0 if p < math.pi else -1.0
        elif shape == "saw":
            v = p / math.pi - 1.0
        elif shape == "tri":
            v = 2 * abs(p / math.pi - 1.0) - 1.0
        else:
            v = random.uniform(-1, 1)
        out[i] = v
    return out


def noise(dur):
    return [random.uniform(-1, 1) for _ in range(int(SR * dur))]


# --- enveloppes et filtres -------------------------------------------------
# L'enveloppe n'est pas un ornement : un son sans attaque ni chute claque, et
# un clic est ce que l'oreille retient à la place du son.

def env(buf, a=0.004, hold=0.0, curve=3.0):
    n = len(buf)
    na, nh = int(SR * a), int(SR * hold)
    for i in range(n):
        if i < na:
            g = i / max(1, na)
        elif i < na + nh:
            g = 1.0
        else:
            u = (i - na - nh) / max(1, n - na - nh)
            g = (1.0 - u) ** curve
        buf[i] *= g
    return buf


def lowpass(buf, cutoff):
    a = math.exp(-2 * math.pi * cutoff / SR)
    y = 0.0
    for i, x in enumerate(buf):
        y = (1 - a) * x + a * y
        buf[i] = y
    return buf


def crush(buf, bits=5):
    """Réduction de résolution : la couleur chiptune, en une ligne."""
    q = 2 ** (bits - 1)
    return [round(x * q) / q for x in buf]


def reverb(buf, delay=0.055, feedback=0.38, wet=0.35, taps=5):
    """Écho court à répétitions : c'est ce qui transforme un bip en un lieu."""
    d = int(SR * delay)
    out = list(buf) + [0.0] * (d * taps)
    for t in range(1, taps + 1):
        g = wet * (feedback ** (t - 1))
        off = d * t
        for i, x in enumerate(buf):
            out[i + off] += x * g
    return out


def mix(parts):
    n = max(len(b) for b, _ in parts)
    out = [0.0] * n
    for b, g in parts:
        for i, x in enumerate(b):
            out[i] += x * g
    return out


def seq(chunks, gap=0.0):
    out = []
    for c in chunks:
        out += c + [0.0] * int(SR * gap)
    return out


def norm(buf, peak=0.7):
    m = max((abs(x) for x in buf), default=0.0)
    if m < 1e-9:
        return buf
    k = peak / m
    return [x * k for x in buf]


NOTES = {"c": 0, "d": 2, "e": 4, "f": 5, "g": 7, "a": 9, "b": 11}


def hz(name):
    """'a4' -> 440.0, 'c#5' -> 554.4"""
    p = NOTES[name[0].lower()]
    i = 1
    if len(name) > i and name[i] in "#b":
        p += 1 if name[i] == "#" else -1
        i += 1
    return 440.0 * 2 ** ((p - 9 + (int(name[i:]) - 4) * 12) / 12)


def melody(names, dur=0.11, shape="square", gap=0.01, detune=0.006):
    """Deux oscillateurs légèrement désaccordés : ça épaissit, et ça s'entend."""
    out = []
    for nm in names:
        f = hz(nm)
        a = env(osc(shape, f, dur), a=0.005, hold=dur * 0.3)
        b = env(osc(shape, f, dur, detune=detune), a=0.005, hold=dur * 0.3)
        out.append(mix([(a, 0.6), (b, 0.4)]))
    return seq(out, gap)


# --- les cues --------------------------------------------------------------
# Un cue est une phrase, pas un bip. Trois règles qui marchent partout :
# un glissando plutôt qu'une note tenue ; du bruit filtré pour le corps ;
# de la réverbération, parce qu'un son sec n'a pas de lieu.

CUES = {}


def cue(fn):
    CUES[fn.__name__] = fn
    return fn


@cue
def impact():
    """Un coup qui porte : corps grave qui plonge + claque de bruit."""
    body = env(osc("sine", lambda u: 150 * (1 - 0.62 * u), 0.20), a=0.001, curve=3.5)
    slap = lowpass(env(noise(0.10), a=0.0005, curve=5.0), 1100)
    return reverb(mix([(body, 1.0), (slap, 0.55)]), wet=0.22)


@cue
def degat():
    """Le joueur encaisse : carré descendant, sale, écrasé en bits."""
    b = env(osc("square", lambda u: 330 * (1 - 0.72 * u), 0.26), a=0.002, curve=2.2)
    return reverb(crush(b, 4), wet=0.25)


@cue
def trouvaille():
    """Arpège montant. Le son que le joueur veut réentendre."""
    return reverb(melody(["c5", "e5", "g5", "c6"], dur=0.085), delay=0.07, wet=0.4)


@cue
def piece():
    """Deux notes brèves, très haut : la petite récompense."""
    return reverb(melody(["b5", "e6"], dur=0.07, gap=0.0), wet=0.3)


@cue
def menace():
    """Nappe basse et battante : deux graves désaccordés qui pulsent.
    À lancer en --loop quand quelque chose arrive."""
    a = osc("saw", 55.0, 2.0)
    b = osc("saw", 55.0, 2.0, detune=0.012)
    d = lowpass(mix([(a, 0.5), (b, 0.5)]), 260)
    n = int(len(d))
    for i in range(n):                      # respiration lente
        d[i] *= 0.55 + 0.45 * math.sin(2 * math.pi * 0.5 * i / SR)
    return env(d, a=0.5, hold=1.0, curve=1.2)


@cue
def porte():
    """Frottement de pierre : bruit filtré très bas, longue réverbération."""
    n = lowpass(env(noise(0.55), a=0.08, curve=1.6), 320)
    return reverb(n, delay=0.09, feedback=0.5, wet=0.5, taps=6)


@cue
def des():
    """Le lot de dés qui tombe : quelques clics secs, aléatoires."""
    out = []
    for _ in range(5):
        c = lowpass(env(noise(0.035), a=0.0005, curve=6.0), 2600)
        out.append(c + [0.0] * int(SR * random.uniform(0.02, 0.07)))
    return reverb(seq(out), wet=0.3)


@cue
def victoire():
    return reverb(melody(["c5", "e5", "g5", "c6", "g5", "c6"], dur=0.13),
                  delay=0.08, wet=0.45)


@cue
def mort():
    """Descente mineure, lente, avec une queue longue."""
    return reverb(melody(["a4", "f4", "d4", "a3"], dur=0.26, shape="tri"),
                  delay=0.1, feedback=0.55, wet=0.5, taps=7)


# --- sortie ----------------------------------------------------------------

def write(buf, path):
    buf = norm(buf)
    buf += [0.0] * int(SR * 0.12)   # coussin de silence : sans lui, les lecteurs
    a = array.array("h")            # coupent la fin des sons courts
    for x in buf:
        a.append(max(-32767, min(32767, int(x * 32767))))
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(a.tobytes())
    return path


def player(path, loop=False):
    if loop:
        for c in (["mpv", "--no-video", "--really-quiet", "--loop=inf", path],
                  ["ffplay", "-nodisp", "-loglevel", "quiet", "-loop", "0", path]):
            if which(c[0]):
                return c
    for c in (["paplay", path], ["pw-play", path],
              ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", path]):
        if which(c[0]):
            return c
    return None


def which(x):
    return any(os.access(os.path.join(p, x), os.X_OK)
               for p in os.environ.get("PATH", "").split(os.pathsep))


def play(path, loop=False, wait=False, delay=0.0):
    """Détaché par défaut : la commande rend la main immédiatement et le son
    continue pendant que tu écris le beat suivant. `delay` décale le
    déclenchement, pour viser le moment où ton texte s'affichera."""
    cmd = player(path, loop)
    if not cmd:
        return
    if delay > 0:
        cmd = ["sh", "-c", "sleep %g; exec \"$@\"" % delay, "-"] + cmd
    p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         stdin=subprocess.DEVNULL, start_new_session=True)
    if loop:
        open(PID, "w").write(str(p.pid))
    if wait:
        p.wait()


def stop():
    try:
        os.killpg(os.getpgid(int(open(PID).read())), 15)
    except Exception:
        pass
    try:
        os.remove(PID)
    except Exception:
        pass


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--stop" in args:
        stop(); sys.exit()
    if "--list" in args:
        print(" ".join(sorted(CUES))); sys.exit()
    if "--demo" in args:
        for name in sorted(CUES):
            print(name, flush=True)
            play(write(CUES[name](), tempfile.mktemp(suffix=".wav")), wait=True)
        sys.exit()
    out = args[args.index("-o") + 1] if "-o" in args else None
    lead = float(args[args.index("--in") + 1]) if "--in" in args else 0.0
    skip = {out, str(lead)} | {a for a in args if a.startswith("-")}
    names = [a for a in args if a not in skip]
    if not names:
        print("cues :", " ".join(sorted(CUES))); sys.exit(1)
    for name in names:
        buf = CUES[name]()
        path = write(buf, out or tempfile.mktemp(suffix=".wav"))
        if not out:
            play(path, loop="--loop" in args, delay=lead)
