// Developer: Hamdy Abou El Anein
// Contact: info@daylightlinux.ch
// SPDX-License-Identifier: GPL-3.0-only
// Real browser checks. Requires Playwright and a local HTTP preview server.
'use strict';
const fs = require('fs');
const path = require('path');
const {chromium} = require(process.env.DAYLIGHT_PLAYWRIGHT || 'playwright');
const base = (process.env.DAYLIGHT_SITE_URL || 'http://127.0.0.1:34402').replace(/\/$/, '');
const output = process.env.DAYLIGHT_SITE_QA || path.join(process.cwd(), 'dist/site-pi-qa');
const pages = ['index.html','raspberry-pi.html','install.html','download.html','discover.html','screenshots.html','try-online.html','wallpapers.html','news.html','faq.html','community.html','information.html','books.html','press.html','old/index.html','privacy.html'];
const results = [];
function assert(value, message) { if (!value) throw new Error(message); }
(async () => {
  fs.mkdirSync(output, {recursive:true});
  const browser = await chromium.launch({executablePath:process.env.DAYLIGHT_BROWSER || '/usr/bin/chromium',headless:true,args:['--disable-dev-shm-usage']});
  try {
    for (const width of [320,390,768,1440]) {
      const context = await browser.newContext({viewport:{width,height:900},isMobile:width<500,hasTouch:width<500});
      const page = await context.newPage();
      const errors=[];
      page.on('pageerror', error=>errors.push(error.message));
      page.on('console', message=>{if(message.type()==='error' && !message.text().includes('favicon.ico'))errors.push(message.text());});
      for (const language of ['en','fr']) {
        const prefix=language==='fr'?'fr/':'';
        for (const name of pages) {
          const url=base+'/'+prefix+name;
          const response=await page.goto(url,{waitUntil:'networkidle'});
          assert(response.status()===200, 'HTTP '+response.status()+' '+url);
          assert(await page.locator('h1').count()===1,'One H1 required: '+url);
          assert(await page.locator('html').getAttribute('lang')===language,'Wrong language: '+url);
          assert(!(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1)),'Horizontal overflow '+width+' '+url);
          const menu=page.locator('.site-menu');
          await menu.locator('summary').click();
          assert(await menu.getAttribute('open')!==null,'Menu did not open: '+url);
          assert(await menu.locator('.menu-panel a').count()===pages.length,'Incomplete navigation: '+url);
          const last=menu.locator('.menu-panel a').last();
          await last.scrollIntoViewIfNeeded();
          assert(await last.isVisible(),'Last navigation page unreachable: '+url);
          await page.keyboard.press('Escape');
          assert(await menu.getAttribute('open')===null,'Escape did not close menu: '+url);
          assert(await page.locator('.site-menu summary').evaluate(el=>el===document.activeElement),'Escape lost keyboard focus: '+url);
          await page.evaluate(async()=>{for(const img of document.images)img.loading='eager';await Promise.all([...document.images].map(img=>img.decode().catch(()=>{})));});
          const broken=await page.evaluate(()=>[...document.images].filter(img=>img.complete && !img.naturalWidth).map(img=>img.src));
          assert(!broken.length,'Broken images '+url+' '+broken.join(','));
          if(name==='index.html') {
            const first=page.locator('main .button').first();
            assert((await first.getAttribute('href')).endsWith('/raspberry-pi.html'),'Hero must lead to Raspberry Pi');
          }
          if(name==='download.html') {
            const order=await page.evaluate(()=>document.getElementById('raspberry-pi').compareDocumentPosition(document.getElementById('pc-live')) & Node.DOCUMENT_POSITION_FOLLOWING);
            assert(order,'Raspberry Pi must precede the PC live image');
          }
          if(language==='fr' && [390,1440].includes(width) && ['index.html','download.html'].includes(name)) {
            await page.screenshot({path:path.join(output,width+'-'+name.replace('.html','.png')),fullPage:true});
            if(name==='index.html') {
              await page.locator('.site-menu summary').click();
              await page.screenshot({path:path.join(output,width+'-navigation.png')});
              await page.keyboard.press('Escape');
            }
          }
          results.push({width,language,page:name,status:200,menuLinks:pages.length,noOverflow:true,noBrokenImages:true});
        }
      }
      assert(errors.length===0,'Browser/CSP errors: '+errors.slice(0,10).join('; '));
      await context.close();
    }
    const noJS = await browser.newContext({viewport:{width:320,height:760},javaScriptEnabled:false});
    const page=await noJS.newPage();
    for(const route of ['/','/fr/','/fr/books.html','/fr/download.html']) {
      await page.goto(base+route,{waitUntil:'networkidle'});
      await page.locator('.site-menu summary').click();
      const links=page.locator('.menu-panel a');
      assert(await links.count()===pages.length,'No-JS menu incomplete');
      await links.last().scrollIntoViewIfNeeded();
      assert(await links.last().isVisible(),'No-JS last link inaccessible');
    }
    await noJS.close();
    fs.writeFileSync(path.join(output,'results.json'),JSON.stringify({result:'PASS',pageChecks:results.length,noJavascriptChecks:4,checks:results},null,2));
    console.log('PASS: '+results.length+' real Chromium page checks across 320, 390, 768 and 1440 px; full menus, keyboard Escape, no overflow, images, no CSP/JS errors; 4 no-JavaScript navigation checks.');
  } finally { await browser.close(); }
})().catch(error=>{console.error(error);process.exitCode=1;});
