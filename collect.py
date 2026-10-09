"""CandiBoost Var — collecte de flux RSS/Atom publics.

sources.txt accepte :
  https://exemple.fr/offres.rss
  CAF du Var | https://exemple.fr/offres.rss
  CPAM du Var | https://exemple.fr/offres.rss
  Préfecture du Var | https://exemple.fr/offres.rss

Les pages HTML classiques ne sont pas des flux RSS : aucune extraction fictive.
"""
import datetime
import html
import json
import pathlib
import re
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent
FEEDS = [('Remotive (emplois à distance)', 'https://remotive.com/remote-jobs/feed')]
TERMS = [
    'communication', 'community manager', 'webmaster', 'administratif',
    'administrative', 'relation usager', 'accueil', 'cabinet', 'assistant',
    'secrétariat', 'chargé de mission', 'gestionnaire', 'numérique',
    'digital', 'projet', 'ressources humaines', 'rédacteur', 'journaliste',
    'marketing', 'animation', 'téléconseiller', 'conseiller service',
    'conseiller services', 'assurance maladie', 'gestionnaire conseil',
    'chargé de recrutement', 'recrutement', 'service public',
]
AREA = [
    'var', 'toulon', 'cuers', 'hyères', 'hyeres', 'brignoles', 'draguignan',
    'ollioules', 'sanary', 'six-fours', 'la garde', 'la seyne', 'fréjus',
    'frejus', 'saint-raphaël', '83', 'provence-alpes-côte d’azur',
    'paca', 'remote', 'france', 'télétravail',
]
EMPLOYERS = {
    'CAF du Var': ('caf du var', 'caisse d’allocations familiales du var',
                   'caisse d\'allocations familiales du var'),
    'CPAM du Var': ('cpam du var', 'caisse primaire d’assurance maladie du var',
                    'caisse primaire d\'assurance maladie du var'),
    'Préfecture du Var': ('préfecture du var', 'prefecture du var',
                          'préfecture de toulon'),
}


def fetch(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'CandiBoostVar/1.1 (personal job alerts)',
        'Accept': 'application/rss+xml,application/atom+xml,application/xml,text/xml,*/*',
    })
    with urllib.request.urlopen(req, timeout=22) as response:
        return response.read(3_000_000)


def clean(value):
    return re.sub(r'<[^>]*>', ' ', html.unescape(value or '')).strip()


def parse_rss(raw, source):
    root = ET.fromstring(raw)
    rows = []
    for item in root.findall('.//item'):
        def field(name):
            return clean(item.findtext(name) or '')
        rows.append({
            'title': field('title'), 'url': field('link'),
            'description': field('description')[:700],
            'date': field('pubDate'), 'source': source, 'location': '',
        })
    atom = '{http://www.w3.org/2005/Atom}'
    for item in root.findall('.//' + atom + 'entry'):
        link = next((el.attrib.get('href', '') for el in item
                     if el.tag == atom + 'link' and
                     el.attrib.get('rel', 'alternate') == 'alternate'), '')
        rows.append({
            'title': clean(item.findtext(atom + 'title') or ''),
            'url': link,
            'description': clean(item.findtext(atom + 'summary') or
                                 item.findtext(atom + 'content') or '')[:700],
            'date': clean(item.findtext(atom + 'published') or
                          item.findtext(atom + 'updated') or ''),
            'source': source, 'location': '',
        })
    return rows


def read_custom_sources():
    path = ROOT / 'sources.txt'
    if not path.exists():
        return []
    feeds = []
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '|' in line:
            name, url = (part.strip() for part in line.split('|', 1))
        else:
            name, url = 'Flux personnalisé', line
        if name and url.startswith('https://'):
            feeds.append((name, url))
    return feeds


def employer_for(offer):
    text = ' '.join(str(offer.get(k, '')) for k in
                    ('title', 'description', 'source', 'location')).casefold()
    for employer, variants in EMPLOYERS.items():
        if employer.casefold() in text or any(v in text for v in variants):
            return employer
    return ''


def relevant(offer):
    text = ' '.join(str(offer.get(k, '')) for k in
                    ('title', 'description', 'location', 'source')).casefold()
    employer = employer_for(offer)
    return (any(term in text for term in TERMS) and
            (any(area in text for area in AREA) or bool(employer)))


def main():
    output = ROOT / 'offres.json'
    try:
        previous = json.loads(output.read_text(encoding='utf-8')) if output.exists() else {}
    except (ValueError, OSError):
        previous = {}
    found, logs = [], []
    for name, url in FEEDS + read_custom_sources():
        try:
            rows = parse_rss(fetch(url), name)
            found.extend(rows)
            logs.append(f'{name}: {len(rows)} entrées')
        except (OSError, ET.ParseError, ValueError) as exc:
            logs.append(f'{name}: indisponible ({type(exc).__name__})')

    combined = found + list(previous.get('offers', []))
    offers, used = [], set()
    for offer in combined:
        url = str(offer.get('url', ''))
        if not url.startswith('https://') or url in used or not relevant(offer):
            continue
        used.add(url)
        record = dict(offer)
        employer = employer_for(record)
        if employer:
            record['employer'] = employer
        offers.append(record)
        if len(offers) >= 350:
            break

    result = {
        'updated_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'offers': offers,
        'log': logs,
        'note': ('Sources RSS/Atom publiques uniquement ; les pages de recrutement '
                 'HTML nécessitent une intégration dédiée. Vérifier chaque annonce.'),
    }
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'total': len(offers), 'sources': logs}, ensure_ascii=False))


if __name__ == '__main__':
    main()
