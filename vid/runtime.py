from functools import lru_cache
from .pipelines.cogvideox import CogVideoX

#cache the generator - might need to switch to something better (TODO: research)
@lru_cache(maxsize=1)
def get_generator():
    return CogVideoX()  #initial - later read model from env and switch
