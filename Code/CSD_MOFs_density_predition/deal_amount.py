import pandas as pd
import re
from sqlalchemy import create_engine
import sys
import os
from dotenv import load_dotenv
load_dotenv()
mysql_path = os.getenv("SQL_URL")

version = sys.argv[1]
DATABASE_URI = f'{mysql_path}/synthethis_condition_{version}'
engine = create_engine(DATABASE_URI)
merge_version = sys.argv[2]
table_suffix = f"_{merge_version}" if merge_version != "" else ""

def extract_amount_value(amount):
    if pd.isna(amount):
        return None
    amount = amount.lower()
    if 'mol/' in amount or 'molar ratio' in amount:
        return None
    elif 'mmol' in amount:
        match = re.search(r"([\d\.]+)\s*mmol", amount)
        if match:
            return float(match.group(1))
    elif '× 10 -3  mol' in amount:
        match = re.search(r"([\d\.]+)\s*×\s*10\s*-\s*3\s*mol", amount)
        if match:
            return float(match.group(1))
    elif 'mol' in amount:
        match = re.search(r"([\d\.]+)\s*mol", amount)
        if match:
            return float(match.group(1)) * 1000
    return None

def extract_solvent_amount(amount):
    if pd.isna(amount):
        return None
    amount = amount.lower()
    if 'mL' in amount or 'ml' in amount or 'ML' in amount or 'cm3' in amount or 'cm 3' in amount:
        match = re.search(r"([\d\.]+)\s*(mL|ml|ML|cm3|cm\s*3)", amount)
        if match:
            return float(match.group(1))
    return None

def process_table(table_name, amount_extraction_function):
    df = pd.read_sql_table(table_name, engine)
    
    df['amount_value'] = df['amount'].apply(amount_extraction_function)
    
    df.to_sql(table_name, engine, if_exists='replace', index=False)

process_table(f'MOF_MetalSource{table_suffix}', extract_amount_value)
process_table(f'MOF_OrganicLinker{table_suffix}', extract_amount_value)
process_table(f'MOF_Solvent{table_suffix}', extract_solvent_amount)

