/* Browser integration tests; an isolated temporary profile is always used. */
const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');
const assert = require('node:assert/strict');
const { chromium } = require('playwright');
const root = path.resolve(__dirname, '..');
const results = [];
const server = http.createServer((req, res) => {
    const file = path.resolve(root, '.' + decodeURIComponent(req.url.split('?')[0]));
    if (!file.startsWith(root + path.sep)) { res.writeHead(403); res.end(); return; }
    fs.readFile(file, (error, data) => {
        if (error) { res.writeHead(404); res.end(); return; }
        const types = {'.html': 'text/html', '.js': 'application/javascript'};
        res.setHeader('Content-Type', (types[path.extname(file)] || 'text/plain') + '; charset=utf-8');
        res.end(data);
    });
});

(async () => {
    let browser;
    try {
        await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
        browser = await chromium.launch({
            headless: true,
            ...(process.env.MOZHI_TEST_BROWSER ? {executablePath: process.env.MOZHI_TEST_BROWSER} : {}),
        });
        const page = await browser.newPage();
        const errors = [];
        page.on('pageerror', error => errors.push(error.message));
        page.setDefaultTimeout(15000);
        const url = `http://127.0.0.1:${server.address().port}/playground/index.html`;
        async function ready() {
            await page.waitForFunction(() => !document.getElementById('run-btn').disabled, null, {timeout: 90000});
        }
        async function start(source) {
            await ready();
            await page.evaluate(code => editor.setValue(code), source);
            await page.locator('#run-btn').click();
        }
        async function finish(source) {
            await start(source);
            await page.waitForFunction(() => ['Finished', 'Finished with an error'].includes(document.getElementById('status').textContent));
            return page.locator('#output').innerText();
        }
        function passed(name) { results.push({name, passed:true}); console.log('PASS ' + name); }
        await page.goto(url);
        await ready();
        passed('engine initializes in a worker');
        for (const [name, expected] of [['demo','1\n2\n3'], ['library','Thiruvalluvar'], ['gossip','See you tomorrow']]) {
            const output = await finish(fs.readFileSync(path.join(root, 'examples', name + '.mozhi'), 'utf8'));
            assert.ok(output.includes(expected), output);
            assert.ok(!output.includes('Error:'), output);
            passed('historical ' + name);
        }
        await start(fs.readFileSync(path.join(root, 'examples/calculator.mozhi'), 'utf8'));
        const input = page.locator('#mozhi-input');
        for (const [value, prompt] of [['1','Enna operation? '], ['10','Amount? '], ['5','Enna operation? '], ['6','Enna operation? ']]) {
            await page.waitForFunction(p => !document.getElementById('input-container').hidden && document.getElementById('mozhi-input').placeholder === p, prompt);
            await input.fill(value); await input.press('Enter');
        }
        await page.waitForFunction(() => document.getElementById('status').textContent === 'Finished');
        assert.ok((await page.locator('#output').innerText()).includes('Ippo total: 10'));
        passed('calculator input and result');
        assert.equal((await finish('seiy quit():\n    podhum\nmudivu\nquit()\n"unreachable" sollu\n')).trim(), '[Mozhi] Podhum, I am out.');
        assert.equal((await finish('2 ** 3 ** 2 sollu\n-2 ** 2 sollu\nfalse mattrum (1 / 0) sollu\n')).trim(), '512\n-4\nfalse');
        passed('exit, powers, and short circuit in real Pyodide');
        await page.locator('#time-limit').fill('0.3');
        await start('"loop started" sollu\ntrue varaikum:\n    thodaru\nmudivu\n');
        await page.waitForFunction(() => document.getElementById('output').textContent.includes('loop started'));
        const heartbeat = await page.evaluate(() => new Promise(resolve => setTimeout(() => resolve('responsive'), 30)));
        assert.equal(heartbeat, 'responsive');
        await page.waitForFunction(() => document.getElementById('output').textContent.includes('Execution time limit reached.'));
        await ready();
        passed('infinite loop times out without freezing the UI and engine restarts');
        await page.locator('#time-limit').fill('10');
        await start('true varaikum:\n    1 sollu\nmudivu\n');
        await page.waitForFunction(() => document.getElementById('output').textContent.includes('Output truncated'));
        assert.ok((await page.locator('#output').innerText()).length < 66000);
        await page.locator('#stop-btn').click();
        await ready();
        assert.ok((await page.locator('#output').innerText()).includes('Stopped by user.'));
        passed('Stop terminates a running worker');
        await page.locator('#time-limit').fill('0.2');
        await start('value = kelu("Wait?") vechukko\nvalue sollu\n');
        await input.waitFor({state:'visible'});
        await page.waitForTimeout(500);
        assert.equal(await page.locator('#status').innerText(), 'Waiting for input (execution timer paused)');
        await input.fill('resumed'); await input.press('Enter');
        await page.waitForFunction(() => document.getElementById('status').textContent === 'Finished');
        assert.ok((await page.locator('#output').innerText()).includes('resumed'));
        passed('input wait pauses the execution budget');
        await page.locator('#time-limit').fill('10');
        await start('kelu("Stop input?") sollu\n');
        await input.waitFor({state:'visible'});
        await page.locator('#stop-btn').click();
        await ready();
        assert.equal(await page.locator('#input-container').isHidden(), true);
        assert.equal((await finish('"fresh run" sollu\n')).trim(), 'fresh run');
        passed('Stop cancels input and a new run has clean state');
        await ready();
        const startId = await page.evaluate(() => runId);
        await page.evaluate(() => {editor.setValue('"once" sollu\n'); runButton.click(); runButton.click();});
        await page.waitForFunction(() => document.getElementById('status').textContent === 'Finished');
        assert.equal(await page.evaluate(() => runId), startId + 1);
        assert.equal((await page.locator('#output').innerText()).trim(), 'once');
        passed('concurrent Run clicks are ignored');
        assert.ok((await finish('enn("bad") sollu\n')).includes('Line 1:'));
        assert.equal(await page.locator('#input-container').isHidden(), true);
        passed('runtime errors are readable and leave controls usable');
        await page.route('**/runtime.py', route => route.fulfill({status:503,body:'Unavailable'}));
        await page.reload();
        await page.locator('#retry-btn').waitFor({state:'visible'});
        assert.ok((await page.locator('#output').innerText()).includes('Runtime download failed (503)'));
        await page.unroute('**/runtime.py');
        await page.locator('#retry-btn').click();
        await ready();
        assert.equal((await finish('"recovered" sollu\n')).trim(), 'recovered');
        passed('engine load failure exposes a working Retry control');
        await page.route('**/codemirror.min.js', route => route.abort());
        await page.reload();
        await ready();
        assert.equal((await finish('"plain editor" sollu\n')).trim(), 'plain editor');
        await page.unroute('**/codemirror.min.js');
        passed('plain textarea fallback works when the editor CDN fails');
        assert.deepEqual(errors, []);
    } catch (error) {
        results.push({passed:false,error:error.stack || String(error)});
        console.error(error);
        process.exitCode = 1;
    } finally {
        if (browser) await browser.close();
        server.close();
        if (process.env.MOZHI_TEST_REPORT) fs.writeFileSync(process.env.MOZHI_TEST_REPORT, JSON.stringify(results,null,2));
    }
})();
