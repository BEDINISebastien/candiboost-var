import json, re, urllib.request, urllib.parse, xml.etree.ElementTree as ET, pathlib, datetime, html
ROOT=pathlib.Path(__file__).parent
SOURCES=[('Emploi Territorial','https://www.emploi-territorial.fr/emploi-mobilite/'),('France Travail recrutement','https://recrute.francetravail.org/Pages/Offre/ListeRss.aspx')]
FEEDS=[('Remotive (emplois à distance)','https://remotive.com/remote-jobs/feed')]
TERMS=['communication','community manager','webmaster','administratif','administrative','relation usager','accueil','cabinet','assistant','secrétariat','chargé de mission','gestionnaire','numérique','digital','projet','ressources humaines','rédacteur','journaliste','marketing','animation']
AREA=['var','toulon','cuers','hyères','hyeres','brignoles','draguignan','ollioules','sanary','six-fours','la garde','la seyne','fréjus','frejus','saint-raphaël','83','provence-alpes-côte d’azur','paca','remote','france','télétravail']
def fetch(url):
 req=urllib.request.Request(url,headers={'User-Agent':'CandiBoostVar/1.0 (+personal job alerts)','Accept':'application/rss+xml,application/atom+xml,application/xml,text/xml,*/*'})
 with urllib.request.urlopen(req,timeout=22) as r:return r.read(3000000)
def clean(s):return re.sub(r'<[^>]*>',' ',html.unescape(s or '')).strip()
def parse_rss(raw,source):
 root=ET.fromstring(raw); rows=[]
 for item in root.findall('.//item'):
  def get(t):return clean(item.findtext(t) or '')
  rows.append(dict(title=get('title'),url=get('link'),description=get('description')[:700],date=get('pubDate'),source=source,location=''))
 for item in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
  title=clean(item.findtext('{http://www.w3.org/2005/Atom}title') or '')
  link=next((a.attrib.get('href','') for a in item if a.tag.endswith('link')),'')
  rows.append(dict(title=title,url=link,description=clean(item.findtext('{http://www.w3.org/2005/Atom}summary') or '')[:700],date='',source=source,location=''))
 return rows
def main():
 old=ROOT/'offres.json'; previous=json.loads(old.read_text(encoding='utf-8')) if old.exists() else {'offers':[]}
 found=[]; logs=[]
 for name,url in FEEDS:
  try:
   rows=parse_rss(fetch(url),name)
   found+=rows;logs.append(f'{name}: {len(rows)} entrées')
  except Exception as e:logs.append(f'{name}: indisponible ({type(e).__name__})')
 # RSS territorial personnalisé à renseigner depuis « Flux RSS » sur la recherche filtrée
 custom=(ROOT/'sources.txt')
 if custom.exists():
  for url in custom.read_text(encoding='utf-8').splitlines():
   url=url.strip()
   if not url or url.startswith('#') or not url.startswith('https://'):continue
   try:
    rows=parse_rss(fetch(url),'Flux personnalisé');found+=rows;logs.append(f'Flux personnalisé: {len(rows)} entrées')
   except Exception as e:logs.append(f'Flux personnalisé: indisponible ({type(e).__name__})')
 seen={x.get('url') for x in found}; combined=found+[x for x in previous.get('offers',[]) if x.get('url') not in seen]
 out=[];used=set()
 for x in combined:
  url=x.get('url','');txt=(x.get('title','')+' '+x.get('description','')+' '+x.get('location','')).lower()
  if not url.startswith('https://') or url in used:continue
  if not any(t in txt for t in TERMS):continue
  if not any(a in txt for a in AREA):continue
  used.add(url);out.append(x)
 out=out[:350]
 data={'updated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'offers':out,'log':logs,'note':'Sources publiques, pas de garantie de couverture exhaustive; vérifier chaque annonce.'}
 old.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'total':len(out),'sources':logs},ensure_ascii=False))
if __name__=='__main__':main()
