import os
import warnings

shape_base_folder = "/home/mbuskies/gxfs/service-characteristics-22.10/yaml2shacl/"
shape_output_path = os.path.join(shape_base_folder, "mergedShapes.ttl")

prefixes = set()
shape_dict = {}
shape_defs = []

for root, dirs, files in os.walk(shape_base_folder, topdown=False):
    for name in files:
        file_path = os.path.join(root, name)
        if file_path == shape_output_path:
            continue
        with open(os.path.join(root, name), "r") as f:

            blocks = []
            tmp_list = []
            for s in f.readlines():
                if s == '\n':
                    blocks.append(tmp_list)
                    tmp_list = []
                else:
                    tmp_list.append(s)
            if tmp_list:
                blocks.append(tmp_list)
                tmp_list = []

            if not blocks:
                continue

            for prefix in blocks[0]:
                if prefix.startswith("@prefix"):
                    prefixes.add(prefix)
                else:
                    warnings.warn("WARNING: Expected @prefix but got " + prefix)

            for shape_list in blocks[1:]:
                shape_header = shape_list[0]
                shape_content = "".join(shape_list[1:])
                target_shape = shape_list[-1].strip()
                if (shape_header in shape_dict.keys()) \
                        and (shape_dict[shape_header]["content"] != shape_content)\
                        and (shape_dict[shape_header]["target_shape"] == target_shape):
                    warnings.warn(
                        "WARNING: Redifining " + shape_header + " with different content, this might cause issues if it is not just order related")
                    #print(file_path, shape_dict[shape_header]["file_path"], target_shape, shape_dict[shape_header]["target_shape"])
                shape_dict[shape_header] = {
                    "content": shape_content,
                    "file_path": file_path,
                    "target_shape": target_shape
                }


with open(shape_output_path, "w") as f:
    f.writelines(prefixes)
    f.write("\n")
    for shape_header in shape_dict.keys():
        f.write(shape_header)
        f.write(shape_dict[shape_header]["content"])
        f.write("\n")
