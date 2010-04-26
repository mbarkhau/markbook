import os

def parse_meta(path, dirs, files):
    metafile = os.path.join(path, "metadata")
    lines = open(metafile).readlines()
    lines = [l.strip() for l in lines if l.strip()]
    key_val = [l.split(":", 1) for l in lines]
    res = {}
    for k, v in key_val:
        res[k.strip()] = v.strip()
    return res
        
def part_key(path, dir, files):
    files.sort()
    files = [f for f in files if f.endswith(".mkd")]
    return open(os.path.join(path, files[0])).readline().strip()

def compile():
    nodes = [n for n in os.walk(".") if "metadata" in n[2]]
    metadata = {"parts": {}}
    for n in nodes:
        curmeta = parse_meta(*n)
        if '.' == n[0]:
            metadata.update(curmeta)
        else:
            key = part_key(*n)
            metadata["parts"][key] = curmeta

    return metadata
