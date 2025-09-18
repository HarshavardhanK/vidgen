## Video Pipeline

Model-backed video generation utilities.

### Structure
- `base.py`: `VideoGenerator` interface and `GenResult`
- `pipelines/cogvideox.py`: CogVideoX implementation (default)
- `runtime.py`: `get_generator()` with simple LRU cache
- `config.py`: placeholder for future config

### Default generator
```
from vid.runtime import get_generator
gen = get_generator()
res = gen.generate("A cat dancing", fps=24)
```

Exports frames; the API task writes MP4 via `export_to_video`.

### Model selection
- Currently fixed to `THUDM/CogVideoX-2b` on CUDA with bfloat16.
- To switch models, extend a new pipeline and update `get_generator()` to read from env.

### Performance notes
- Heavy model load; runs on GPU worker.
- Cached singleton via `lru_cache` to avoid reloads per task.


