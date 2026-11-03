// Developer: Hamdy Abou El Anein | Contact: info@daylightlinux.ch
// SPDX-License-Identifier: GPL-3.0-only
'use strict';
const {chromium}=require(process.env.DAYLIGHT_PLAYWRIGHT||'playwright');
const crypto=require('crypto');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true});
 try{
  const page=await browser.newPage();
  await page.goto(process.env.DAYLIGHT_DEMO_URL||'http://127.0.0.1:34413/live/');
  const blocks=[Buffer.from('first-block'),Buffer.from('second-block')];
  const record={bytes:blocks[0].length+blocks[1].length,sha256:sha(Buffer.concat(blocks)),parts:blocks.map((b,i)=>({file:'fixture-'+i+'.bin',bytes:b.length,sha256:sha(b)}))};
  let mode='valid',calls=0;
  await page.route('**/fixture-*.bin?*',async route=>{
   calls++;const i=Number(new URL(route.request().url()).pathname.match(/fixture-(\d)/)[1]);
   if(mode==='retry'&&calls===1)return route.fulfill({status:503,body:'temporary'});
   if(mode==='missing'&&i===1)return route.fulfill({status:404,body:'missing'});
   if(mode==='mid-cancel')return route.abort('aborted');
   const b=Buffer.from(blocks[i]);if(mode==='corrupt'&&i===1)b[0]^=1;
   return route.fulfill({status:200,body:mode==='oversize'?Buffer.concat([b,Buffer.from('x')]):b});
  });
  for(const selected of ['valid','retry','corrupt','whole-hash','oversize','missing','total','duplicate','nested','cancel','mid-cancel']){
   mode=selected;calls=0;const item=JSON.parse(JSON.stringify(record));
   if(mode==='whole-hash')item.sha256='0'.repeat(64);
   if(mode==='total')item.bytes++;
   if(mode==='duplicate')item.parts[1].file=item.parts[0].file;
   if(mode==='nested')item.parts[0].parts=[];
   const result=await page.evaluate(async({item,mode})=>{
    const c=new AbortController();if(mode==='cancel')c.abort();if(mode==='mid-cancel')setTimeout(()=>c.abort(),20);let progress=0;
    try{const b=await verified('test.bin',item,c.signal,n=>progress+=n);return {ok:true,size:b.byteLength,progress};}
    catch(e){return {ok:false,error:e.message,name:e.name};}
   },{item,mode});
   const expected={corrupt:'integrity', 'whole-hash':'integrity',oversize:'size',missing:'404',total:'total',duplicate:'Duplicate',nested:'chunk',cancel:'Cancelled','mid-cancel':'Cancelled'}[mode];
   if(expected){if(result.ok||!result.error.includes(expected))throw Error(mode+': '+JSON.stringify(result));}
   else if(!result.ok||result.size!==record.bytes||result.progress!==record.bytes)throw Error(mode+': '+JSON.stringify(result));
   if(mode==='retry'&&calls!==3)throw Error('Retry must fetch only the failed block again');
   if(['total','duplicate','nested','cancel'].includes(mode)&&calls!==0)throw Error('Invalid manifest must not download');
   console.log('PASS',mode,calls,'requests');
  }
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
