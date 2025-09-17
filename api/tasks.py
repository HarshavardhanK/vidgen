#Video generation tasks

import os
from diffusers.utils import export_to_video
from vid.runtime import get_generator

def generate_video(self, prompt: str, fps: int = 24) -> str:
    
    gen = get_generator() #loads model once (GPU)
    
    self.update_state(state="STARTED", meta={"progress": 0.1})
    
    res = gen.generate(prompt, fps=fps) 
    
    output_dir = "/app/output"
    os.makedirs(output_dir, exist_ok=True)
    
    out = f"{output_dir}/{self.request.id}.mp4"
    export_to_video(res.frames, out, fps=res.fps)
    
    return out