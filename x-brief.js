// Each reader's X brief and xAI credential stay in that reader's browser.
const X_KEY_STORAGE='gazette-xai-key';
const X_BRIEF_STORAGE='gazette-x-brief-v1';
const X_BRIEF_ATTEMPT_STORAGE='gazette-x-brief-last-attempt';
const X_BRIEF_INTERVAL=90*60*1000;
let xBrief=null,xBriefWorking=false,xBriefError='';
let xBriefAttemptAt=0;
try{xBriefAttemptAt=Number(localStorage.getItem(X_BRIEF_ATTEMPT_STORAGE))||0}catch(e){}
const X_BRIEF_FORMAT={type:'json_schema',name:'x_brief',strict:true,schema:{type:'object',properties:{items:{type:'array',items:{type:'object',properties:{headline:{type:'string'},explanation:{type:'string'},signal:{type:'string'},posts:{type:'array',items:{type:'object',properties:{url:{type:'string'},handle:{type:'string'}},required:['url','handle'],additionalProperties:false}}},required:['headline','explanation','signal','posts'],additionalProperties:false}}},required:['items'],additionalProperties:false}};
try{xBrief=JSON.parse(localStorage.getItem(X_BRIEF_STORAGE)||'null')}catch(e){}
function xKey(){try{return localStorage.getItem(X_KEY_STORAGE)||''}catch(e){return ''}}
function xBriefTime(){return xBrief?.generated_at?new Date(xBrief.generated_at).toLocaleString('en-US',{month:'short',day:'numeric',hour:'numeric',minute:'2-digit'}):''}
function xPost(post){
 let url='';try{const parsed=new URL(post?.url);if(['x.com','www.x.com','twitter.com','www.twitter.com'].includes(parsed.hostname)&&/^\/[^/]+\/status\/\d+/.test(parsed.pathname))url=parsed.href}catch(e){}
 if(!url)return '';
 return `<a href="${esc(url)}" target="_blank" rel="noopener noreferrer">${esc(post.handle||'X post')} ↗</a>`;
}
function xStory(item){return `<article class="x-story"><p class="x-signal">${esc(item.signal||'NEW SIGNAL')}</p><h3>${esc(item.headline)}</h3><p>${esc(item.explanation)}</p><div class="x-posts">${(item.posts||[]).map(xPost).filter(Boolean).join('')}</div></article>`}
function xBriefBody(limit){
 if(xBrief?.items?.length)return `<p class="x-updated">Updated ${esc(xBriefTime())} · Based on public X posts · ${xBrief.items.length} signals</p><div class="x-story-grid">${xBrief.items.slice(0,limit).map(xStory).join('')}</div>${xBrief.items.length>limit?'<a class="x-more" href="#module/x">Read the full X Brief ↗</a>':''}`;
 if(!xKey())return '<div class="x-empty"><p>Connect your xAI key to find novel posts, product launches, and emerging arguments across X.</p><button class="button" data-x-act="connect">Add your xAI key ↗</button></div>';
 return `<div class="x-empty"><p>${xBriefWorking?'Researching recent posts across X…':'Your X Brief is ready to build.'}</p></div>`;
}
function xBriefControls(){return `<button class="button" data-x-act="refresh" ${xBriefWorking||!xKey()?'disabled':''}>${xBriefWorking?'Finding signals…':'Refresh X Brief ↻'}</button>${!xKey()?'<button class="text-button" data-x-act="connect">Connect xAI</button>':''}`}
window.xBriefHome=()=>`<section class="gazette-module module-wide x-brief"><div class="module-heading"><div><h2><a href="#module/x">X Brief ↗</a></h2><p>Fresh public posts, filtered for useful and unusual ideas.</p></div><span class="module-caption">${xBriefWorking?'RESEARCHING':xBrief?.items?.length?'PERSONAL BRIEF':'CONNECT TO START'}</span></div><div class="x-controls">${xBriefControls()}<span>Checks every 90 minutes while this page is open. Each check uses your xAI API billing.</span></div>${xBriefError?`<p class="status-note error">${esc(xBriefError)}</p>`:''}${xBriefBody(6)}</section>`;
window.xBriefArchive=()=>`<a class="back" href="#">← BACK TO THE EDITION</a><section class="x-brief"><div class="page-heading compact-heading"><div><p class="eyebrow">PUBLIC X RESEARCH</p><h1>X Brief</h1><p>Signals from recent posts, ranked for novelty and usefulness.</p></div></div><div class="x-controls">${xBriefControls()}<span>Checks every 90 minutes while this page is open. Each check uses your xAI API billing.</span></div>${xBriefError?`<p class="status-note error">${esc(xBriefError)}</p>`:''}${xBriefBody(Infinity)}</section>`;

const xKeyDialog=document.createElement('dialog');
xKeyDialog.id='x-key-settings';
xKeyDialog.innerHTML='<form id="x-key-form"><div class="dialog-heading"><p class="eyebrow">YOUR X CONNECTION</p><button type="button" id="x-key-close" aria-label="Close key settings">×</button></div><h2>Add your own key.</h2><p>An <a href="https://console.x.ai/" target="_blank" rel="noopener noreferrer">xAI API key</a> powers your X Brief. It searches public X posts, not your personal For You feed. The key stays in this browser and is sent directly to xAI; this site does not receive it. It is stored locally without encryption, so use a browser you trust.</p><label for="x-api-key">xAI API key</label><input id="x-api-key" type="password" autocomplete="off" placeholder="xai-…" required><p class="small">Search and model usage are billed by xAI. The brief refreshes at most every 90 minutes while this page is open.</p><div class="x-key-actions"><button class="button primary" type="submit">Save key & build brief</button><button class="text-button" id="x-key-remove" type="button">Remove saved key</button></div><p id="x-key-result" role="status"></p></form>';
document.body.append(xKeyDialog);
window.openXKeySettings=()=>{document.querySelector('#x-key-result').textContent=xKey()?'A key is saved in this browser. Enter a new one to replace it.':'';xKeyDialog.showModal()};
document.querySelector('#x-key-close').onclick=()=>xKeyDialog.close();
document.querySelector('#x-key-remove').onclick=()=>{try{localStorage.removeItem(X_KEY_STORAGE)}catch(e){}document.querySelector('#x-api-key').value='';xKeyDialog.close();xBriefError='';if(window.render)render();if(window.notice)notice('xAI key removed from this browser')};
document.querySelector('#x-key-form').onsubmit=event=>{event.preventDefault();const key=document.querySelector('#x-api-key').value.trim();if(!key.startsWith('xai-')){document.querySelector('#x-key-result').textContent='Please enter an xAI API key beginning with xai-.';return}try{localStorage.setItem(X_KEY_STORAGE,key)}catch(e){document.querySelector('#x-key-result').textContent='This browser could not save the key. Allow site storage and try again.';return}document.querySelector('#x-api-key').value='';xKeyDialog.close();if(window.render)render();refreshXBrief(true)};
document.addEventListener('click',event=>{const action=event.target.closest('[data-x-act]')?.dataset.xAct;if(action==='connect')openXKeySettings();if(action==='refresh')refreshXBrief(true)});

function xResponseText(response){
 if(typeof response.output_text==='string')return response.output_text;
 return (response.output||[]).flatMap(entry=>(entry.content||[]).filter(part=>part.type==='output_text'||part.type==='text').map(part=>part.text||'')).join('\n');
}
function parseXBrief(response){
 const raw=xResponseText(response).trim().replace(/^```(?:json)?\s*/i,'').replace(/\s*```$/,'');
 const result=JSON.parse(raw);
 if(!Array.isArray(result.items))throw Error('xAI returned a brief in an unexpected format. Please retry.');
 const items=result.items.filter(item=>item&&typeof item.headline==='string'&&typeof item.explanation==='string'&&Array.isArray(item.posts)&&item.posts.some(post=>xPost(post)));
 if(!items.length)throw Error('No source-linked X posts came back. Please retry later.');
 return {generated_at:new Date().toISOString(),items:items.slice(0,15)};
}
async function refreshXBrief(force=false){
 if(xBriefWorking||!xKey()||typeof data==='undefined'||!data)return;
 if(!force&&((xBrief?.generated_at&&Date.now()-new Date(xBrief.generated_at).getTime()<X_BRIEF_INTERVAL)||Date.now()-xBriefAttemptAt<X_BRIEF_INTERVAL))return;
 xBriefAttemptAt=Date.now();try{localStorage.setItem(X_BRIEF_ATTEMPT_STORAGE,String(xBriefAttemptAt))}catch(e){}xBriefWorking=true;xBriefError='';render();
 const controller=new AbortController(),timeout=setTimeout(()=>controller.abort(),120000);
 try{
  const response=await fetch('https://api.x.ai/v1/responses',{
   method:'POST',signal:controller.signal,
   headers:{'Content-Type':'application/json','Authorization':`Bearer ${xKey()}`},
   body:JSON.stringify({model:'grok-4.6',store:false,text:{format:X_BRIEF_FORMAT},tools:[{type:'x_search',from_date:new Date(Date.now()-24*60*60*1000).toISOString(),to_date:new Date().toISOString()}],input:[{role:'system',content:'You are the editor of a high-signal AI and technology intelligence brief. Research public X posts from the last 24 hours using X Search. Find distinct, source-linked signals about frontier AI, models, infrastructure, chips, robotics, physical manufacturing, funding, or surprising product launches. Prefer original insights and non-obvious observations over popular takes or engagement. A unique well-reasoned post may be included even if no one else discusses it. When a theme has several materially different takes, include representative links and explain the disagreement. Do not invent posts or URLs. Keep the search focused to control cost. Return 8-12 items if evidence warrants, otherwise fewer. Every item must have at least one genuine direct X status URL. Rank by novelty, importance, and usefulness. Use plain English and attribute claims.'},{role:'user',content:'Build my X Brief now. Today is '+new Date().toISOString()+'. Search recent posts directly; do not rely on old cached news.'}]})
  });
  const body=await response.json();
  if(!response.ok)throw Error(body.error?.message||body.message||`xAI returned ${response.status}. Check your key and billing.`);
  const next=parseXBrief(body);
  localStorage.setItem(X_BRIEF_STORAGE,JSON.stringify(next));xBrief=next;
  if(window.notice)notice('X Brief updated from recent posts');
 }catch(error){xBriefError=error.name==='AbortError'?'X search took too long. Please try again.':error.message}
 finally{clearTimeout(timeout);xBriefWorking=false;render()}
}
window.refreshXBrief=refreshXBrief;
window.addEventListener('storage',event=>{if([X_KEY_STORAGE,X_BRIEF_STORAGE].includes(event.key)){try{xBrief=JSON.parse(localStorage.getItem(X_BRIEF_STORAGE)||'null')}catch(e){xBrief=null}if(typeof data!=='undefined'&&data)render()}});
setInterval(()=>{if(!document.hidden)refreshXBrief()},5*60*1000);
window.addEventListener('focus',()=>refreshXBrief());
