"""Gera o painel interno (painel.html) com os contadores da telemetria."""

import html
import json
import pathlib
import random
import sys
import urllib.request
import webbrowser

HERE = pathlib.Path(__file__).parent
URL = "https://planos2026-telemetria.planos2026.workers.dev/stats?token="
ITEMS = pathlib.Path.home() / "planos-anonimos/_trabalho/propostas_v3.json"
CHOICES = [
    ("a", "Opção A"),
    ("b", "Opção B"),
    ("undecided", "Não consigo escolher"),
    ("info", "Faltam informações"),
]
SOURCES = [
    "whatsapp",
    "instagram",
    "facebook",
    "x",
    "tiktok",
    "google",
    "direto",
    "outro",
]


def fetch():
    token = (HERE / ".stats-token").read_text().strip()
    req = urllib.request.Request(URL + token, headers={'User-Agent': 'planos2026-painel/1.0'})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def demo(items, candidates):
    rnd = random.Random(7)
    c = {"ev:start": 1200, "ev:done": 830, "ev:copy": 210, "ans:envios": 390}
    for i in range(len(items)):
        c[f"ev:q:{i}"] = int(1200 * (1 - 0.035 * i))
    for s in SOURCES:
        c[f"src:{s}"] = rnd.randint(10, 500)
    for it in items:
        for k, _ in CHOICES:
            c[f"ans:{it['id']}:{k}"] = rnd.randint(5, 180)
    for cand in candidates:
        c[f"lider:{cand['key']}"] = rnd.randint(60, 160)
    c["lider:empate"] = 22
    return c


def pct(n, total):
    return 0 if not total else round(100 * n / total)


def bars(rows, total_label):
    top = max([n for _, n in rows] + [1])
    out = []
    for label, n in rows:
        w = 100 * n / top
        out.append(
            f'<div class="row" title="{html.escape(label)}: {n}"><span class="lbl">{html.escape(label)}</span>'
            f'<span class="track"><span class="bar" style="width:{w:.1f}%"></span></span>'
            f'<span class="val">{n}{total_label(n)}</span></div>'
        )
    return "".join(out)


def stacked(item, c):
    counts = [(k, name, c.get(f"ans:{item['id']}:{k}", 0)) for k, name in CHOICES]
    total = sum(n for _, _, n in counts)
    if not total:
        return '<p class="muted">Ainda sem respostas enviadas.</p>'
    seg = "".join(
        f'<span class="seg s-{k}" style="width:{100 * n / total:.2f}%" title="{html.escape(name)}: {n} ({pct(n, total)}%)"></span>'
        for k, name, n in counts
        if n
    )
    names = {"a": item["options"]["a"]["title"], "b": item["options"]["b"]["title"]}
    legend = "".join(
        f'<span class="key"><i class="dot s-{k}"></i>{html.escape(names.get(k, name))}: <b>{pct(n, total)}%</b> <span class="muted">({n})</span></span>'
        for k, name, n in counts
    )
    return f'<div class="stack">{seg}</div><div class="legend">{legend}</div><p class="muted small">{total} respostas</p>'


def build(c, items, candidates, is_demo):
    start, done, copy, sent = (
        c.get(k, 0) for k in ("ev:start", "ev:done", "ev:copy", "ans:envios")
    )
    leaders = [
        (f"{x['name']} ({x['party']})", c.get(f"lider:{x['key']}", 0))
        for x in candidates
    ] + [("Empate", c.get("lider:empate", 0))]
    leaders.sort(key=lambda r: -r[1])
    lead_total = sum(n for _, n in leaders)
    funnel = [
        (f"{i + 1}. {it['title']}", c.get(f"ev:q:{i}", 0)) for i, it in enumerate(items)
    ] + [("Resultado", done)]
    sources = sorted(((s, c.get(f"src:{s}", 0)) for s in SOURCES), key=lambda r: -r[1])
    src_total = sum(n for _, n in sources)
    table = "".join(
        f"<tr><td>{html.escape(k)}</td><td>{v}</td></tr>" for k, v in sorted(c.items())
    )
    per_q = "".join(
        f'<section class="q"><h3>{i + 1}. {html.escape(it["title"])}</h3>{stacked(it, c)}</section>'
        for i, it in enumerate(items)
    )
    banner = (
        '<p class="demo">DADOS FICTÍCIOS (modo demo). Rode sem --demo para ver os números reais.</p>'
        if is_demo
        else ""
    )
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex"><title>Painel interno · planos2026</title><style>
.viz-root{{color-scheme:light;--surface-1:#fcfcfb;--bg:#f2f1ec;--text-primary:#0b0b0b;--text-secondary:#52514e;--line:#e2e1db;--series-1:#2a78d6;--s-a:#2a78d6;--s-b:#eb6834;--s-u:#1baf7a;--s-i:#eda100}}
@media (prefers-color-scheme:dark){{.viz-root{{color-scheme:dark;--surface-1:#1a1a19;--bg:#111110;--text-primary:#fff;--text-secondary:#c3c2b7;--line:#33322f;--series-1:#3987e5;--s-a:#3987e5;--s-b:#d95926;--s-u:#199e70;--s-i:#c98500}}}}
*{{box-sizing:border-box}}body{{margin:0}}
.viz-root{{background:var(--bg);color:var(--text-primary);font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;min-height:100vh;padding:16px}}
main{{max-width:900px;margin:auto}}h1{{font-size:1.5rem;margin:8px 0 4px}}h2{{font-size:1.1rem;margin:0 0 12px}}h3{{font-size:.95rem;margin:0 0 8px}}
.card{{background:var(--surface-1);border:1px solid var(--line);border-radius:14px;padding:16px;margin:14px 0}}
.muted{{color:var(--text-secondary)}}.small{{font-size:.82rem;margin:6px 0 0}}
.tiles{{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}}@media(min-width:640px){{.tiles{{grid-template-columns:repeat(4,1fr)}}}}
.tile{{background:var(--surface-1);border:1px solid var(--line);border-radius:12px;padding:12px}}.tile b{{display:block;font-size:1.7rem}}.tile span{{font-size:.8rem;color:var(--text-secondary)}}
.row{{display:grid;grid-template-columns:minmax(0,1fr) 7.5em;gap:2px 10px;align-items:center;margin:8px 0}}.row .lbl{{grid-column:1/3;white-space:normal}}.val{{text-align:right}}@media(min-width:640px){{.row{{grid-template-columns:minmax(0,1.3fr) minmax(0,2fr) 7.5em}}.row .lbl{{grid-column:auto;white-space:nowrap}}}}
.lbl{{font-size:.85rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}.val{{font-size:.85rem;font-variant-numeric:tabular-nums;color:var(--text-primary)}}
.track{{height:12px}}.bar{{display:block;height:12px;background:var(--series-1);border-radius:0 4px 4px 0;min-width:2px}}
.stack{{display:flex;gap:2px;height:16px;border-radius:4px;overflow:hidden;background:var(--surface-1)}}.seg{{display:block;height:100%}}
.s-a{{background:var(--s-a)}}.s-b{{background:var(--s-b)}}.s-undecided{{background:var(--s-u)}}.s-info{{background:var(--s-i)}}
.legend{{display:flex;flex-wrap:wrap;gap:6px 14px;margin-top:8px;font-size:.82rem}}.key{{display:inline-flex;align-items:center;gap:6px}}.dot{{width:10px;height:10px;border-radius:3px;display:inline-block}}
.q{{border-top:1px solid var(--line);padding:12px 0}}.q:first-of-type{{border-top:0;padding-top:0}}
.demo{{background:#eda10033;border:1px solid #eda100;border-radius:10px;padding:8px 12px;font-weight:600}}
.note{{font-size:.82rem;color:var(--text-secondary)}}table{{width:100%;border-collapse:collapse;font-size:.8rem}}td{{border-bottom:1px solid var(--line);padding:4px}}
</style></head><body><div class="viz-root"><main>
<h1>Painel interno · planos2026</h1><p class="muted">Uso interno. Não publique estes números durante a campanha eleitoral.</p>{banner}
<div class="tiles"><div class="tile"><b>{start}</b><span>começaram o quiz</span></div><div class="tile"><b>{done}</b><span>viram o resultado ({pct(done, start)}%)</span></div>
<div class="tile"><b>{sent}</b><span>enviaram respostas ({pct(sent, done)}% de quem terminou)</span></div><div class="tile"><b>{copy}</b><span>copiaram o resultado</span></div></div>
<section class="card"><h2>Candidato mais parecido, somado</h2>{bars(leaders, lambda n: f" · {pct(n, lead_total)}%")}<p class="note">Só entra quem tocou em "Enviar minhas respostas" ({lead_total} envios). Não é amostra da população.</p></section>
<section class="card"><h2>Onde as pessoas param</h2>{bars(funnel, lambda n: f" · {pct(n, start)}%")}<p class="note">Pessoas que chegaram a cada pergunta, em % de quem começou.</p></section>
<section class="card"><h2>De onde vêm</h2>{bars(sources, lambda n: f" · {pct(n, src_total)}%")}</section>
<section class="card"><h2>O que escolheram em cada pergunta</h2>{per_q}<p class="note">Muito "Não consigo escolher" ou "Faltam informações" indica pergunta confusa.</p></section>
<section class="card"><details><summary>Tabela com todos os contadores</summary><table>{table}</table></details></section>
</main></div></body></html>"""


def main():
    data = json.loads(ITEMS.read_text(encoding="utf-8"))
    items, candidates = data["items"], data["candidates"]
    is_demo = "--demo" in sys.argv
    counts = demo(items, candidates) if is_demo else fetch()
    out = HERE / ("painel-demo.html" if is_demo else "painel.html")
    out.write_text(build(counts, items, candidates, is_demo), encoding="utf-8")
    print(out)
    if "--no-open" not in sys.argv:
        webbrowser.open(out.as_uri())


if __name__ == "__main__":
    main()
