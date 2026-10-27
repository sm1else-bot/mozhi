/* Pyodide is confined to a terminable worker, never the browser UI thread. */
let engine;
let runId = null;
let inputRequest = null;
let inputSequence = 0;
let pendingOutput = '';
let outputSize = 0;
let lastFlush = 0;
const OUTPUT_LIMIT = 65536;

function flushOutput() {
    if (pendingOutput) {
        self.postMessage({type: 'output', runId, text: pendingOutput});
        pendingOutput = '';
        lastFlush = performance.now();
    }
}

self.appendMozhiOutput = text => {
    text = String(text);
    const remaining = OUTPUT_LIMIT - outputSize;
    if (remaining <= 0) return;
    pendingOutput += text.slice(0, remaining);
    outputSize += Math.min(text.length, remaining);
    if (outputSize >= OUTPUT_LIMIT) pendingOutput += '\n[Output truncated at 65,536 characters.]\n';
    if (pendingOutput.length >= 4096 || outputSize >= OUTPUT_LIMIT || lastFlush === 0 || performance.now() - lastFlush >= 16) flushOutput();
};

self.getMozhiInput = prompt => {
    flushOutput();
    if (inputRequest) return Promise.reject(new Error('Input is already pending.'));
    return new Promise(resolve => {
        const id = ++inputSequence;
        inputRequest = {id, resolve};
        self.postMessage({type: 'input', runId, id, prompt: String(prompt)});
    });
};

self.onmessage = async event => {
    const message = event.data;
    if (message.type === 'input') {
        if (message.runId === runId && inputRequest && message.id === inputRequest.id) {
            const {resolve} = inputRequest;
            inputRequest = null;
            resolve(message.value);
        }
        return;
    }
    if (message.type === 'initialize') {
        try {
            importScripts('https://cdn.jsdelivr.net/pyodide/v0.23.4/full/pyodide.js');
            engine = await loadPyodide();
            const response = await fetch('./runtime.py');
            if (!response.ok) throw new Error(`Runtime download failed (${response.status}).`);
            await engine.runPythonAsync(await response.text());
            self.postMessage({type: 'ready'});
        } catch (error) {
            self.postMessage({type: 'load-error', error: String(error.message || error)});
        }
        return;
    }
    if (message.type !== 'run' || !engine || runId !== null) return;
    runId = message.runId;
    pendingOutput = '';
    outputSize = 0;
    lastFlush = 0;
    try {
        engine.globals.set('user_code', message.source);
        const result = await engine.runPythonAsync('await execute_mozhi(user_code)');
        const error = result.get('error');
        result.destroy();
        flushOutput();
        self.postMessage({type: 'done', runId, error});
    } catch (error) {
        flushOutput();
        self.postMessage({type: 'done', runId, error: String(error.message || error)});
    } finally {
        inputRequest = null;
        runId = null;
    }
};
