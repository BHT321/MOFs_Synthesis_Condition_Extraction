"""
This script is used to merge files like 'merge1.json' and 'merge2.json'.
Modify the parameters, `filenames` to the input files and  `version` to the output dir
"""
import itertools
import json
import re

def read_file(filename):
    with open(filename, encoding="utf-8") as f:
        data = json.loads(f.read())
    return data

VALID_CHARS = "0123456789abcdefghijklmnopqrstuvwxyz"
def modify_string(string):
    # return string
    string = string.lower()
    characters = [c for c in string if c in VALID_CHARS]
    return "".join(characters)

def merge_all_groups(groups):
    all_substance_groups = []
    for group in groups:
        all_substance_groups.extend(group)
    union_find_set = [i for i in range(len(all_substance_groups))]
    for i, j in itertools.combinations(range(len(all_substance_groups)), 2):
        if j < i:
            i, j = j, i
        group1 = set([modify_string(string) for string in all_substance_groups[i]])
        group2 = set([modify_string(string) for string in all_substance_groups[j]])
        if len(group1 & group2) != 0:
            union_find_set[j] = i
    merged_substance_groups = {}
    def get_parent(index):
        if union_find_set[index] == index:
            return index
        return get_parent(union_find_set[index])
    for i in range(len(all_substance_groups)):
        p = get_parent(i)
        if p == i:
            merged_substance_groups[i] = all_substance_groups[i].copy()
        else:
            merged_substance_groups[p].extend(all_substance_groups[i])
            
    new_substance_groups = []
    for group in merged_substance_groups.values():
        new_substance_groups.append(sorted(list(set(group))))
    return new_substance_groups

tables = ["MOF_MetalSource", "MOF_Modulator", "MOF_OrganicLinker", "MOF_Solvent"]

import sys
version1 = sys.argv[1]
version2 = sys.argv[2]
merge_name = sys.argv[3]
filenames = [
    f"{version1}/{merge_name}.json",
    f"{version2}/{merge_name}.json"
]

file_datas = []
for filename in filenames:
    file_datas.append(read_file(filename))
merged_data = {}
for table in tables:
    table_datas = []
    for file_data in file_datas:
        table_datas.append(file_data.get(table, []))
    merged_names = merge_all_groups(table_datas)
    merged_data[table] = sorted(merged_names)
    
with open(f'{version1}/{merge_name}.json', "w", encoding="utf-8") as f:
    f.write(json.dumps(merged_data, indent=2, ensure_ascii=False))
with open(f'{version2}/{merge_name}.json', "w", encoding="utf-8") as f:
    f.write(json.dumps(merged_data, indent=2, ensure_ascii=False))