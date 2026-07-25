from __future__ import annotations


class DriveGeometryGuard:
    def __init__(self, lidar_range_m: float = 0.5, timeout_on_retreat_s: float = 10.0):
        self.lidar_range_m = lidar_range_m
        self.timeout_on_retreat_s = timeout_on_retreat_s
        self._retreat_start: float | None = None
        self._wounded_dignity_return: bool = False

    def check_retreat_safe(self, obstacle_distance_m: float | None) -> bool:
        if obstacle_distance_m is None:
            return True
        return obstacle_distance_m > self.lidar_range_m

    def is_retreat_timed_out(self, current_time_s: float) -> tuple[bool, bool]:
        if self._retreat_start is None:
            return False, False
        elapsed = current_time_s - self._retreat_start
        if elapsed >= self.timeout_on_retreat_s:
            self._wounded_dignity_return = True
            return True, True
        return False, False

    def begin_retreat(self, current_time_s: float) -> None:
        self._retreat_start = current_time_s
        self._wounded_dignity_return = False

    def end_retreat(self) -> None:
        self._retreat_start = None
        self._wounded_dignity_return = True

    def reset(self) -> None:
        self._retreat_start = None
        self._wounded_dignity_return = False

    @property
    def should_return(self) -> bool:
        return self._wounded_dignity_return
