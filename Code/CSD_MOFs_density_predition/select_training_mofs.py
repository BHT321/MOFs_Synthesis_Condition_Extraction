"""
This script is used to select mof to prepare data
NOTE: In this script, we get the top n precursor for each condition, and select the mof related to the top-n precursor.
But there are two things we DO NOT care:
1. Whether the mof is related to top-n Modulator. That means the mof we selected may NOT have any of the top-n modulator.
2. Whether the mof has multiple precursor for each condition.
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import re
import sys
import os
from dotenv import load_dotenv
load_dotenv()
mysql_path = os.getenv("SQL_URL")

VALID_CHARS = "0123456789abcdefghijklmnopqrstuvwxyz"
def remove_spaces(string):
    string = string.replace("\n", "")
    string = re.sub(r"\s+", "", string)
    string = string.lower()
    characters = [c for c in string if c in VALID_CHARS]
    string = "".join(characters)
    return string

version1 = sys.argv[1]
version2 = sys.argv[2]
table_suffix = sys.argv[3]
top_n_array = [int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
               ]
print(f"Get subset and fingerprint for {version1} and {version2}, table is {table_suffix}. Top n: M:O:S={top_n_array[0]}:{top_n_array[1]}:{top_n_array[2]}")
table_suffix = "_" + table_suffix
engine1 = create_engine(f'{mysql_path}/synthethis_condition_{version1}')
engine2 = create_engine(f'{mysql_path}/synthethis_condition_{version2}')
precursor_types = ["MetalSource", "OrganicLinker", "Solvent",
                #    "Modulator"
                   ]
# save_dir = "subset_and_fingerprint"
fingerprints = []

def get_top_precursors(precursor_type, top_n):
    table1 = pd.read_sql_table(f"MOF_{precursor_type}{table_suffix}", engine1)
    table2 = pd.read_sql_table(f"MOF_{precursor_type}{table_suffix}", engine2)
    merged_table = pd.concat([table1, table2])
    merged_table = merged_table[
        (merged_table["precursor_name"].notna()) &\
        (merged_table["precursor_name"].str.len() > 0)
        ]
    precursor_count = merged_table["precursor_name"].value_counts()
    top_precursors = set()
    for item in sorted(precursor_count.items(), key=lambda item:-item[1])[:top_n]:
        precursor_name, count = item
        fingerprints.append({
            "precursor_name": precursor_name,
            "cnt": count,
            "type": precursor_type
        })
        top_precursors.add(precursor_name)
    return top_precursors
    
def select_mof_identifier_by_top_precursor(precursor_type, top_precursors):
    table1 = pd.read_sql_table(f"MOF_{precursor_type}{table_suffix}", engine1)
    table2 = pd.read_sql_table(f"MOF_{precursor_type}{table_suffix}", engine2)

    def get_one_table_mof_identifiers(table:pd.DataFrame):
        mof_ids = set()
        mutiple_precursor_mof_ids = set()
        def is_select_group(group):
            precursors_names = set(group["precursor_name"])
            mof_id = group["mof_identifier"].iloc[0]
            if len(precursors_names&top_precursors) > 0:
                mof_ids.add(mof_id)
            if len(set(group["precursor_name"])) > 1:
                mutiple_precursor_mof_ids.add(mof_id)

        table.groupby("mof_identifier").apply(is_select_group)
        return mof_ids, mutiple_precursor_mof_ids

    mof_ids1, multiple_precursor_mof_ids1 = get_one_table_mof_identifiers(table1)
    mof_ids2, multiple_precursor_mof_ids2 = get_one_table_mof_identifiers(table2)
    mof_ids = mof_ids1 | mof_ids2
    # remove_mof_ids = multiple_precursor_mof_ids1 | multiple_precursor_mof_ids2
    # print(len(mof_ids), len(remove_mof_ids), len(multiple_precursor_mof_ids1), len(multiple_precursor_mof_ids2))
    # if remove_multiple_mof_ids:
    #     mof_ids = mof_ids - remove_mof_ids
    return mof_ids

selected_mof_ids = None
for precursor_type, top_n in zip(precursor_types, top_n_array):
    print("deal table", precursor_type)
    top_precursors = get_top_precursors(precursor_type, top_n)
    if precursor_type == "Modulator":
        continue
    
    mof_ids = select_mof_identifier_by_top_precursor(precursor_type, top_precursors)
    if selected_mof_ids is None:
        selected_mof_ids = mof_ids
    else:
        selected_mof_ids = selected_mof_ids & mof_ids
    print("Remain:", len(selected_mof_ids), f", {precursor_type} mof ids:", len(mof_ids))

df = pd.DataFrame(data=fingerprints)
def write_to_dir(dir):
    with open(f"{dir}/subset.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(selected_mof_ids))
    for precursor_type in precursor_types:
        df_subset = df[df["type"]==precursor_type]
        df_subset = df_subset.drop(columns=["type"])
        df_subset.to_csv(f"{dir}/{precursor_type}.csv", encoding="utf-8", index=None)
    df.to_csv(f"{dir}/origin_fingerprint.csv", encoding="utf-8", index=None)
write_to_dir(version1)
write_to_dir(version2)

    
    
    
    




