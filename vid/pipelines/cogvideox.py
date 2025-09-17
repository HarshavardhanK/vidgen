import torch
from diffusers import CogVideoXPipeline
from ..base import VideoGenerator, GenResult

class CogVideoX(VideoGenerator):
    
    def __init__(self, model_id: str = "THUDM/CogVideoX-2b"):
        
        self.pipe = CogVideoXPipeline.from_pretrained(
            model_id, torch_dtype=torch.bfloat16
        ).to("cuda")
        
        self.pipe.vae.enable_slicing()
        self.pipe.vae.enable_tiling()

    @torch.inference_mode()
    
    def generate(self, prompt: str, fps: int = 24, **kw) -> GenResult:
        
        out = self.pipe(
            
            prompt=prompt,
            num_videos_per_prompt=kw.get('num_videos_per_prompt', 1),
            num_inference_steps=kw.get('num_inference_steps', 50),
            num_frames=kw.get('num_frames', 36),
            guidance_scale=kw.get('guidance_scale', 4.5),
            generator=kw.get('generator', None)
            
        )
        
        frames = out.frames[0]
        
        return GenResult(frames=frames, fps=fps)