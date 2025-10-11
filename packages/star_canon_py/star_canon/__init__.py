from importlib.resources import files
import json, functools

@functools.lru_cache()
def canon():
    p = files(__package__) / "star_canon.json"
    return json.loads(p.read_text(encoding="utf-8"))

def normalize(name: str) -> str:
    c = canon()
    stars = set(c["stars"])
    aliases = c["aliases"]
    if name in stars: return name
    return aliases.get(name, name)
