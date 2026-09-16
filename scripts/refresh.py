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
    return catalog.parse_source(text_parser,source,raw)

def canonical_url(url):
    return (url or '').rstrip('/').replace('https://www.','https://',1)

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
                    for existing_id,existing in list(items.items()):
                        if existing_id!=item['id'] and canonical_url(existing.get('url'))==canonical_url(item['url']):del items[existing_id]
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
