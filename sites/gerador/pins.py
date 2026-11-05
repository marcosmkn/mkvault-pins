"""Gera pins 1000x1500 no padrão de cada site.
Uso: python3 pins.py lote.json pasta_saida
lote.json: lista de pins {id, site, layout, ...}. Ver exemplos em lote-inicial.json.
"""
import json, sys, os, html, asyncio, pathlib
from playwright.async_api import async_playwright

BASE = pathlib.Path(__file__).resolve().parent
FONTS = BASE / "fonts"

THEMES = {
  "cafe": dict(name="Viciado em Café", url="viciadoemcafe.com.br", bg="#FFFCF8", ink="#2B1A12", muted="#6B4B36",
               accent="#7A4A22", on_accent="#FFFFFF", card="#FFFFFF", line="#E8DCCB", photo_bg="#FFFFFF",
               display="Fraunces", body="Inter", dark=False),
  "btu": dict(name="Calcula BTU", url="calculabtu.com.br", bg="#FFFFFF", ink="#12161C", muted="#5B636E",
              accent="#1C7CF2", on_accent="#FFFFFF", card="#F5F7FA", line="#E9ECF0", photo_bg="#FFFFFF",
              display="Inter", body="Inter", dark=False),
  "tv": dict(name="escolhaTV", url="escolhatv.com.br", bg="#0A0E16", ink="#E7ECF5", muted="#A3ADC2",
             accent="#4C8DFF", on_accent="#FFFFFF", card="#141B28", line="#222C3D", photo_bg="#FFFFFF",
             display="Manrope", body="Manrope", dark=True),
  "tech": dict(name="Marcolizando", url="marcolizando.com.br", bg="#0B0B0D", ink="#F4F4F6", muted="#B4B4BE",
               accent="#4C9AFF", on_accent="#0B0B0D", card="#141417", line="#26262C", photo_bg="#FFFFFF",
               display="Inter", body="Inter", dark=True),
}

def font_faces():
    css = []
    for fam, folder, weights in [("Inter", "inter", [400, 600, 700, 800]), ("Fraunces", "fraunces", [600, 700]),
                                 ("Manrope", "manrope", [500, 700, 800])]:
        for w in weights:
            f = FONTS / folder / "files" / f"{folder}-latin-{w}-normal.woff2"
            css.append(f"@font-face{{font-family:'{fam}';font-weight:{w};src:url('{f.as_uri()}') format('woff2')}}")
    return "\n".join(css)

def e(s): return html.escape(str(s))
def img(path): return (BASE / path).as_uri()

def header(t, tag):
    tag_style = (f"background:{t['accent']};color:{t['on_accent']}")
    return f"""<div class="row between"><div class="logo">{e(t['name'])}</div>
<div class="tag" style="{tag_style}">{e(tag)}</div></div>"""

def footer(t, cta):
    return f"""<div class="row between foot"><div class="url">{e(t['url'])}</div>
<div class="cta">{e(cta)} →</div></div>"""

def layout_foto(t, p):
    photos = "".join(f'<div class="ph"><img src="{img(f)}"></div>' for f in p["photos"])
    return f"""{header(t, p.get('tag','GUIA'))}
<div class="hero">{photos}</div>
<div class="col gap20"><div class="kicker">{e(p['kicker'])}</div>
<h1>{e(p['title'])}</h1><p class="sub">{e(p['sub'])}</p></div>
{footer(t, p.get('cta','Leia o guia'))}"""

def layout_lista(t, p):
    rows = []
    for i, it in enumerate(p["items"], 1):
        badge = '<span class="badge">Melhor escolha</span>' if i == 1 else ""
        rows.append(f"""<div class="item"><div class="num">{i}</div>
<div class="thumb"><img src="{img(it['file'])}"></div>
<div class="col gap6"><div class="iname">{e(it['name'])}</div>{badge}</div></div>""")
    return f"""{header(t, p.get('tag','RANKING'))}
<h1 class="lh">{e(p['title'])}</h1>
<div class="col gap16 grow">{''.join(rows)}</div>
{footer(t, p.get('cta','Ver o ranking'))}"""

def layout_dica(t, p):
    if p.get("checks"):
        body = "".join(f"""<div class="trow chk"><div class="num">{i}</div><div class="ct">{e(c)}</div></div>""" for i, c in enumerate(p["checks"], 1))
        body = f'<div class="col gap14 grow">{body}</div>'
    elif p.get("rows"):
        body = "".join(f"""<div class="trow"><div class="tl">{e(r[0])}</div><div class="tr">{e(r[1])}</div></div>""" for r in p["rows"])
        body = f'<div class="col gap14 grow">{body}</div>'
    else:
        body = "".join(f"""<div class="cell"><div class="cl">{e(c[0])}</div><div class="cv">{e(c[1])}</div></div>""" for c in p["cells"])
        body = f'<div class="grid grow">{body}</div>'
    note = f'<p class="note">{e(p["note"])}</p>' if p.get("note") else ""
    return f"""{header(t, p.get('tag','SALVE ESTA DICA'))}
<div class="col gap16"><h1>{e(p['title'])}</h1><p class="sub">{e(p['sub'])}</p></div>
{body}{note}
{footer(t, p.get('cta','Guia completo'))}"""

def page(p):
    t = THEMES[p["site"]]
    content = {"foto": layout_foto, "lista": layout_lista, "dica": layout_dica}[p["layout"]](t, p)
    disp = t["display"]
    serif = disp == "Fraunces"
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>
{font_faces()}
*{{box-sizing:border-box}} body{{margin:0}}
.pin{{width:1000px;height:1500px;padding:60px;display:flex;flex-direction:column;gap:34px;overflow:hidden;background:{t['bg']};color:{t['ink']};font-family:'{t['body']}',sans-serif}}
.row{{display:flex;align-items:center}} .between{{justify-content:space-between}}
.col{{display:flex;flex-direction:column}} .gap20{{gap:20px}} .gap16{{gap:16px}} .gap14{{gap:14px}} .gap6{{gap:6px}} .grow{{flex:1 1 0;min-height:0}}
.logo{{font-family:'{disp}';font-weight:{700 if serif else 800};font-size:40px;letter-spacing:{'0' if serif else '-1px'}}}
.tag{{padding:11px 22px;border-radius:999px;font-size:22px;font-weight:700;letter-spacing:2px}}
h1{{margin:0;font-family:'{disp}';font-weight:{700 if serif else 800};font-size:{p.get('size',88)}px;line-height:1.03;letter-spacing:{'-1px' if serif else '-3px'}}}
.lh{{font-size:{p.get('size',82)}px}}
.kicker{{font-size:25px;font-weight:700;letter-spacing:3px;color:{t['accent'] if not t['dark'] else t['accent']}}}
.sub{{margin:0;font-size:31px;line-height:1.4;color:{t['muted']}}}
.hero{{flex-grow:1;display:flex;gap:24px;min-height:0}}
.ph{{flex:1;border-radius:32px;background:{t['photo_bg']};display:flex;align-items:center;justify-content:center;overflow:hidden;border:2px solid {t['line']}}}
.ph img{{max-width:86%;max-height:86%;object-fit:contain}}
.item{{display:flex;align-items:center;gap:26px;padding:14px 24px;border-radius:24px;background:{t['card']};border:2px solid {t['line']};flex:1 1 0;min-height:0}}
.num{{width:72px;height:72px;flex-shrink:0;border-radius:{'50%' if serif else '18px'};background:{t['accent']};color:{t['on_accent']};display:flex;align-items:center;justify-content:center;font-family:'{disp}';font-weight:800;font-size:38px}}
.thumb{{width:130px;height:130px;flex-shrink:0;border-radius:18px;background:#FFFFFF;display:flex;align-items:center;justify-content:center;overflow:hidden}}
.thumb img{{max-width:88%;max-height:88%;object-fit:contain}}
.iname{{font-size:33px;font-weight:700;line-height:1.2}}
.badge{{align-self:flex-start;padding:6px 14px;border-radius:999px;font-size:20px;font-weight:700;background:{t['ink']};color:{t['bg']}}}
.grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:22px}}
.cell{{border-radius:28px;background:{t['card']};border:2px solid {t['line']};padding:34px;display:flex;flex-direction:column;justify-content:space-between}}
.cl{{font-size:30px;font-weight:700;color:{t['muted']}}}
.cv{{font-family:'{disp}';font-weight:800;font-size:{p.get('cv',72)}px;line-height:1.05;color:{t['accent']};letter-spacing:-1px}}
.trow{{display:flex;align-items:center;justify-content:space-between;padding:26px 36px;border-radius:24px;background:{t['card']};border:2px solid {t['line']};flex:1;gap:20px}}
.tl{{font-size:42px;font-weight:700}} .tr{{font-size:44px;font-weight:800;color:{t['accent']};text-align:right}}
.chk{{justify-content:flex-start;gap:30px}} .ct{{font-size:40px;font-weight:700}}
.note{{margin:0;font-size:24px;line-height:1.4;color:{t['muted']}}}
.foot{{padding-top:26px;border-top:2px solid {t['line']}}}
.url{{font-size:26px;font-weight:600}}
.cta{{padding:18px 32px;border-radius:999px;background:{t['accent']};color:{t['on_accent']};font-size:26px;font-weight:700}}
</style></head><body><div class="pin">{content}</div></body></html>"""

async def render(pins, outdir):
    os.makedirs(outdir, exist_ok=True)
    async with async_playwright() as pw:
        b = await pw.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--allow-file-access-from-files"])
        pg = await b.new_page(viewport={"width": 1000, "height": 1500})
        for p in pins:
            f = BASE / f"_{p['id']}.html"
            f.write_text(page(p), encoding="utf-8")
            await pg.goto(f.as_uri()); await pg.wait_for_timeout(300)
            await pg.screenshot(path=os.path.join(outdir, p["id"] + ".png"))
            f.unlink()
        await b.close()

if __name__ == "__main__":
    pins = json.load(open(sys.argv[1]))
    asyncio.run(render(pins, sys.argv[2]))
    print("ok", len(pins))
