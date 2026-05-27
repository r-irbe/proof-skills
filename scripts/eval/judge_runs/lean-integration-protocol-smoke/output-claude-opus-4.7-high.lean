Contract (TypeScript-shaped, transport-agnostic):

```ts
interface MeasurementEvent {
  id: string;              // ULID, monotonic
  source: "MeasureBridge";
  schemaVersion: 1;
  emittedAt: string;       // ISO-8601 UTC
  sampleAt: string;        // ISO-8601 UTC of measurement
  metric: string;          // dotted name, e.g. "sensor.temp"
  unit: string;            // UCUM symbol, e.g. "Cel", "m/s"
  value: number | null;    // null ⇒ missing; never NaN
  quality: "ok" | "stale" | "estimated" | "error";
  tags?: Record<string, string>;
  traceId?: string;
}

interface InformationSink {
  ingest(batch: readonly MeasurementEvent[]): Promise<IngestAck>;
  health(): Promise<{ ready: boolean; lastAckId?: string }>;
}

interface IngestAck { acceptedIds: string[]; rejected: { id: string; reason: string }[]; }
```

Semantics: push-based, at-least-once delivery; `Information` MUST be idempotent on `id`. Ordering guaranteed only per `metric+tags` key. Batches ≤ 500 events or 256 KiB, whichever first. Backpressure via rejected promise or HTTP 429/503 → `MeasureBridge` retries with exponential backoff (base 250 ms, max 30 s, jitter ±20 %). Schema evolution: additive only within `schemaVersion`; breaking changes bump the integer. Errors surfaced as `quality:"error"` with `tags.errorCode`, never by omission.