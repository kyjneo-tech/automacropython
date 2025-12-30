from dataclasses import dataclass

@dataclass
class ScreenInfo:
    id: int
    x: int      # 논리적 시작점 (Logical X)
    y: int      # 논리적 시작점 (Logical Y)
    width: int  # 논리적 너비
    height: int # 논리적 높이
    scale_factor: float = 1.0 # 배율 (Retina = 2.0)

    @property
    def physical_width(self) -> int:
        return int(self.width * self.scale_factor)

    @property
    def physical_height(self) -> int:
        return int(self.height * self.scale_factor)
