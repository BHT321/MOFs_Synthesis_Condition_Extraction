"""
This module contains the io method, mainly load and save data
"""

import os
import json
from typing import Dict, List, Tuple

def load_files(dir:str)->List[Dict]:
    """
    load multiply json files from a directory.

    :param dir: the input dir path
    :return: a list of dict, with each item contains `file_name`, `data`, and params parsed from `file_name`
    """
    results = []
    for file_name in os.listdir(dir):
        if not file_name.endswith(".json"):
            continue
        result = {}
        result["file_name"] = file_name
        params = file_name[:-5].split("-")
        for param in params:
            result[param[:param.index('_')]] = param[param.index('_')+1:]
        with open(f"{dir}/{file_name}", "r", encoding="utf-8") as f:
            result["data"] = json.loads(f.read())
        results.append(result)
    return results


def load_mof_file(file_name:str)->Tuple[List[Dict],Dict]:
    """
    load result or data from file. The file should be a json and formated as [{...},...]

    :param file_name: path of file
    :return: the json loads from file and a dict mapping mof id to mof json
    """
    with open(file_name, "r", encoding="utf-8") as f:
        mofs:list = json.loads(f.read())
    mof_dict = {}
    for mof in mofs:
        mof_dict[mof["mof_id"]] = mof
    return mofs, mof_dict

def save_file(data, file_path:str):
    """
    save result or data to file
    """
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(data, indent=2, ensure_ascii=False))