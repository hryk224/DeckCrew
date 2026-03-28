"use client";

import { useEffect, useRef, useState } from "react";

const WS_URL =
  (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000")
    .replace(/^http/, "ws") + "/session/audio";

// Minimum bytes buffered before starting playback.
const MIN_BUFFER_BYTES = 48000 * 2 * 2 * 2; // ~2s at 48kHz/16bit/stereo

interface AudioState {
  connected: boolean;
  playing: boolean;
}

interface UseAudioOptions {
  enabled: boolean;
  volume: number; // 0-100
  /** Pre-created AudioContext (should be created on user gesture). */
  audioContext: AudioContext | null;
}

export interface UseAudioReturn {
  state: AudioState;
}

/**
 * Stream audio from backend WebSocket and play via Web Audio API.
 *
 * - Connects to /session/audio when enabled
 * - Uses the externally provided AudioContext (created on user gesture
 *   to satisfy browser autoplay policy)
 * - Buffers initial chunks before starting playback
 * - GainNode controls volume (0-1)
 *
 * NOTE: Single-client design. Multiple browser tabs sharing the same
 * backend will split audio chunks between them.
 */
export function useAudio(options: UseAudioOptions): UseAudioReturn {
  const { enabled, volume, audioContext } = options;
  const [state, setState] = useState<AudioState>({
    connected: false,
    playing: false,
  });

  const gainRef = useRef<GainNode | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const bufferRef = useRef<ArrayBuffer[]>([]);
  const playingRef = useRef(false);
  const sampleRateRef = useRef(48000);
  const channelsRef = useRef(2);
  const nextTimeRef = useRef(0);

  // Update volume without reconnecting
  useEffect(() => {
    if (gainRef.current) {
      gainRef.current.gain.value = volume / 100;
    }
  }, [volume]);

  // Connect WebSocket and set up audio pipeline
  useEffect(() => {
    if (!enabled || !audioContext) return;

    const ctx = audioContext;
    const gain = ctx.createGain();
    gain.gain.value = volume / 100;
    gain.connect(ctx.destination);
    gainRef.current = gain;
    nextTimeRef.current = 0;

    function scheduleBuffer(data: ArrayBuffer) {
      if (data.byteLength === 0) return; // keepalive ping
      if (!gainRef.current) return;

      const sampleRate = sampleRateRef.current;
      const channels = channelsRef.current;
      const bytesPerSample = 2; // 16-bit
      const frameCount = data.byteLength / (bytesPerSample * channels);
      if (frameCount <= 0) return;

      const audioBuffer = ctx.createBuffer(channels, frameCount, sampleRate);
      const view = new DataView(data);

      for (let ch = 0; ch < channels; ch++) {
        const channelData = audioBuffer.getChannelData(ch);
        for (let i = 0; i < frameCount; i++) {
          const offset = (i * channels + ch) * bytesPerSample;
          if (offset + 1 < data.byteLength) {
            channelData[i] = view.getInt16(offset, true) / 32768;
          }
        }
      }

      const source = ctx.createBufferSource();
      source.buffer = audioBuffer;
      source.connect(gainRef.current);

      const now = ctx.currentTime;
      if (nextTimeRef.current < now) {
        nextTimeRef.current = now;
      }
      source.start(nextTimeRef.current);
      nextTimeRef.current += audioBuffer.duration;
    }

    const ws = new WebSocket(WS_URL);
    ws.binaryType = "arraybuffer";
    wsRef.current = ws;

    let firstMessage = true;

    ws.onopen = () => {
      setState((s) => ({ ...s, connected: true }));
    };

    ws.onmessage = (event: MessageEvent) => {
      // First text message is MIME type metadata
      if (firstMessage && typeof event.data === "string") {
        firstMessage = false;
        const mime = event.data;
        const rateMatch = mime.match(/rate=(\d+)/);
        const chMatch = mime.match(/channels=(\d+)/);
        if (rateMatch) sampleRateRef.current = parseInt(rateMatch[1], 10);
        if (chMatch) channelsRef.current = parseInt(chMatch[1], 10);
        return;
      }

      if (!(event.data instanceof ArrayBuffer)) return;
      const data = event.data as ArrayBuffer;

      if (!playingRef.current) {
        bufferRef.current.push(data);
        const totalBytes = bufferRef.current.reduce((s, b) => s + b.byteLength, 0);
        if (totalBytes >= MIN_BUFFER_BYTES) {
          for (const buf of bufferRef.current) {
            scheduleBuffer(buf);
          }
          bufferRef.current = [];
          playingRef.current = true;
          setState((s) => ({ ...s, playing: true }));
        }
      } else {
        scheduleBuffer(data);
      }
    };

    ws.onclose = (event: CloseEvent) => {
      if (event.code === 4000) {
        // Mock mode — no audio backend, clean up silently
      }
      setState({ connected: false, playing: false });
      playingRef.current = false;
    };

    ws.onerror = () => {
      setState({ connected: false, playing: false });
      playingRef.current = false;
    };

    return () => {
      ws.close();
      wsRef.current = null;
      if (gainRef.current) {
        gainRef.current.disconnect();
        gainRef.current = null;
      }
      bufferRef.current = [];
      playingRef.current = false;
      setState({ connected: false, playing: false });
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps -- volume handled via gainRef
  }, [enabled, audioContext]);

  return { state };
}
