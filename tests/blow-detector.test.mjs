import assert from "node:assert/strict";
import test from "node:test";
import { detectCandleBlow } from "../app/blow-detector.ts";

function microphone() {
  let nextFrame;
  let now = 0;
  let level = 128;
  let blows = 0;
  let timeouts = 0;
  const analyser = {
    fftSize: 2048,
    getByteTimeDomainData(samples) {
      // Like Web Audio, only the analyser's current fftSize bytes are written.
      samples.fill(level, 0, this.fftSize);
    },
  };
  const stop = detectCandleBlow(analyser, () => blows++, () => timeouts++, {
    request(callback) { nextFrame = callback; return 1; },
    cancel() { nextFrame = undefined; },
    now: () => now,
  });
  return {
    stop,
    frame(newLevel = 128, elapsed = 0) {
      level = newLevel;
      now = elapsed;
      const callback = nextFrame;
      nextFrame = undefined;
      callback?.();
    },
    get state() { return { blows, timeouts, scheduled: Boolean(nextFrame) }; },
  };
}

test("silence and quiet background audio do not blow out the candle", () => {
  const mic = microphone();
  mic.frame();
  mic.frame(138, 1000);
  assert.deepEqual(mic.state, { blows: 0, timeouts: 0, scheduled: true });
  mic.stop();
});

test("a blow finishes once and stops sampling", () => {
  const mic = microphone();
  mic.frame(160);
  mic.frame(160, 100);
  assert.deepEqual(mic.state, { blows: 1, timeouts: 0, scheduled: false });
});

test("silence times out after twelve seconds with no later detection", () => {
  const mic = microphone();
  mic.frame(128, 12000);
  mic.frame(160, 13000);
  assert.deepEqual(mic.state, { blows: 0, timeouts: 1, scheduled: false });
});

test("manual candle completion or navigation cancels the pending detector", () => {
  const mic = microphone();
  mic.stop();
  mic.frame(160, 1000);
  assert.deepEqual(mic.state, { blows: 0, timeouts: 0, scheduled: false });
});
