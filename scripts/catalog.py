import hashlib,json,re,threading,subprocess,xml.etree.ElementTree as ET,html as html_module

from datetime import datetime,timezone,timedelta

from email.utils import parsedate_to_datetime

from html.parser import HTMLParser

from urllib.parse import urlparse,urljoin

SOURCES=[
 {'id':'dwarkesh','name':'Dwarkesh Podcast','module':'authorities','feed':'https://www.dwarkesh.com/feed','days':30},
 {'id':'a16z','name':'The a16z Show','module':'authorities','feed':'https://feeds.simplecast.com/JGE3yC0V','days':30},
 {'id':'a16z-articles','name':'a16z Articles','module':'authorities','feed':'https://a16z.com/post-sitemap3.xml','parser':'sitemap','days':30,'logo':'/a16z-logo.jpg'},
 {'id':'semianalysis','name':'SemiAnalysis','module':'authorities','feed':'https://semianalysis.substack.com/feed','days':30},
 {'id':'all-in','name':'All-In Podcast','module':'authorities','feed':'https://rss.libsyn.com/shows/254861/destinations/1928300.xml','days':30,'logo':'/all-in-logo.jpg'},
 {'id':'this-week-in-startups','name':'This Week in Startups','module':'authorities','feed':'https://rss.libsyn.com/shows/624860/destinations/5500155.xml','days':30,'logo':'/this-week-in-startups-logo.jpg'},
 {'id':'dialectic','name':'Dialectic','module':'figures','feed':'https://feeds.megaphone.fm/ICDEI1431648742','days':30,'logo':'/dialectic-logo.jpg'},
 {'id':'colossus-magazine','name':'Colossus Magazine','module':'authorities','feed':'https://feeds.megaphone.fm/colossus-magazine','days':30,'logo':'/colossus-logo.jpg'},
 {'id':'this-week-in-ai','name':'This Week in AI','module':'authorities','feed':'https://anchor.fm/s/10803d078/podcast/rss','days':30,'logo':'/this-week-in-ai-logo.jpg'},
 {'id':'epoch-after-hours','name':'Epoch AI · After Hours','module':'authorities','feed':'https://feeds.transistor.fm/epoch-ai-after-hours','days':30,'logo':'/epoch-ai-logo.svg'},
 {'id':'epoch-ai','name':'Epoch AI','module':'authorities','page':'https://epoch.ai/latest','days':30,'logo':'/epoch-ai-logo.svg'},
 {'id':'altimeter','name':'Altimeter / BG2','module':'authorities','feed':'https://anchor.fm/s/f06c2370/podcast/rss','days':365,'logo':'https://is1-ssl.mzstatic.com/image/thumb/PodcastSource126/v4/4b/ab/e5/4babe58b-7cda-b2b3-40a5-bcac3f262764/33f9cff7-dc0b-4293-a5bf-d8cc62ab8c98.jpg/600x600bb.jpg'},
 {'id':'sequoia','name':'Sequoia Capital','module':'authorities','feed':'https://sequoiacap.com/sitemap.xml','parser':'sequoia','days':45,'logo':'https://framerusercontent.com/images/ItZ3Og0z4GahXe5uWHqwk69EPRw.png'},
 {'id':'kleiner-perkins','name':'Kleiner Perkins','module':'authorities','feed':'https://www.kleinerperkins.com/feed/','days':30},
 {'id':'khosla-ventures','name':'Khosla Ventures','module':'authorities','feed':'https://www.youtube.com/feeds/videos.xml?channel_id=UCF92qR15QflJFGO7c_PeT-g','days':30,'logo':'https://yt3.googleusercontent.com/1MIsy9RWNLd6WI-B7Fy-vblrkyuXXv1xevfLGd35pesZBWyucNrMMXzAgDOstc0K7_nl4J4pRg=s200-c-k-c0x00ffffff-no-rj'},
 {'id':'coatue','name':'Coatue Management','module':'authorities','page':'https://www.coatue.com/','parser':'coatue','days':180,'logo':'https://yt3.googleusercontent.com/AnfLsLJsZ-SbIvyz9e7Dx0UxdmieuP6lEVEnDFU3C_vNZf_aGwA1x5K2UG_a9I6ns3YP6SP35Qg=s200-c-k-c0x00ffffff-no-rj'},
 {'id':'20vc','name':'20VC','module':'figures','feed':'https://rss.libsyn.com/shows/61840/destinations/240976.xml','days':30,'logo':'/20vc-logo.jpg'},
 {'id':'uncapped','name':'Uncapped with Jack Altman','module':'figures','feed':'https://anchor.fm/s/1156f1c04/podcast/rss','days':30,'logo':'/uncapped-logo.jpg'},
 {'id':'my-first-million','name':'My First Million','module':'figures','feed':'https://feeds.megaphone.fm/HS2300184645','days':30,'logo':'/my-first-million-logo.jpg'},
 {'id':'invested','name':'Invested by Aleph','module':'figures','feed':'https://feeds.megaphone.fm/AMCL3368122371','days':30,'logo':'/invested-logo.jpg'},
 {'id':'david-senra','name':'David Senra','module':'figures','feed':'https://feeds.megaphone.fm/david-senra','days':30,'logo':'/david-senra-logo.jpg'},
 {'id':'relentless','name':'Relentless','module':'figures','feed':'https://anchor.fm/s/e402cdc8/podcast/rss','days':30,'logo':'/relentless-logo.jpg'},
 {'id':'invest-like-the-best','name':'Invest Like the Best','module':'figures','feed':'https://feeds.megaphone.fm/CLS2859450455','days':30,'logo':'/invest-like-the-best-logo.jpg'},
 {'id':'lex-fridman','name':'Lex Fridman Podcast','module':'figures','feed':'https://lexfridman.com/feed/podcast/','days':30},
 {'id':'greg-isenberg','name':'The Startup Ideas Podcast · Greg Isenberg','module':'figures','feed':'https://rss2.flightcast.com/ordbkg8yojpehffas7vr7qpc.xml','days':30},
 {'id':'sabrina-halper','name':'The Sabrina Halper Show','module':'figures','feed':'https://anchor.fm/s/9c3d9f04/podcast/rss','days':30},
 {'id':'y-combinator','name':'Y Combinator Startup Podcast','module':'figures','feed':'https://anchor.fm/s/8c1524bc/podcast/rss','days':30},
 {'id':'sourcery','name':'Sourcery with Molly O’Shea','module':'figures','feed':'https://anchor.fm/s/f192713c/podcast/rss','days':30},
 {'id':'ai-engineer','name':'AI Engineer','module':'figures','feed':'https://www.youtube.com/feeds/videos.xml?channel_id=UCLKPca3kwwd-B59HNr-_lvA','days':30,'logo':'https://yt3.googleusercontent.com/ajVemEB89DAOemsbfuMY6ZOWXJAACx3cbty9z21jeqRKODaVkDBSRun1b1xfQJljEsziOWS_Mg=s200-c-k-c0x00ffffff-no-rj'},
 {'id':'tbpn','name':'TBPN','module':'tbpn','feed':'https://feeds.transistor.fm/technology-brother','days':8},
 {'id':'openai','name':'OpenAI','module':'products','feed':'https://openai.com/news/rss.xml','days':120,'categories':['Product'],'logo':'/openai-logo.png'},
 {'id':'anthropic','name':'Anthropic','module':'products','page':'https://www.anthropic.com/news','parser':'anthropic','days':120,'logo':'/anthropic-logo.png'},
 {'id':'cursor','name':'Cursor','module':'products','feed':'https://cursor.com/changelog/rss.xml','days':120,'logo':'/cursor-logo.png'},
 {'id':'nvidia','name':'NVIDIA','module':'products','feed':'https://blogs.nvidia.com/feed/','days':120,'include_keywords':['launch','introduc','unveil','release','available','new','AI','robot'],'logo':'/nvidia-logo.png'},
 {'id':'amd','name':'AMD','module':'products','page':'https://newsroom.amd.com/category/ai/','parser':'amd','days':120,'include_keywords':['launch','introduc','unveil','release','available','new','ROCm'],'logo':'/amd-logo.png'},
 {'id':'deepmind','name':'Google DeepMind','module':'products','feed':'https://deepmind.google/blog/rss.xml','days':120,'include_keywords':['introduc','model','agent','gemini','alphafold','imagen','veo','robot','release','launch'],'logo':'/deepmind-logo.png'},
 {'id':'mistral','name':'Mistral AI','module':'products','feed':'https://mistral.ai/news/rss','days':120,'include_keywords':['introduc','launch','release','agent','model','vibe','search','studio','mcp','ocr','voice','workflow'],'logo':'/mistral-logo.png'},
 {'id':'stripe','name':'Stripe','module':'products','feed':'https://stripe.com/blog/feed.rss','days':120,'include_keywords':['AI','agent','model','launch','introduc'],'logo':'/stripe-logo.png'},
 {'id':'ramp','name':'Ramp','module':'products','page':'https://ramp.com/product-releases','parser':'ramp','days':120,'logo':'/ramp-logo.png'},
 {'id':'fed-policy','name':'Federal Reserve · Monetary policy','module':'economics','feed':'https://www.federalreserve.gov/feeds/press_monetary.xml','days':30,'logo':''},
 {'id':'fed-speeches','name':'Federal Reserve · Speeches','module':'economics','feed':'https://www.federalreserve.gov/feeds/speeches_and_testimony.xml','days':30,'logo':''},
]

def fetch(url):
 if urlparse(url).scheme!='https':raise ValueError('Source must use HTTPS.')
 p=subprocess.run(['curl','-fLsS','--max-time','40','--max-filesize','15000000','--proto','=https','--proto-redir','=https','-A','Mozilla/5.0',url],capture_output=True)
 if p.returncode:raise ValueError('Source unavailable. Try again later.')
 return p.stdout.decode('utf-8')

def plain(app,html):
 p=app.PageText();p.feed(html or '');return '\n'.join(x.strip() for x in ''.join(p.parts).splitlines() if x.strip())

def parse_feed(app,source,xml):
 root=ET.fromstring(xml);channel=root.find('channel')
 if channel is None and root.tag.endswith('feed'):
  atom='{http://www.w3.org/2005/Atom}';media='{http://search.yahoo.com/mrss/}';items=[]
  for entry in root.findall(atom+'entry'):
   title=entry.findtext(atom+'title','').strip();published_text=entry.findtext(atom+'published','') or entry.findtext(atom+'updated','')
   link=next((x.get('href','') for x in entry.findall(atom+'link') if x.get('rel','alternate')=='alternate'), '')
   try:published=datetime.fromisoformat(published_text.replace('Z','+00:00')).astimezone(timezone.utc)
   except (ValueError,TypeError):continue
   if not title or urlparse(link).scheme!='https' or published < datetime.now(timezone.utc)-timedelta(days=source.get('days',30)):continue
   group=entry.find(media+'group');description=group.findtext(media+'description','') if group is not None else entry.findtext(atom+'content','')
   identifier=hashlib.sha256(link.rstrip('/').encode()).hexdigest()[:24]
   items.append(dict(id=identifier,url=link,title=title,published=published.isoformat(),source=source['name'],source_id=source['id'],module=source['module'],guests=[],format='Video',length='',logo=source.get('logo',''),video=link,description=plain(app,description)[:5000],transcript_url=None,categories=[],is_diet=False))
  return items
 if channel is None:raise ValueError('Publisher did not return a valid RSS feed.')
 items=[]
 for item in channel.findall('item'):
  url=item.findtext('link','').strip();title=item.findtext('title','').strip()
  if not url:
   enclosure=item.find('enclosure')
   url=enclosure.get('url','') if enclosure is not None else ''
  if not title or urlparse(url).scheme!='https':continue
  try:published=parsedate_to_datetime(item.findtext('pubDate')).astimezone(timezone.utc)
  except (ValueError,TypeError):continue
  # First capture seeds 30 days; later refreshes retain every previously captured item.
  if published < datetime.now(timezone.utc)-timedelta(days=source.get('days',30)):continue
  categories=[x.text.strip() for x in item.findall('category') if x.text]
  if source.get('categories') and not set(categories).intersection(source['categories']):continue
  haystack=(title+' '+item.findtext('description','')).lower()
  if source.get('include_keywords') and not any(word.lower() in haystack for word in source['include_keywords']):continue
  enclosure=item.find('enclosure');transcript=item.find('{https://podcastindex.org/namespace/1.0}transcript')
  duration=item.findtext('{http://www.itunes.com/dtds/podcast-1.0.dtd}duration','')
  identifier=hashlib.sha256(url.rstrip('/').encode()).hexdigest()[:24]
  logo=source.get('logo','')
  if not logo:
   image=channel.find('{http://www.itunes.com/dtds/podcast-1.0.dtd}image');logo=image.get('href','') if image is not None else channel.findtext('image/url','')
  items.append(dict(id=identifier,url=url,title=title,published=published.isoformat(),source=source['name'],source_id=source['id'],module=source['module'],guests=[],format='Podcast' if enclosure is not None and enclosure.get('type','').startswith(('audio/','video/')) else 'Publication',length=duration,logo=logo,video='',description=plain(app,item.findtext('description',''))[:5000],transcript_url=transcript.get('url') if transcript is not None else None,categories=categories,is_diet=source['id']=='tbpn' and 'diet tbpn' in title.lower()))
  if enclosure is not None and enclosure.get('type','').startswith('audio/'):
   items[-1]['audio_url']=enclosure.get('url','')
  video=re.search(r'https://(?:www\.)?(?:youtube\.com/watch\?v=[\w-]+|youtu\.be/[\w-]+)',item.findtext('description',''))
  if video:items[-1]['video']=video.group()
 return items

def authority_item(app,source,url,title,published,description='',format='Publication'):
 identifier=hashlib.sha256(url.rstrip('/').encode()).hexdigest()[:24]
 return dict(id=identifier,url=url,title=title,published=published.isoformat(),source=source['name'],source_id=source['id'],module='authorities',guests=[],format=format,length='',logo=source.get('logo',''),video=url if format=='Video' else '',description=plain(app,description)[:5000],transcript_url=None,categories=[],is_diet=False)

def parse_sitemap(app,source,xml):
 root=ET.fromstring(xml);namespace='{http://www.sitemaps.org/schemas/sitemap/0.9}';cutoff=datetime.now(timezone.utc)-timedelta(days=source.get('days',30));items=[]
 for node in root.findall(namespace+'url'):
  url=node.findtext(namespace+'loc','').strip();stamp=node.findtext(namespace+'lastmod','')
  try:published=datetime.fromisoformat(stamp.replace('Z','+00:00')).astimezone(timezone.utc)
  except (ValueError,TypeError):continue
  if published<cutoff or urlparse(url).scheme!='https':continue
  slug=url.rstrip('/').split('/')[-1];title=' '.join(word.upper() if word.lower() in ('ai','agi','api','gpu') else word.capitalize() for word in slug.split('-'))
  items.append(authority_item(app,source,url,title,published))
 return items

def parse_coatue(app,source,html):
 match=re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',html,re.S)
 if not match:raise ValueError('Publisher page did not contain its article catalog.')
 data=json.loads(html_module.unescape(match.group(1)));cutoff=datetime.now(timezone.utc)-timedelta(days=source.get('days',180));items=[];seen=set()
 def walk(value):
  if isinstance(value,dict):
   if all(key in value for key in ('slug','heading','date','blogCategory')) and isinstance(value.get('blogCategory'),dict):
    category=value['blogCategory'].get('slug','perspective');url='https://www.coatue.com/blog/'+category+'/'+value['slug']
    try:published=datetime.fromisoformat(value['date'].replace('Z','+00:00')).astimezone(timezone.utc)
    except (ValueError,TypeError):published=None
    if published and published>=cutoff and url not in seen:
     seen.add(url);description=value.get('subheading') or value.get('author') or ''
     items.append(authority_item(app,source,url,value['heading'],published,description,'Video' if category=='video' else 'Publication'))
   for child in value.values():walk(child)
  elif isinstance(value,list):
   for child in value:walk(child)
 walk(data);return items

def parse_sequoia(app,source,xml):
 root=ET.fromstring(xml);namespace='{http://www.sitemaps.org/schemas/sitemap/0.9}';cutoff=datetime.now(timezone.utc)-timedelta(days=source.get('days',45));items=[];older=0
 urls=[node.findtext(namespace+'loc','').strip() for node in root.findall(namespace+'url')]
 for url in [url for url in urls if '/article/' in url][:24]:
  url=url.replace('https://sequoiacap.com/','https://www.sequoiacap.com/')
  page=fetch(url);date_match=re.search(r'"datePublished"\s*:\s*"([^"]+)',page);title_match=re.search(r'<title>(.*?)\s*\|\s*Sequoia Capital',page,re.S)
  if not date_match or not title_match:continue
  try:published=datetime.fromisoformat(date_match.group(1).replace('Z','+00:00')).astimezone(timezone.utc)
  except ValueError:continue
  if published<cutoff:
   older+=1
   if older>=5:break
   continue
  title=html_module.unescape(re.sub(r'<[^>]+>','',title_match.group(1))).strip();description_match=re.search(r'<meta[^>]+name="description"[^>]+content="([^"]*)',page,re.I)
  items.append(authority_item(app,source,url,title,published,html_module.unescape(description_match.group(1)) if description_match else ''))
 return items

class LinkCards(HTMLParser):
 def __init__(self):super().__init__();self.current=None;self.cards=[];self.heading=0
 def handle_starttag(self,tag,attrs):
  if tag=='a':self.current={'href':dict(attrs).get('href',''),'text':'','heading':''}
  if self.current and tag in ('h1','h2','h3','h4'):self.heading+=1
 def handle_endtag(self,tag):
  if self.current and tag in ('h1','h2','h3','h4') and self.heading:self.heading-=1
  if tag=='a' and self.current:self.cards.append(self.current);self.current=None;self.heading=0
 def handle_data(self,data):
  if self.current:
   self.current['text']+=' '+data
   if self.heading:self.current['heading']+=' '+data

def product_item(app,source,url,title,published,description=''):
 identifier=hashlib.sha256(url.rstrip('/').encode()).hexdigest()[:24]
 return dict(id=identifier,url=url,title=title,published=published.isoformat(),source=source['name'],source_id=source['id'],module='products',guests=[],format='Product release',length='',logo=source['logo'],video='',description=plain(app,description)[:5000],transcript_url=None,categories=['Product'],is_diet=False)

def parse_product_page(app,source,html):
 cutoff=datetime.now(timezone.utc)-timedelta(days=source.get('days',30));items=[];seen=set()
 if source['parser']=='ramp':
  pattern=re.compile(r'\\"date\\":\\"(?P<date>\d{4}-\d{2}-\d{2})\\",\\"description\\":\\"(?P<description>.*?)\\".*?\\"name\\":\\"(?P<title>.*?)\\",\\"pathname\\":\\"(?P<path>/product-releases/[^\\"]+)',re.S)
  for match in pattern.finditer(html):
   published=datetime.fromisoformat(match['date']).replace(tzinfo=timezone.utc);url=urljoin(source['page'],match['path'])
   if published>=cutoff and url not in seen:
    seen.add(url);items.append(product_item(app,source,url,match['title'],published,match['description']))
  return items
 parser=LinkCards();parser.feed(html)
 months='January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec'
 date_re=re.compile(r'(?P<date>(?:'+months+r')\s+\d{1,2},\s+\d{4})')
 for card in parser.cards:
  href=card['href'];text=' '.join(card['text'].split());match=date_re.search(text)
  if not match or '/news/' not in href:continue
  if source['parser']=='anthropic' and not re.search(r'\bProduct\b',text[:match.start()+20]):continue
  published=datetime.strptime(match['date'],'%B %d, %Y' if len(match['date'].split()[0])>3 else '%b %d, %Y').replace(tzinfo=timezone.utc)
  url=urljoin(source['page'],href)
  if published<cutoff or url in seen:continue
  title=' '.join(card['heading'].split())
  after=text[match.end():].strip();after=re.sub(r'^(Product|Artificial Intelligence|Software|Embedded|Data Center)\s+','',after)
  if not title:
   slug=href.rstrip('/').split('/')[-1];title=' '.join(x.capitalize() if x.lower() not in ('ai','amd') else x.upper() for x in slug.split('-'))
  haystack=(title+' '+after).lower()
  if source.get('include_keywords') and not any(word.lower() in haystack for word in source['include_keywords']):continue
  seen.add(url);items.append(product_item(app,source,url,title,published,after))
 return items

def parse_epoch(app,source,html):
 text=html_module.unescape(html)
 pattern=re.compile(r'"url":\[0,"(?P<url>/[^"]+)"\],"title":\[0,"(?P<title>[^"]+)"\],"date":\[3,"(?P<date>\d{4}-\d{2}-\d{2})T[^\"]+"\].*?"description":\[0,"(?P<description>[^"]*)"\]',re.S)
 items=[];seen=set();cutoff=datetime.now(timezone.utc)-timedelta(days=source.get('days',30))
 for match in pattern.finditer(text):
  url='https://epoch.ai'+match['url'];published=datetime.fromisoformat(match['date']).replace(tzinfo=timezone.utc)
  if url in seen or published<cutoff:continue
  seen.add(url);identifier=hashlib.sha256(url.rstrip('/').encode()).hexdigest()[:24]
  items.append(dict(id=identifier,url=url,title=match['title'],published=published.isoformat(),source=source['name'],source_id=source['id'],module=source['module'],guests=[],format='Publication',length='',logo='',video='',description=plain(app,match['description'])[:5000],transcript_url=None,categories=[],is_diet=False))
 return items

def parse_source(app,source,raw):
 if source['id']=='epoch-ai':return parse_epoch(app,source,raw)
 if source.get('parser')=='sitemap':return parse_sitemap(app,source,raw)
 if source.get('parser')=='coatue':return parse_coatue(app,source,raw)
 if source.get('parser')=='sequoia':return parse_sequoia(app,source,raw)
 if source.get('parser'):return parse_product_page(app,source,raw)
 return parse_feed(app,source,raw)
