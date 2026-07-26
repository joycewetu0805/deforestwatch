"""
Rend la synthèse technique en page web autonome, à partir de la même source
que le PDF (le `document()` de scripts.generate_synthese_technique).

Les figures sont encodées en base64 dans le HTML : le fichier produit est
autonome, consultable hors ligne et publiable tel quel.

Usage :
    python -m scripts.generate_synthese_html [chemin_de_sortie.html]
"""

from __future__ import annotations

import base64
import html
import sys
from pathlib import Path

from config.settings import PROJECT_ROOT
from src.utils.logger import get_logger

log = get_logger("generate_synthese_html")

FIG_DIR = PROJECT_ROOT / "docs" / "figures"
DEFAULT_OUT = PROJECT_ROOT / "docs" / "synthese_technique.html"


def _slug(text: str) -> str:
    keep = [c.lower() if c.isalnum() else "-" for c in text]
    out = "".join(keep)
    while "--" in out:
        out = out.replace("--", "-")
    return out.strip("-")[:60]


def _data_uri(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def _esc(text: str) -> str:
    return html.escape(str(text), quote=False)


# ──────────────────────────────────────────────────────────────────────────
# Feuille de style
# ──────────────────────────────────────────────────────────────────────────
CSS = """
:root {
  color-scheme: light;
  --paper:      #fbfbf7;
  --paper-2:    #f3f4ec;
  --ink:        #14180f;
  --ink-2:      #3d4237;
  --ink-3:      #6b6f62;
  --accent:     #0b6e2d;
  --accent-2:   #a8701c;
  --rule:       #dcded2;
  --note-bg:    #eef4ea;
  --code-bg:    #f1f3ea;
  --shadow:     0 1px 2px rgba(20, 24, 15, .06);
  --sans: ui-sans-serif, -apple-system, "Segoe UI", "Helvetica Neue", Arial, sans-serif;
  --serif: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, "Times New Roman", serif;
  --mono: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
}
@media (prefers-color-scheme: dark) {
  :root:where(:not([data-theme="light"])) {
    color-scheme: dark;
    --paper:    #111409;
    --paper-2:  #191d12;
    --ink:      #eef0e4;
    --ink-2:    #c3c7b6;
    --ink-3:    #8f9483;
    --accent:   #57ac6e;
    --accent-2: #d9a441;
    --rule:     #2c3122;
    --note-bg:  #182013;
    --code-bg:  #1a1e13;
    --shadow:   0 1px 2px rgba(0, 0, 0, .4);
  }
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --paper:    #111409;
  --paper-2:  #191d12;
  --ink:      #eef0e4;
  --ink-2:    #c3c7b6;
  --ink-3:    #8f9483;
  --accent:   #57ac6e;
  --accent-2: #d9a441;
  --rule:     #2c3122;
  --note-bg:  #182013;
  --code-bg:  #1a1e13;
  --shadow:   0 1px 2px rgba(0, 0, 0, .4);
}
:root[data-theme="light"] {
  color-scheme: light;
  --paper:    #fbfbf7;
  --paper-2:  #f3f4ec;
  --ink:      #14180f;
  --ink-2:    #3d4237;
  --ink-3:    #6b6f62;
  --accent:   #0b6e2d;
  --accent-2: #a8701c;
  --rule:     #dcded2;
  --note-bg:  #eef4ea;
  --code-bg:  #f1f3ea;
}

body {
  margin: 0;
  background: var(--paper);
  color: var(--ink);
  font-family: var(--serif);
  font-size: 17px;
  line-height: 1.62;
  -webkit-text-size-adjust: 100%;
}

/* ── Couverture ── */
.cover {
  background: var(--accent);
  color: #fff;
  padding: clamp(2.5rem, 7vw, 5.5rem) clamp(1.25rem, 5vw, 3rem) clamp(2rem, 5vw, 4rem);
}
.cover-inner { max-width: 62rem; margin: 0 auto; }
.cover h1 {
  font-family: var(--sans);
  font-weight: 800;
  letter-spacing: -.025em;
  font-size: clamp(2.1rem, 6vw, 3.6rem);
  line-height: 1.05;
  margin: 0 0 .6rem;
  text-wrap: balance;
}
.cover p {
  font-family: var(--sans);
  font-size: clamp(1rem, 2.2vw, 1.2rem);
  margin: 0;
  opacity: .92;
  max-width: 46ch;
}
.cover .meta {
  margin-top: 2rem;
  display: flex;
  flex-wrap: wrap;
  gap: .5rem 2rem;
  font-family: var(--mono);
  font-size: .78rem;
  letter-spacing: .04em;
  text-transform: uppercase;
  opacity: .85;
}

/* ── Ossature ── */
.shell {
  max-width: 78rem;
  margin: 0 auto;
  padding: 0 clamp(1.25rem, 5vw, 3rem);
  display: grid;
  grid-template-columns: 1fr;
  gap: 3rem;
}
@media (min-width: 62rem) {
  .shell { grid-template-columns: 15rem minmax(0, 1fr); gap: 4rem; }
}

/* ── Sommaire ── */
.toc {
  font-family: var(--sans);
  font-size: .875rem;
  padding-top: 3rem;
}
@media (min-width: 62rem) {
  .toc { position: sticky; top: 0; align-self: start; max-height: 100vh; overflow-y: auto; }
}
.toc h2 {
  font-size: .72rem;
  text-transform: uppercase;
  letter-spacing: .12em;
  color: var(--ink-3);
  margin: 0 0 .9rem;
  font-weight: 700;
}
.toc ol { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: .1rem; }
.toc a {
  display: flex;
  gap: .6rem;
  padding: .35rem .5rem .35rem 0;
  color: var(--ink-2);
  text-decoration: none;
  border-left: 2px solid transparent;
  padding-left: .7rem;
  transition: color .15s, border-color .15s;
}
.toc a:hover, .toc a:focus-visible { color: var(--accent); border-left-color: var(--accent); }
.toc a .n { color: var(--ink-3); font-variant-numeric: tabular-nums; }

/* ── Contenu ── */
main { padding: 3rem 0 6rem; min-width: 0; }
.prose { max-width: 40rem; }
p { margin: 0 0 1.15rem; }
.lead { font-size: 1.08rem; color: var(--ink-2); }

h2.sec {
  font-family: var(--sans);
  font-weight: 800;
  letter-spacing: -.02em;
  font-size: clamp(1.6rem, 3.4vw, 2.1rem);
  line-height: 1.15;
  margin: 4.5rem 0 1.6rem;
  padding-top: 1.4rem;
  border-top: 3px solid var(--accent);
  color: var(--ink);
  text-wrap: balance;
  scroll-margin-top: 1rem;
}
h2.sec:first-of-type { margin-top: 1rem; }
h3 {
  font-family: var(--sans);
  font-weight: 700;
  font-size: 1.22rem;
  letter-spacing: -.01em;
  color: var(--accent);
  margin: 2.6rem 0 .8rem;
  text-wrap: balance;
}
h4 {
  font-family: var(--sans);
  font-weight: 700;
  font-size: 1rem;
  margin: 1.9rem 0 .5rem;
  color: var(--ink);
}

ul, ol { margin: 0 0 1.3rem; padding-left: 1.4rem; }
li { margin-bottom: .5rem; }
ol { counter-reset: none; }

hr { border: 0; border-top: 1px solid var(--rule); margin: 2.5rem 0; }

/* ── Encadrés ── */
.note {
  background: var(--note-bg);
  border-left: 3px solid var(--accent);
  padding: 1rem 1.15rem;
  margin: 1.8rem 0 2rem;
  font-size: .95rem;
  color: var(--ink-2);
}
.note p:last-child { margin-bottom: 0; }

/* ── Code ── */
pre {
  background: var(--code-bg);
  border: 1px solid var(--rule);
  border-radius: 3px;
  padding: .9rem 1rem;
  overflow-x: auto;
  margin: 1.4rem 0 1.8rem;
}
code {
  font-family: var(--mono);
  font-size: .82rem;
  line-height: 1.6;
}
p code, li code, td code {
  background: var(--code-bg);
  padding: .1em .35em;
  border-radius: 3px;
  font-size: .86em;
}

/* ── Tableaux ── */
.table-wrap { overflow-x: auto; margin: 1.5rem 0 2rem; max-width: 52rem; }
table { border-collapse: collapse; width: 100%; font-family: var(--sans); font-size: .88rem; }
thead th {
  background: var(--accent);
  color: #fff;
  text-align: left;
  font-weight: 700;
  padding: .6rem .75rem;
  white-space: nowrap;
}
tbody td {
  padding: .55rem .75rem;
  border-bottom: 1px solid var(--rule);
  vertical-align: top;
  color: var(--ink-2);
}
tbody tr:nth-child(odd) td { background: var(--paper-2); }
tbody td:first-child { color: var(--ink); font-weight: 600; }

/* ── Figures ── */
figure {
  margin: 2.2rem 0 2.6rem;
  max-width: 52rem;
}
figure img {
  display: block;
  width: 100%;
  height: auto;
  background: #fff;
  border: 1px solid var(--rule);
  border-radius: 3px;
  box-shadow: var(--shadow);
}
figcaption {
  font-family: var(--sans);
  font-size: .82rem;
  color: var(--ink-3);
  margin-top: .65rem;
  line-height: 1.5;
}

footer {
  border-top: 1px solid var(--rule);
  margin-top: 4rem;
  padding-top: 1.5rem;
  font-family: var(--sans);
  font-size: .84rem;
  color: var(--ink-3);
  max-width: 40rem;
}

a { color: var(--accent); }
:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
@media (prefers-reduced-motion: reduce) {
  * { transition: none !important; scroll-behavior: auto !important; }
}
html { scroll-behavior: smooth; }
"""


# ──────────────────────────────────────────────────────────────────────────
# Rendu
# ──────────────────────────────────────────────────────────────────────────
def render(blocks) -> str:
    cover_title = cover_sub = ""
    sections: list[tuple[str, str]] = []      # (ancre, titre) pour le sommaire
    body: list[str] = []
    in_prose = False

    def open_prose():
        nonlocal in_prose
        if not in_prose:
            body.append('<div class="prose">')
            in_prose = True

    def close_prose():
        nonlocal in_prose
        if in_prose:
            body.append("</div>")
            in_prose = False

    first_para = True
    skip_next_list = False
    for kind, content in blocks:
        if kind == "cover":
            cover_title, cover_sub = content
            continue

        # Le sommaire du PDF fait doublon avec la navigation latérale.
        if kind == "h3" and content.strip().lower() == "sommaire":
            skip_next_list = True
            continue
        if skip_next_list and kind in ("ol", "ul"):
            skip_next_list = False
            continue

        if kind == "h1":
            close_prose()
            anchor = _slug(content)
            sections.append((anchor, content))
            body.append(f'<h2 class="sec" id="{anchor}">{_esc(content)}</h2>')
            open_prose()
        elif kind == "h2":
            open_prose()
            body.append(f"<h3>{_esc(content)}</h3>")
        elif kind == "h3":
            open_prose()
            body.append(f"<h4>{_esc(content)}</h4>")
        elif kind == "p":
            open_prose()
            cls = ' class="lead"' if first_para else ""
            body.append(f"<p{cls}>{_esc(content)}</p>")
            first_para = False
        elif kind == "ul":
            open_prose()
            items = "".join(f"<li>{_esc(i)}</li>" for i in content)
            body.append(f"<ul>{items}</ul>")
        elif kind == "ol":
            open_prose()
            items = "".join(f"<li>{_esc(i)}</li>" for i in content)
            body.append(f"<ol>{items}</ol>")
        elif kind == "code":
            open_prose()
            body.append(f"<pre><code>{_esc(content)}</code></pre>")
        elif kind == "note":
            open_prose()
            body.append(f'<aside class="note"><p>{_esc(content)}</p></aside>')
        elif kind == "table":
            close_prose()
            headers, rows, _widths = content
            head = "".join(f"<th>{_esc(h)}</th>" for h in headers)
            trs = "".join(
                "<tr>" + "".join(f"<td>{_esc(c)}</td>" for c in row) + "</tr>"
                for row in rows
            )
            body.append(
                '<div class="table-wrap"><table>'
                f"<thead><tr>{head}</tr></thead><tbody>{trs}</tbody>"
                "</table></div>"
            )
            open_prose()
        elif kind == "img":
            close_prose()
            name, caption, _w = content
            path = FIG_DIR / name
            if not path.exists():
                log.warning(f"Figure absente : {path}")
                continue
            body.append(
                f'<figure><img src="{_data_uri(path)}" alt="{_esc(caption)}">'
                f"<figcaption>{_esc(caption)}</figcaption></figure>"
            )
            open_prose()
        elif kind == "hr":
            open_prose()
            body.append("<hr>")
        elif kind == "page":
            continue

    close_prose()

    toc = "".join(
        f'<li><a href="#{a}"><span class="n">{i}</span><span>{_esc(t.split(". ", 1)[-1])}</span></a></li>'
        for i, (a, t) in enumerate(sections, 1)
    )

    return f"""<title>{_esc(cover_title)} — Synthèse technique</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>{CSS}</style>

<header class="cover">
  <div class="cover-inner">
    <h1>{_esc(cover_title)}</h1>
    <p>{_esc(cover_sub)}</p>
    <div class="meta">
      <span>Mai-Ndombe, RDC</span>
      <span>2015 – 2025</span>
      <span>9 sections · 13 figures</span>
    </div>
  </div>
</header>

<div class="shell">
  <nav class="toc" aria-label="Sommaire">
    <h2>Sommaire</h2>
    <ol>{toc}</ol>
  </nav>
  <main>
    {"".join(body)}
    <footer>
      Document généré par <code>scripts/generate_synthese_html.py</code> à partir
      de la même source que <code>docs/SYNTHESE_TECHNIQUE.pdf</code>. Les figures
      sont produites par <code>scripts/figures_synthese.py</code> depuis le code
      du projet. Pour tout régénérer : <code>make synthese</code>.
    </footer>
  </main>
</div>
"""


def main() -> None:
    from scripts.generate_synthese_technique import document

    out = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(document()), encoding="utf-8")
    log.info(f"Synthese web -> {out} ({out.stat().st_size / 1024:.0f} Ko)")


if __name__ == "__main__":
    main()
