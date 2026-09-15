"""Refresh public listings without credentials, transcripts, or model calls."""
import concurrent.futures
import json
from datetime import datetime, timezone
from pathlib import Path
import sys
import catalog
import text_parser

def collect(source):
    raw = catalog.fetch(source.get('feed') or source['page'])
    parser = catalog.parse_epoch if source['id']=='epoch-ai' else catalog.parse_product_page if source.get('parser') else catalog.parse_feed
    return parser(text_parser,source,raw)

def refresh(snapshot, fetch_source=collect):
    stamp=datetime.now(timezone.utc).isoformat()
    items={item['id']:item for item in snapshot['publications']}
    statuses={s['id']:s for s in snapshot.get('sources',[])}
    failures=0
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        tasks={executor.submit(fetch_source,source):source for source in catalog.SOURCES}
        for future in concurrent.futures.as_completed(tasks):
            source=tasks[future]
            try:
                captured=future.result()
                for item in captured:
                    if item['url'].rstrip('/')==snapshot['episode']['url'].rstrip('/'):continue
                    old=items.get(item['id'],{})
                    items[item['id']]={**old,**item,'status':'ready' if old.get('result') else 'idle','saved':0,'error':None,'result':old.get('result'),'transcript_words':0,'provenance':None}
                statuses[source['id']]={'id':source['id'],'checked':stamp,'error':None,'count':len(captured)}
                print(source['id'],len(captured),'releases')
            except Exception as error:
                failures+=1
                statuses[source['id']]={**statuses.get(source['id'],{}),'id':source['id'],'error':'Feed unavailable; previous releases retained.','attempted':stamp}
                print(source['id'],'refresh failed:',type(error).__name__)
    if failures==len(catalog.SOURCES):raise RuntimeError('All sources failed; retaining previous edition')
    snapshot.update(publications=sorted(items.values(),key=lambda x:x['published'],reverse=True),sources=list(statuses.values()),refreshed_at=stamp,refresh_failures=failures)
    return snapshot

if __name__=='__main__':
    path=Path(sys.argv[1] if len(sys.argv)>1 else 'shared-state.json')
    snapshot=refresh(json.loads(path.read_text()))
    temp=path.with_suffix('.tmp')
    temp.write_text(json.dumps(snapshot,separators=(',',':')))
    temp.replace(path)
