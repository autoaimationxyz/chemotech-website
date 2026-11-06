const assert = require('node:assert/strict');
module.exports = async function checkJourneys(browser, base) {
 const context = await browser.newContext({viewport:{width:390,height:844}, reducedMotion:'reduce'});
 const page = await context.newPage();
 const errors=[];
 page.on('pageerror',error=>errors.push(error.message));
 try {
  await page.goto(base+'/products.html');
  await page.locator('#cat-search').fill('UPS');
  await page.locator('#cat-make').selectOption('Delta');
  await page.locator('[data-cat="pb"]').click();
  const sharedURL=page.url();
  assert.equal(new URL(sharedURL).searchParams.get('q'),'UPS');
  assert.equal(new URL(sharedURL).searchParams.get('make'),'Delta');
  const found=await page.locator('.pcard:visible').count();
  assert(found>0);
  await page.reload();
  assert.equal(await page.locator('#cat-search').inputValue(),'UPS');
  assert.equal(await page.locator('#cat-make').inputValue(),'Delta');
  assert.equal(await page.locator('.pcard:visible').count(),found);
  await page.locator('[data-no="27"] .pcard__open').click();
  await page.reload();
  assert(await page.locator('#pdialog').isVisible());
  await page.keyboard.press('Escape');
  assert.equal(await page.locator('#cat-search').inputValue(),'UPS');
  assert.equal(await page.locator('#cat-make').inputValue(),'Delta');
  await page.locator('[data-reset]').first().click();
  assert.equal(new URL(page.url()).searchParams.has('q'),false);
  assert.equal(new URL(page.url()).searchParams.has('make'),false);
  assert.equal(await page.locator('.pcard:visible').count(),12);
  await page.goto(base+'/products.html?make=Unknown-maker');
  assert.equal(await page.locator('#cat-make').inputValue(),'');
  assert.equal(await page.locator('#cat-make').evaluate(el=>el.selectedIndex),0);
  assert.equal(await page.locator('.pcard:visible').count(),12);

  await page.locator('.menu-toggle').click();
  const menuBox=await page.locator('#site-nav').boundingBox();
  await page.mouse.click(5,Math.min(839,menuBox.y+menuBox.height+8));
  assert.equal(await page.locator('.menu-toggle').getAttribute('aria-expanded'),'false');
  await page.locator('.menu-toggle').click();
  await page.setViewportSize({width:1440,height:1000});
  await page.setViewportSize({width:390,height:844});
  assert.equal(await page.locator('.menu-toggle').getAttribute('aria-expanded'),'false');

  const other=await context.newPage();
  await other.goto(base+'/products.html#p-27');
  await other.locator('#pdialog [data-add]').click();
  await page.goto(base+'/quote.html');
  assert.equal(await page.locator('#picked li').count(),1);
  for(const [id,value] of Object.entries({name:'Journey check',company:'Test company',email:'review@example.com',phone:'1234567890',requirement:'Please quote for an online UPS.',site:'Patna'})) await page.locator('#'+id).fill(value);
  await page.evaluate(()=>Object.defineProperty(navigator,'clipboard',{configurable:true,value:undefined}));
  await page.locator('[data-copy-message]').click();
  assert((await page.locator('.prepared-message').inputValue()).includes('Online UPS'));
  await page.locator('#picked [data-remove]').click();
  assert(await page.locator('.prepared-message').isHidden());
  assert(await page.locator('.form-status').isHidden());
  assert(await page.locator('#quote-catalogue-link').evaluate(el=>el===document.activeElement));
  assert((await page.locator('#picked-notice').textContent()).includes('No products selected'));
  await page.locator('[data-copy-message]').click();
  assert(!(await page.locator('.prepared-message').inputValue()).includes('Catalogue products:'));

  // Another open tab must see additions/removals, and an old prepared draft must disappear.
  await other.locator('#pdialog [data-add]').click();
  await page.waitForFunction(()=>document.querySelectorAll('#picked li').length===1);
  assert(await page.locator('.prepared-message').isHidden());
  await page.locator('[data-copy-message]').click();
  assert((await page.locator('.prepared-message').inputValue()).includes('Online UPS'));
  await other.locator('#pdialog [data-add]').click();
  await page.waitForFunction(()=>document.querySelectorAll('#picked li').length===0);
  assert(await page.locator('.prepared-message').isHidden());
  assert((await page.locator('#picked-notice').textContent()).includes('another tab'));
  assert.deepEqual(errors,[]);
  console.log('PASS: shared/reloaded catalogue filters, filtered product deep links, reset, invalid make fallback, mobile dismissal, selection-removal focus, draft invalidation and cross-tab enquiry sync.');
 } finally { await context.close(); }
};
if (require.main === module) {
 (async () => {
  const {chromium}=require('playwright');
  const browser=await chromium.launch({headless:true});
  try { await module.exports(browser, process.env.SITE_URL || 'http://127.0.0.1:8080'); }
  finally { await browser.close(); }
 })().catch(error=>{console.error(error);process.exitCode=1;});
}
