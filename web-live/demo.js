// Developer: Hamdy Abou El Anein
// Contact: info@daylightlinux.ch
// SPDX-License-Identifier: GPL-3.0-only
'use strict';
let emulator=null, generation=0, controller=null, state='idle', deadline=null, lifetime=null, serial='';
let lang=new URLSearchParams(location.search).get('lang')==='en'?'en':'fr';
const $=id=>document.getElementById(id);
const text=(fr,en)=>lang==='fr'?fr:en;
const english={title:'A real Linux desktop.<br>Inside your browser.',intro:'A lightweight, temporary preview of the Daylight spirit. Computing happens on your device, not on our Raspberry Pi.','scope-title':'A preview, not the complete distribution.',scope:'This experimental edition uses Alpine Linux x86 and Fluxbox. Daylight for Raspberry Pi remains based on Debian / Raspberry Pi OS ARM64. This preview does not include all of its Rust tools.',instructions:'Daylight Start opens your terminal automatically. Calculator opens only when selected. Click inside the terminal to use the keyboard. Move windows by their title bar. Right-click the wallpaper or use Linux menu for Fluxbox. Try the real graphical calculator, or use uname, free, top, ls and vi in the terminal.','privacy-title':'Your session stays local',privacy:'No account, no disk shared with our server, no external guest-network relay and no telemetry. Demo files download over HTTPS; the host sees that connection like any webpage request.','temporary-title':'Nothing to install',temporary:'Changes are temporary: closing, stopping or restarting discards the session. Do not enter passwords or sensitive data. The demo pauses when its tab is hidden and stops after 20 minutes.','requirements-title':'A bounded preview',requirements:'The Linux guest receives 256 MiB of RAM; the browser also needs its own memory. Startup depends on your device and connection. No public container runs on our Pi.','technical-title':'Technical details and licenses',technical:'Linux is actually emulated in WebAssembly using v86. This is not an interactive screenshot. The guest has no external network relay. Free-software components retain their own licenses.',cta:'Ready to use Daylight on your Raspberry Pi?','placeholder-text':'Your session starts here.'};
const original=Object.fromEntries(Object.keys(english).map(id=>[id,$(id).innerHTML]));
function labels(){
 document.documentElement.lang=lang;
 document.title=text('Daylight Web — un vrai Linux dans votre navigateur','Daylight Web — real Linux inside your browser');
 $('cta').href=lang==='fr'?'/fr/raspberry-pi.html':'/raspberry-pi.html';
 for(const [id,value] of Object.entries(lang==='en'?english:original))$(id).innerHTML=value;
 $('language').textContent=lang==='fr'?'English':'Français';
 $('start').textContent='Daylight Start';
 $('desktop').textContent=text('Bureau','Desktop');$('menu').textContent=text('Menu Linux','Linux menu');$('terminal').textContent='Terminal';$('calculator').textContent=text('Calculatrice','Calculator');$('about').textContent=text('À propos','About');
 $('display').setAttribute('aria-label',text('Bureau Linux interactif','Interactive Linux desktop'));
 $('pause').textContent=state==='paused'?text('Reprendre','Resume'):text('Pause','Pause');
 $('reset').textContent=text('Recommencer','Restart');$('stop').textContent=text('Arrêter','Stop');$('fullscreen').textContent=text('Plein écran','Fullscreen');
 if(state==='idle')status(text('Aucun système lancé. Environ 42 Mo seront téléchargés au premier démarrage.','Nothing is running. The first start downloads about 42 MB.'));
}
function status(value){$('status').textContent=value;}
function setState(value){
 state=value;document.body.dataset.state=value;
 $('start').disabled=!['idle','error'].includes(value);
 $('stop').disabled=['idle','error'].includes(value);
 $('pause').disabled=!['running','paused'].includes(value);
 $('reset').disabled=!['running','paused','error'].includes(value);
 $('fullscreen').disabled=!['running','paused'].includes(value)||!$('display').requestFullscreen;
 for(const id of ['desktop','menu','terminal','calculator','about'])$(id).disabled=value!=='running';
 labels();
}
function hex(bytes){return Array.from(bytes,b=>b.toString(16).padStart(2,'0')).join('');}
async function verified(name,record,signal,onProgress){
 if(!/^[a-zA-Z0-9_.-]+$/.test(name)||!record||!Number.isSafeInteger(record.bytes)||record.bytes<1||record.bytes>100000000||!/^[a-f0-9]{64}$/.test(record.sha256))throw Error('Invalid asset manifest');
 const file=record.file||name;
 if(!/^[a-zA-Z0-9_.-]+$/.test(file))throw Error('Invalid asset filename');
 // Retry transport failures only, never a bad hash or an oversized payload.
 for(let attempt=0;attempt<3;attempt++){
  if(signal.aborted)throw new DOMException('Cancelled','AbortError');
  const transfer=new AbortController();
  const cancel=()=>transfer.abort();signal.addEventListener('abort',cancel,{once:true});
  const timeout=setTimeout(()=>transfer.abort(),90000);
  let length=0;
  try{
   const response=await fetch(file+'?sha256='+record.sha256,{credentials:'omit',signal:transfer.signal,cache:'force-cache'});
   if(!response.ok){const error=Error('HTTP '+response.status+' for '+name);error.retryable=[408,429,500,502,503,504].includes(response.status);throw error;}
   if(!response.body)throw Error('Empty response body: '+name);
   const reader=response.body.getReader();const chunks=[];
   while(true){const {done,value}=await reader.read();if(done)break;if(length+value.length>record.bytes){await reader.cancel();throw Error('Unexpected asset size');}length+=value.length;chunks.push(value);onProgress(value.length);}
   if(length!==record.bytes){const error=Error('Incomplete asset: '+name);error.retryable=true;throw error;}
   const bytes=new Uint8Array(length);let offset=0;for(const chunk of chunks){bytes.set(chunk,offset);offset+=chunk.length;}
   if(hex(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)))!==record.sha256)throw Error('Asset integrity check failed: '+name);
   return bytes.buffer;
  }catch(error){
   if(signal.aborted)throw new DOMException('Cancelled','AbortError');
   const network=error instanceof TypeError||error.name==='AbortError'||error.retryable===true;
   if(!network)throw error;
   if(attempt===2)throw Error(text('Connexion interrompue après trois essais. Vérifiez le réseau puis cliquez sur Recommencer.','Connection interrupted after three attempts. Check your network and select Restart.'));
   if(length)onProgress(-length);
   status(text('Connexion interrompue. Nouvel essai ','Connection interrupted. Retrying ')+(attempt+2)+'/3…');
   await new Promise(resolve=>setTimeout(resolve,500*(attempt+1)));
  }finally{clearTimeout(timeout);signal.removeEventListener('abort',cancel);}
 }
}
async function library(manifest){
 if(window.V86)return;
 const hash=manifest.files['libv86.js'].sha256;
 const filename=manifest.files['libv86.js'].file||'libv86.js';
 if(!/^[a-f0-9]{64}$/.test(hash)||!/^[A-Za-z0-9_.-]+$/.test(filename))throw Error('Invalid emulator library metadata');
 await new Promise((resolve,reject)=>{
  const script=document.createElement('script');script.src=filename+'?sha256='+hash;
  script.integrity='sha256-'+btoa(String.fromCharCode(...hash.match(/../g).map(x=>parseInt(x,16))));
  script.onload=resolve;script.onerror=()=>reject(Error('Emulator library could not be verified'));document.head.append(script);
 });
}
async function stop(){
 generation++;clearTimeout(deadline);deadline=null;clearTimeout(lifetime);lifetime=null;
 if(controller){controller.abort();controller=null;}
 const current=emulator;emulator=null;window.daylightEmulator=null;
 if(current){ await Promise.race([current.destroy().catch(()=>{}),new Promise(resolve=>setTimeout(resolve,2000))]); }
 $('screen').replaceChildren(Object.assign(document.createElement('div'),{className:'text-screen'}),document.createElement('canvas'));
 $('placeholder').hidden=false;$('progress').hidden=true;
 setState('idle');status(text('Session arrêtée et fichiers temporaires abandonnés.','Session stopped; temporary changes discarded.'));
}
async function start(){
 const id=++generation;controller=new AbortController();const signal=controller.signal;
 setState('loading');$('progress').hidden=false;$('progress').value=0;
 try{
  if(!window.WebAssembly||!crypto.subtle)throw Error(text('WebAssembly et HTTPS sont nécessaires.','WebAssembly and HTTPS are required.'));
  const result=await fetch('manifest.json',{credentials:'omit',cache:'no-cache',signal});
  if(!result.ok)throw Error('Manifest HTTP '+result.status);
  const manifest=await result.json();
  if(manifest.schema!==1||manifest.memory_mib!==256)throw Error('Unsupported demo manifest');
  const names=['seabios.bin','vgabios.bin','vmlinuz.bin','initrd.bin','v86.wasm'];
  const total=names.reduce((sum,name)=>sum+manifest.files[name].bytes,0);let loaded=0;
  const onProgress=bytes=>{loaded+=bytes;$('progress').value=Math.min(100,100*loaded/total);status(text('Téléchargement vérifié : ','Verified download: ')+(loaded/1048576).toFixed(1)+' / '+(total/1048576).toFixed(1)+' MiB');};
  await library(manifest);const assets={};
  for(const name of names)assets[name]=await verified(name,manifest.files[name],signal,onProgress);
  if(id!==generation)return;
  $('progress').hidden=true;$('placeholder').hidden=true;
  setState('booting');status(text('Daylight Start — ouverture du terminal…','Daylight Start — opening your terminal…'));
  serial='';
  emulator=new V86({
   wasm_fn:async imports=>(await WebAssembly.instantiate(assets['v86.wasm'],imports)).instance.exports,
   memory_size:256*1024*1024,vga_memory_size:8*1024*1024,
   screen_container:$('screen'),bios:{buffer:assets['seabios.bin']},vga_bios:{buffer:assets['vgabios.bin']},
   bzimage:{buffer:assets['vmlinuz.bin']},initrd:{buffer:assets['initrd.bin']},
   cmdline:'rdinit=/init console=ttyS0,115200 console=tty0 loglevel=4 random.trust_cpu=on pci=conf1 tsc=reliable',
   acpi:false,autostart:true,disable_speaker:true
   // Deliberately no net_device relay, filesystem sharing, disk upload or clipboard bridge.
  });
  window.daylightEmulator=emulator;
  emulator.keyboard_set_enabled(false);
  emulator.add_listener('serial0-output-byte',byte=>{
   if(id!==generation)return;
   serial=(serial+String.fromCharCode(byte)).slice(-6000);
   if(serial.includes('DAYLIGHT_WEB_GRAPHICS_FAILED'))fail(Error('Guest graphics startup failed'));
   if(serial.includes('DAYLIGHT_WEB_DESKTOP_READY')&&state==='booting'){
    clearTimeout(deadline);deadline=null;setState('running');
    lifetime=setTimeout(async()=>{await stop();status(text('Session terminée après 20 minutes. Vous pouvez recommencer.','Session ended after 20 minutes. You can start again.'));},20*60*1000);
    status(text('Daylight Start est prêt. Cliquez dans le terminal pour écrire.','Daylight Start is ready. Click inside the terminal to type.'));
   }
  });
  deadline=setTimeout(()=>fail(Error(text('Le démarrage a dépassé la limite sur cet appareil.','Startup exceeded the time limit on this device.'))),180000);
 }catch(error){if(error.name!=='AbortError'&&id===generation)await fail(error);}
}
async function fail(error){await stop();setState('error');status(text('Impossible de démarrer : ','Unable to start: ')+error.message);}
async function pause(){if(!emulator)return;if(state==='running'){await emulator.stop();setState('paused');status(text('En pause : le processeur invité est arrêté.','Paused: guest CPU stopped.'));}else if(state==='paused'){await emulator.run();setState('running');status(text('Session reprise.','Session resumed.'));}}
// Convenience controls send physical keys to the real guest window manager.
function guestShortcut(code){
 if(!emulator||state!=='running')return;
 emulator.keyboard_send_scancodes([0xE0,0x5B,code,code|0x80,0xE0,0xDB]);
}
$('desktop').addEventListener('click',()=>guestShortcut(0x20));
$('menu').addEventListener('click',()=>guestShortcut(0x39));
$('terminal').addEventListener('click',()=>guestShortcut(0x1C));
$('calculator').addEventListener('click',()=>guestShortcut(0x2E));
$('about').addEventListener('click',()=>guestShortcut(0x17));
$('start').addEventListener('click',start);$('stop').addEventListener('click',stop);$('pause').addEventListener('click',pause);
$('reset').addEventListener('click',async()=>{await stop();await start();});
$('fullscreen').addEventListener('click',()=>{$('display').requestFullscreen().catch(error=>status(error.message));});
$('language').addEventListener('click',()=>{lang=lang==='fr'?'en':'fr';labels();});
$('display').addEventListener('pointerdown',()=>{if(emulator){$('display').focus();emulator.keyboard_set_enabled(true);}});
$('display').addEventListener('contextmenu',event=>event.preventDefault());
$('display').addEventListener('blur',()=>{if(emulator)emulator.keyboard_set_enabled(false);});
document.addEventListener('visibilitychange',()=>{if(document.hidden&&state==='running')pause();});
window.addEventListener('pagehide',()=>{if(emulator)emulator.destroy();if(controller)controller.abort();});
labels();setState('idle');
