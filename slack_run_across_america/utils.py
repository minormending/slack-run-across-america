from datetime import timedelta
from typing import List


def pretty_timedelta(duration: timedelta) -> str:
    parts: List[str] = []
    if duration.days:
        parts.append(f"{duration.days} days")

    hours: int = int(float(duration.seconds) / 3600) % 24
    if hours:
        parts.append(f"{hours} hours")

    minutes: int = int(float(duration.seconds) / 60) % 60
    if minutes:
        parts.append(f"{minutes} mins")

    return " ".join(parts)
