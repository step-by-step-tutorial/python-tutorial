from dataclasses import dataclass


@dataclass(frozen=True)
class DetectionModel:
    label: str
    score: float
    # x_min, y_min, x_max, y_max in pixels
    box: tuple[float, float, float, float]

    def to_dict(self) -> dict[str, str | float]:
        x_min, y_min, x_max, y_max = self.box
        return {
            "label": self.label,
            "score": round(self.score, 4),
            "x_min": round(x_min, 1),
            "y_min": round(y_min, 1),
            "x_max": round(x_max, 1),
            "y_max": round(y_max, 1),
        }
