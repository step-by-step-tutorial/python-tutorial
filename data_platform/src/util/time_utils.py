import time


def elapsed_milliseconds(started_at: float) -> int:
    return int((time.perf_counter() - started_at) * 1000)
