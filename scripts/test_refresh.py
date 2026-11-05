import contextlib,io,unittest
from unittest.mock import patch
import refresh
import catalog
import text_parser

class RefreshTests(unittest.TestCase):
 def test_preserves_analysis_and_failed_source_history(self):
  snapshot={'episode':{'url':'https://example.com/pilot'},'publications':[{'id':'one','url':'https://example.com/one','published':'2026-09-01','result':{'summary':'saved analysis'},'profiles':[{'name':'Guest'}]},{'id':'two','published':'2026-08-01'}]}
  def fetch(source):
   if source['id']=='bad':raise ValueError('unavailable')
   return [{'id':'one','url':'https://example.com/one','published':'2026-09-15','title':'Updated title'}]
  with patch.object(refresh.catalog,'SOURCES',[{'id':'good'},{'id':'bad'}]),contextlib.redirect_stdout(io.StringIO()):out=refresh.refresh(snapshot,fetch)
  self.assertEqual(out['publications'][0]['result']['summary'],'saved analysis')
  self.assertEqual(out['publications'][0]['profiles'][0]['name'],'Guest')
  self.assertEqual(len(out['publications']),2)
  self.assertEqual(out['refresh_failures'],1)
 def test_removes_old_product_items_that_no_longer_match_source_filter(self):
  snapshot={'episode':{'url':'https://example.com/pilot'},'publications':[{'id':'old','url':'https://example.com/old','published':'2026-09-01','module':'products','source_id':'maker','title':'An opinion about AI','description':''}]}
  source={'id':'maker','module':'products','title_keywords':['launch']}
  with patch.object(refresh.catalog,'SOURCES',[source]),contextlib.redirect_stdout(io.StringIO()):out=refresh.refresh(snapshot,lambda s:[])
  self.assertEqual(out['publications'],[])
 def test_total_failure_does_not_publish(self):
  with patch.object(refresh.catalog,'SOURCES',[{'id':'bad'}]),contextlib.redirect_stdout(io.StringIO()),self.assertRaises(RuntimeError):
   refresh.refresh({'episode':{},'publications':[]},lambda s:1/0)
 def test_anthropic_current_newsroom_layout_captures_products_and_models(self):
  source={'id':'anthropic','name':'Anthropic','module':'products','page':'https://www.anthropic.com/news','parser':'anthropic','days':120,'logo':'/anthropic-logo.png'}
  html='''
  <article><header><a href="/news/announcements">Announcements</a><time>Oct 7, 2026</time></header><a class="tileLink" href="/claude-haiku-5-5"><h3>Introducing Claude Haiku 5.5</h3><p>Our fastest small model.</p></a></article>
  <li data-listing-row="one"><a class="title-link" href="/news/agent-skills"><h3>Donating Agent Skills</h3></a><p>An open standard for agents.</p><a href="/news/product">Product</a><time>Oct 22, 2026</time></li>
  <article><header><a href="/news/company">Company</a><time>Oct 20, 2026</time></header><a class="tileLink" href="/news/new-office"><h3>Opening a new office</h3><p>Company news.</p></a></article>
  '''
  items=catalog.parse_product_page(text_parser,source,html)
  self.assertEqual([item['title'] for item in items],['Introducing Claude Haiku 5.5','Donating Agent Skills'])

if __name__=='__main__':unittest.main()
