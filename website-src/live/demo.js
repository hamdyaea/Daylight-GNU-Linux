// Developer: Hamdy Abou El Anein
// Contact: info@daylightlinux.ch
// SPDX-License-Identifier: GPL-3.0-only
'use strict';
let emulator=null, generation=0, controller=null, state='idle', deadline=null, lifetime=null, serial='';
let stopTask=null, visibilityBusy=false, loadedLibraryHash=null;
const lang=new URLSearchParams(location.search).get('lang')==='en'?'en':'fr';
const $=id=>document.getElementById(id);
if(new URLSearchParams(location.search).get('embed')==='1')document.body.classList.add('embedded-preview');
const text=(fr,en)=>lang==='fr'?fr:en;
const english={title:'A real Linux desktop.<br>Inside your browser.',intro:'A lightweight, temporary preview of the Daylight spirit. Computing happens on your device, not on our Raspberry Pi.','scope-title':'A preview, not the complete distribution.',scope:'This experimental edition uses Alpine Linux x86 and Fluxbox. Daylight for Raspberry Pi remains based on Debian / Raspberry Pi OS ARM64. This preview does not include all of its Rust tools.',instructions:'Daylight Start opens your terminal automatically. Click inside it to type. Right-click the wallpaper for applications, or use Super+Enter for another terminal. Restart discards the current session; Stop releases it.','privacy-title':'Your session stays local',privacy:'No account, no disk shared with our server, no external guest-network relay and no telemetry. Demo files download over HTTPS; the host sees that connection like any webpage request.','temporary-title':'Nothing to install',temporary:'Changes are temporary: closing, stopping or restarting discards the session. Do not enter passwords or sensitive data. The demo pauses when its tab is hidden, resumes when you return, and stops after 20 minutes.','requirements-title':'A bounded preview',requirements:'The Linux guest receives 256 MiB of RAM; the browser also needs its own memory. Startup depends on your device and connection. No public container runs on our Pi.','technical-title':'Technical details and licenses',technical:'Linux is actually emulated in WebAssembly using v86. This is not an interactive screenshot. The guest has no external network relay. Free-software components retain their own licenses.',cta:'Ready to use Daylight on your Raspberry Pi?','placeholder-text':'Your session starts here.','mobile-title':'Daylight Web is designed for desktop and laptop computers.','mobile-detail':'On phones and tablets, some features may not work correctly: keyboard, mouse, right-click menus, shortcuts and display. For the full Linux desktop experience, use a computer with an up-to-date browser.','loading-hint':'First startup may take one to three minutes depending on your device and connection. Please keep this tab open.'};
const original=Object.fromEntries(Object.keys(english).map(id=>[id,$(id).innerHTML]));
const RUNTIME_NAMES=['libv86.js','seabios.bin','vgabios.bin','vmlinuz.bin','initrd.bin','v86.wasm'];
function labels(){
 document.documentElement.lang=lang;
 document.title=text('Daylight Start — un vrai Linux dans votre navigateur','Daylight Start — real Linux inside your browser');
 $('cta').href=lang==='fr'?'/fr/raspberry-pi.html':'/raspberry-pi.html';
 for(const [id,value] of Object.entries(lang==='en'?english:original))$(id).innerHTML=value;
 $('language').textContent=lang==='fr'?'English':'Français';
 $('language').href=lang==='fr'?'?lang=en':'?lang=fr';
 $('start').textContent=text('Démarrer','Start');
 $('reset').textContent=text('Redémarrer','Restart');
 $('stop').textContent='Stop';
 $('display').setAttribute('aria-label',text('Bureau Linux interactif','Interactive Linux desktop'));
 $('mobile-input-label').textContent=text('Clavier tactile · saisissez une commande Linux','Touch keyboard · enter a Linux command');
 $('mobile-command').placeholder=text('Ex. ls -la','e.g. ls -la');
 $('mobile-command').setAttribute('aria-label',text('Commande à envoyer au terminal Linux','Command to send to the Linux terminal'));
 $('mobile-send').textContent=text('Envoyer ↵','Send ↵');
 $('mobile-input-help').textContent=text('Touchez le champ pour ouvrir le clavier de votre téléphone. « Envoyer » transmet la ligne au véritable terminal. Pour Vim et les raccourcis graphiques, un ordinateur est conseillé.','Tap the field to open your phone keyboard. Send passes the line to the real terminal. A computer is recommended for Vim and graphical keyboard shortcuts.');
 if(state==='idle')status(text('Aucun système lancé. Environ 46,4 Mo seront téléchargés au premier démarrage.','Nothing is running. The first start downloads about 46.4 MB.'));
}
function status(value){
 $('status').textContent=value;
 $('loading-detail').textContent=value;
}
function setState(value){
 state=value;document.body.dataset.state=value;
 $('start').disabled=!['idle','error'].includes(value);
 $('stop').disabled=['idle','stopping'].includes(value);
 $('reset').disabled=['idle','stopping'].includes(value);
 $('display').setAttribute('aria-busy',String(['loading','booting'].includes(value)));
 labels();
 if(value==='loading')$('loading-title').textContent=text('Préparation de Daylight Web…','Preparing Daylight Web…');
 if(value==='booting')$('loading-title').textContent=text('Démarrage du bureau Linux…','Starting the Linux desktop…');
}
function hex(bytes){return Array.from(bytes,b=>b.toString(16).padStart(2,'0')).join('');}
function cancelled(){return new DOMException('Cancelled','AbortError');}
function checkCancelled(signal){if(signal.aborted)throw cancelled();}
function wait(milliseconds,signal){
 return new Promise((resolve,reject)=>{
  if(signal.aborted){reject(cancelled());return;}
  const abort=()=>{clearTimeout(timer);signal.removeEventListener('abort',abort);reject(cancelled());};
  const timer=setTimeout(()=>{signal.removeEventListener('abort',abort);resolve();},milliseconds);
  signal.addEventListener('abort',abort,{once:true});
 });
}
// All startup downloads, including the first manifest, use bounded/cancellable retry.
// Retrying is limited to transport errors and selected transient HTTP responses.
async function requestBytes(path,label,signal,{limit,expected=null,cache='no-store',timeoutMs=20000,onProgress=()=>{}}){
 if(!/^[A-Za-z0-9][A-Za-z0-9_.-]*(?:\?[A-Za-z0-9_=&.-]+)?$/.test(path)||!Number.isSafeInteger(limit)||limit<1||limit>100000000)throw Error('Invalid download request');
 for(let attempt=0;attempt<3;attempt++){
  checkCancelled(signal);
  const transfer=new AbortController();
  const abort=()=>transfer.abort();signal.addEventListener('abort',abort,{once:true});
  const timer=setTimeout(()=>transfer.abort(),timeoutMs);
  let length=0;
  try{
   const response=await fetch(path,{credentials:'omit',signal:transfer.signal,cache:attempt?'reload':cache,redirect:'error'});
   if(!response.ok){
    const error=Error(label+' : HTTP '+response.status);
    error.retryable=[408,429,500,502,503,504].includes(response.status);throw error;
   }
   if(!response.body)throw Error(label+' : empty response body');
   const reader=response.body.getReader(),chunks=[];
   while(true){
    const {done,value}=await reader.read();if(done)break;
    if(length+value.length>limit){await reader.cancel();throw Error(label+' : unexpected asset size');}
    length+=value.length;chunks.push(value);onProgress(value.length);
   }
   if(expected!==null&&length!==expected){const error=Error(label+' : incomplete download');error.retryable=true;throw error;}
   const bytes=new Uint8Array(length);let offset=0;
   for(const chunk of chunks){bytes.set(chunk,offset);offset+=chunk.length;}
   return bytes;
  }catch(error){
   checkCancelled(signal);
   const retryable=error instanceof TypeError||error.name==='AbortError'||error.retryable===true;
   if(!retryable)throw error;
   if(length)onProgress(-length);
   if(attempt===2)throw Error(label+text(' : téléchargement impossible après trois essais. Vérifiez la connexion ou un éventuel filtrage de ce site, puis cliquez sur Redémarrer.',' : download failed after three attempts. Check connectivity or filtering of this site, then choose Restart.'));
   status(label+text(' — connexion interrompue, nouvel essai ',' — connection interrupted, retry ')+(attempt+2)+'/3…');
   await wait(500*(attempt+1),signal);
  }finally{clearTimeout(timer);signal.removeEventListener('abort',abort);}
 }
}
function checkRecord(name,record){
 if(!record||!Number.isSafeInteger(record.bytes)||record.bytes<1||record.bytes>100000000||!/^[a-f0-9]{64}$/.test(record.sha256))throw Error('Invalid asset manifest: '+name);
 if(record.parts!==undefined){
  if(record.file||!Array.isArray(record.parts)||record.parts.length<2||record.parts.length>16||name==='libv86.js')throw Error('Invalid chunk manifest: '+name);
  let total=0;const files=new Set();
  for(const part of record.parts){
   if(!part||part.parts!==undefined||part.bytes>16*1024*1024)throw Error('Invalid asset chunk: '+name);
   const file=checkRecord(name,part);if(files.has(file))throw Error('Duplicate asset chunk: '+name);files.add(file);total+=part.bytes;
  }
  if(total!==record.bytes)throw Error('Invalid chunk total: '+name);
  return null;
 }
 const file=record.file||name;
 if(!/^[A-Za-z0-9][A-Za-z0-9_.-]+$/.test(file))throw Error('Invalid asset filename: '+name);
 return file;
}
async function loadManifest(signal){
 const label=text('Liste des fichiers Daylight','Daylight file list');
 status(text('Chargement de la liste des fichiers Daylight…','Loading the Daylight file list…'));
 const bytes=await requestBytes('manifest.json',label,signal,{limit:65536});
 let manifest;
 try{manifest=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes));}
 catch{throw Error(text('Liste des fichiers Daylight invalide : le serveur n’a pas renvoyé le manifeste JSON attendu.','Invalid Daylight file list: the server did not return the expected JSON manifest.'));}
 if(manifest.schema!==1||manifest.memory_mib!==256||manifest.network_relay!==false||manifest.persistence!==false||!manifest.files)throw Error('Unsupported demo manifest');
 if(Object.keys(manifest.files).sort().join()!==[...RUNTIME_NAMES].sort().join())throw Error('Incomplete runtime manifest');
 let total=0;
 for(const name of RUNTIME_NAMES){checkRecord(name,manifest.files[name]);total+=manifest.files[name].bytes;}
 if(total>100000000)throw Error('Runtime exceeds the preview download limit');
 return manifest;
}
async function verified(name,record,signal,onProgress){
 const file=checkRecord(name,record);checkCancelled(signal);
 let bytes;
 if(record.parts){
  bytes=new Uint8Array(record.bytes);let offset=0;
  for(const part of record.parts){
   const block=new Uint8Array(await verified(name+' part',part,signal,onProgress));
   checkCancelled(signal);bytes.set(block,offset);offset+=block.length;
  }
 }else{
  bytes=await requestBytes(file+'?sha256='+record.sha256,name,signal,{
   limit:record.bytes,expected:record.bytes,cache:'force-cache',timeoutMs:90000,onProgress
  });
 }
 checkCancelled(signal);
 if(hex(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)))!==record.sha256)throw Error('Asset integrity check failed: '+name);
 checkCancelled(signal);return bytes.buffer;
}
async function library(manifest,signal,onProgress){
 const record=manifest.files['libv86.js'],file=checkRecord('libv86.js',record);
 if(window.V86&&loadedLibraryHash===record.sha256){onProgress(record.bytes);return;}
 // Verify the actual bytes first; the script element independently enforces SRI.
 await verified('libv86.js',record,signal,onProgress);
 checkCancelled(signal);
 await new Promise((resolve,reject)=>{
  const script=document.createElement('script');let done=false;
  const finish=error=>{
   if(done)return;done=true;clearTimeout(timer);signal.removeEventListener('abort',abort);
   script.onload=null;script.onerror=null;if(error){script.remove();reject(error);}else resolve();
  };
  const abort=()=>finish(cancelled());
  const timer=setTimeout(()=>finish(Error(text('Le moteur vérifié ne se charge pas. Un filtrage du navigateur peut bloquer ce fichier. Cliquez sur Redémarrer.','The verified engine did not load. Browser filtering may be blocking this file. Choose Restart.'))),20000);
  signal.addEventListener('abort',abort,{once:true});
  script.src=file+'?sha256='+record.sha256;
  script.integrity='sha256-'+btoa(String.fromCharCode(...record.sha256.match(/../g).map(x=>parseInt(x,16))));
  script.onload=()=>finish();
  script.onerror=()=>finish(Error(text('Chargement du moteur Daylight refusé ou interrompu. Cliquez sur Redémarrer.','Daylight engine loading was blocked or interrupted. Choose Restart.')));
  document.head.append(script);
 });
 checkCancelled(signal);
 if(typeof window.V86!=='function')throw Error('Verified emulator library did not initialize');
 loadedLibraryHash=record.sha256;
}
async function stop(){
 if(stopTask)return stopTask;
 generation++;clearTimeout(deadline);deadline=null;clearTimeout(lifetime);lifetime=null;
 if(controller){controller.abort();controller=null;}
 const current=emulator;emulator=null;window.daylightEmulator=null;setState('stopping');
 stopTask=(async()=>{
  try{if(current)await current.destroy();}
  finally{
   $('screen').replaceChildren(Object.assign(document.createElement('div'),{className:'text-screen'}),document.createElement('canvas'));
   $('placeholder').hidden=false;$('progress').hidden=true;
   setState('idle');status(text('Session arrêtée. Les modifications temporaires sont abandonnées.','Session stopped. Temporary changes are discarded.'));
  }
 })();
 try{await stopTask;}finally{stopTask=null;}
}
async function fail(error,id){
 if(id!==generation)return;
 await stop();setState('error');
 const message=error instanceof TypeError?text('Une connexion nécessaire a échoué. Cliquez sur Redémarrer après avoir vérifié le réseau.','A required connection failed. Check connectivity and choose Restart.'):error.message;
 status(text('Impossible de démarrer : ','Unable to start: ')+message);
}
async function start(){
 if(!['idle','error'].includes(state))return;
 const id=++generation;controller=new AbortController();const signal=controller.signal;
 setState('loading');$('progress').hidden=false;$('progress').value=0;
 try{
  if(!window.WebAssembly||!window.crypto?.subtle)throw Error(text('WebAssembly et HTTPS sont nécessaires. Ouvrez cette page en HTTPS dans un navigateur récent.','WebAssembly and HTTPS are required. Open this page over HTTPS in a recent browser.'));
  const manifest=await loadManifest(signal);
  const names=['seabios.bin','vgabios.bin','vmlinuz.bin','initrd.bin','v86.wasm'];
  const total=RUNTIME_NAMES.reduce((sum,name)=>sum+manifest.files[name].bytes,0);let loaded=0;
  const onProgress=bytes=>{
   if(id!==generation||signal.aborted)return;
   loaded+=bytes;$('progress').value=Math.max(0,Math.min(100,100*loaded/total));
   status(text('Téléchargement vérifié : ','Verified download: ')+(loaded/1048576).toFixed(1)+' / '+(total/1048576).toFixed(1)+' MiB');
  };
  await library(manifest,signal,onProgress);const assets={};
  for(const name of names)assets[name]=await verified(name,manifest.files[name],signal,onProgress);
  checkCancelled(signal);if(id!==generation)return;
  $('progress').hidden=false;$('progress').removeAttribute('value');$('placeholder').hidden=true;serial='';
  setState('booting');status(text('Daylight Start — ouverture du terminal…','Daylight Start — opening your terminal…'));
  emulator=new V86({
   wasm_fn:async imports=>(await WebAssembly.instantiate(assets['v86.wasm'],imports)).instance.exports,
   memory_size:256*1024*1024,vga_memory_size:8*1024*1024,
   screen_container:$('screen'),bios:{buffer:assets['seabios.bin']},vga_bios:{buffer:assets['vgabios.bin']},
   bzimage:{buffer:assets['vmlinuz.bin']},initrd:{buffer:assets['initrd.bin']},
   cmdline:'rdinit=/init console=ttyS0,115200 loglevel=0 quiet random.trust_cpu=on pci=conf1 tsc=reliable',
   acpi:false,autostart:true,disable_speaker:true
   // No external guest-network relay, shared host disk, clipboard bridge or telemetry.
  });
  window.daylightEmulator=emulator;emulator.keyboard_set_enabled(false);
  emulator.add_listener('serial0-output-byte',byte=>{
   if(id!==generation)return;
   serial=(serial+String.fromCharCode(byte)).slice(-6000);
   if(serial.includes('DAYLIGHT_WEB_GRAPHICS_FAILED')){void fail(Error('Guest graphics startup failed'),id);return;}
   if(serial.includes('DAYLIGHT_WEB_DESKTOP_READY')&&state==='booting'){
    clearTimeout(deadline);deadline=null;$('progress').hidden=true;setState('running');
    lifetime=setTimeout(async()=>{if(id!==generation)return;await stop();status(text('Session terminée après 20 minutes. Cliquez sur Démarrer pour une nouvelle session.','Session ended after 20 minutes. Select Start for a new session.'));},20*60*1000);
    status(text('Daylight Start est prêt. Cliquez dans le terminal pour écrire.','Daylight Start is ready. Click inside the terminal to type.'));
    void syncVisibility();
   }
  });
  deadline=setTimeout(()=>void fail(Error(text('Le démarrage a dépassé la limite sur cet appareil.','Startup exceeded the time limit on this device.')),id),180000);
 }catch(error){if(error.name!=='AbortError'&&id===generation)await fail(error,id);}
}
async function restart(){await stop();await start();}
// With no Pause button, a hidden running guest must resume automatically on return.
async function syncVisibility(){
 if(visibilityBusy||!emulator)return;
 const current=emulator;
 const pausing=document.hidden&&state==='running';
 const resuming=!document.hidden&&state==='paused';
 if(!pausing&&!resuming)return;
 visibilityBusy=true;
 try{
  if(pausing){current.keyboard_set_enabled(false);await current.stop();}
  else await current.run();
  if(emulator!==current)return;
  setState(pausing?'paused':'running');
  status(pausing?text('Session en pause pendant que cet onglet est masqué.','Session paused while this tab is hidden.'):text('Session reprise. Cliquez dans le terminal pour écrire.','Session resumed. Click inside the terminal to type.'));
 }finally{
  visibilityBusy=false;
  if(emulator===current&&((document.hidden&&state==='running')||(!document.hidden&&state==='paused')))void syncVisibility();
 }
}
$('start').addEventListener('click',()=>void start());
$('reset').addEventListener('click',()=>void restart());
$('stop').addEventListener('click',()=>void stop());
$('display').addEventListener('pointerdown',()=>{if(emulator&&state==='running'){$('display').focus();emulator.keyboard_set_enabled(true);}});
$('display').addEventListener('contextmenu',event=>event.preventDefault());
$('display').addEventListener('blur',()=>{if(emulator)emulator.keyboard_set_enabled(false);});
const letterCodes={q:16,w:17,e:18,r:19,t:20,y:21,u:22,i:23,o:24,p:25,a:30,s:31,d:32,f:33,g:34,h:35,j:36,k:37,l:38,z:44,x:45,c:46,v:47,b:48,n:49,m:50};
const keyCodes={' ':57,'1':2,'2':3,'3':4,'4':5,'5':6,'6':7,'7':8,'8':9,'9':10,'0':11,'-':12,'_':12,'=':13,'+':13,'[':26,'{':26,']':27,'}':27,'\\':43,'|':43,';':39,':':39,"'":40,'"':40,',':51,'<':51,'.':52,'>':52,'/':53,'?':53,'!':2,'@':3,'#':4,'$':5,'%':6,'^':7,'&':8,'*':9,'(':10,')':11};
const shifted=new Set(['_','+','{','}','|',':','"','<','>','?','!','@','#','$','%','^','&','*','(',')']);
function sendCodes(codes){if(!emulator||state!=='running'){status(text('Démarrez Linux avant de saisir une commande.','Start Linux before entering a command.'));return false;}emulator.keyboard_send_scancodes(codes);return true;}
function sendMobileCommand(){
 const input=$('mobile-command'),value=input.value;if(!value)return;
 if(value.length>512){status(text('Commande trop longue (512 caractères maximum).','Command too long (512 characters maximum).'));return;}
 const codes=[];
 for(const character of value){
  const key=character.toLowerCase(),scan=letterCodes[key]||keyCodes[key];
  if(!scan){status(text('Caractère non pris en charge par le clavier tactile : ','Character not supported by touch keyboard: ')+character);return;}
  if(character!==key||shifted.has(character))codes.push(0x2a);
  codes.push(scan,scan|0x80);
  if(character!==key||shifted.has(character))codes.push(0xaa);
 }
 codes.push(0x1c,0x9c);
 if(sendCodes(codes)){input.value='';status(text('Commande envoyée au terminal.','Command sent to the terminal.'));input.focus();}
}
$('mobile-command-form').addEventListener('submit',event=>{event.preventDefault();sendMobileCommand();});
$('mobile-command').addEventListener('keydown',event=>{if(event.key==='Escape'){event.preventDefault();$('display').focus();}});
const specialKeys={TAB:[0x0f,0x8f],UP:[0xe0,0x48,0xe0,0xc8],DOWN:[0xe0,0x50,0xe0,0xd0],LEFT:[0xe0,0x4b,0xe0,0xcb],RIGHT:[0xe0,0x4d,0xe0,0xcd],CTRL_C:[0x1d,0x2e,0xae,0x9d]};
document.querySelectorAll('.touch-keys [data-key]').forEach(button=>button.addEventListener('click',()=>{if(sendCodes(specialKeys[button.dataset.key]))$('mobile-command').focus();}));
document.addEventListener('visibilitychange',()=>void syncVisibility());
window.addEventListener('pagehide',()=>{void stop();});
labels();setState('idle');
