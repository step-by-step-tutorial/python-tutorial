from dataclasses import dataclass

ALL_LABELS = "all"


@dataclass(frozen=True)
class EvaluationModel:
    label: str
    images: int
    objects: int
    # COCO average precision over IoU 0.50:0.95, average precision at IoU 0.50 and average recall
    ap: float
    ap50: float
    ar: float

    def to_dict(self) -> dict[str, str | int | float]:
        return {
            "label": self.label,
            "images": self.images,
            "objects": self.objects,
            "ap": round(self.ap, 4),
            "ap50": round(self.ap50, 4),
            "ar": round(self.ar, 4),
        }
