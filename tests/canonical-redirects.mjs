import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
const src=await readFile(new URL('../scripts/cloudflare-canonical-worker.js',import.meta.url),'utf8');
const {default:w}=await import('data:text/javascript;base64,'+Buffer.from(src).toString('base64'));
let calls=0; const env={ASSETS:{fetch:async()=>{calls++;return new Response('asset',{headers:{'X-Test':'preserved'}});}}};
for(const [from,to] of [
['http://daylightlinux.ch/index.html','https://daylightlinux.ch/'],
['https://www.daylightlinux.ch/index.html','https://daylightlinux.ch/'],
['https://www.daylightlinux.ch/download.html','https://daylightlinux.ch/download'],
['https://daylightlinux.ch:8443/download.html?ref=test%20x','https://daylightlinux.ch/download?ref=test%20x'],
['https://www.daylightlinux.ch/fr/index.html','https://daylightlinux.ch/fr/'],
['https://www.daylightlinux.ch/fr/download.html','https://daylightlinux.ch/fr/download'],
['https://www.daylightlinux.ch/live/index.html','https://daylightlinux.ch/live/']
]){const r=await w.fetch(new Request(from),env);assert.equal(r.status,301);assert.equal(r.headers.get('Location'),to);}
assert.equal(calls,0);
for(const url of ['https://daylightlinux.ch/','https://daylightlinux.ch/download','https://daylightlinux.ch/fr/','https://daylightlinux.ch/live/','https://daylight-gnu-linux.pages.dev/download.html']){
const r=await w.fetch(new Request(url),env);assert.equal(r.status,200);assert.equal(r.headers.get('X-Test'),'preserved');}
console.log('Canonical redirects: all 12 cases passed.');
