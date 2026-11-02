// Developer: Hamdy Abou El Anein
// Contact: info@daylightlinux.ch
// SPDX-License-Identifier: GPL-3.0-only
'use strict';
const {chromium}=require(process.env.DAYLIGHT_PLAYWRIGHT||'../dist/browser-tools/node_modules/playwright');
const fs=require('fs');const path=require('path');const crypto=require('crypto');
const base=process.env.DAYLIGHT_DEMO_URL||'http://127.0.0.1:34403/';
const output=path.resolve('dist/web-live-validation');fs.mkdirSync(output,{recursive:true});
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.DAYLIGHT_BROWSER||'/usr/bin/chromium',headless:true,args:['--disable-dev-shm-usage']});
 const context=await browser.newContext({viewport:{width:1280,height:1050}});
 const page=await context.newPage();const errors=[],requests=[];let manifestResponse=null;
 page.on('response',response=>{if(new URL(response.url()).pathname.endsWith('/manifest.json')&&response.status()===200)manifestResponse=response.body();});
 page.on('pageerror',e=>errors.push(e.message));
 page.on('console',message=>{if(message.type()==='error')errors.push(message.text());});
 page.on('request',r=>requests.push(r.url()));
 try{
  const response=await page.goto(base,{waitUntil:'networkidle'});
  if(response.status()!==200)throw Error('Demo document unavailable');
  if(await page.evaluate(()=>!!window.daylightEmulator))throw Error('Emulator starts without consent');
  if(requests.some(u=>/initrd|vmlinuz|v86.wasm/.test(u)))throw Error('Guest downloaded before Start click');
  const started=Date.now();await page.locator('#start').click();
  await page.waitForFunction(()=>['running','error'].includes(document.body.dataset.state),{},{timeout:200000});
  if(await page.locator('body').getAttribute('data-state')!=='running')throw Error(await page.locator('#status').innerText());
  const canvas=page.locator('#screen canvas');await canvas.waitFor({state:'visible',timeout:10000});
  await page.waitForTimeout(3000);
  await page.screenshot({path:path.join(output,'desktop-browser.png'),fullPage:true});
  await canvas.screenshot({path:path.join(output,'desktop.png')});
  const size=await canvas.evaluate(el=>({width:el.width,height:el.height}));
  if(size.width<640||size.height<480)throw Error('Guest graphical surface too small');
  // Real browser keyboard input must reach xterm, not just a successful serial boot marker.
  await page.evaluate(()=>{window.testSerial='';window.daylightEmulator.add_listener('serial0-output-byte',b=>{window.testSerial=(window.testSerial+String.fromCharCode(b)).slice(-16000);});});
  const box=await canvas.boundingBox();
  await page.mouse.click(box.x+160,box.y+170);
  await page.keyboard.type('echo keyboardworks ',{delay:30});
  // v86 emulates physical keys: shifted punctuation must carry its real modifier.
  await page.keyboard.press('Shift+Period');
  await page.keyboard.type(' /tmp/browser-keyboard-test',{delay:30});
  await page.keyboard.press('Enter');await page.waitForTimeout(1500);
  await page.evaluate(()=>window.daylightEmulator.serial0_send('cat /tmp/browser-keyboard-test; echo SERIAL_CHECK_DONE\n'));
  await page.waitForFunction(()=>window.testSerial.includes('\r\nkeyboardworks\r\n'),{},{timeout:15000});
  const serial=await page.evaluate(()=>window.testSerial);
  fs.writeFileSync(path.join(output,'interaction.log'),serial);
  // Verify actual Fluxbox windows rather than only a successful terminal boot.
  async function guiState(expectedProcesses, visible) {
    await page.evaluate(()=>{window.testSerial='';window.daylightEmulator.serial0_send('n=$(pgrep -x xterm | wc -l); v=$(DISPLAY=:0 xdotool search --onlyvisible --class XTerm 2>/dev/null | wc -l); printf "\nGUISTATE=%s,%s\n" "$n" "$v"\n');});
    await page.waitForFunction(()=>/\r\nGUISTATE=[0-9]+,[0-9]+\r\n/.test(window.testSerial),{},{timeout:15000});
    const values=await page.evaluate(()=>window.testSerial.match(/\r\nGUISTATE=([0-9]+),([0-9]+)\r\n/).slice(1).map(Number));
    if(values[0]!==expectedProcesses || (visible ? values[1]<expectedProcesses : values[1]!==0))throw Error('Unexpected real GUI state: '+values);
  }
  await guiState(1,true);
  await page.locator('#terminal').click();await page.waitForTimeout(2000);await guiState(2,true);
  await page.locator('#desktop').click();await page.waitForTimeout(800);await guiState(2,false);
  await page.locator('#menu').click();await page.waitForTimeout(800);
  await canvas.screenshot({path:path.join(output,'desktop-menu.png')});
  await page.evaluate(()=>window.daylightEmulator.keyboard_send_scancodes([0x01,0x81]));
  await page.locator('#desktop').click();await page.waitForTimeout(800);await guiState(2,true);
  await page.locator('#pause').click();await page.waitForFunction(()=>document.body.dataset.state==='paused');
  await page.locator('#pause').click();await page.waitForFunction(()=>document.body.dataset.state==='running');
  await page.locator('#stop').click();await page.waitForFunction(()=>document.body.dataset.state==='idle'&&!window.daylightEmulator);
  const own=new URL(base).origin;
  if(requests.some(u=>new URL(u).origin!==own))throw Error('Unexpected external browser request');
  if(errors.length)throw Error('Browser errors: '+errors.join('; '));
  if(!manifestResponse)throw Error('The actual boot manifest was not observed');
  const manifestSha256=crypto.createHash('sha256').update(await manifestResponse).digest('hex');
  const result={result:'PASS',url:base,manifestSha256,bootAndInteractionMilliseconds:Date.now()-started,canvas:size,realKeyboard:true,graphicalControls:true,twoTerminalWindows:true,desktopHideRestore:true,pauseResume:true,stop:true,externalRequests:0,autostart:false};
  fs.writeFileSync(path.join(output,'result.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result));
 }catch(error){
  await page.screenshot({path:path.join(output,'failure.png'),fullPage:true}).catch(()=>{});
  const state=await page.evaluate(()=>({state:document.body.dataset.state,status:document.getElementById('status')?.textContent,serial:window.testSerial||'',bootSerial:typeof serial!=='undefined'?serial:''})).catch(()=>({}));
  fs.writeFileSync(path.join(output,'failure.json'),JSON.stringify({error:error.stack,state,errors,requests},null,2));throw error;
 }finally{await context.close();await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
