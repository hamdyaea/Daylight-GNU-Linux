// Developer: Hamdy Abou El Anein
// Contact: info@daylightlinux.ch
// SPDX-License-Identifier: GPL-3.0-only
'use strict';
const {chromium}=require(process.env.DAYLIGHT_PLAYWRIGHT||'../dist/browser-tools/node_modules/playwright');
const crypto=require('crypto'), fs=require('fs');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.DAYLIGHT_BROWSER||'/usr/bin/chromium',headless:true});
 try{
  const page=await browser.newPage();
  await page.goto('http://127.0.0.1:34403/',{waitUntil:'networkidle'});
  const response=await page.request.get('http://127.0.0.1:34403/daylight.svg');
  const payload=await response.body();
  const record={file:'daylight.svg',bytes:payload.length,sha256:crypto.createHash('sha256').update(payload).digest('hex')};
  let requests=0,mode='recover';
  await page.route('**/daylight.svg?sha256=*',async route=>{
   requests++;
   if(mode==='recover'&&requests===1||mode==='exhaust')return route.fulfill({status:503,body:'controlled transient failure'});
   if(mode==='corrupt'){const wrong=Buffer.from(payload);wrong[0]^=1;return route.fulfill({status:200,body:wrong});}
   if(mode==='oversize')return route.fulfill({status:200,body:Buffer.concat([payload,Buffer.from('X')])});
   return route.fulfill({status:200,body:payload});
  });
  async function check(selected,expectedCalls,expectedError){
   mode=selected;requests=0;
   const result=await page.evaluate(async ({record,selected})=>{
    const controller=new AbortController();if(selected==='cancel')controller.abort();let progress=0;
    try{const data=await verified('daylight.svg',record,controller.signal,n=>progress+=n);return {size:data.byteLength,progress};}
    catch(error){return {name:error.name,error:error.message,progress};}
   },{record,selected});
   if(requests!==expectedCalls)throw Error(selected+': requests '+requests+' != '+expectedCalls);
   if(expectedError&&!String(result.error).includes(expectedError))throw Error(selected+': wrong failure '+JSON.stringify(result));
   if(!expectedError&&(result.size!==payload.length||result.progress!==payload.length))throw Error(selected+': wrong success '+JSON.stringify(result));
   return {case:selected,requests,result:'PASS'};
  }
  const tests=[];
  tests.push(await check('recover',2,null));
  tests.push(await check('corrupt',1,'integrity'));
  tests.push(await check('oversize',1,'size'));
  tests.push(await check('cancel',0,'Cancelled'));
  tests.push(await check('exhaust',3,'trois essais'));
  fs.mkdirSync('dist/web-live-validation',{recursive:true});
  fs.writeFileSync('dist/web-live-validation/transfer-tests.json',JSON.stringify({result:'PASS',controlledFaultTests:tests},null,2));
  console.log('PASS: bounded retry, unchanged SHA256 rejection, size bound, cancellation and retry exhaustion (5 controlled transport tests).');
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
