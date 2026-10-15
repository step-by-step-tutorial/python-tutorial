from dataclasses import dataclass


@dataclass(frozen=True)
class DetectionTaskModel:
    name: str
    labels: tuple[str, ...]
    score_threshold: float = 0.5
