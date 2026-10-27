const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const assert = require('node:assert/strict');
const {chromium} = require('playwright');
const root = path.resolve(__dirname, '..');
const results = [];
const server = http.createServer((req,res) => {
    const file=path.resolve(root,'.'+decodeURIComponent(req.url.split('?')[0]));
    if(!file.startsWith(root+path.sep)){res.writeHead(403);res.end();return;}
    fs.readFile(file,(error,data)=>{
        if(error){res.writeHead(404);res.end();return;}
        res.setHeader('Content-Type',({'.html':'text/html','.js':'application/javascript','.css':'text/css'}[path.extname(file)]||'text/plain')+'; charset=utf-8');res.end(data);
    });
});

(async()=>{
 let browser;
 try{
    await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
    browser=await chromium.launch({headless:true,...(process.env.MOZHI_TEST_BROWSER?{executablePath:process.env.MOZHI_TEST_BROWSER}:{})});
    const context=await browser.newContext({viewport:{width:1440,height:1000},permissions:['clipboard-read','clipboard-write'],acceptDownloads:true});
    const page=await context.newPage();const errors=[];page.on('pageerror',error=>errors.push(error.message));page.setDefaultTimeout(15000);
    const url=`http://127.0.0.1:${server.address().port}/playground/index.html`;
    const pass=name=>{results.push({name,passed:true});console.log('PASS '+name);};
    const ready=()=>page.waitForFunction(()=>!document.getElementById('run-btn').disabled,null,{timeout:90000});
    const done=()=>page.waitForFunction(()=>['Finished','Finished with an error'].includes(document.getElementById('status').textContent));
    await page.goto(url);await ready();
    assert.equal(await page.locator('.lesson-item').count(),8);
    assert.equal(await page.locator('#course-progress').getAttribute('aria-valuenow'),'0');
    assert.ok(await page.locator('.cm-string').count()>0);
    assert.ok(!await page.evaluate(()=>document.body.innerText.includes('\u2014')));
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
    pass('light studio renders, syntax highlighting works, and initial progress is honest');
    await page.locator('#download-btn').hover();await page.locator('#tooltip').waitFor({state:'visible'});
    assert.ok((await page.locator('#tooltip').innerText()).includes('Download'));
    await page.locator('#hint-toggle').click();assert.equal(await page.locator('#lesson-hint').isVisible(),true);
    pass('tooltips and lesson hints reveal useful content');
    await page.keyboard.press('Control+k');await page.locator('#palette-input').fill('Functions');await page.locator('#palette-input').press('Enter');
    await page.waitForFunction(()=>document.getElementById('filename').value==='double.mozhi');
    pass('command palette finds lessons and opens them with the keyboard');
    const lessons=await page.evaluate(()=>LESSONS.map(l=>({id:l.id,filename:l.filename})));
    for(const lesson of lessons){
        await page.locator(`[data-lesson="${lesson.id}"]`).click();
        await ready();await page.locator('#run-btn').click();
        if(lesson.id==='input'){
            await page.locator('#mozhi-input').waitFor({state:'visible'});await page.locator('#mozhi-input').fill('Nanba');await page.locator('#mozhi-input').press('Enter');
        }
        await done();assert.ok(!(await page.locator('#output').innerText()).includes('Error:'),lesson.id);
        assert.ok(await page.evaluate(id=>completed.has(id),lesson.id),lesson.id+' must pass its actual check');
    }
    assert.equal(await page.locator('#course-progress').getAttribute('aria-valuenow'),'8');
    assert.ok((await page.locator('#progress-label').innerText()).includes('8 of 8'));
    pass('all eight lesson programs run and earn real, persisted completion');
    await page.locator('#reference-tab').click();await page.locator('#reference-search').fill('thirumbu');
    assert.equal(await page.locator('.reference-item').count(),1);await page.locator('.reference-item button').click();
    assert.ok((await page.evaluate(()=>navigator.clipboard.readText())).includes('thirumbu'));
    pass('reference search and copyable snippets work');
    await page.locator('#editor-settings summary').click();await page.locator('#font-plus').click();
    assert.equal(await page.locator('#font-value').textContent(),'15');await page.locator('#line-wrap').uncheck();
    await page.locator('#editor-settings summary').click();
    await page.evaluate(()=>editor.setValue('"Saved locally" sollu\n'));
    await page.locator('#filename').fill('my-program');await page.locator('#filename').press('Tab');
    await page.waitForFunction(()=>JSON.parse(localStorage.getItem('mozhi.studio.v1.draft'))?.source==='"Saved locally" sollu\n');
    await page.reload();await ready();
    assert.equal(await page.evaluate(()=>editor.getValue()),'"Saved locally" sollu\n');
    assert.equal(await page.locator('#filename').inputValue(),'my-program.mozhi');
    assert.equal(await page.locator('#font-value').textContent(),'15');
    assert.equal(await page.locator('#course-progress').getAttribute('aria-valuenow'),'8');
    pass('code, filename, preferences and learning progress survive reload');
    await page.locator('[data-lesson="hello"]').click();await page.locator('#confirm-dialog').waitFor({state:'visible'});await page.locator('#confirm-cancel').click();
    assert.equal(await page.evaluate(()=>editor.getValue()),'"Saved locally" sollu\n');
    await page.locator('[data-lesson="hello"]').click();await page.locator('#confirm-replace').click();
    await page.waitForFunction(()=>document.getElementById('filename').value==='hello.mozhi');
    await page.locator('#editor-settings summary').click();await page.locator('#restore-draft').click();
    await page.waitForFunction(()=>document.getElementById('filename').value==='my-program.mozhi');
    assert.equal(await page.evaluate(()=>editor.getValue()),'"Saved locally" sollu\n');
    pass('replacement confirmation protects edits and previous-draft recovery works');
    await page.locator('#nav-examples').click();await page.locator('#example-search').fill('library');
    assert.equal(await page.locator('.example-card').count(),1);await page.locator('[data-example="library"]').click();
    await page.waitForFunction(()=>document.getElementById('filename').value==='library.mozhi');
    assert.ok((await page.evaluate(()=>editor.getValue())).includes('vagai Book'));
    await page.locator('#run-btn').click();await done();assert.ok((await page.locator('#output').innerText()).includes('Thiruvalluvar'));
    pass('example library searches and loads the actual source files');
    const source='"வணக்கம், Nanba!" sollu\n';
    await page.locator('#file-input').setInputFiles({name:'imported.mozhi',mimeType:'text/plain',buffer:Buffer.from(source)});
    await page.waitForFunction(()=>document.getElementById('filename').value==='imported.mozhi');
    assert.equal(await page.evaluate(()=>editor.getValue()),source);
    const [download]=await Promise.all([page.waitForEvent('download'),page.locator('#download-btn').click()]);
    assert.equal(download.suggestedFilename(),'imported.mozhi');
    const chunks=[];for await(const chunk of await download.createReadStream())chunks.push(chunk);
    assert.equal(Buffer.concat(chunks).toString('utf8'),source);
    pass('file import and UTF-8 download preserve exact program text');
    await page.locator('#share-btn').click();const shared=await page.locator('#share-url').inputValue();
    assert.ok(shared.includes('#code='));await page.locator('#copy-share').click();
    assert.equal(await page.evaluate(()=>navigator.clipboard.readText()),shared);
    await page.locator('#share-dialog [data-close]').click();
    const recipient=await context.newPage();await recipient.goto(shared);
    await recipient.waitForFunction(()=>!document.getElementById('run-btn').disabled,null,{timeout:90000});
    assert.equal(await recipient.evaluate(()=>editor.getValue()),source);
    await recipient.locator('#run-btn').click();await recipient.waitForFunction(()=>document.getElementById('status').textContent==='Finished');
    assert.ok((await recipient.locator('#output').innerText()).includes('வணக்கம்'));
    await recipient.close();
    pass('shared links round-trip Unicode code and run without server-side storage');
    await page.locator('#run-btn').click();await done();
    await page.locator('#history-tab').click();assert.ok(await page.locator('.history-item').count()>0);
    await page.locator('.history-item button').first().click();
    assert.equal(await page.evaluate(()=>editor.getValue()),source);
    await page.locator('#history-tab').click();await page.locator('#clear-history').click();
    assert.equal(await page.locator('#history-count').innerText(),'0');
    pass('run history restores source and can be cleared locally');
    await page.locator('#output-tab').click();
    await page.evaluate(()=>editor.setValue('1 / 0 sollu\n'));
    await page.keyboard.press('Control+Enter');await done();
    await page.locator('#error-help').waitFor({state:'visible'});
    assert.equal(await page.locator('.line-error').count(),1);
    await page.locator('#go-to-error').click();assert.equal(await page.evaluate(()=>editor.getCursor().line),0);
    pass('error explanations and line navigation point to the real diagnostic');
    await page.locator('#guide-toggle').click();assert.equal(await page.locator('#guide-panel').isHidden(),true);
    await page.locator('#guide-toggle').click();assert.equal(await page.locator('#guide-panel').isVisible(),true);
    await page.locator('#help-btn').click();assert.equal(await page.locator('#help-dialog').isVisible(),true);await page.keyboard.press('Escape');
    pass('guide layout and keyboard help are usable');
    assert.deepEqual(errors,[]);
    const mobile=await browser.newPage({viewport:{width:390,height:844}});
    await mobile.goto(url);await mobile.waitForFunction(()=>!document.getElementById('run-btn').disabled,null,{timeout:90000});
    assert.equal(await mobile.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
    await mobile.locator('#sidebar-toggle').click();assert.equal(await mobile.locator('#learning-sidebar').isVisible(),true);
    await mobile.locator('[data-lesson="arrays"]').click();
    assert.equal(await mobile.locator('#learning-sidebar').isHidden(),true);
    assert.equal(await mobile.locator('#filename').inputValue(),'fruit-basket.mozhi');
    await mobile.close();pass('phone layout avoids overflow and learning drawer works');
    const blocked=await browser.newContext();
    await blocked.addInitScript(()=>{Storage.prototype.setItem=function(){throw new Error('Storage disabled');};});
    const blockedPage=await blocked.newPage();await blockedPage.goto(url);
    await blockedPage.waitForFunction(()=>!document.getElementById('run-btn').disabled,null,{timeout:90000});
    assert.ok((await blockedPage.locator('#save-status').innerText()).includes('unavailable'));
    await blockedPage.locator('#run-btn').click();await blockedPage.waitForFunction(()=>document.getElementById('status').textContent==='Finished');
    await blocked.close();pass('blocked browser storage degrades gracefully without breaking execution');
 }catch(error){results.push({passed:false,error:error.stack||String(error)});console.error(error);process.exitCode=1;}
 finally{if(browser)await browser.close();server.close();if(process.env.MOZHI_STUDIO_REPORT)fs.writeFileSync(process.env.MOZHI_STUDIO_REPORT,JSON.stringify(results,null,2));}
})();


