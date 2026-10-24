from database.db import list_versions

def next_version(model_name):
    nums=[]
    for v in list_versions():
        if v["model_name"]==model_name and v["version"].startswith("v") and v["version"][1:].isdigit():
            nums.append(int(v["version"][1:]))
    return f"v{max(nums,default=0)+1}"
