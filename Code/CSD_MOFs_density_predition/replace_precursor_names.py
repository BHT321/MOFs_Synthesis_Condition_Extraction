"""
Modified from replace.py. Try to replace with the name in fingerprint.
"""


import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
import json
import sys, os
import re
import argparse
import os
from dotenv import load_dotenv
load_dotenv()
mysql_path = os.getenv("SQL_URL")

def get_args_parser():
    parser = argparse.ArgumentParser(description="Merge names in the mysql database", add_help=True)
    parser.add_argument("version", type=str, help="name of database")
    parser.add_argument("src", type=str, help="Mysql table to merge, empty string means get from origin table. For example, if is 'merge1', it will load name from like Solvent_merge1")
    parser.add_argument("tgt", type=str, help="The merged names json file and the target mysql table. For example, if is 'merge2', it will write to table like Solvent_merge2")
    parser.add_argument("--use-fingerprint-name", action="store_true", help="Whether to use fingerprint names when the merge file contains fingerprint name")
    parser.add_argument("--remove-whitespace", action="store_true", help="Whether to ignore whitespace when matching precursor names")
    parser.add_argument("--remove-invalid", action="store_true", help="Whether to ignore whitespace when matching precursor names")
    return parser

args = get_args_parser().parse_args()
src = args.src
tgt = args.tgt

print(f"Source: {src}, Target: {tgt}")
# os._exit(0)

version = args.version
DATABASE_URI = f'{mysql_path}/synthethis_condition_{version}?charset=utf8mb4'
engine = create_engine(DATABASE_URI)
metadata = MetaData()

with open(f'{version}/{tgt}.json', 'r') as file:
    matched_words = json.load(file)

VALID_CHARS = "0123456789abcdefghijklmnopqrstuvwxyz"
def modify_string(string):
    if args.remove_whitespace:
        string = string.replace("\n", "")
        string = re.sub(r"\s+", "", string)
        string = string.lower()
        characters = [c for c in string if c in VALID_CHARS]
        string = "".join(characters)
    return string

if args.use_fingerprint_name:
    fingerprint = pd.read_csv(f'{version}/fingerprint.csv')
    fingerprint_names = fingerprint["precursor_name"].unique()
    fingerprint_modified_name_to_origin = {modify_string(name):name for name in fingerprint_names}

if src == '':
    tables = ['MOF_MetalSource', 'MOF_Modulator', 'MOF_OrganicLinker', 'MOF_Solvent']
else: 
    tables = [f'MOF_MetalSource_{src}', f'MOF_Modulator_{src}', f'MOF_OrganicLinker_{src}', f'MOF_Solvent_{src}']


def get_replace_name(name_list):
    if not args.use_fingerprint_name:
        return min(name_list, key=len)
    
    for name in name_list:
        if modify_string(name) in fingerprint_modified_name_to_origin:
            return fingerprint_modified_name_to_origin[modify_string(name)]
    return min(name_list, key=len)

def create_disambiguation_table(table_name):
    df = pd.read_sql_table(table_name, engine)
    if src:
        new_table_name = table_name.replace(src, tgt)
    else:
        new_table_name = f"{table_name}_{tgt}"
    df.to_sql(new_table_name, engine, if_exists='replace', index=False)
    return new_table_name

replacement_map = {}
for table, lists in matched_words.items():
    for name_list in lists:
        shortest_name = get_replace_name(name_list)
        for name in name_list:
            replacement_map[modify_string(name)] = shortest_name
            
def update_names_in_table(table_name, new_table_name):
    df = pd.read_sql_table(table_name, engine)
    df['precursor_name'] = df['precursor_name'].apply(lambda x: replacement_map.get(modify_string(x), get_replace_name([x])))
    df.to_sql(new_table_name, engine, if_exists='replace', index=False)

for table in tables:
    print(f"Processing table: {table}")
    new_table = create_disambiguation_table(table)
    update_names_in_table(table, new_table)

print("Processing completed and updated tables saved to database.")