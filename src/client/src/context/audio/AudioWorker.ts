// Define the structure of messages sent to the worker
interface WorkerMessage {
    type: "processAudio" | "setConfig" | "finalizeBuffer";
    data?: Float32Array | { amplitudeThreshold: number };
}

let amplitudeThreshold = 0.02; // Lowered threshold for better silence detection
let buffer = new Float32Array();
let lastSpeechTime = 0;
const silenceThreshold = 1000; // 1 second of silence before sending buffer
let isSpeakingState = false;

const ctx: Worker = self as any;

ctx.onmessage = (event: MessageEvent<WorkerMessage>) => {
    switch (event.data.type) {
        case "processAudio":
            processAudioChunk(event.data.data as Float32Array);
            break;
        case "setConfig":
            const config = event.data.data as { amplitudeThreshold: number };
            amplitudeThreshold = config.amplitudeThreshold;
            break;
        case "finalizeBuffer":
            finalizeBuffer();
            break;
    }
};

function processAudioChunk(input: Float32Array) {
    const currentTime = Date.now();

    // Append input to buffer
    const newBuffer = new Float32Array(buffer.length + input.length);
    newBuffer.set(buffer);
    newBuffer.set(input, buffer.length);
    buffer = newBuffer;

    // Detect speech in the new input
    let isSpeech = false;
    for (let i = 0; i < input.length; i++) {
        if (Math.abs(input[i]) > amplitudeThreshold) {
            isSpeech = true;
            lastSpeechTime = currentTime;
            break;
        }
    }

    // Update isSpeaking state and send to main thread only if it changes
    if (isSpeech && !isSpeakingState) {
        isSpeakingState = true;
        ctx.postMessage({ isSpeaking: true });
    } else if (!isSpeech && isSpeakingState) {
        isSpeakingState = false;
        ctx.postMessage({ isSpeaking: false });
    }

    // Check if we've had silence for more than the threshold
    if (!isSpeech && currentTime - lastSpeechTime > silenceThreshold) {
        if (!isBufferSilent(buffer)) {
            ctx.postMessage({ type: "speechBuffer", buffer: buffer.slice() });
        } else {
            ctx.postMessage({ type: "silentBuffer" });
        }
        buffer = new Float32Array();
        lastSpeechTime = currentTime;
    }
}

function finalizeBuffer() {
    if (!isBufferSilent(buffer)) {
        ctx.postMessage({ type: "finalBuffer", buffer });
    } else {
        ctx.postMessage({ type: "silentBuffer" });
    }
    buffer = new Float32Array();
    lastSpeechTime = 0;
    isSpeakingState = false;
    ctx.postMessage({ isSpeaking: false });
}

function isBufferSilent(buffer: Float32Array): boolean {
    for (let i = 0; i < buffer.length; i++) {
        if (Math.abs(buffer[i]) > amplitudeThreshold) {
            return false;
        }
    }
    return true;
}
