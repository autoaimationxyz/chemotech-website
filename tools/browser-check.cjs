const assert = require('node:assert/strict');
async function checkSite(browser, base = 'http://127.0.0.1:8080') {
 const errors=[];
 const page=await browser.newPage();
 page.on('pageerror',e=>errors.push(e.message));
 const pages=['index','products','about','company-profile','certifications','contact','quote'];
 for(const width of [320,390,768,1024,1440,1920]){
  await page.setViewportSize({width,height:900});
  for(const name of pages){
   await page.goto(`${base}/${name}.html`);
   await page.locator('h1').waitFor();
   const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1);
   if(overflow)console.log('OVERFLOW DETAILS',width,name,await page.evaluate(()=>[...document.querySelectorAll('body *')].filter(e=>e.getBoundingClientRect().right>innerWidth+1).slice(0,8).map(e=>[e.tagName,e.className,e.getBoundingClientRect().right])));
   assert.equal(overflow,false,`${name} overflows ${width}px`);
   assert.equal(await page.locator('img').evaluateAll(imgs=>imgs.filter(i=>i.complete&&i.naturalWidth===0).length),0,`broken image ${name}`);
  }
  console.log(`PASS: seven pages at ${width}px`);
 }
 await page.setViewportSize({width:1440,height:1000});
 await page.goto(base + '/index.html');
 await page.locator('[data-system-mode="water"]').click();
 assert.equal(await page.locator('.system-experience').getAttribute('data-system'), 'water');
 assert((await page.locator('#system-copy').textContent()).includes('Treatment'));
 await page.locator('.motion-toggle').click();
 assert.equal(await page.locator('.motion-toggle').getAttribute('aria-pressed'), 'true');
 assert.equal(await page.locator('.signal-flow').first().evaluate(el => getComputedStyle(el).animationPlayState), 'paused');
 await page.locator('.motion-toggle').click();
 await page.goto(base + '/contact.html');
 const gstTops = await page.locator('.office .gstin').evaluateAll(rows => rows.map(r => r.getBoundingClientRect().top));
 assert(Math.abs(gstTops[0]-gstTops[1]) < 1, 'GST rows must align on desktop');
 assert.equal(await page.locator('a[href$=".pdf"]').count(), 0, 'Profile PDF links must be removed');
 await page.goto(base + '/products.html');
 await page.locator('[data-gateway="wp"]').click();
 assert.equal(await page.locator('.pcard:visible').count(), 8);
 await page.locator('[data-reset]').first().click();
 assert.equal(await page.locator('.pcard:visible').count(),56);
 await page.locator('#cat-search').fill('MBBR');
 assert.equal(await page.locator('.pcard:visible').count(),2);
 await page.locator('[data-reset]').first().click();
 await page.locator('[data-cat="au"]').click();
 assert.equal(await page.locator('.pcard:visible').count(),5);
 await page.locator('#cat-make').selectOption('Delta');
 assert((await page.locator('.pcard:visible').count())>0);
 await page.locator('[data-reset]').first().click();
 await page.locator('#cat-search').fill('no-such-product-xyz');
 assert(await page.locator('#cat-empty').isVisible());
 await page.locator('#cat-empty [data-reset]').click();
 await page.locator('[data-no="27"] .pcard__open').click();
 assert(await page.locator('#pdialog').isVisible());
 assert((await page.locator('.spec-grid').textContent()).includes('1–4000 kVA'));
 await page.locator('#pdialog [data-add]').click();
 await page.locator('#pdialog [data-close]').click();
 assert(await page.locator('#tray').isVisible());
 await page.goto(base + '/quote.html');
 assert((await page.locator('#picked').textContent()).includes('Online UPS'));
 await page.goto(base + '/products.html#p-41');
 assert((await page.locator('#pd-title').textContent()).includes('Sewage'));
 await page.keyboard.press('Escape');
 await page.locator('#cat-search').fill('L&T');
 await page.locator('.pcard:visible .pcard__open').first().click();
 assert.equal(await page.locator('#pdialog mark').evaluateAll(ms=>ms.every(m=>m.textContent.toLowerCase()==='l&t')),true);
 await page.keyboard.press('Escape');
 await page.setViewportSize({width:320,height:740});
 await page.goto(base + '/products.html#p-27');
 const dialogFits=await page.locator('#pdialog').evaluate(el=>el.scrollWidth<=el.clientWidth+1);
 assert(dialogFits,'dialog overflows on smallest phone');
 await page.keyboard.press('Escape');
 await page.locator('.menu-toggle').click();
 assert.equal(await page.locator('.menu-toggle').getAttribute('aria-expanded'),'true');
 await page.keyboard.press('Escape');
 assert.equal(await page.locator('.menu-toggle').getAttribute('aria-expanded'),'false');
 await page.emulateMedia({reducedMotion:'reduce'});
 await page.goto(base + '/index.html');
 assert.equal(await page.locator('.hero__copy').evaluate(el=>getComputedStyle(el).animationName),'none');
 await page.setViewportSize({width:390,height:844});
 assert.deepEqual(errors,[]);
 console.log('PASS: system focus and pause, aligned GST rows, PDF removal, capability navigation, search, categories, makes, reset, empty state, specs, enquiry persistence, deep links, search highlighting, mobile dialog/menu, reduced motion; no JS errors.');
 await page.close();
}
module.exports = checkSite;
if (require.main === module) {
 (async () => {
  const { chromium } = require('playwright');
  const browser = await chromium.launch({headless:true});
  try { await checkSite(browser, process.env.SITE_URL || 'http://127.0.0.1:8080'); }
  finally { await browser.close(); }
 })().catch(error => { console.error(error); process.exitCode = 1; });
}
