/* Run tools/build_site.py before these checks. Tests include a repository URL prefix. */
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const assert = require('node:assert/strict');
const {chromium} = require('playwright');
const root = path.resolve(__dirname, '../site');
const server = http.createServer((req, res) => {
    const url = new URL(req.url, 'http://localhost');
    if (!url.pathname.startsWith('/mozhi/')) {res.writeHead(404);res.end();return;}
    let file = path.resolve(root, '.' + decodeURIComponent(url.pathname.slice('/mozhi'.length)));
    if (!file.startsWith(root + path.sep)) {res.writeHead(403);res.end();return;}
    if (url.pathname.endsWith('/')) file = path.join(file, 'index.html');
    fs.readFile(file, (error, data) => {
        if (error) {res.writeHead(404);res.end();return;}
        const types = {'.html':'text/html','.js':'application/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml'};
        res.setHeader('Content-Type', types[path.extname(file)] || 'application/octet-stream');res.end(data);
    });
});
(async () => {
    let browser;
    try {
        assert.ok(fs.existsSync(path.join(root, 'learn/index.html')), 'Build the combined website first');
        await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
        browser = await chromium.launch({headless:true,...(process.env.MOZHI_TEST_BROWSER ? {executablePath:process.env.MOZHI_TEST_BROWSER} : {})});
        const page = await browser.newPage({viewport:{width:1440,height:1000}});
        const errors = [];page.on('pageerror', error => errors.push(error.message));
        const base = `http://127.0.0.1:${server.address().port}/mozhi`;
        await page.goto(base + '/playground/');
        const checkNav = async () => {
            const centers = await page.locator('.topnav .nav-button').evaluateAll(items => items.map(item => {
                const range = document.createRange();range.selectNodeContents(item);
                const rect = range.getBoundingClientRect();return rect.top + rect.height / 2;
            }));
            assert.ok(Math.max(...centers) - Math.min(...centers) < 2, 'Navigation text must align');
        };
        await checkNav();
        await page.locator('#nav-learn').click();await page.waitForURL('**/learn/');
        assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
        await page.goto(base + '/learn/basics/variables/');
        await page.locator('.mozhi-nav a').filter({hasText:'Examples'}).click();
        await page.locator('#examples-dialog').waitFor({state:'visible'});
        assert.equal(await page.locator('.example-card').count(), 8);
        await page.keyboard.press('Escape');
        await page.locator('#guide-toggle').click();await page.locator('#nav-studio').click();
        assert.equal(await page.locator('#guide-panel').isVisible(), true);
        console.log('PASS combined website navigation, nested documentation links, gallery and Studio lessons');
        await page.setViewportSize({width:390,height:844});
        await checkNav();
        await page.locator('#nav-learn').click();await page.waitForURL('**/learn/');
        assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
        await page.locator('label[for="__search"]').first().click();
        await page.locator('.md-search__input').pressSequentially('vechukko', {delay:80});
        await page.locator('.md-search-result__item').first().waitFor();
        assert.deepEqual(errors, []);
        console.log('PASS phone navigation, documentation search and layout under a repository path');
        await page.goto(base + '/learn/install/');
        assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, 'Installation tables and download commands must fit a phone');
        await page.setViewportSize({width:1440,height:1000});
        await page.getByRole('link', {name:'Command Reference', exact:true}).first().click();
        await page.waitForURL('**/learn/cli/');
        await page.locator('article').getByRole('link', {name:'REPL behavior', exact:true}).click();
        await page.waitForURL('**/learn/cli/repl/');
        assert.ok((await page.locator('article').innerText()).includes('Multiline blocks'));
        assert.deepEqual(errors, []);
        console.log('PASS mobile installation page and CLI-to-REPL navigation');
    } catch (error) {console.error(error);process.exitCode=1;}
    finally {if (browser) await browser.close();server.close();}
})();
