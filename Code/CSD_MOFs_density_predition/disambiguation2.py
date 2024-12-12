import pandas as pd
from sqlalchemy import create_engine
from fuzzywuzzy import fuzz
from itertools import combinations
from multiprocessing import Pool, cpu_count
import json
from collections import defaultdict
import os
from dotenv import load_dotenv
load_dotenv()
mysql_path = os.getenv("SQL_URL")
import sys
version = sys.argv[1]
DATABASE_URI = f'{mysql_path}/synthethis_condition_{version}?charset=utf8mb4'
engine = create_engine(DATABASE_URI)

tables = ['MOF_MetalSource', 'MOF_Modulator', 'MOF_OrganicLinker', 'MOF_Solvent']

unique_precursors = {}

for table in tables:
    df = pd.read_sql_table(table, engine)
    unique_precursors[table] = df['precursor_name'].unique()


# Modify precursor names, generate a new name(usually a short name without any special character)
# In order to merge some similar precursor names like 4,4' bpy and 4,4-bpy
VALID_CHARS = "0123456789abcdefghijklmnopqrstuvwxyz"
def modify_string(string):
    # return string
    string = string.lower()
    characters = [c for c in string if c in VALID_CHARS]
    return "".join(characters)

all_matched_words = {}

for table, precursors in unique_precursors.items():
    print(f"Processing table: {table}")
    precursor_names = unique_precursors[table]
    modified_name_to_origin_names = defaultdict(list)
    for precursor_name in precursor_names:
        modified_name_to_origin_names[modify_string(precursor_name)].append(precursor_name)
    matched_words = [sorted(origin_names) for origin_names in modified_name_to_origin_names.values() if len(origin_names) > 1]
    all_matched_words[table] = sorted(matched_words)


with open(f'{version}/disambiguation_v2.json', 'w') as f:
    json.dump(all_matched_words, f, indent=4, ensure_ascii=False)

print("Processing completed and results saved to JSON files.")
