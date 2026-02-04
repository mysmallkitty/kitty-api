from __future__ import annotations
from typing import TYPE_CHECKING
import math

if TYPE_CHECKING:
    from app.records.models import Record
    from app.maps.models import Map


FLOOR_RATIO = 0.30  # 클리어 최소치 30%

LENGTH_SOFTCAP = 12.0
LENGTH_GAMMA = 0.75  # 0.6~1.0 사이로 조절 (낮을수록 완만)

DEATH_SOFTCAP_RATIO = 1.0  # deaths/death_meter가 1일 때 기준점
DEATH_POWER = 1.15  # 데스 민감도
FLAWLESS_GAP = 0.10  # 퍼펙트런시 더 높게

SECONDS_PER_EXPECTED_DEATH = 1800  # 만약 clear_time이 프레임 단위면 1800.0으로
TIME_WEIGHT = 0.3  # 시간 가중치
TIME_TANH_K = 0.9  # 시간 민감도 조절 상수


def _clamp(x: float, lo: float, hi: float) -> float:
    return lo if x < lo else hi if x > hi else x


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def _max_pp_from_rating(rating: float) -> float:
    anchors = [
        (0.0, 5.0),
        (1.0, 15.0),
        (2.0, 42.0),
        (3.0, 75.0),
        (4.0, 112.0),
        (5.0, 165.0),
        (6.0, 310.0),
        (7.0, 520.0),
        (8.0, 720.0),
        (9.0, 920.0),
        (10.0, 1250.0),
    ]

    r = _clamp(float(rating), anchors[0][0], anchors[-1][0])

    for i in range(len(anchors) - 1):
        r0, p0 = anchors[i]
        r1, p1 = anchors[i + 1]
        if r0 <= r <= r1:
            t = 0.0 if r1 == r0 else (r - r0) / (r1 - r0)
            return _lerp(p0, p1, t)

    return anchors[-1][1]


def _length_factor(death_meter: int) -> float:
    dm = max(float(death_meter), 0.0)
    if dm <= 0.0:
        return 0.0
    return (dm / (dm + LENGTH_SOFTCAP)) ** LENGTH_GAMMA


def _death_score(deaths: int, death_meter: int) -> float:
    if death_meter <= 0:
        return 0.0

    x = float(deaths) / float(death_meter)
    x = max(x, 0.0)

    c = DEATH_SOFTCAP_RATIO
    base = 1.0 / ((1.0 + (x / c)) ** DEATH_POWER)
    base = _clamp(base, 0.0, 1.0)

    if deaths == 0:
        return 1.0
    return base * (1.0 - FLAWLESS_GAP)


def _time_factor(clear_time: int, expected_time: float) -> float:
    if clear_time <= 0 or expected_time <= 0.0:
        return 1.0 - (TIME_WEIGHT * 0.5)

    ratio = expected_time / float(clear_time)
    # Keep a low-end clamp to avoid extreme penalties, but allow faster clears
    # to keep improving PP (no hard upper cap).
    ratio = max(ratio, 0.25)

    s = 0.5 + 0.5 * math.tanh(TIME_TANH_K * math.log(ratio))  # 0..1
    return (1.0 - TIME_WEIGHT) + (TIME_WEIGHT * s)


def calculate_pp(_map: Map, _record: Record) -> float:
    # Treat non-positive death_meter as 1 to keep PP calculable and avoid div-by-zero.
    dm = max(int(_map.death_meter), 1)

    base_max_pp = _max_pp_from_rating(_map.rating)
    max_pp = base_max_pp * _length_factor(dm)
    expected_time = float(dm) * SECONDS_PER_EXPECTED_DEATH

    death_component = _death_score(_record.deaths, dm)
    time_component = _time_factor(_record.clear_time, expected_time)

    performance = _clamp(death_component * time_component, 0.0, 1.0)

    pp = max_pp * (FLOOR_RATIO + (1.0 - FLOOR_RATIO) * performance)
    return pp
