# Gerador de pins dos sites

- `pins.py lote.json pasta_saida` gera PNGs 1000x1500 (layouts: foto, lista, dica).
- Fontes: `npm pack @fontsource/inter @fontsource/fraunces @fontsource/manrope`, extrair cada uma em `fonts/<nome>/` ao lado do pins.py.
- Precisa de Playwright + Chrome (`/usr/bin/google-chrome`).
- Campos de cada pin: id, site (cafe|btu|tv|tech), layout, title, sub/kicker/tag/cta, photos (foto) | items[{name,file}] (lista) | cells/rows/checks (dica), link, ptitle, pdesc, board.
- `../publicados.json` é o histórico: não repetir artigo já publicado.
