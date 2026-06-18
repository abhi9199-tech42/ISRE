"""Load testing benchmark for ISRE pipeline."""

import time
import statistics
from isre.pipeline import ISREPipeline


SAMPLES = [
    "apple",
    "run quickly",
    "stay slow",
    "fly to the moon",
    "run fast but stay slow",
    "apple orange banana grape fruit",
    "quickly slowly walk fast stay still run jump",
    "I want to eat a healthy apple and run quickly but stay slow",
]

WARMUP = 3
ITERATIONS = 100


def benchmark():
    pipeline = ISREPipeline()

    # Warmup
    for _ in range(WARMUP):
        for s in SAMPLES:
            pipeline.process(s, "text")

    # Measure
    latencies = []
    for i in range(ITERATIONS):
        for s in SAMPLES:
            start = time.perf_counter()
            pipeline.process(s, "text")
            elapsed = time.perf_counter() - start
            latencies.append(elapsed)

    avg = statistics.mean(latencies)
    med = statistics.median(latencies)
    p99 = sorted(latencies)[int(len(latencies) * 0.99)]
    rps = len(latencies) / sum(latencies)

    print(f"Benchmark Results ({ITERATIONS * len(SAMPLES)} requests):")
    print(f"  Average latency: {avg*1000:.1f}ms")
    print(f"  Median latency:  {med*1000:.1f}ms")
    print(f"  P99 latency:     {p99*1000:.1f}ms")
    print(f"  Throughput:      {rps:.0f} req/s")


if __name__ == "__main__":
    benchmark()
