#demo script

import torch
from diffusers.utils import export_to_video
from vid.pipelines.cogvideox import CogVideoX

def main():
    prompt = "A panda, dressed in a small, red jacket and a tiny hat, sits on a wooden stool in a serene bamboo forest. The panda's fluffy paws strum a miniature acoustic guitar, producing soft, melodic tunes. Nearby, a few other pandas gather, watching curiously and some clapping in rhythm. Sunlight filters through the tall bamboo, casting a gentle glow on the scene. The panda's face is expressive, showing concentration and joy as it plays. The background includes a small, flowing stream and vibrant green foliage, enhancing the peaceful and magical atmosphere of this unique musical performance."

   
    generator = CogVideoX()
    
    result = generator.generate(
        prompt=prompt,
        fps=8,
        num_videos_per_prompt=1,
        num_inference_steps=50,
        num_frames=36,
        guidance_scale=4.5,
        generator=torch.Generator(device="cuda").manual_seed(42)
    )
    
    export_to_video(result.frames, "output.mp4", fps=result.fps)

if __name__ == "__main__":
    main()
