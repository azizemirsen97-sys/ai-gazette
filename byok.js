const AI_SETTINGS_KEY='gazette-ai-settings-v1';
const AI_PROVIDERS={
 openai:{name:'OpenAI',placeholder:'sk-…',model:'gpt-5.5',link:'https://platform.openai.com/api-keys'},
 anthropic:{name:'Anthropic',placeholder:'sk-ant-…',model:'claude-sonnet-5',link:'https://console.anthropic.com/settings/keys'},
 gemini:{name:'Google Gemini',placeholder:'AI…',model:'gemini-3.8-flash',link:'https://aistudio.google.com/app/apikey'},
 xai:{name:'xAI',placeholder:'xai-…',model:'grok-4.7',link:'https://console.x.ai/'}
};
function readAISettings(){try{const value=JSON.parse(localStorage.getItem(AI_SETTINGS_KEY)||'{}');return {provider:value.provider||'openai',keys:value.keys||{}}}catch(e){return {provider:'openai',keys:{}}}}
function writeAISettings(value){localStorage.setItem(AI_SETTINGS_KEY,JSON.stringify(value))}
window.gazetteAI={
 settings:readAISettings,
 key(provider){return readAISettings().keys[provider]||''},
 configured(provider){const s=readAISettings();return !!s.keys[provider||s.provider]},
 provider(){return readAISettings().provider},
 name(provider){return AI_PROVIDERS[provider||readAISettings().provider]?.name||'AI'},
 async ask({system,prompt,provider,maxTokens=1800}){
  const settings=readAISettings(),id=provider||settings.provider,key=settings.keys[id],config=AI_PROVIDERS[id];
  if(!key)throw Error(`Add your ${config.name} API key first.`);
  let response,body;
  if(id==='openai'||id==='xai'){
   response=await fetch(id==='openai'?'https://api.openai.com/v1/responses':'https://api.x.ai/v1/responses',{method:'POST',headers:{'Content-Type':'application/json','Authorization':`Bearer ${key}`},body:JSON.stringify({model:config.model,store:false,max_output_tokens:maxTokens,tools:[{type:'web_search'}],input:[{role:'system',content:system},{role:'user',content:prompt}]})});
   body=await response.json();if(!response.ok)throw Error(body.error?.message||`${config.name} rejected this request.`);
   return body.output_text||(body.output||[]).flatMap(x=>x.content||[]).filter(x=>x.type==='output_text').map(x=>x.text).join('\n');
  }
  if(id==='anthropic'){
   response=await fetch('https://api.anthropic.com/v1/messages',{method:'POST',headers:{'Content-Type':'application/json','x-api-key':key,'anthropic-version':'2023-06-01','anthropic-dangerous-direct-browser-access':'true'},body:JSON.stringify({model:config.model,max_tokens:maxTokens,system,tools:[{type:'web_search_20250305',name:'web_search',max_uses:8}],messages:[{role:'user',content:prompt}]})});
   body=await response.json();if(!response.ok)throw Error(body.error?.message||'Anthropic rejected this request.');return (body.content||[]).filter(x=>x.type==='text').map(x=>x.text).join('\n');
  }
  response=await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${config.model}:generateContent`,{method:'POST',headers:{'Content-Type':'application/json','x-goog-api-key':key},body:JSON.stringify({systemInstruction:{parts:[{text:system}]},contents:[{role:'user',parts:[{text:prompt}]}],generationConfig:{maxOutputTokens:maxTokens},tools:[{googleSearch:{}}]})});
  body=await response.json();if(!response.ok)throw Error(body.error?.message||'Gemini rejected this request.');return (body.candidates?.[0]?.content?.parts||[]).map(x=>x.text||'').join('\n');
 }
};

const aiDialog=document.createElement('dialog');aiDialog.id='ai-key-settings';
aiDialog.innerHTML=`<form id="ai-key-form"><div class="dialog-heading"><p class="eyebrow">BRING YOUR OWN AI</p><button type="button" id="ai-key-close" aria-label="Close key settings">×</button></div><h2>Add your AI key.</h2><p>Choose the provider you want for questions and further analysis on Gazette pages. Your key stays in this browser and goes directly to that provider. The Gazette never receives it. It is stored locally without encryption, so use a browser you trust.</p><label for="ai-provider">AI provider</label><select id="ai-provider">${Object.entries(AI_PROVIDERS).map(([id,p])=>`<option value="${id}">${p.name}</option>`).join('')}</select><label for="ai-api-key">API key</label><input id="ai-api-key" type="password" autocomplete="off" required><p id="ai-key-help" class="small"></p><div class="x-key-actions"><button class="button primary" type="submit">Save this key</button><button class="text-button" id="ai-key-remove" type="button">Remove saved key</button></div><p id="ai-key-result" role="status"></p></form>`;
document.body.append(aiDialog);
function drawAIKey(provider){const p=AI_PROVIDERS[provider],has=!!gazetteAI.key(provider);document.querySelector('#ai-provider').value=provider;document.querySelector('#ai-api-key').placeholder=p.placeholder;document.querySelector('#ai-api-key').value='';document.querySelector('#ai-key-help').innerHTML=`Used for page questions and analysis with ${p.name}. <a href="${p.link}" target="_blank" rel="noopener noreferrer">Get a key ↗</a> ${has?'A key is already saved for this provider.':''}`;document.querySelector('#ai-key-result').textContent=''}
window.openAIKeySettings=(provider)=>{drawAIKey(provider||gazetteAI.provider());aiDialog.showModal()};
document.querySelector('#ai-provider').onchange=e=>drawAIKey(e.target.value);
document.querySelector('#ai-key-close').onclick=()=>aiDialog.close();
document.querySelector('#ai-key-remove').onclick=()=>{const provider=document.querySelector('#ai-provider').value,s=readAISettings();delete s.keys[provider];writeAISettings(s);drawAIKey(provider);window.render?.();window.notice?.(`${AI_PROVIDERS[provider].name} key removed from this browser`)};
document.querySelector('#ai-key-form').onsubmit=e=>{e.preventDefault();const provider=document.querySelector('#ai-provider').value,key=document.querySelector('#ai-api-key').value.trim();if(key.length<8){document.querySelector('#ai-key-result').textContent='That key looks incomplete.';return}const s=readAISettings();s.provider=provider;s.keys[provider]=key;try{writeAISettings(s)}catch(error){document.querySelector('#ai-key-result').textContent='This browser could not save the key.';return}aiDialog.close();window.render?.();window.notice?.(`${AI_PROVIDERS[provider].name} connected for private page analysis`)};
