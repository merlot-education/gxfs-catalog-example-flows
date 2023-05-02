import os

shape_base_folder = "/home/mbuskies/gxfs/service-characteristics-22.10/yaml2shacl/"
shape_output_path = os.path.join(shape_base_folder, "mergedShapes.ttl")

prefixes = set()
shape_defs = []

for root, dirs, files in os.walk(shape_base_folder, topdown=False):
    for name in files:
        with open(os.path.join(root, name), "r") as f:
            shape_def = []
            for l in f.readlines():
                if l.startswith("@prefix"):
                    prefixes.add(l)
                else:
                    shape_def.append(l)
            shape_defs.append("".join(shape_def))

with open(shape_output_path, "w") as f:
    f.writelines(prefixes)
    f.writelines(shape_defs)
