type FrameClock = {
  request: (callback: FrameRequestCallback) => number;
  cancel: (handle: number) => void;
  now: () => number;
};

// Allocate after setting fftSize so unused zero bytes cannot look like loud audio.
export function detectCandleBlow(
  analyser: AnalyserNode,
  onBlow: () => void,
  onTimeout: () => void,
  clock: FrameClock = {
    request: (callback) => requestAnimationFrame(callback),
    cancel: (handle) => cancelAnimationFrame(handle),
    now: () => performance.now(),
  },
) {
  analyser.fftSize = 512;
  const samples = new Uint8Array(analyser.fftSize);
  const startedAt = clock.now();
  let stopped = false;
  let frame: number;

  const stop = () => {
    stopped = true;
    clock.cancel(frame);
  };

  const detect = () => {
    if (stopped) return;
    analyser.getByteTimeDomainData(samples);
    const volume = samples.reduce((total, sample) => total + Math.abs(sample - 128), 0) / samples.length;
    if (volume > 18) {
      stop();
      onBlow();
    } else if (clock.now() - startedAt >= 12000) {
      stop();
      onTimeout();
    } else {
      frame = clock.request(detect);
    }
  };

  frame = clock.request(detect);
  return stop;
}
