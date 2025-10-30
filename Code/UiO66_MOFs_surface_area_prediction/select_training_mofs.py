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
import sys
import os
from dotenv import load_dotenv
load_dotenv()
mysql_path = os.getenv("SQL_URL")

version1 = sys.argv[1]
version2 = sys.argv[2]
engine1 = create_engine(f'{mysql_path}/synthethis_condition_{version1}')
engine2 = create_engine(f'{mysql_path}/synthethis_condition_{version2}')
precursor_types = ["MetalSource", "Solvent", "OrganicLinker", 
                   "Modulator"
                   ]
table_suffix = "_merge1"
save_dir = "subset_and_fingerprint"
top_n_array = [2, 1, 1, 6]
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

with open(f"{save_dir}/subset.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(selected_mof_ids))
fingerprint_df = pd.DataFrame(data=fingerprints)
fingerprint_df.to_csv(f"{save_dir}/fingerprint.csv", encoding="utf-8", index=None)
    
    
    




