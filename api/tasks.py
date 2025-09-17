#Video generation tasks

import os
from sqlalchemy import text

from diffusers.utils import export_to_video

from vid.runtime import get_generator

from .db import get_engine


def _db_exec(stmt: str, params: dict) -> None:
    #helper for task DB writes
    with get_engine().begin() as conn:
        conn.execute(text(stmt), params)


def generate_video(self, prompt: str, fps: int = 24) -> str:
    
    task_id = self.request.id
    
    _db_exec(
        "SELECT update_video_generation_status(:task_id, :status)",
        {"task_id": task_id, "status": "processing"},
    )
    
    gen = get_generator() #loads model once (GPU)
    
    self.update_state(state="STARTED", meta={"progress": 0.1})
    
    try:
        res = gen.generate(prompt, fps=fps)
        
        output_dir = "/app/output"
        os.makedirs(output_dir, exist_ok=True)
        
        out = f"{output_dir}/{task_id}.mp4"
        export_to_video(res.frames, out, fps=res.fps)
        
        file_size = os.path.getsize(out) if os.path.exists(out) else None
        video_duration = getattr(res, "duration", None) or float(len(res.frames)) / float(res.fps)
        
        _db_exec(
            "SELECT update_video_generation_result(:task_id, :path, :size, :duration)",
            {"task_id": task_id, "path": out, "size": file_size, "duration": video_duration},
        )
        
        return out
    
    except Exception as e:
        
        #update DB with error
        _db_exec(
            "SELECT update_video_generation_error(:task_id, :err)",
            {"task_id": task_id, "err": str(e)},
        )
        
        raise