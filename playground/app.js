/* The studio is local-first. Programs are never uploaded by this interface. */
const $ = id => document.getElementById(id);
const icon = name => `<svg class="icon" aria-hidden="true"><use href="#i-${name}"/></svg>`;
const escapeHTML = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const KEY = 'mozhi.studio.v1.';
const MAX_SOURCE = 262144;
let storageAvailable = true;
function readStore(name, fallback) {
    try { return JSON.parse(localStorage.getItem(KEY + name)) ?? fallback; }
    catch { return fallback; }
}
function writeStore(name, value) {
    try { localStorage.setItem(KEY + name, JSON.stringify(value)); return true; }
    catch { storageAvailable = false; return false; }
}
function validSource(value) { return typeof value === 'string' && value.length <= MAX_SOURCE; }
function fileName(value) {
    let name = String(value || 'untitled.mozhi').split(/[\\/]/).pop().replace(/[^a-zA-Z0-9._-]/g, '-').slice(0, 75);
    if (!name || /^\.+$/.test(name)) name = 'untitled';
    return name.endsWith('.mozhi') ? name : name.replace(/\.txt$/, '') + '.mozhi';
}
const saved = readStore('draft', null);
let currentLesson = LESSONS.some(l => l.id === saved?.lessonId) ? saved.lessonId : 'hello';
let baselineSource = validSource(saved?.baseline) ? saved.baseline.replace(/\r\n?/g,'\n') : LESSONS[0].source;
const completed = new Set((Array.isArray(readStore('completed', [])) ? readStore('completed', []) : []).filter(id => LESSONS.some(l => l.id === id)));
let runs = readStore('runs', []);
runs = (Array.isArray(runs) ? runs : []).filter(r => validSource(r?.source) && typeof r.output === 'string' && typeof r.filename === 'string').slice(0, 8);
const preferences = readStore('preferences', {});
let fontSize = Math.max(12, Math.min(20, Number(preferences?.fontSize) || 14));
let wrapLines = preferences?.wrap !== false;
let guideVisible = preferences?.guide !== false;
let toastTimer;
let saveTimer;
let errorLine = null;
let tooltipTarget = null;
let activeRun = null;
let selectedCategory = 'All';
let paletteItems = [];
let paletteIndex = 0;

if (typeof CodeMirror !== 'undefined') {
    CodeMirror.defineMode('mozhi', () => ({
        token(stream) {
            if (stream.eatSpace()) return null;
            if (stream.peek() === '#') { stream.skipToEnd(); return 'comment'; }
            if (stream.match(/^(?:"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')/)) return 'string';
            if (stream.match(/^\d+(?:\.\d+)?/)) return 'number';
            if (stream.match(/^[A-Za-z_][A-Za-z0-9_]*/)) {
                const word = stream.current();
                if (['ketukko','kelu','neelam','enn','padam','vaari'].includes(word)) return 'builtin';
                return REFERENCE.some(r => r.word === word) ? 'keyword' : 'variable';
            }
            if (stream.match(/^(?:\*\*|==|!=|<=|>=|[+\-*/%=<>])/)) return 'operator';
            stream.next(); return null;
        },
        lineComment: '#',
    }));
}
const textarea = $('code-editor');
const editor = typeof CodeMirror === 'undefined' ? {
    getValue: () => textarea.value,
    setValue: value => { textarea.value = value; onEditorChange(); },
    focus: () => textarea.focus(),
} : CodeMirror.fromTextArea(textarea, {
    mode:'mozhi', theme:'default', lineNumbers:true, indentUnit:4, tabSize:4,
    lineWrapping:wrapLines, gutters:['CodeMirror-linenumbers','diagnostic-gutter'],
    extraKeys:{Tab:cm => cm.indentSelection('add'), 'Shift-Tab':cm => cm.indentSelection('subtract')},
});
const runButton = $('run-btn');
const stopButton = $('stop-btn');
const retryButton = $('retry-btn');
const output = $('output');
const status = $('status');
const inputForm = $('input-container');
const input = $('mozhi-input');
const limit = $('time-limit');
let worker = null;
let phase = 'loading';
let runId = 0;
let pendingInput = null;
let timer = null;
let startupTimer = null;
let remaining = 0;
let resumedAt = 0;

function toast(text) {
    clearTimeout(toastTimer); $('toast').textContent = text; $('toast').hidden = false;
    toastTimer = setTimeout(() => { $('toast').hidden = true; }, 3600);
}
function updateCursor() {
    const source = editor.getValue();
    const cursor = editor.getCursor ? editor.getCursor() : {
        line:source.slice(0, textarea.selectionStart).split('\n').length - 1,
        ch:source.slice(0, textarea.selectionStart).split('\n').pop().length,
    };
    $('cursor-position').textContent = `Ln ${cursor.line + 1}, Col ${cursor.ch + 1}`;
    const lines = source.split('\n').length;
    $('line-count').textContent = `${lines} ${lines === 1 ? 'line' : 'lines'}`;
}
function persistDraft() {
    clearTimeout(saveTimer);
    const source = editor.getValue();
    const ok = validSource(source) && writeStore('draft', {source, baseline:baselineSource, filename:fileName($('filename').value), lessonId:currentLesson});
    $('save-status').textContent = ok ? 'Saved in this browser' : 'Local save unavailable. Download a copy.';
    $('save-dot').classList.toggle('unsaved', !ok);
}
function onEditorChange() {
    updateCursor();
    $('save-status').textContent = 'Saving your draft...';
    $('save-dot').classList.add('unsaved');
    clearTimeout(saveTimer); saveTimer = setTimeout(persistDraft, 350);
}
function savePreferences() {
    writeStore('preferences', {fontSize, wrap:wrapLines, guide:guideVisible});
}
function applyPreferences() {
    if (editor.getWrapperElement) editor.getWrapperElement().style.fontSize = fontSize + 'px';
    textarea.style.fontSize = fontSize + 'px';
    editor.setOption?.('lineWrapping', wrapLines);
    $('font-value').textContent = fontSize;
    $('line-wrap').checked = wrapLines;
    $('font-minus').disabled = fontSize <= 12;
    $('font-plus').disabled = fontSize >= 20;
    $('guide-panel').hidden = !guideVisible;
    $('workbench').classList.toggle('guide-hidden', !guideVisible);
    $('guide-toggle').setAttribute('aria-expanded', String(guideVisible));
    requestAnimationFrame(() => editor.refresh?.());
}
function clearDiagnostics() {
    if (errorLine !== null) editor.removeLineClass?.(errorLine - 1, 'background', 'line-error');
    editor.clearGutter?.('diagnostic-gutter'); errorLine = null; $('error-help').hidden = true;
}
function showError(message) {
    const match = message.match(/\bLine (\d+):/);
    errorLine = match ? Number(match[1]) : null;
    $('error-title').textContent = errorLine ? `Let's check line ${errorLine}.` : 'A small thing to check.';
    let hint = 'Read the message above, make a change, then run your program again.';
    if (/indent|INDENT|DEDENT/i.test(message)) hint = 'Use a consistent indentation level inside each block. A block follows a colon and closes with mudivu.';
    else if (/quote|string/i.test(message)) hint = 'Check that every opening quote has a matching closing quote.';
    else if (/Variable.*illa|not defined/i.test(message)) hint = 'Give this variable a value with vechukko before using it. Check its spelling too.';
    else if (/argument|parameter/i.test(message)) hint = 'Compare this call with the function or method definition. Each declared parameter needs a value.';
    else if (/invalid literal|convert/i.test(message)) hint = 'Input is a string. Give enn an integer, or use padam for a decimal number.';
    else if (/division by zero/i.test(message)) hint = 'The divisor is zero. Change it, or guard the calculation with a na condition.';
    $('error-detail').textContent = hint;
    $('go-to-error').hidden = errorLine === null;
    $('error-help').hidden = false;
    if (errorLine && editor.addLineClass) {
        editor.addLineClass(errorLine - 1, 'background', 'line-error');
        const marker = document.createElement('span'); marker.className = 'error-marker'; marker.textContent = '●'; marker.title = message;
        editor.setGutterMarker(errorLine - 1, 'diagnostic-gutter', marker);
    }
}
function selectTab(first, second, firstPanel, secondPanel, showFirst) {
    $(first).classList.toggle('active', showFirst); $(second).classList.toggle('active', !showFirst);
    $(first).setAttribute('aria-selected', String(showFirst)); $(second).setAttribute('aria-selected', String(!showFirst));
    $(first).tabIndex = showFirst ? 0 : -1; $(second).tabIndex = showFirst ? -1 : 0;
    $(firstPanel).hidden = !showFirst; $(secondPanel).hidden = showFirst;
}
function showOutput() { selectTab('output-tab','history-tab','output-panel','history-panel',true); }
function showLesson() { selectTab('lesson-tab','reference-tab','lesson-panel','reference-panel',true); }
function emptyOutput(message = null) {
    $('output-empty').hidden = output.textContent.length > 0 || phase === 'input';
    $('output-empty').querySelector('strong').textContent = message || 'A small line. A new possibility.';
    $('output-empty').querySelector('p').textContent = message ? 'Use sollu to print something.' : 'Run your code to see what it says.';
}
function renderLessons() {
    $('lesson-list').innerHTML = LESSONS.map((l,i) => `<button class="lesson-item ${l.id === currentLesson ? 'active' : ''} ${completed.has(l.id) ? 'completed' : ''}" data-lesson="${l.id}" ${l.id === currentLesson ? 'aria-current="step"' : ''}><span class="lesson-number">${completed.has(l.id) ? icon('check') : String(i + 1).padStart(2,'0')}</span><span><span class="lesson-name">${l.name}</span><span class="lesson-description">${l.subtitle}${completed.has(l.id) ? ' · Completed' : ''}</span></span>${l.id === currentLesson ? '<svg class="icon lesson-chevron"><use href="#i-chevron"/></svg>' : ''}</button>`).join('');
    const count = completed.size;
    $('progress-label').textContent = `${count} of ${LESSONS.length} completed`;
    $('progress-percent').textContent = Math.round(count / LESSONS.length * 100) + '%';
    $('progress-fill').style.width = count / LESSONS.length * 100 + '%';
    $('course-progress').setAttribute('aria-valuenow', String(count));
    renderLesson();
}
function renderLesson() {
    const lesson = LESSONS.find(l => l.id === currentLesson);
    $('current-section').textContent = lesson?.level || 'FREE EXPLORATION';
    if (!lesson) {
        $('lesson-panel').innerHTML = `<div class="lesson-kicker">YOUR SCRATCHPAD <span class="lesson-pill">EXPLORE</span></div><h2>Follow your own idea.</h2><p>There is no lesson to finish here. Just a blank space for whatever you want to make.</p><div class="lesson-code">"What if?" sollu</div><p>Need a word? The quick reference has every keyword, with a short explanation and a copyable example.</p><button class="button button-outline" id="return-lessons">Back to the first lesson ${icon('arrow')}</button>`;
        $('return-lessons').onclick = () => loadLesson('hello');
        return;
    }
    const index = LESSONS.indexOf(lesson);
    const isDone = completed.has(lesson.id);
    $('lesson-panel').innerHTML = `<div class="lesson-kicker">${String(index+1).padStart(2,'0')} / ${String(LESSONS.length).padStart(2,'0')}<span class="lesson-pill">${lesson.level}</span></div><h2>${lesson.title}</h2><p>${lesson.intro}</p><p>${lesson.explanation}</p><pre class="lesson-code"></pre><div class="concept-label">THE WORD BEHIND THE CODE</div><div class="concept-row"><button class="keyword-chip" data-tooltip="${escapeHTML(lesson.meaning)}">${lesson.keyword}</button><span>→</span><span>${lesson.meaning}</span></div><div class="challenge-box"><div class="challenge-heading">${icon('spark')} Make it yours</div><p>${lesson.task}</p><button class="hint-button" id="hint-toggle" aria-expanded="false" aria-controls="lesson-hint">Need a little hint? ${icon('chevron')}</button><div class="hint-content" id="lesson-hint" hidden></div></div><div class="expected-label">EXAMPLE OUTPUT</div><pre class="expected-output"></pre><div class="lesson-completion" ${isDone ? '' : 'hidden'}><strong>${icon('check')} ${index === LESSONS.length-1 && completed.size === LESSONS.length ? 'You finished the learning path.' : 'A little progress, well earned.'}</strong><p>This lesson's program ran successfully. Keep experimenting, or take the next step.</p><button id="next-lesson" class="button button-outline next-lesson">${index < LESSONS.length-1 ? 'Next: ' + LESSONS[index+1].name : 'Explore examples'} ${icon('arrow')}</button></div>`;
    $('lesson-panel').querySelector('.lesson-code').textContent = lesson.snippet;
    $('lesson-panel').querySelector('.expected-output').textContent = lesson.expected;
    $('lesson-hint').textContent = lesson.hint;
    $('hint-toggle').onclick = () => {
        const expanded = $('hint-toggle').getAttribute('aria-expanded') === 'true';
        $('hint-toggle').setAttribute('aria-expanded', String(!expanded)); $('lesson-hint').hidden = expanded;
    };
    $('next-lesson').onclick = () => index < LESSONS.length-1 ? loadLesson(LESSONS[index+1].id) : openExamples();
}
function renderReference() {
    const query = $('reference-search').value.toLowerCase().trim();
    const items = REFERENCE.filter(r => (r.word+' '+r.meaning).toLowerCase().includes(query));
    $('reference-list').replaceChildren();
    for (const item of items) {
        const card = document.createElement('article'); card.className = 'reference-item';
        card.innerHTML = `<header><code></code><button class="icon-button" aria-label="Copy ${item.word} example" data-tooltip="Copy this example">${icon('copy')}</button></header><p></p><pre></pre>`;
        card.querySelector('code').textContent = item.word; card.querySelector('p').textContent = item.meaning; card.querySelector('pre').textContent = item.syntax;
        card.querySelector('button').onclick = () => copyText(item.syntax).then(ok => toast(ok ? 'Example copied.' : 'Clipboard unavailable. Select the example to copy it.'));
        $('reference-list').append(card);
    }
    if (!items.length) $('reference-list').innerHTML = '<div class="no-results">No keyword found. Try another word.</div>';
}
function persistRun(outcome) {
    if (!activeRun) return;
    const lesson = LESSONS.find(l => l.id === activeRun.lessonId);
    if (outcome === 'success' && lesson && lesson.check(activeRun.source, output.textContent) && !completed.has(lesson.id)) {
        completed.add(lesson.id); writeStore('completed', [...completed]); renderLessons(); toast(`Lesson complete: ${lesson.name}`);
    }
    runs.unshift({source:activeRun.source.slice(0,MAX_SOURCE),filename:activeRun.filename,lessonId:activeRun.lessonId,output:output.textContent.slice(0,65580),outcome,time:new Date().toISOString(),elapsed:activeRun.elapsed});
    runs = runs.slice(0,8); writeStore('runs',runs);
    $('run-duration').textContent = activeRun.elapsed < 1000 ? `${Math.round(activeRun.elapsed)} ms` : `${(activeRun.elapsed/1000).toFixed(2)} s`;
    $('result-dot').className = `result-dot ${outcome === 'success' ? 'success' : 'error'}`;
    activeRun = null; renderHistory();
}
function renderHistory() {
    $('history-count').textContent = String(runs.length); $('history-list').replaceChildren();
    for (const run of runs) {
        const card = document.createElement('div'); card.className = 'history-item';
        card.innerHTML = `<span class="history-icon ${run.outcome === 'success' ? '' : 'failed'}">${icon(run.outcome === 'success' ? 'check' : 'stop')}</span><div><strong></strong><p></p></div><button class="small-text-button">Restore</button>`;
        card.querySelector('strong').textContent = fileName(run.filename);
        const date = new Date(run.time);
        const when = Number.isNaN(date.getTime()) ? 'Saved run' : date.toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'});
        card.querySelector('p').textContent = `${when} · ${run.outcome || 'saved'} · ${Math.round(Number(run.elapsed)||0)} ms`;
        card.querySelector('button').onclick = async () => {
            if (await replaceProgram(run.source,run.filename,run.lessonId || null)) {
                output.textContent = run.output; emptyOutput(); showOutput(); toast('Code restored. Run it when you are ready.');
            }
        };
        $('history-list').append(card);
    }
    if (!runs.length) $('history-list').innerHTML = '<div class="no-results">Your next run is the beginning of your history.</div>';
}
function confirmReplacement() {
    if ($('confirm-dialog').open) return Promise.resolve(false);
    if (editor.getValue() === baselineSource) return Promise.resolve(true);
    return new Promise(resolve => {
        const dialog = $('confirm-dialog'); let settled = false;
        function finish(value) {
            if (settled) return; settled = true;
            dialog.close(); dialog.removeEventListener('cancel',cancel); resolve(value);
        }
        function cancel(event) { event.preventDefault(); finish(false); }
        $('confirm-cancel').onclick = () => finish(false); $('confirm-replace').onclick = () => finish(true);
        dialog.addEventListener('cancel',cancel); dialog.showModal(); $('confirm-cancel').focus();
    });
}
async function replaceProgram(source,name,lessonId) {
    if (!validSource(source)) { toast('This program is too large for the editor. Limit: 256K characters.'); return false; }
    if (!await confirmReplacement()) return false;
    writeStore('previous', {source:editor.getValue(),filename:fileName($('filename').value),lessonId:currentLesson});
    if (['running','input'].includes(phase)) stopRun('Stopped to open another program.');
    currentLesson = LESSONS.some(l => l.id === lessonId) ? lessonId : null;
    $('filename').value = fileName(name); editor.setValue(source); baselineSource = editor.getValue(); clearDiagnostics();
    renderLessons(); persistDraft(); closeSidebar();
    requestAnimationFrame(() => {editor.refresh?.(); editor.focus();});
    return true;
}
async function loadLesson(id) {
    const lesson = LESSONS.find(l => l.id === id); if (!lesson) return;
    if (await replaceProgram(lesson.source, lesson.filename, id)) {
        guideVisible = true; applyPreferences(); savePreferences(); showLesson();
    }
}
async function loadExample(example) {
    let source = example.source; let name = example.filename || example.file;
    if (example.lesson) { const lesson = LESSONS.find(l => l.id === example.lesson); source = lesson.source; name = lesson.filename; }
    if (example.file) {
        try {
            const response = await fetch('../examples/'+example.file);
            if (!response.ok) throw new Error('Could not open this example.');
            source = await response.text();
        } catch { toast('The example could not load. Check that you are serving the repository root.'); return; }
    }
    $('examples-dialog').close();
    if (await replaceProgram(source,name,example.lesson || null)) toast(`Opened ${example.title.toLowerCase()}.`);
}
function renderExamples() {
    const query = $('example-search').value.toLowerCase().trim();
    const categories = ['All',...new Set(EXAMPLES.map(e=>e.category))];
    $('example-filters').innerHTML = categories.map(c=>`<button class="filter-button ${selectedCategory===c?'active':''}" data-category="${c}" aria-pressed="${selectedCategory===c}">${c}</button>`).join('');
    $('example-grid').replaceChildren();
    for (const example of EXAMPLES.filter(e=>(selectedCategory==='All'||e.category===selectedCategory)&&(e.title+' '+e.description).toLowerCase().includes(query))) {
        const card = document.createElement('button'); card.className='example-card'; card.dataset.example=example.id;
        card.innerHTML=`<span class="example-category">${example.category}</span><h3>${example.title}</h3><p>${example.description}</p><span class="text-button">Open program ${icon('arrow')}</span>`;
        card.onclick=()=>loadExample(example); $('example-grid').append(card);
    }
    if (!$('example-grid').children.length) $('example-grid').innerHTML='<div class="no-results">Nothing here yet. Try another search.</div>';
}
function openExamples() { renderExamples(); $('examples-dialog').showModal(); $('example-search').focus(); }
async function copyText(text) {
    try { await navigator.clipboard.writeText(text); return true; } catch { return false; }
}
function downloadProgram() {
    const blob = new Blob([editor.getValue()], {type:'text/plain;charset=utf-8'});
    const url = URL.createObjectURL(blob); const link = document.createElement('a');
    link.href=url; link.download=fileName($('filename').value); document.body.append(link); link.click(); link.remove();
    setTimeout(()=>URL.revokeObjectURL(url),1000); toast('Your program is ready to keep.');
}
function shareProgram() {
    const payload=JSON.stringify({source:editor.getValue(),filename:fileName($('filename').value),lessonId:currentLesson});
    const bytes=new TextEncoder().encode(payload);
    if (bytes.length>18000) { toast('This program is too long for a reliable link. Download the file instead.'); return; }
    const encoded=btoa(Array.from(bytes,b=>String.fromCharCode(b)).join('')).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
    const url=new URL(location.href); url.hash='code='+encoded;
    $('share-url').value=url.href; $('share-feedback').textContent='The link includes your code. Recipients need access to this website; localhost links only work on your computer.';
    $('share-dialog').showModal();
}
function restoreSharedCode() {
    const encoded=new URLSearchParams(location.hash.slice(1)).get('code'); if (!encoded) return null;
    try {
        if(encoded.length>50000) throw new Error();
        const binary=atob(encoded.replace(/-/g,'+').replace(/_/g,'/'));
        const data=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(Uint8Array.from(binary,c=>c.charCodeAt(0))));
        if(!validSource(data.source)) throw new Error();
        return data;
    } catch { toast('This shared link could not be read. Your saved draft was kept.'); return null; }
}
function openSidebar() {
    $('learning-sidebar').classList.add('open'); $('sidebar-toggle').setAttribute('aria-expanded','true');
    $('sidebar-scrim').hidden=false;
}
function closeSidebar() {
    $('learning-sidebar').classList.remove('open'); $('sidebar-toggle').setAttribute('aria-expanded','false'); $('sidebar-scrim').hidden=true;
}
function renderPalette() {
    const query=$('palette-input').value.toLowerCase().trim();
    const commands=[
        {label:'Run program',kind:'Command',glyph:'play',action:()=>runButton.click()},
        {label:'Stop program',kind:'Command',glyph:'stop',action:()=>stopRun()},
        {label:'New scratchpad',kind:'Command',glyph:'file',action:()=>replaceProgram('# Your next idea starts here.\n','untitled.mozhi',null)},
        {label:'Download program',kind:'Command',glyph:'download',action:downloadProgram},
        {label:'Share code',kind:'Command',glyph:'share',action:shareProgram},
        {label:'Quick reference',kind:'Command',glyph:'code',action:()=>{guideVisible=true;applyPreferences();selectTab('lesson-tab','reference-tab','lesson-panel','reference-panel',false);}},
        {label:'Keyboard shortcuts',kind:'Command',glyph:'help',action:()=>$('help-dialog').showModal()},
    ];
    paletteItems=[...LESSONS.map(l=>({label:l.name+' '+l.subtitle,kind:'Lesson',glyph:'book',action:()=>loadLesson(l.id)})),...EXAMPLES.map(e=>({label:e.title,kind:'Example',glyph:'grid',action:()=>loadExample(e)})),...commands].filter(i=>i.label.toLowerCase().includes(query)).slice(0,14);
    paletteIndex=Math.min(paletteIndex,Math.max(0,paletteItems.length-1));
    $('palette-results').replaceChildren();
    paletteItems.forEach((item,index)=>{
        const button=document.createElement('button');button.className='palette-result'+(index===paletteIndex?' selected':'');button.id='palette-option-'+index;button.setAttribute('role','option');button.setAttribute('aria-selected',String(index===paletteIndex));button.tabIndex=-1;
        button.innerHTML=icon(item.glyph)+'<strong></strong><small></small>';button.querySelector('strong').textContent=item.label;button.querySelector('small').textContent=item.kind;
        button.onclick=()=>{$('palette-dialog').close();item.action();};$('palette-results').append(button);
    });
    if(paletteItems.length) $('palette-input').setAttribute('aria-activedescendant','palette-option-'+paletteIndex);
    else { $('palette-input').removeAttribute('aria-activedescendant');$('palette-results').innerHTML='<div class="no-results">No matches. Try a keyword or a lesson name.</div>'; }
}
function openPalette() { $('palette-input').value='';paletteIndex=0;renderPalette();$('palette-dialog').showModal();$('palette-input').focus(); }
function showTooltip(text,rect,target=null) {
    const tooltip=$('tooltip');tooltip.textContent=text;tooltip.hidden=false;
    if(tooltipTarget) tooltipTarget.removeAttribute('aria-describedby');
    tooltipTarget=target;if(target)target.setAttribute('aria-describedby','tooltip');
    const width=tooltip.offsetWidth;const height=tooltip.offsetHeight;
    tooltip.style.left=Math.max(8,Math.min(rect.left,innerWidth-width-8))+'px';
    tooltip.style.top=(rect.bottom+height+12<innerHeight?rect.bottom+7:Math.max(8,rect.top-height-7))+'px';
}
function hideTooltip() { $('tooltip').hidden=true;if(tooltipTarget)tooltipTarget.removeAttribute('aria-describedby');tooltipTarget=null; }

function setPhase(next,text) {
    phase=next;status.textContent=text;
    runButton.disabled=next!=='ready';stopButton.disabled=!['running','input'].includes(next);limit.disabled=['running','input'].includes(next);retryButton.hidden=next!=='error';
    $('engine-dot').className='status-dot'+(['running','loading'].includes(next)?' busy':next==='error'?' error':'');
    if(next!=='input'){inputForm.hidden=true;pendingInput=null;input.value='';}
}
function pauseClock() {
    if(timer!==null){clearTimeout(timer);timer=null;const elapsed=performance.now()-resumedAt;remaining=Math.max(0,remaining-elapsed);if(activeRun)activeRun.elapsed+=elapsed;}
}
function resumeClock() { resumedAt=performance.now();timer=setTimeout(()=>stopRun('Execution time limit reached.'),remaining); }
function engineError(text) {
    pauseClock();clearTimeout(startupTimer);if(worker)worker.terminate();worker=null;
    const message=String(text).replace(/\u2014/g,':');output.textContent+=`\nError: ${message}\n`;emptyOutput();showError(message);persistRun('error');setPhase('error','Engine unavailable. Use Retry engine.');
}
function startWorker() {
    pauseClock();clearTimeout(startupTimer);if(worker)worker.terminate();setPhase('loading','Loading engine...');
    try{
        const activeWorker=new Worker('./worker.js');worker=activeWorker;
        startupTimer=setTimeout(()=>{if(worker===activeWorker)engineError('Engine loading timed out. Check your network and retry.');},60000);
        activeWorker.onerror=event=>{if(worker===activeWorker)engineError(event.message||'Worker failed to load.');};
        activeWorker.onmessage=event=>{
            if(worker!==activeWorker)return;const message=event.data;
            if(message.type==='ready'){clearTimeout(startupTimer);setPhase('ready','Ready');}
            else if(message.type==='load-error')engineError(message.error);
            else if(message.runId===runId){
                if(message.type==='output'){output.textContent+=message.text;emptyOutput();$('output-panel').scrollTop=$('output-panel').scrollHeight;}
                else if(message.type==='input'&&phase==='running'){
                    pauseClock();pendingInput=message.id;setPhase('input','Waiting for input (execution timer paused)');input.placeholder=message.prompt||'Type your answer...';$('input-label').textContent=message.prompt||'Your program is asking';inputForm.hidden=false;$('output-empty').hidden=true;showOutput();input.focus();
                }else if(message.type==='done'){
                    pauseClock();if(message.error){const error=String(message.error).replace(/\u2014/g,':');output.textContent+=`\nError: ${error}\n`;showError(error);}
                    persistRun(message.error?'error':'success');setPhase('ready',message.error?'Finished with an error':'Finished');emptyOutput(output.textContent?'': 'Finished, with nothing to print.');
                }
            }
        };
        activeWorker.postMessage({type:'initialize'});
    }catch(error){engineError(error.message);}
}
function stopRun(reason='Stopped by user.') {
    if(!['running','input'].includes(phase))return;pauseClock();if(worker)worker.terminate();worker=null;
    output.textContent+=`\n[Mozhi] ${reason}\n`;emptyOutput();persistRun(reason.includes('limit')?'timeout':'stopped');startWorker();
}
runButton.addEventListener('click',()=>{
    if(phase!=='ready')return;const seconds=Number(limit.value);
    if(!Number.isFinite(seconds)||seconds<0.1||seconds>3600){status.textContent='Choose an execution limit between 0.1 and 3600 seconds.';return;}
    output.textContent='';clearDiagnostics();$('result-dot').className='result-dot';$('run-duration').textContent='';showOutput();
    const source=editor.getValue();remaining=seconds*1000;runId+=1;activeRun={source,filename:fileName($('filename').value),lessonId:currentLesson,elapsed:0};
    setPhase('running','Running');$('output-empty').hidden=true;resumeClock();worker.postMessage({type:'run',runId,source});persistDraft();
});
inputForm.addEventListener('submit',event=>{
    event.preventDefault();if(phase!=='input'||pendingInput===null)return;const value=input.value;const id=pendingInput;
    setPhase('running','Running');resumeClock();worker.postMessage({type:'input',runId,id,value});
});
stopButton.addEventListener('click',()=>stopRun());retryButton.addEventListener('click',startWorker);
$('lesson-list').addEventListener('click',event=>{const button=event.target.closest('[data-lesson]');if(button)loadLesson(button.dataset.lesson);});
$('reference-search').addEventListener('input',renderReference);
$('example-search').addEventListener('input',renderExamples);
$('example-filters').addEventListener('click',event=>{const button=event.target.closest('[data-category]');if(button){selectedCategory=button.dataset.category;renderExamples();}});
for(const id of ['nav-examples','browse-examples'])$(id).onclick=openExamples;
$('nav-studio').onclick=()=>{guideVisible=true;applyPreferences();savePreferences();showLesson();$('guide-panel').scrollIntoView({block:'nearest'});};
$('palette-trigger').onclick=openPalette;
$('palette-input').addEventListener('input',()=>{paletteIndex=0;renderPalette();});
$('palette-input').addEventListener('keydown',event=>{
    if(event.key==='ArrowDown'||event.key==='ArrowUp'){event.preventDefault();paletteIndex=(paletteIndex+(event.key==='ArrowDown'?1:-1)+Math.max(1,paletteItems.length))%Math.max(1,paletteItems.length);renderPalette();$('palette-option-'+paletteIndex)?.scrollIntoView({block:'nearest'});}
    if(event.key==='Enter'&&paletteItems[paletteIndex]){event.preventDefault();$('palette-dialog').close();paletteItems[paletteIndex].action();}
});
for(const id of ['help-btn','shortcuts-btn'])$(id).onclick=()=>$('help-dialog').showModal();
$('share-btn').onclick=shareProgram;
$('copy-share').onclick=async()=>{const ok=await copyText($('share-url').value);$('share-feedback').textContent=ok?'Link copied. Your idea is ready to travel.':'Clipboard unavailable. Select and copy the link below.';if(!ok){$('share-url').focus();$('share-url').select();}};
$('download-btn').onclick=downloadProgram;
$('open-btn').onclick=()=>$('file-input').click();
$('file-input').addEventListener('change',async event=>{
    const file=event.target.files[0];event.target.value='';if(!file)return;
    if(file.size>MAX_SOURCE){toast('Please choose a file smaller than 256 KB.');return;}
    try{await replaceProgram(await file.text(),file.name,null);}catch{toast('This file could not be read. Your current code is safe.');}
});
$('filename').addEventListener('change',()=>{$('filename').value=fileName($('filename').value);persistDraft();});
$('new-btn').onclick=()=>replaceProgram('# Your next idea starts here.\n','untitled.mozhi',null);
$('reset-btn').onclick=()=>{const lesson=LESSONS.find(l=>l.id===currentLesson);if(lesson)loadLesson(lesson.id);else replaceProgram('# Your next idea starts here.\n','untitled.mozhi',null);};
$('restore-draft').onclick=async()=>{const previous=readStore('previous',null);if(!validSource(previous?.source)){toast('There is no previous draft to restore yet.');return;}$('editor-settings').open=false;await replaceProgram(previous.source,previous.filename,previous.lessonId);};
$('copy-output').onclick=async()=>toast(await copyText(output.textContent)?'Output copied.':'Clipboard unavailable. Select the output to copy it.');
$('clear-output').onclick=()=>{if(['running','input'].includes(phase)){toast('Stop the program before clearing its output.');return;}output.textContent='';clearDiagnostics();$('run-duration').textContent='';$('result-dot').className='result-dot';emptyOutput();};
$('clear-history').onclick=()=>{runs=[];writeStore('runs',runs);renderHistory();toast('Run history cleared on this device.');};
$('go-to-error').onclick=()=>{if(errorLine){editor.setCursor?.({line:errorLine-1,ch:0});editor.scrollIntoView?.({line:errorLine-1,ch:0},60);editor.focus();}};
$('font-minus').onclick=()=>{fontSize=Math.max(12,fontSize-1);applyPreferences();savePreferences();};
$('font-plus').onclick=()=>{fontSize=Math.min(20,fontSize+1);applyPreferences();savePreferences();};
$('line-wrap').onchange=event=>{wrapLines=event.target.checked;applyPreferences();savePreferences();};
$('guide-toggle').onclick=()=>{guideVisible=!guideVisible;applyPreferences();savePreferences();};
$('sidebar-toggle').onclick=()=> $('learning-sidebar').classList.contains('open')?closeSidebar():openSidebar();
$('sidebar-close').onclick=closeSidebar;$('sidebar-scrim').onclick=closeSidebar;
for(const [a,b,p,q] of [['output-tab','history-tab','output-panel','history-panel'],['lesson-tab','reference-tab','lesson-panel','reference-panel']]){
    $(a).onclick=()=>selectTab(a,b,p,q,true);$(b).onclick=()=>selectTab(a,b,p,q,false);
    for(const id of [a,b])$(id).addEventListener('keydown',event=>{if(['ArrowLeft','ArrowRight','Home','End'].includes(event.key)){event.preventDefault();const target=event.key==='Home'?a:event.key==='End'?b:id===a?b:a;$(target).click();$(target).focus();}});
}
document.querySelectorAll('dialog [data-close]').forEach(button=>button.onclick=()=>button.closest('dialog').close());
document.querySelectorAll('dialog:not(#confirm-dialog)').forEach(dialog=>dialog.addEventListener('click',event=>{if(event.target===dialog){const rect=dialog.getBoundingClientRect();if(event.clientX<rect.left||event.clientX>rect.right||event.clientY<rect.top||event.clientY>rect.bottom)dialog.close();}}));
document.addEventListener('keydown',event=>{
    if(event.key==='Escape'){hideTooltip();closeSidebar();}
    if((event.ctrlKey||event.metaKey)&&event.key==='Enter'&&!document.querySelector('dialog[open]')){event.preventDefault();event.shiftKey?stopRun():runButton.click();}
    if((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==='k'){event.preventDefault();if(!document.querySelector('dialog[open]'))openPalette();}
    if((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==='s'){event.preventDefault();downloadProgram();}
    if(event.key==='?'&&!event.target.closest('input,textarea,.CodeMirror')&&!document.querySelector('dialog[open]'))$('help-dialog').showModal();
});
document.addEventListener('mouseover',event=>{const target=event.target.closest('[data-tooltip]');if(target)showTooltip(target.dataset.tooltip,target.getBoundingClientRect(),target);});
document.addEventListener('mouseout',event=>{if(event.target.closest('[data-tooltip]'))hideTooltip();});
document.addEventListener('focusin',event=>{const target=event.target.closest('[data-tooltip]');if(target)showTooltip(target.dataset.tooltip,target.getBoundingClientRect(),target);});
document.addEventListener('focusout',hideTooltip);
window.addEventListener('scroll',hideTooltip,true);
window.addEventListener('pagehide',persistDraft);
if(editor.on){
    editor.on('change',onEditorChange);editor.on('cursorActivity',updateCursor);
    editor.getWrapperElement().addEventListener('mousemove',event=>{
        const pos=editor.coordsChar({left:event.clientX,top:event.clientY});const token=editor.getTokenAt(pos);const word=REFERENCE.find(r=>r.word===token.string);
        if(word)showTooltip(`${word.word}: ${word.meaning}`,{left:event.clientX+5,top:event.clientY,bottom:event.clientY+14});else hideTooltip();
    });
    editor.getWrapperElement().addEventListener('mouseleave',hideTooltip);
}else{
    textarea.addEventListener('input',onEditorChange);textarea.addEventListener('click',updateCursor);textarea.addEventListener('keyup',updateCursor);
    textarea.addEventListener('keydown',event=>{if(event.key==='Tab'){event.preventDefault();textarea.setRangeText('    ',textarea.selectionStart,textarea.selectionEnd,'end');onEditorChange();}});
}
const shared=restoreSharedCode();
if(shared){
    if(validSource(saved?.source))writeStore('previous',saved);
    currentLesson=LESSONS.some(l=>l.id===shared.lessonId)?shared.lessonId:null;
    baselineSource=shared.source;editor.setValue(shared.source);$('filename').value=fileName(shared.filename);
    toast('Shared code loaded. Your previous draft is kept in editor settings.');
}else if(validSource(saved?.source)){
    currentLesson=LESSONS.some(l=>l.id===saved.lessonId)?saved.lessonId:null;
    editor.setValue(saved.source);$('filename').value=fileName(saved.filename);
}else{
    baselineSource=LESSONS[0].source;editor.setValue(baselineSource);$('filename').value=LESSONS[0].filename;
}
renderLessons();renderReference();renderHistory();applyPreferences();updateCursor();persistDraft();startWorker();
if(new URLSearchParams(location.search).get('examples')==='1')openExamples();
