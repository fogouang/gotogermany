/**
 * pcm-capture-processor.js
 * ==========================
 * AudioWorkletProcessor — converts the mic's Float32 samples to
 * PCM16 and posts each block back to the main thread. Loaded via
 * `audioContext.audioWorklet.addModule('/pcm-capture-processor.js')`
 * (must be served as a static file — Nuxt: drop it in `public/`).
 *
 * NOT unit-testable outside a real browser audio thread — no
 * automated coverage for this file, same caveat as live_client.py's
 * network calls on the backend.
 */

class PcmCaptureProcessor extends AudioWorkletProcessor {
  process(inputs) {
    const input = inputs[0];
    const channel = input && input[0];
    if (!channel || channel.length === 0) {
      return true; // keep the processor alive even on silent/empty blocks
    }

    const pcm16 = new Int16Array(channel.length);
    for (let i = 0; i < channel.length; i++) {
      const clamped = Math.max(-1, Math.min(1, channel[i]));
      pcm16[i] = clamped < 0 ? clamped * 0x8000 : clamped * 0x7fff;
    }

    this.port.postMessage(pcm16.buffer, [pcm16.buffer]);
    return true;
  }
}

registerProcessor('pcm-capture-processor', PcmCaptureProcessor);