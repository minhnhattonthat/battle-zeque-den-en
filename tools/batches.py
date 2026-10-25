"""batches.py: phase-6 translation batches for script/dialogue.json.

    python -X utf8 tools/batches.py split [--size 60]   untranslated entries -> work/tl/bNNN.tsv + build/terms_bNNN.txt
    python -X utf8 tools/batches.py check bNNN          validate work/tl/bNNN.out.tsv; prints OK or one line per error
    python -X utf8 tools/batches.py merge bNNN..        checked batches -> the `en` field, wrapped to the box width
    python -X utf8 tools/batches.py pairs bNNN..        work/tl/pairs_<first>.txt for the reviewer
    python -X utf8 tools/batches.py fit BOX "text"      wrap a draft the way merge will and print each line's width

English is written as one paragraph per entry: the tool wraps it greedily by pixel width (fonts/vwf.txt advances,
budgets in tools/boxes.py). `{n}` forces a line break, `{page}` a new page; pages of 3 lines are automatic in the
game. `{end}` is appended by the tool. Effect codes ({c04}...) must match the Japanese.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import font  # noqa: E402
from boxes import BOXES  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "script" / "dialogue.json"
TL = ROOT / "work" / "tl"
GLOSSARY = ROOT / "glossary.md"
CODE = re.compile(r"\{\w+\}")
EFFECT = re.compile(r"\{c\w\w\}|\{wait\}")
# enemy portrait (high byte of the "uses" portrait word) -> speaker; low byte -> heroine (docs/re/debug.md)
ENEMY = {"05": "Seiryu", "03": "Koryu", "04": "Genbu", "08": "fire-clan guard", "07": "Suzaku", "06": "Byakko"}
HEROINE = {"00": "Hamusu", "01": "Rufu", "02": "Kairu"}
SCENE = {range(0, 3): "ch1 boss", range(3, 6): "ch2 boss", range(6, 9): "ch3 boss", range(9, 12): "ch4 boss",
         range(12, 15): "ch5 boss", range(15, 18): "final boss, before", range(19, 20): "ch3 boss defeated",
         range(23, 24): "ch4 boss defeated", range(24, 25): "ch5 boss defeated", range(27, 30): "final boss defeated",
         range(30, 45): "chapter opening", range(45, 48): "ch4 temple, guard", range(48, 51): "ch4 guard defeated",
         range(84, 87): "profile screen"}
HONORIFICS = {"さん": "-san", "様": "-sama"}
STUB = 6  # a paragraph's last line under this many characters is an orphaned word (tests/test_lint.py)
NOT_HONORIFIC = ("お嬢さん",)


def load():
    return json.loads(SCRIPT.read_text(encoding="utf-8"))


def speaker(e):
    slot, _, port = e["uses"][0].split(":")
    scene = next((v for r, v in SCENE.items() if int(slot) in r), "?")
    if scene == "chapter opening":
        scene = f"ch{(int(slot) - 30) // 3 + 1} opening"
    if e["box"] == "profile":
        return "profile", scene
    if e["box"] == "toutetsu":
        who = "Totetsu"
    elif e["box"] == "enemy":
        who = ENEMY.get(port[:2], "?")
    else:
        who = e["heroine"] or "?"
    hers = sorted({HEROINE.get(u.split(":")[2][2:], "?") for u in e["uses"]})
    to = "" if e["box"] == "hero" else f" (to {'/'.join(hers)})"
    return who + to, scene


def width(line, adv):
    return sum(adv.get(c, 0) for c in CODE.sub("", line))  # unknown characters are reported by check


def greedy(seg, px, adv):
    lines, cur = [], ""
    for word in seg.split():
        trial = f"{cur} {word}" if cur else word
        if cur and width(trial, adv) > px:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    return lines + [cur]


def stub(line):
    """An orphaned last line: one word, or under STUB characters (phase-8 QA flagged "power.", "Suzaku?")."""
    s = CODE.sub("", line).strip()
    return " " not in s or len(s) < STUB


def wrap(text, px, adv):
    """Paragraph text -> lines joined by {n}, pages by {page}; greedy on spaces. No {end}. A segment whose last
    line would be a stub (see stub()) is re-wrapped at the narrowest width that keeps its line count."""
    pages = []
    for page in text.split("{page}"):
        lines = []
        for seg in page.split("{n}"):
            out = greedy(seg, px, adv)
            narrow = px
            while len(out) > 1 and stub(out[-1]) and narrow > px // 2:
                narrow -= 1
                trial = greedy(seg, narrow, adv)
                if len(trial) != len(out):
                    break
                out = trial
            lines += out
        pages.append("{n}".join(lines))
    return "{page}".join(pages)


def glossary():
    """[(jp, [en forms], [avoid forms])] from the glossary tables (JP cells split on ' / ', '(...)' rows skipped)."""
    rows = []
    for line in GLOSSARY.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not line.startswith("|") or len(cells) < 5 or cells[0] in ("JP", "---") or cells[0].startswith("("):
            continue
        avoid = [a.strip() for a in cells[4].split(",") if a.strip()]
        jps, ens = cells[0].split(" / "), cells[1].split(" / ")
        for i, jp in enumerate(jps):
            rows.append((jp, [ens[min(i, len(ens) - 1)]], avoid))
    return rows


def read_tsv(path, cols):
    out = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            parts = line.split("\t")
            if len(parts) != cols:
                raise SystemExit(f"{path.name}:{n}: {len(parts)} columns, want {cols}")
            out.append(parts)
    return out


def split(size):
    TL.mkdir(parents=True, exist_ok=True)
    todo = [e for e in load() if e["jp"].removesuffix("{end}") and not e["en"]]
    n = max((int(p.stem[1:4]) for p in TL.glob("b[0-9][0-9][0-9].tsv")), default=0)
    gl = glossary()
    for i in range(0, len(todo), size):
        n += 1
        name, chunk = f"b{n:03d}", todo[i:i + size]
        path = TL / f"{name}.tsv"
        if path.exists():
            raise SystemExit(f"{path} exists")
        rows = []
        for e in chunk:
            who, scene = speaker(e)
            jp = e["jp"].removesuffix("{end}").replace("{n}", " / ")
            rows.append(f"{e['id']}\t{who}\t{scene}\t{BOXES[e['box']]['px']}px/line\t{jp}")
        path.write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
        text = "".join(e["jp"] for e in chunk)
        terms = [f"{jp} = {en[0]}" + (f" (avoid: {', '.join(av)})" if av else "") for jp, en, av in gl if jp in text]
        (ROOT / "build").mkdir(exist_ok=True)
        (ROOT / "build" / f"terms_{name}.txt").write_text("\n".join(terms) + "\n", encoding="utf-8", newline="\n")
        print(f"{path.relative_to(ROOT)}: {len(chunk)} entries, {len(text)} jp chars, {len(terms)} terms")


def check(name, quiet=False):
    """Error strings for work/tl/<name>.out.tsv (empty = OK)."""
    src = read_tsv(TL / f"{name}.tsv", 5)
    out_path = TL / f"{name}.out.tsv"
    if not out_path.exists():
        print(f"{out_path.relative_to(ROOT)} missing")
        return ["missing"]
    out = read_tsv(out_path, 2)
    by_id = {e["id"]: e for e in load()}
    adv = font.advance_map(font.load())
    gl = glossary()
    errs = []
    ids, got = [r[0] for r in src], [r[0] for r in out]
    if ids != got:
        errs.append(f"ids differ from the input: missing {sorted(set(ids) - set(got))}, "
                    f"extra {sorted(set(got) - set(ids))}, duplicates {[i for i, c in Counter(got).items() if c > 1]}"
                    + (", order differs" if sorted(ids) == sorted(got) else ""))
    for id_, en in out:
        if id_ in by_id:
            errs += entry_errors(by_id[id_], en, adv, gl)
    if not quiet:
        print("\n".join(errs) if errs else f"OK {name}: {len(out)} entries")
    return errs


def entry_errors(e, en, adv, gl):
    """Lint one entry's English (paragraph or merged text, no {end}); also run by tests/test_lint.py."""
    id_, errs = e["id"], []
    box = BOXES[e["box"]]
    bad = sorted({c for c in CODE.sub("", en) if not (" " <= c <= "~") or c in "{}[]"})
    if bad:
        errs.append(f"{id_}: characters not allowed: {''.join(bad)!r} (ASCII only, no {{}} [] outside codes)")
    unknown = [c for c in CODE.findall(en) if c not in ("{n}", "{page}") and not EFFECT.fullmatch(c)]
    if unknown:
        errs.append(f"{id_}: unknown codes {unknown} ({{end}} is added by the tool)")
    if Counter(EFFECT.findall(en)) != Counter(EFFECT.findall(e["jp"])):
        errs.append(f"{id_}: effect codes {EFFECT.findall(en)} != jp {EFFECT.findall(e['jp'])}")
    if re.search(r"(^|\{n\}|\{page\})\s*(\{n\}|\{page\}|$)", en):
        errs.append(f"{id_}: empty line (a break at column 0 is ignored by the game)")
    wrapped = wrap(en, box["px"], adv)
    lines = re.split(r"\{n\}|\{page\}", wrapped)
    for ln in lines:
        if width(ln, adv) > box["px"]:
            errs.append(f"{id_}: word too wide: {ln!r} {width(ln, adv)} px > {box['px']}")
    if e["box"] == "profile" and len(lines) > box["lines"]:
        errs.append(f"{id_}: {len(lines)} lines, the profile shows {box['lines']}")
    for p, page in enumerate(wrapped.split("{page}"), 1):
        if e["box"] != "profile" and page.count("{n}") >= box["lines"]:
            errs.append(f"{id_}: page {p} wraps to {page.count('{n}') + 1} lines (box shows {box['lines']}): "
                        "shorten, or put {page} at a sentence break")
    flat = re.sub(r"\{n\}|\{page\}", " ", en).lower()  # merged text breaks terms across lines
    for jp, ens, avoid in gl:
        if jp in e["jp"] and not any(x.lower() in flat for x in ens):
            errs.append(f"{id_}: glossary: {jp} -> {ens[0]!r} missing")
        for a in avoid if jp in e["jp"] else ():  # "old man" is fine outside an おっちゃん line
            if re.search(rf"\b{re.escape(a)}\b", en):
                errs.append(f"{id_}: glossary: avoid {a!r}")
    jp = e["jp"]
    for x in NOT_HONORIFIC:
        jp = jp.replace(x, "")
    for h, form in HONORIFICS.items():
        if jp.count(h) > en.count(form):
            errs.append(f"{id_}: honorific {h} -> {form!r} missing (D1: keep honorifics)")
    return errs


def merge(names):
    data = load()
    by_id = {e["id"]: e for e in data}
    adv = font.advance_map(font.load())
    for name in names:
        if check(name, quiet=True):
            raise SystemExit(f"{name} fails check; run: python -X utf8 tools/batches.py check {name}")
    for name in names:
        for id_, en in read_tsv(TL / f"{name}.out.tsv", 2):
            e = by_id[id_]
            e["en"] = wrap(en, BOXES[e["box"]]["px"], adv) + "{end}"
        print(f"merged {name}")
    with open(SCRIPT, "w", encoding="utf-8", newline="\n") as f:  # same format as tools/extract.py
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")


def pairs(names):
    rows = []
    for name in names:
        out = dict(read_tsv(TL / f"{name}.out.tsv", 2))
        for id_, who, scene, _, jp in read_tsv(TL / f"{name}.tsv", 5):
            rows.append(f">> {id_} | {who} | {scene} | {jp}\n   {out.get(id_, '(missing)')}\n")
    path = TL / f"pairs_{names[0]}.txt"
    path.write_text("\n".join(rows), encoding="utf-8", newline="\n")
    print(path.relative_to(ROOT))


def fit(box, text):
    adv = font.advance_map(font.load())
    px = BOXES[box]["px"]
    for p, page in enumerate(wrap(text, px, adv).split("{page}"), 1):
        for n, ln in enumerate(page.split("{n}"), 1):
            w = width(ln, adv)
            print(f"{p}.{n} {w:3d}/{px}{' OVER' if w > px else ''} | {ln}")


def main(argv):
    if not argv or argv[0] not in ("split", "check", "merge", "pairs", "fit"):
        print(__doc__)
        return 2
    cmd, args = argv[0], argv[1:]
    if cmd == "split":
        split(int(args[args.index("--size") + 1]) if "--size" in args else 60)
    elif cmd == "check":
        return 1 if any([check(n) for n in args]) else 0
    elif cmd == "merge":
        merge(args)
    elif cmd == "pairs":
        pairs(args)
    else:
        fit(args[0], args[1])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
