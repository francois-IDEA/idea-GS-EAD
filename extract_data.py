"""
Extraction des données depuis les 2 PDFs Power BI (Masque Suivi Performance EAD).
Entrées attendues : source/ytd.pdf  et  source/mois.pdf
Sortie : processed.json (mois, ytd, regional, retained, meta)
"""
import pdfplumber
import json
import re
import sys
import os
from datetime import datetime

# Centres x des colonnes (calibrés sur les PDFs Power BI Allianz)
COLUMNS = [
    ("expert", 35),
    ("volume", 159),
    ("cm", 260),
    ("panier", 390),
    ("gain", 540),
    ("accordDirect", 640),
    ("ddeModif", 775),
    ("miseTerrain", 880),
    ("delaiEad", 1017),
    ("delaiFacture", 1115),
    ("missionDepot", 1243),
    ("pre", 1320),
    ("pqe", 1390),
    ("tauxEad", 1470),
    ("tauxEadAgree", 1580),
    ("repar", 1700),
    ("reparJantes", 1830),
    ("reparOptique", 1960),
    ("reparPlastique", 2130),
]

NUMERIC_KEYS = [k for k, _ in COLUMNS if k != 'expert']
MIN_VOLUME_YTD = 50  # filtre volume minimum

MOIS_FR = {
    1: "janvier", 2: "février", 3: "mars", 4: "avril", 5: "mai", 6: "juin",
    7: "juillet", 8: "août", 9: "septembre", 10: "octobre", 11: "novembre", 12: "décembre"
}

def conv(v):
    if v is None or v == '':
        return None
    s = str(v).replace(' ', '').replace('€','').replace('%','').replace(',', '.').strip()
    try:
        return float(s)
    except:
        return None

def group_value_tokens(line):
    """Groupe les tokens consécutifs qui forment une seule valeur (espaces dans nombres, % et € collés)."""
    groups = []
    for w in line:
        if not groups:
            groups.append([w])
            continue
        prev = groups[-1][-1]
        gap = w['x0'] - prev['x1']
        prev_t = prev['text']
        cur_t = w['text']
        if gap < 15 and (
            cur_t in ('€','%') or
            (re.fullmatch(r'\d+', prev_t) and re.fullmatch(r'\d{3}', cur_t)) or
            (re.fullmatch(r'\d+', prev_t) and cur_t in ('%','€')) or
            (re.fullmatch(r'\d+[.,]\d+', prev_t) and cur_t in ('%','€'))
        ):
            groups[-1].append(w)
        else:
            groups.append([w])
    return [{
        'text': ' '.join(g['text'] for g in grp),
        'cx': (grp[0]['x0'] + grp[-1]['x1']) / 2
    } for grp in groups]

def assign_to_columns(groups):
    out = {k: None for k, _ in COLUMNS}
    for g in groups:
        best_key, best_dist = None, 1e9
        for k, cx in COLUMNS:
            d = abs(g['cx'] - cx)
            if d < best_dist:
                best_dist, best_key = d, k
        if best_dist < 70:
            out[best_key] = g['text']
    return out

def detect_date(page):
    """Détecte la date de début dans le PDF (format dd/mm/yyyy) -> returns (year, month) ou None."""
    txt = page.extract_text() or ""
    m = re.search(r'(\d{2})/(\d{2})/(\d{4})', txt)
    if m:
        d, mo, y = m.groups()
        return int(y), int(mo)
    return None

def parse_pdf(path):
    with pdfplumber.open(path) as pdf:
        page = pdf.pages[0]
        words = page.extract_words(use_text_flow=False, keep_blank_chars=False)
        date_info = detect_date(page)

    lines = []
    cur = []
    for w in sorted(words, key=lambda w: (round(w['top']), w['x0'])):
        if not cur or abs(round(w['top']) - round(cur[0]['top'])) <= 3:
            cur.append(w)
        else:
            lines.append(sorted(cur, key=lambda w: w['x0']))
            cur = [w]
    if cur:
        lines.append(sorted(cur, key=lambda w: w['x0']))

    rows = []
    for ln in lines:
        if not ln: continue
        t0 = ln[0]['text']
        y = ln[0]['top']
        if 2 <= len(t0) <= 4 and t0.isalpha() and t0.isupper() and 330 < y < 1320:
            if t0 in ("EAD","HT","PT"):
                continue
            rest_has_digit = any(any(c.isdigit() for c in w['text']) for w in ln[1:])
            if not rest_has_digit:
                continue
            grp = group_value_tokens(ln)
            data = assign_to_columns(grp)
            rows.append(data)

    return rows, date_info

def to_num(rows):
    out = {}
    for r in rows:
        e = r['expert']
        out[e] = {k: conv(r.get(k)) for k in NUMERIC_KEYS}
    return out

def main():
    ytd_path = sys.argv[1] if len(sys.argv) > 1 else "source/ytd.pdf"
    mois_path = sys.argv[2] if len(sys.argv) > 2 else "source/mois.pdf"

    if not os.path.exists(ytd_path):
        print(f"ERREUR : {ytd_path} introuvable")
        sys.exit(1)
    if not os.path.exists(mois_path):
        print(f"ERREUR : {mois_path} introuvable")
        sys.exit(1)

    print(f"Extraction YTD  : {ytd_path}")
    ytd_rows, ytd_date = parse_pdf(ytd_path)
    print(f"Extraction MOIS : {mois_path}")
    mois_rows, mois_date = parse_pdf(mois_path)

    ytd = to_num(ytd_rows)
    mois = to_num(mois_rows)

    # Auto-détection : si le YTD a moins de volume que le mois, on inverse
    total_y = sum((d['volume'] or 0) for d in ytd.values())
    total_m = sum((d['volume'] or 0) for d in mois.values())
    if total_m > total_y:
        print("⚠ Inversion détectée : YTD et MOIS échangés.")
        ytd, mois = mois, ytd
        ytd_date, mois_date = mois_date, ytd_date

    # Filtre volume
    retained = [e for e, d in ytd.items() if d['volume'] and d['volume'] >= MIN_VOLUME_YTD]
    excluded = [e for e, d in ytd.items() if not (d['volume'] and d['volume'] >= MIN_VOLUME_YTD)]

    # Moyenne pondérée par volume
    regional = {}
    for k in NUMERIC_KEYS:
        if k == 'volume':
            vols = [ytd[e]['volume'] for e in retained if ytd[e]['volume']]
            regional[k] = sum(vols) / len(vols) if vols else None
        else:
            num, den = 0.0, 0.0
            for e in retained:
                v = ytd[e][k]
                w = ytd[e]['volume']
                if v is not None and w:
                    num += v * w
                    den += w
            regional[k] = (num / den) if den else None

    # Méta (mois label)
    if mois_date:
        year, month = mois_date
        mois_label = f"{MOIS_FR[month].capitalize()} {year}"
        mois_file = f"{MOIS_FR[month]}{year}"
        # Bornes YTD
        if ytd_date:
            y_y, y_m = ytd_date
            ytd_label = f"1er {MOIS_FR[y_m]} {y_y} au {datetime.now().day} {MOIS_FR[month]} {year}"
        else:
            ytd_label = f"Depuis le début de l'année jusqu'au {MOIS_FR[month]} {year}"
        maj_label = datetime.now().strftime("%d/%m/%Y")
    else:
        mois_label = "Mois en cours"
        mois_file = "mois"
        ytd_label = "Depuis le début de l'année"
        maj_label = datetime.now().strftime("%d/%m/%Y")

    out = {
        'mois': mois,
        'ytd': ytd,
        'retained': retained,
        'excluded': excluded,
        'regional': regional,
        'meta': {
            'mois_label': mois_label,
            'mois_file': mois_file,
            'ytd_label': ytd_label,
            'maj_label': maj_label,
        }
    }

    with open('processed.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"\nRésultat : {len(retained)} experts retenus, {len(excluded)} exclus (volume < {MIN_VOLUME_YTD})")
    print(f"Période  : {mois_label} / YTD {ytd_label}")
    print(f"Exclus   : {', '.join(excluded) if excluded else '(aucun)'}")

if __name__ == '__main__':
    main()
