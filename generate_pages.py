"""
Génère une page HTML par expert à partir de processed.json.
Sortie : _site/expert_<CODE>.html  (noms stables d'un mois à l'autre)
"""
import json
import os

OUT_DIR = "_site"
os.makedirs(OUT_DIR, exist_ok=True)

with open('processed.json', encoding='utf-8') as f:
    data = json.load(f)

MOIS = data['mois']
YTD = data['ytd']
REGIONAL = data['regional']
RETAINED = data['retained']
META = data['meta']

MOIS_LABEL = META['mois_label']
YTD_LABEL = META['ytd_label']
MAJ_LABEL = META['maj_label']

# --- Helpers de formatage ---
def fmt_pct(v):
    if v is None: return "—"
    return f"{v:.1f} %".replace('.', ',')

def fmt_eur(v):
    if v is None: return "—"
    return f"{v:,.0f} €".replace(',', ' ')

def fmt_h(v):
    if v is None: return "—"
    return f"{v:.1f} h".replace('.', ',')

def fmt_j(v):
    if v is None: return "—"
    return f"{v:.1f} j".replace('.', ',')

def fmt_int(v):
    if v is None: return "—"
    return f"{int(v):,}".replace(',', ' ')

def fmt_eur_simple(v):
    if v is None: return "—"
    return f"{int(round(v)):,} €".replace(',', ' ')

def big_pct(v):
    if v is None: return "—"
    return f"{v:.1f}".replace('.', ',') + '<span class="kpi-unit">%</span>'

def big_eur(v):
    if v is None: return "—"
    return f"{int(round(v))}<span class=\"kpi-unit\">€</span>"

def big_h(v):
    if v is None: return "—"
    return f"{v:.1f}".replace('.', ',') + '<span class="kpi-unit">h</span>'

def status(kpi, v):
    if v is None: return None
    if kpi == 'accordDirect':
        if v <= 20: return 'success'
        if v <= 25: return 'warning'
        return 'danger'
    if kpi == 'miseTerrain':
        if v <= 20: return 'success'
        if v <= 25: return 'warning'
        return 'danger'
    if kpi == 'delaiEad':
        if v < 4: return 'success'
        if v <= 6: return 'warning'
        return 'danger'
    if kpi == 'repar':
        if v >= 52: return 'success'
        if v >= 50: return 'warning'
        return 'danger'
    if kpi == 'reparJantes':
        if v > 80: return 'success'
        if v >= 70: return 'warning'
        return 'danger'
    if kpi == 'reparPlastique':
        if v > 45: return 'success'
        if v >= 40: return 'warning'
        return 'danger'
    if kpi == 'gain':
        if v > 200: return 'success'
        if v >= 150: return 'warning'
        return 'danger'
    if kpi == 'pre':
        if v > 18: return 'success'
        if v >= 15: return 'warning'
        return 'danger'
    return None

BADGE_LABEL = {
    'success': 'Objectif atteint',
    'warning': 'Vigilance',
    'danger':  'À redresser',
}

def kpi_card(label, kpi, mois_val, ytd_val, target_txt, regional_val, formatter, value_formatter=None):
    st = status(kpi, ytd_val)
    klass = f"is-{st}" if st else ""
    badge_html = f'<span class="kpi-badge badge-{st}">{BADGE_LABEL[st]}</span>' if st else ''
    vf = value_formatter or formatter
    ytd_big = vf(ytd_val) if ytd_val is not None else "—"
    mois_big = vf(mois_val) if mois_val is not None else "—"
    return f"""
      <article class="kpi-card {klass}">
        <div class="kpi-head">
          <p class="kpi-label">{label}</p>
          {badge_html}
        </div>
        <div class="kpi-dual">
          <div class="kpi-dual-item">
            <div class="kpi-dual-eyebrow">YTD</div>
            <div class="kpi-dual-value">{ytd_big}</div>
          </div>
          <div class="kpi-dual-item">
            <div class="kpi-dual-eyebrow">{MOIS_LABEL}</div>
            <div class="kpi-dual-value">{mois_big}</div>
          </div>
        </div>
        <div class="kpi-meta">
          <div class="kpi-meta-item"><div class="kpi-meta-label">Objectif</div><div class="kpi-meta-value">{target_txt}</div></div>
          <div class="kpi-meta-item"><div class="kpi-meta-label">Région</div><div class="kpi-meta-value">{formatter(regional_val)}</div></div>
        </div>
      </article>"""

def info_card(label, mois_val, ytd_val, regional_val, formatter):
    return f"""
      <article class="info-card">
        <p class="info-label">{label}</p>
        <p class="info-value">{formatter(ytd_val)}</p>
        <p class="info-meta"><span>{MOIS_LABEL} : <strong>{formatter(mois_val)}</strong></span><span>Région : <strong>{formatter(regional_val)}</strong></span></p>
      </article>"""

TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow">
<title>Performance — {expert_code} · {mois_label}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;600;700;900&family=Source+Sans+3:wght@400;600;700&display=swap" rel="stylesheet">
<style>
:root {{
  --idea-blue: #0F4FA0;
  --idea-blue-fold: #A5B5DA;
  --idea-blue-deep: #08326B;
  --idea-blue-50: #F0F4FB;
  --idea-blue-100: #D9E2F1;
  --idea-blue-300: #6F8FC4;
  --idea-taupe: #6B635E;
  --idea-taupe-100: #E4E0DD;
  --idea-steel: #5C6670;
  --idea-steel-100: #DDE0E4;
  --idea-steel-50: #F1F2F4;
  --idea-paper: #F5F4F2;
  --idea-ink: #1A1A1A;
  --idea-success: #4A8B5E;
  --idea-success-bg: #E8F1EC;
  --idea-warning: #C28A2C;
  --idea-warning-bg: #FAF1DF;
  --idea-danger: #B84B3D;
  --idea-danger-bg: #F7E4E1;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: 'Source Sans 3', 'Aptos', 'Calibri', Arial, sans-serif; font-size: 14px; color: var(--idea-ink); background: var(--idea-paper); line-height: 1.45; }}
.container {{ max-width: 1400px; margin: 0 auto; background: #fff; }}
.header {{ position: relative; background: var(--idea-blue-deep); color: #fff; padding: 32px 48px 28px; overflow: hidden; }}
.header::after {{ content: ""; position: absolute; top: 0; right: 0; width: 56px; height: 56px; background: var(--idea-blue-fold); clip-path: polygon(0 0, 100% 100%, 100% 0); }}
.header-grid {{ display: flex; justify-content: space-between; align-items: flex-end; gap: 40px; flex-wrap: wrap; }}
.header-left {{ flex: 1 1 420px; }}
.header-right {{ text-align: right; }}
.eyebrow {{ font-family: 'Archivo', sans-serif; font-weight: 700; font-size: 11px; letter-spacing: 0.18em; text-transform: uppercase; color: var(--idea-blue-fold); margin-bottom: 10px; display: flex; align-items: center; gap: 8px; }}
.eyebrow .bullet {{ display: inline-block; width: 0.6em; height: 0.6em; background: var(--idea-blue-fold); }}
.expert-name {{ font-family: 'Archivo', sans-serif; font-weight: 700; font-size: 36px; letter-spacing: -0.01em; color: #fff; margin-bottom: 4px; }}
.expert-code {{ font-family: 'Archivo', sans-serif; font-weight: 400; font-size: 18px; color: var(--idea-blue-fold); }}
.period {{ font-family: 'Archivo', sans-serif; font-weight: 600; font-size: 22px; color: #fff; }}
.period-sub {{ font-size: 13px; color: var(--idea-blue-fold); margin-top: 4px; }}
.maj {{ font-size: 11px; color: var(--idea-blue-fold); letter-spacing: 0.05em; margin-top: 8px; }}
.section {{ padding: 40px 48px 24px; }}
.section-title {{ font-family: 'Archivo', sans-serif; font-weight: 700; font-size: 18px; color: var(--idea-blue); margin-bottom: 4px; display: flex; align-items: center; gap: 10px; }}
.section-title .bullet {{ display: inline-block; width: 10px; height: 10px; background: var(--idea-steel); }}
.section-sub {{ font-size: 13px; color: var(--idea-taupe); margin-bottom: 24px; }}
.kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }}
@media (max-width: 1100px) {{ .kpi-grid {{ grid-template-columns: repeat(2, 1fr); }} }}
@media (max-width: 600px) {{ .kpi-grid {{ grid-template-columns: 1fr; }} }}
.kpi-card {{ position: relative; background: #fff; border: 1px solid var(--idea-steel-100); padding: 18px 20px 16px; overflow: hidden; }}
.kpi-card.is-success {{ border-top: 3px solid var(--idea-success); }}
.kpi-card.is-warning {{ border-top: 3px solid var(--idea-warning); }}
.kpi-card.is-danger {{ border-top: 3px solid var(--idea-danger); }}
.kpi-head {{ display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; margin-bottom: 14px; min-height: 32px; }}
.kpi-label {{ font-family: 'Archivo', sans-serif; font-weight: 600; font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--idea-steel); flex: 1; line-height: 1.25; }}
.kpi-badge {{ font-family: 'Archivo', sans-serif; font-weight: 700; font-size: 9px; letter-spacing: 0.08em; text-transform: uppercase; padding: 4px 8px; white-space: nowrap; align-self: flex-start; }}
.badge-success {{ background: var(--idea-success-bg); color: var(--idea-success); }}
.badge-warning {{ background: var(--idea-warning-bg); color: var(--idea-warning); }}
.badge-danger {{ background: var(--idea-danger-bg); color: var(--idea-danger); }}
.kpi-dual {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 14px; padding-bottom: 12px; border-bottom: 1px solid var(--idea-steel-100); }}
.kpi-dual-item .kpi-dual-eyebrow {{ font-family: 'Archivo', sans-serif; font-weight: 700; font-size: 10px; letter-spacing: 0.14em; text-transform: uppercase; color: var(--idea-steel); margin-bottom: 6px; display: flex; align-items: center; gap: 6px; }}
.kpi-dual-item .kpi-dual-eyebrow::before {{ content: ""; width: 6px; height: 6px; background: var(--idea-blue); display: inline-block; }}
.kpi-dual-item .kpi-dual-value {{ font-family: 'Archivo', sans-serif; font-weight: 900; font-size: 30px; color: var(--idea-blue); letter-spacing: -0.02em; line-height: 1; font-variant-numeric: tabular-nums; }}
.kpi-unit {{ font-family: 'Archivo', sans-serif; font-weight: 600; font-size: 14px; color: var(--idea-blue); margin-left: 2px; }}
.kpi-meta {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }}
.kpi-meta-item {{ text-align: left; }}
.kpi-meta-label {{ font-size: 9px; letter-spacing: 0.1em; text-transform: uppercase; color: var(--idea-steel); margin-bottom: 2px; }}
.kpi-meta-value {{ font-family: 'Source Sans 3', sans-serif; font-weight: 600; font-size: 13px; color: var(--idea-taupe); font-variant-numeric: tabular-nums; }}
.info-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }}
@media (max-width: 900px) {{ .info-grid {{ grid-template-columns: repeat(2, 1fr); }} }}
@media (max-width: 600px) {{ .info-grid {{ grid-template-columns: 1fr; }} }}
.info-card {{ background: var(--idea-blue-50); padding: 18px 20px; border-left: 3px solid var(--idea-blue); }}
.info-label {{ font-family: 'Archivo', sans-serif; font-weight: 600; font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--idea-steel); margin-bottom: 8px; }}
.info-value {{ font-family: 'Archivo', sans-serif; font-weight: 700; font-size: 26px; color: var(--idea-blue); line-height: 1; margin-bottom: 8px; font-variant-numeric: tabular-nums; }}
.info-meta {{ display: flex; gap: 14px; font-size: 12px; color: var(--idea-taupe); flex-wrap: wrap; }}
.info-meta span strong {{ color: var(--idea-ink); font-weight: 600; font-variant-numeric: tabular-nums; }}
.footer {{ padding: 24px 48px 32px; border-top: 1px solid var(--idea-steel-100); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-top: 16px; }}
.footer-tag {{ font-family: 'Archivo', sans-serif; font-weight: 600; font-size: 13px; color: var(--idea-taupe); }}
.footer-mention {{ font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase; color: var(--idea-steel); }}
</style>
</head>
<body>
<div class="container">
  <header class="header">
    <div class="header-grid">
      <div class="header-left">
        <p class="eyebrow"><span class="bullet"></span>Tableau de bord individuel — Photo-expertise</p>
        <h1 class="expert-name">{expert_code}</h1>
        <p class="expert-code">Code expert</p>
      </div>
      <div class="header-right">
        <p class="period">{mois_label}</p>
        <p class="period-sub">YTD · {ytd_label}</p>
        <p class="maj">Dernière mise à jour : {maj_label}</p>
      </div>
    </div>
  </header>
  <section class="section">
    <h2 class="section-title"><span class="bullet"></span>Indicateurs avec objectif</h2>
    <p class="section-sub">Cumul depuis le 1<sup>er</sup> janvier · mois en cours · objectif plateforme · moyenne régionale</p>
    <div class="kpi-grid">
{kpi_cards}
    </div>
  </section>
  <section class="section">
    <h2 class="section-title"><span class="bullet"></span>Autres indicateurs de suivi</h2>
    <p class="section-sub">Sans cible chiffrée — valeur YTD principale, mois et région en complément</p>
    <div class="info-grid">
{info_cards}
    </div>
  </section>
  <footer class="footer">
    <p class="footer-tag">Une nouvelle idée de l'expertise.</p>
    <p class="footer-mention">Document de pilotage interne · IDEA Expertises</p>
  </footer>
</div>
</body>
</html>"""

def generate_for(code):
    m = MOIS.get(code) or {k: None for k in YTD[code].keys()}
    y = YTD[code]
    r = REGIONAL

    kpi_cards = []
    kpi_cards.append(kpi_card("Taux d'accord direct", "accordDirect",
                              m.get('accordDirect'), y.get('accordDirect'),
                              "≤ 20 %", r.get('accordDirect'), fmt_pct, big_pct))
    kpi_cards.append(kpi_card("Taux de mise en terrain", "miseTerrain",
                              m.get('miseTerrain'), y.get('miseTerrain'),
                              "≤ 20 %", r.get('miseTerrain'), fmt_pct, big_pct))
    kpi_cards.append(kpi_card("Délai de traitement EAD", "delaiEad",
                              m.get('delaiEad'), y.get('delaiEad'),
                              "< 4 h", r.get('delaiEad'), fmt_h, big_h))
    kpi_cards.append(kpi_card("Taux de réparation", "repar",
                              m.get('repar'), y.get('repar'),
                              "≥ 52 %", r.get('repar'), fmt_pct, big_pct))
    kpi_cards.append(kpi_card("Taux de réparation jantes", "reparJantes",
                              m.get('reparJantes'), y.get('reparJantes'),
                              "> 80 %", r.get('reparJantes'), fmt_pct, big_pct))
    kpi_cards.append(kpi_card("Taux de réparation plastique", "reparPlastique",
                              m.get('reparPlastique'), y.get('reparPlastique'),
                              "> 45 %", r.get('reparPlastique'), fmt_pct, big_pct))
    kpi_cards.append(kpi_card("Gain moyen HT par dossier", "gain",
                              m.get('gain'), y.get('gain'),
                              "> 200 €", r.get('gain'), fmt_eur, big_eur))
    kpi_cards.append(kpi_card("Taux de PRE", "pre",
                              m.get('pre'), y.get('pre'),
                              "> 18 %", r.get('pre'), fmt_pct, big_pct))

    info_cards = []
    info_cards.append(info_card("Volume EAD", m.get('volume'), y.get('volume'), r.get('volume'), fmt_int))
    info_cards.append(info_card("Coût moyen HT", m.get('cm'), y.get('cm'), r.get('cm'), fmt_eur_simple))
    info_cards.append(info_card("Panier pièce moyen", m.get('panier'), y.get('panier'), r.get('panier'), fmt_eur_simple))
    info_cards.append(info_card("Délai mission dépôt", m.get('missionDepot'), y.get('missionDepot'), r.get('missionDepot'), fmt_j))
    info_cards.append(info_card("Taux de PQE", m.get('pqe'), y.get('pqe'), r.get('pqe'), fmt_pct))
    info_cards.append(info_card("Taux de réparation optique", m.get('reparOptique'), y.get('reparOptique'), r.get('reparOptique'), fmt_pct))

    html = TEMPLATE.format(
        expert_code=code,
        mois_label=MOIS_LABEL,
        ytd_label=YTD_LABEL,
        maj_label=MAJ_LABEL,
        kpi_cards='\n'.join(kpi_cards),
        info_cards='\n'.join(info_cards),
    )
    path = os.path.join(OUT_DIR, f"expert_{code}.html")
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    return path

def generate_index():
    """Page d'index simple listant les liens (utile pour le manager)."""
    rows = []
    for code in RETAINED:
        rows.append(f'<li><a href="expert_{code}.html">{code}</a></li>')
    html = f"""<!DOCTYPE html>
<html lang="fr"><head>
<meta charset="UTF-8"><meta name="robots" content="noindex,nofollow">
<title>Index — Performance Photo-expertise</title>
<style>
body{{font-family:'Source Sans 3',Arial,sans-serif;max-width:600px;margin:40px auto;padding:0 20px;color:#1A1A1A}}
h1{{font-family:'Archivo',Arial,sans-serif;color:#0F4FA0;font-weight:700;font-size:24px;margin-bottom:8px}}
p.sub{{color:#6B635E;font-size:13px;margin-bottom:24px}}
ul{{list-style:none;padding:0}}
li{{padding:8px 0;border-bottom:1px solid #DDE0E4}}
a{{color:#0F4FA0;font-weight:600;text-decoration:none}}
a:hover{{text-decoration:underline}}
</style></head>
<body><h1>Pages experts — {MOIS_LABEL}</h1>
<p class="sub">Liste des liens individuels. Dernière mise à jour : {MAJ_LABEL}</p>
<ul>{''.join(rows)}</ul></body></html>"""
    with open(os.path.join(OUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == '__main__':
    generated = []
    for code in RETAINED:
        generated.append(generate_for(code))
    generate_index()
    # robots.txt pour empêcher l'indexation
    with open(os.path.join(OUT_DIR, 'robots.txt'), 'w') as f:
        f.write("User-agent: *\nDisallow: /\n")
    print(f"Pages générées : {len(generated)} + index.html + robots.txt dans {OUT_DIR}/")
