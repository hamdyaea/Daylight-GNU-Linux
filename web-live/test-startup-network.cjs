// Developer: Hamdy Abou El Anein
// Contact: info@daylightlinux.ch
// SPDX-License-Identifier: GPL-3.0-only
// Fault injection is limited to the local preview browser, never production.
'use strict';
const {chromium}=require(process.env.DAYLIGHT_PLAYWRIGHT||'../dist/browser-tools/node_modules/playwright');
const fs=require('fs');
const base=process.env.DAYLIGHT_TEST_BASE||'http://127.0.0.1:34403/';
if(!['localhost','127.0.0.1'].includes(new URL(base).hostname))throw Error('Local preview required for controlled network faults');
function check(value,message){if(!value)throw Error(message);}
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.DAYLIGHT_BROWSER||'/usr/bin/chromium',headless:true});
 const results=[];
 try{
  const context=await browser.newContext();
  const page=await context.newPage();const pageErrors=[];page.on('pageerror',error=>pageErrors.push(error.message));
  await page.goto(base,{waitUntil:'networkidle'});
  const actual=await page.request.get(new URL('manifest.json',base).toString());check(actual.ok(),'Local manifest unavailable');
  const manifest=await actual.body();let count=0,mode='recover';
  await page.route('**/manifest.json',async route=>{
   count++;
   if(mode==='recover'&&count===1||mode==='exhaust')return route.abort('internetdisconnected');
   if(mode==='http503'&&count===1)return route.fulfill({status:503,body:'controlled failure'});
   if(mode==='html')return route.fulfill({status:200,contentType:'text/html',body:'<!doctype html><title>Not a manifest</title>'});
   if(mode==='oversize')return route.fulfill({status:200,body:Buffer.alloc(65537,32)});
   if(mode==='missing')return route.fulfill({status:404,body:'controlled missing file'});
   if(mode==='hold'){
    await new Promise(resolve=>setTimeout(resolve,700));
    return route.abort('internetdisconnected').catch(()=>{});
   }
   return route.fulfill({status:200,contentType:'application/json',body:manifest});
  });
  async function manifestCase(selected,expectedCalls,expectedError){
   mode=selected;count=0;
   const result=await page.evaluate(async()=>{
    try{const data=await loadManifest(new AbortController().signal);return {ok:true,memory:data.memory_mib,files:Object.keys(data.files).length};}
    catch(error){return {ok:false,error:error.message};}
   });
   check(count===expectedCalls,selected+': wrong request count '+count);
   if(expectedError)check(!result.ok&&result.error.includes(expectedError),selected+': wrong error '+JSON.stringify(result));
   else check(result.ok&&result.memory===256&&result.files===6,selected+': invalid recovery '+JSON.stringify(result));
   check(!String(result.error).includes('Failed to fetch'),selected+': raw transport error escaped');
   results.push({case:'manifest-'+selected,requests:count,result:'PASS'});
  }
  await manifestCase('recover',2,null);
  await manifestCase('http503',2,null);
  await manifestCase('exhaust',3,'Liste des fichiers Daylight');
  await manifestCase('html',1,'manifeste JSON');
  await manifestCase('oversize',1,'size');
  await manifestCase('missing',1,'HTTP 404');
  // A failure through the actual Start button must provide a usable Restart path.
  mode='exhaust';count=0;
  await page.locator('#start').click();await page.waitForFunction(()=>document.body.dataset.state==='error');
  const message=await page.locator('#status').innerText();
  check(count===3&&!message.includes('Failed to fetch')&&message.includes('Redémarrer')&&message.includes('Liste des fichiers Daylight'),'Start button did not report an actionable manifest failure');
  check(await page.locator('#reset').isEnabled(),'Restart unavailable after failure');
  results.push({case:'start-button-failure',requests:count,message,result:'PASS'});
  // Restart replaces the failed attempt; Stop must suppress a late network rejection.
  mode='hold';count=0;
  await page.locator('#reset').click();
  await page.waitForFunction(()=>document.body.dataset.state==='loading');
  await page.locator('#stop').click();await page.waitForFunction(()=>document.body.dataset.state==='idle');
  await page.waitForTimeout(1100);
  check(await page.locator('body').getAttribute('data-state')==='idle','Cancelled manifest changed state afterwards');
  check(!(await page.evaluate(()=>!!window.daylightEmulator)),'Cancellation created a guest');
  check(!String(await page.locator('#status').innerText()).includes('Impossible'),'Cancellation became an error');
  results.push({case:'restart-and-stop-during-manifest',result:'PASS'});
  // Verify all buttons, including small viewports and the English interface.
  for(const width of [320,390,1280]){
   await page.setViewportSize({width,height:850});
   check(!(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1)),'Horizontal overflow at '+width);
   check(JSON.stringify(await page.locator('button').evaluateAll(items=>items.map(x=>x.id)))===JSON.stringify(['start','reset','stop']),'Extra buttons remain');
   check(JSON.stringify(await page.locator('.toolbar button').allTextContents())===JSON.stringify(['Démarrer','Redémarrer','Stop']),'Wrong French controls');
  }
  results.push({case:'exact-three-controls-320-390-1280',result:'PASS'});
  await page.goto(base+'?lang=en',{waitUntil:'networkidle'});
  check(JSON.stringify(await page.locator('.toolbar button').allTextContents())===JSON.stringify(['Start','Restart','Stop']),'Wrong English controls');
  check(!await page.evaluate(()=>!!window.daylightEmulator),'Language navigation starts a guest');
  results.push({case:'english-and-no-autostart',result:'PASS'});
  check(pageErrors.length===0,'Unexpected JavaScript errors: '+pageErrors.join(';'));
  fs.mkdirSync('dist/web-live-validation',{recursive:true});
  fs.writeFileSync('dist/web-live-validation/startup-network-tests.json',JSON.stringify({result:'PASS',checks:results},null,2));
  console.log('PASS: '+results.length+' controlled startup/network/interface cases, including exact Failed-to-fetch reproduction and Stop cancellation.');
  await context.close();
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
