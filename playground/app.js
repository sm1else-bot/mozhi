const textarea = document.getElementById('code-editor');
const editor = typeof CodeMirror === 'undefined' ? {
    getValue: () => textarea.value,
    setValue: value => { textarea.value = value; },
} : CodeMirror.fromTextArea(textarea, {
    mode: 'text', theme: 'dracula', lineNumbers: true, indentUnit: 4,
});
editor.setValue(`name = "Nanba" vechukko
greeting = "Vanakkam, " kooda name vechukko
greeting sollu

numbers = [10, 20, 30] vechukko
99 ullapodu numbers
"Array: " kooda numbers sollu

i = 0 vechukko
i < 3 varaikum:
    i = i + 1 vechukko
    i sollu
mudivu
`);

const runButton = document.getElementById('run-btn');
const stopButton = document.getElementById('stop-btn');
const retryButton = document.getElementById('retry-btn');
const output = document.getElementById('output');
const status = document.getElementById('status');
const inputForm = document.getElementById('input-container');
const input = document.getElementById('mozhi-input');
const limit = document.getElementById('time-limit');
let worker = null;
let phase = 'loading';
let runId = 0;
let pendingInput = null;
let timer = null;
let startupTimer = null;
let remaining = 0;
let resumedAt = 0;

function setPhase(next, text) {
    phase = next;
    status.textContent = text;
    runButton.disabled = next !== 'ready';
    stopButton.disabled = !['running', 'input'].includes(next);
    limit.disabled = ['running', 'input'].includes(next);
    retryButton.hidden = next !== 'error';
    if (next !== 'input') {
        inputForm.hidden = true;
        pendingInput = null;
        input.value = '';
    }
}

function pauseClock() {
    if (timer !== null) {
        clearTimeout(timer);
        timer = null;
        remaining = Math.max(0, remaining - (performance.now() - resumedAt));
    }
}

function resumeClock() {
    resumedAt = performance.now();
    timer = setTimeout(() => stopRun('Execution time limit reached.'), remaining);
}

function engineError(text) {
    pauseClock();
    clearTimeout(startupTimer);
    if (worker) worker.terminate();
    worker = null;
    output.textContent += `\nError: ${text}\n`;
    setPhase('error', 'Engine unavailable. Use Retry engine.');
}

function startWorker() {
    pauseClock();
    clearTimeout(startupTimer);
    if (worker) worker.terminate();
    setPhase('loading', 'Loading engine…');
    try {
        const activeWorker = new Worker('./worker.js');
        worker = activeWorker;
        startupTimer = setTimeout(() => {
            if (worker === activeWorker) engineError('Engine loading timed out. Check your network and retry.');
        }, 60000);
        activeWorker.onerror = event => {
            if (worker === activeWorker) engineError(event.message || 'Worker failed to load.');
        };
        activeWorker.onmessage = event => {
            if (worker !== activeWorker) return;
            const message = event.data;
            if (message.type === 'ready') {
                clearTimeout(startupTimer);
                setPhase('ready', 'Ready');
            } else if (message.type === 'load-error') {
                engineError(message.error);
            } else if (message.runId === runId) {
                if (message.type === 'output') {
                    output.textContent += message.text;
                    output.scrollTop = output.scrollHeight;
                } else if (message.type === 'input' && phase === 'running') {
                    pauseClock();
                    pendingInput = message.id;
                    setPhase('input', 'Waiting for input (execution timer paused)');
                    input.placeholder = message.prompt || 'Mozhi-la type pannu...';
                    inputForm.hidden = false;
                    input.focus();
                } else if (message.type === 'done') {
                    pauseClock();
                    if (message.error) output.textContent += `\nError: ${message.error}\n`;
                    setPhase('ready', message.error ? 'Finished with an error' : 'Finished');
                }
            }
        };
        activeWorker.postMessage({type: 'initialize'});
    } catch (error) {
        engineError(error.message);
    }
}

function stopRun(reason = 'Stopped by user.') {
    if (!['running', 'input'].includes(phase)) return;
    pauseClock();
    if (worker) worker.terminate();
    worker = null;
    output.textContent += `\n[Mozhi] ${reason}\n`;
    startWorker();
}

runButton.addEventListener('click', () => {
    if (phase !== 'ready') return;
    const seconds = Number(limit.value);
    if (!Number.isFinite(seconds) || seconds < 0.1 || seconds > 3600) {
        status.textContent = 'Choose an execution limit between 0.1 and 3600 seconds.';
        return;
    }
    output.textContent = '';
    remaining = seconds * 1000;
    runId += 1;
    setPhase('running', 'Running');
    resumeClock();
    worker.postMessage({type: 'run', runId, source: editor.getValue()});
});

inputForm.addEventListener('submit', event => {
    event.preventDefault();
    if (phase !== 'input' || pendingInput === null) return;
    const value = input.value;
    const id = pendingInput;
    setPhase('running', 'Running');
    resumeClock();
    worker.postMessage({type: 'input', runId, id, value});
});
stopButton.addEventListener('click', () => stopRun());
retryButton.addEventListener('click', startWorker);
startWorker();
