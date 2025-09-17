from typing import List
from dataclasses import dataclass

@dataclass
class GenResult:
    frames: List 
    fps: int

class VideoGenerator:
    def generate(self, prompt: str, **kw) -> GenResult:
        raise NotImplementedError
