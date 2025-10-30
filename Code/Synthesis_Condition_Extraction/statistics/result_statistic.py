"""
This module defines the functions to calculate the score of results.
Containing different statistics strategy, like calculate the result of one file, calculate by columns or calculate by one mof
"""

import collections
from typing import List
import json
import re
import os
from io_handler import load_files, load_mof_file
import pandas as pd

VALID_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") 
COLUMN_NAMES = [#"mof_name", 
            "metal_name", "organic_name", "solvent_name", "modulator_name",
            "metal_amount", "organic_amount", "solvent_amount", "modulator_amount",
            "reaction_time", "reaction_temp", 
            # "active_time", "active_temp"
            ]
SCORE_NAMES = ["F1", "acc", "precision", "recall"]

def change_name(s:str):
    """
    Change the string representing name/amount of material, temperature or time.
    remove error encodings and some unnecessary characters like comma.
    Only left alphabet and number.
    """
    if not isinstance(s, str):
        print("Get error item:", s)
        return None
    if s.lower() == "nan":
        return None
    s = "".join([c for c in s if c in VALID_CHARS])
    # remove_solution_names = ["solution", "distilled", "deionized", "hot", "solutions", "dilute"]
    # for solution_name in remove_solution_names:
    #     s = s.replace(solution_name, "").strip()
    # replce_solution_names = {
    #     "aqueous": "water",
    #     "methanolic": "methanol"
    # }
    # for name in replce_solution_names:
    #     s = s.replace(name, replce_solution_names[name])
    return s.lower()

def generate_name_amount_dict(dict_list):
    """
    Generate a dict mapping name to amount.
    Parsed the solvent volumn to add amounts togather.
    """
    assert isinstance(dict_list, list)
    parsed_d, n_parsed_d = {}, collections.defaultdict(list)
    for item in dict_list:
        assert isinstance(item, dict)
        name, amount = change_name(item.get("precursor_name", "")), change_name(item.get("amount", ""))
        if not name:
            continue
        if "notspecified" == amount:
            amount = ""
        if amount is None:
            amount = ""
        match_obj = re.match(r"(\d+(\.\d+)?)ml", amount.replace(" ", ""), re.I)
        if match_obj:
            parsed_d[name] = parsed_d.get(name, 0) + float(match_obj.group(1))
        else:
            n_parsed_d[name].append(amount)
    name_amount_d = collections.defaultdict(list)
    for name in parsed_d.keys():
        name_amount_d[name].append(change_name(str(parsed_d[name]) + "ml"))
    for name in n_parsed_d.keys():
        is_empty = False
        for amount in n_parsed_d[name]:
            if amount == "":
                is_empty = True
                continue
            name_amount_d[name].append(amount)
        if is_empty and len(name_amount_d[name]) == 0:
            name_amount_d[name].append("")
    return name_amount_d
    

def check_same_by_paragraph_only_name(true_labels:List[str], pred_labels:List[str], cnt:dict):
    """
    Check if the labels are same.
    Assume the true labels and predict labels just contains precursor_name and has no amount
    """
    if len(true_labels) == 0 and len(pred_labels) == 0:
        cnt["TN"] += 1
        return True
    elif true_labels == pred_labels:
        cnt["TP"] += 1
        return True
    elif len(pred_labels) == 0:
        cnt["FN"] += 1
        return False
    elif len(pred_labels) > 0:
        cnt["FP"] += 1
        return False
    else:
        raise Exception()
    
def check_same_mof_name(true_labels, pred_labels, cnt):
    """
    Check whether the given true labels and predict labels of mof names are same.
    """
    if len(true_labels) == 0 and len(pred_labels) == 0:
        cnt["TN"] += 1
        return True
    elif len(pred_labels) == 0:
        cnt["FN"] += 1
        return False
    elif len(true_labels & pred_labels) > 0:
        cnt["TP"] += 1
        return True
    else:
        cnt["FP"] += 1
        return False

def check_same_by_paragraph_and_split_name_amount(true_labels, pred_labels, cnt, is_mof_name=False):
    """
    Check whether the true labels and predict labels are same.
    """
    # this means current result has both name and amount
    if isinstance(cnt, list):
        true_labels = generate_name_amount_dict(true_labels)
        pred_labels = generate_name_amount_dict(pred_labels)
        name_cnt, amount_cnt = cnt
        # true and pred all empty
        if len(true_labels) == 0 and len(pred_labels) == 0:
            name_cnt["TN"] += 1
            amount_cnt["TN"] += 1
            return True
        # llm not extract params
        elif len(pred_labels) == 0:
            name_cnt["FN"] += 1
            amount_cnt["FN"] += 1
            return False
        # llm extract something more
        elif len(true_labels) == 0:
            name_cnt["FP"] += 1
            amount_cnt["FP"] += 1
            return False
        # name same
        elif set(true_labels.keys()) == set(pred_labels.keys()):
            name_cnt["TP"] += 1
            for name, amount1 in true_labels.items():
                if collections.Counter(amount1) != collections.Counter(pred_labels[name]):
                    amount_cnt["FP"] += 1
                    return False
            amount_cnt["TP"] += 1
            return True
        # name not same
        else:
            name_cnt["FP"] += 1
            amount_cnt["FP"] += 1
            return False
    # this means current results is mof name
    elif is_mof_name:
        assert is_mof_name != True
        true_labels = set([change_name(label) for label in true_labels if change_name(label)])
        pred_labels = set([change_name(label) for label in pred_labels if change_name(label)])
        return check_same_mof_name(true_labels, pred_labels, cnt)
    else:
        true_labels = set([change_name(label) for label in true_labels if change_name(label)])
        pred_labels = set([change_name(label) for label in pred_labels if change_name(label)])
        return check_same_by_paragraph_only_name(true_labels, pred_labels, cnt)
    
# def check_same_by_paragraph(true_labels, pred_labels, cnt):
#     item = true_labels[0] if len(true_labels) > 0 else (pred_labels[0] if len(pred_labels) > 0 else None)
#     if isinstance(item, dict):
#         true_labels = set(["precursor_name@"+change_name(d["precursor_name"])+"@amount@"+change_name(d["amount"]) for d in true_labels if change_name(d["precursor_name"]) and change_name(d["amount"])])
#         pred_labels = set(["precursor_name@"+change_name(d["precursor_name"])+"@amount@"+change_name(d["amount"]) for d in pred_labels if change_name(d["precursor_name"]) and change_name(d["amount"])])
#     else:
#         true_labels = set([change_name(label) for label in true_labels if change_name(label)])
#         pred_labels = set([change_name(label) for label in pred_labels if change_name(label)])
#         check_same_by_paragraph_only_name(true_labels, pred_labels, cnt)
    
def check_same(true_labels, pred_labels, cnt, version=1, is_mof_name=False):
    assert isinstance(true_labels, list) and isinstance(pred_labels, list)
    # Version 1, calculate by paragraphs
    if version == 1:
        return check_same_by_paragraph_and_split_name_amount(true_labels, pred_labels, cnt, is_mof_name)

    # Version 2, calculate by params
    # elif version == 2:
    #     return check_same_by_params(true_labels, pred_labels, cnt)

def select_result(true_labels, results):
    return -1

def cal_score(cnt, version):
    if (cnt["TP"] + cnt["FP"]) != 0:
        cnt["precision"] = cnt["TP"] / (cnt["TP"] + cnt["FP"])
    else:
        cnt["precision"] = 0

    if (cnt["TP"] + cnt["FN"]) != 0:
        cnt["recall"] = cnt["TP"] / (cnt["TP"] + cnt["FN"])
    else:
        cnt["recall"] = 0

    if (cnt["precision"] + cnt["recall"]) != 0:
        cnt["F1"] = 2 * cnt["precision"] * cnt["recall"] / (cnt["precision"] + cnt["recall"])
    else:
        cnt["F1"] = 0

    if (cnt["TP"] + cnt["TN"] + cnt["FP"] + cnt["FN"]) != 0:
        cnt["acc"] = (cnt["TP"] + cnt["TN"]) / (cnt["TP"] + cnt["TN"] + cnt["FP"] + cnt["FN"])
    else:
        cnt["acc"] = 0



def cal_data(data, version):
    # init some variable
    missing_result = 0
    column_to_confusion_matrix = {}
    for column_name in COLUMN_NAMES:
        column_to_confusion_matrix[column_name] = {"TP": 0, "FP": 0, "TN": 0, "FN": 0}

    # statistics for each data
    for mof_index, mof_json in enumerate(data):
        # extraction_results should be all possible synthesis processes
        extraction_results:list = mof_json.get("result", None)
        if extraction_results is None:
            extraction_results = [{}]
        if isinstance(mof_json["result"], dict):
            extraction_results = [mof_json["result"]]

        result_index = select_result(mof_json.get("Compound_Name", None), extraction_results)
        assert isinstance(extraction_results, list)
        # extraction_result is the matched synthesis process
        if len(extraction_results) == 0:
            extraction_result:dict = {}
        else:
            extraction_result:dict = extraction_results[result_index]

        for key, cnt_list in [
            ("Metal_Source", [column_to_confusion_matrix["metal_name"], column_to_confusion_matrix["metal_amount"]]),
            ("Organic_Linker", [column_to_confusion_matrix["organic_name"], column_to_confusion_matrix["organic_amount"]]),
            ("Solvent", [column_to_confusion_matrix["solvent_name"], column_to_confusion_matrix["solvent_amount"]]),
            ("Modulator", [column_to_confusion_matrix["modulator_name"], column_to_confusion_matrix["modulator_amount"]]),
            ("Reaction_Time", column_to_confusion_matrix["reaction_time"]),
            ("Reaction_Temperature", column_to_confusion_matrix["reaction_temp"])
        ]:
            check_same(mof_json[key], extraction_result.get(key, []), 
                cnt_list, version)
    result = {}
    result["missing"] = missing_result
    for column_name in COLUMN_NAMES:
        assert sum(column_to_confusion_matrix[column_name].values()) == len(data) > 0
        cal_score(column_to_confusion_matrix[column_name], version)
        result.update({f"{column_name}_{key}": value for key, value in column_to_confusion_matrix[column_name].items()})
    for score_name in SCORE_NAMES:
        sum_score = 0
        for column_name in COLUMN_NAMES:
            sum_score += result[f"{column_name}_{score_name}"]
        result[f"avg_{score_name}"] = sum_score / len(COLUMN_NAMES)
        # sum_score = 0
        # for column_name in column_names_new:
        #     sum_score += result[f"{column_name}_{score_name}"]
        # result[f"avg2_{score_name}"] = sum_score / len(column_names_new)
    return result


def cal_one_result_for_each_condition(mof_json, version=1):
    """
    Get statistics for each condition.
    Add key "column_scores" to `mof_json`, containing the TP, FP, TN, FN for each synthesis condition in extraction result.
    """
    def get_cnt_result(cnt:dict):
        assert cnt["TP"] + cnt["FP"] + cnt["TN"] + cnt["FN"] == 1
        for key in cnt:
            if cnt[key] == 1:
                return key
            
    column_to_confusion_matrix = {column_name:{"TP": 0, "FP": 0, "TN": 0, "FN": 0} for column_name in COLUMN_NAMES}
    
    # extraction_results should be all possible synthesis processes
    extraction_results:list = mof_json.get("result", None)
    if extraction_results is None:
        extraction_results = [{}]
    if isinstance(mof_json["result"], dict):
        extraction_results = [mof_json["result"]]

    result_index = select_result(mof_json.get("Compound_Name", None), extraction_results)
    assert isinstance(extraction_results, list)
    # extraction_result is the matched synthesis process
    if len(extraction_results) == 0:
        extraction_result:dict = {}
    else:
        extraction_result:dict = extraction_results[result_index]

    for key, cnt_list in [
            ("Metal_Source", [column_to_confusion_matrix["metal_name"], column_to_confusion_matrix["metal_amount"]]),
            ("Organic_Linker", [column_to_confusion_matrix["organic_name"], column_to_confusion_matrix["organic_amount"]]),
            ("Solvent", [column_to_confusion_matrix["solvent_name"], column_to_confusion_matrix["solvent_amount"]]),
            ("Modulator", [column_to_confusion_matrix["modulator_name"], column_to_confusion_matrix["modulator_amount"]]),
            ("Reaction_Time", column_to_confusion_matrix["reaction_time"]),
            ("Reaction_Temperature", column_to_confusion_matrix["reaction_temp"])
        ]:
        check_same(mof_json[key], extraction_result.get(key, {}), 
            cnt_list, version)
        
    for column_name in COLUMN_NAMES:
        column_to_confusion_matrix[column_name] = get_cnt_result(column_to_confusion_matrix[column_name])
    mof_json["column_scores"] = column_to_confusion_matrix
    mof_json["column_scores"]["result_index"] = result_index
    # return cnt

def get_statistics_result_by_condition_of_one_dir(input_dir, output_dir):
    """
    Get statistics for each condition. Generate new statistics file.
    @param input_dir: dir contains synthesis condition extraction result
    @param output_dir: target dir to put statistics of files in `input_dir`
    """
    for file in os.listdir(input_dir):
        if not file.endswith(".json"):
            continue
        print(file)
        with open(f"{input_dir}/{file}") as f:
            mofs = json.loads(f.read())
        for mof in mofs:
            cal_one_result_for_each_condition(mof)
        with open(f"{output_dir}/{file}", "w") as f:
            f.write(json.dumps(mofs, indent=2, ensure_ascii=False))

def get_results_df_of_one_dir(dir_path):
    """
    Statistics for every result file (ends with .json)
    """
    df_data = []
    for result in load_files(dir_path):
        # print(result["file_name"])
        df_result = result.copy()
        del df_result["data"]
        df_result.update(cal_data(result["data"], 1))
        df_data.append(df_result)
    df = pd.DataFrame(df_data, index=None)
    # df.to_csv(f"{BASE_DIR}/results_statistics.csv", index=None)
    return df

def get_result_of_one_file(file_path):
    result, _ = load_mof_file(file_path)
    return cal_data(result, 1)