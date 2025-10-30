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
merge_version = "merge1"
table_suffix = f"_{merge_version}" if merge_version != "" else ""

molar_mass_df = pd.read_csv("molar_mass.csv")
name_to_molar_mass = {}
for _, row in molar_mass_df.iterrows():
    name, molar_mass = row["precursor_name"], row["molar_mass"]
    assert molar_mass.endswith("g/mol")
    name_to_molar_mass[re.sub(r"\s", "", name)] = float(molar_mass.replace("g/mol", ""))

import re

def remove_garbled_text(text):
    cleaned_text = re.sub(r'[^\x20-\x7E]+', '', text)
    return cleaned_text


def extract_molar_amount_value(amount):
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
    elif 'millimoles' in amount:
        match = re.search(r"([\d\.]+)\s*millimoles", amount)
        if match:
            return float(match.group(1))
    elif 'mol' in amount:
        match = re.search(r"([\d\.]+)\s*mol", amount)
        if match:
            return float(match.group(1)) * 1000
    return None

def extract_mass_amount_value(amount):
    if pd.isna(amount):
        return None
    amount = amount.lower()
    match = re.search(r"([\d\.]+)\s*m\s*g", amount)
    if match:
        return float(match.group(1))
    match = re.search(r"([\d\.]+)\s*×\s*10\s*-\s*3\s*g", amount)
    if match:
        return float(match.group(1))
    match = re.search(r"([\d\.]+)\s*g", amount)
    if match:
        return float(match.group(1)) * 1000
    match = re.search(r"([\d\.]+)\s*kg", amount)
    if match:
        return float(match.group(1)) * 1000 * 1000
    return None

def extract_amount_value(row):
    precursor_name, amount = remove_garbled_text(row["precursor_name"]), remove_garbled_text(row["amount"])
    molar_mass = extract_molar_amount_value(amount)
    if molar_mass is not None:
        return molar_mass
    mass = extract_mass_amount_value(amount)
    if mass is None:
        return None
    precursor_name = re.sub(r"\s", "", precursor_name)
    if precursor_name not in name_to_molar_mass:
        return None
    return round(mass / name_to_molar_mass[precursor_name], 4)
    
    

def extract_solvent_amount(row):
    amount = remove_garbled_text(row["amount"])
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
    
    df['amount_value'] = df.apply(amount_extraction_function, axis=1)
    
    df.to_sql(table_name, engine, if_exists='replace', index=False)

process_table(f'MOF_MetalSource{table_suffix}', extract_amount_value)
process_table(f'MOF_OrganicLinker{table_suffix}', extract_amount_value)
process_table(f'MOF_Solvent{table_suffix}', extract_solvent_amount)
process_table(f'MOF_Modulator{table_suffix}', extract_solvent_amount)

