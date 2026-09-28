import contextlib,io,unittest
from unittest.mock import patch
import refresh

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

if __name__=='__main__':unittest.main()
