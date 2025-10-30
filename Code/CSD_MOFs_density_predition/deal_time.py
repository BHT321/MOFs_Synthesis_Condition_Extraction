import pandas as pd
import numpy as np
import re
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy import create_engine, MetaData, Table, Column, Float
from sqlalchemy.exc import IntegrityError
from tqdm import tqdm
import os
import sys
from dotenv import load_dotenv
load_dotenv()
mysql_path = os.getenv("SQL_URL")

version = sys.argv[1]
DATABASE_URI = f'{mysql_path}/synthethis_condition_{version}'
engine = create_engine(DATABASE_URI)
metadata = MetaData(bind=engine)

def extract_number(text):
    numbers = re.findall(r'\d+(?:\.\d+)?', text)
    if len(numbers) == 0:
        return np.nan        
    elif '-' in text and len(numbers) == 2:
        return (float(numbers[0]) + float(numbers[1])) / 2
    
    return float(numbers[0])


def convert_temperature(temperature_str):
    if pd.isna(temperature_str):
        return np.nan

    temperature_str = temperature_str.lower()
    temperatures = re.split(r'[;,]\s*', temperature_str)
    total_temp = 0
    count = 0

    for temp in temperatures:
        # print(f"Processing Temp segment: {temp}")
        if 'room temperature' in temp or 'rt' in temp:
            total_temp += 23
            count += 1
        else:
            number = extract_number(temp)
            # print(f"Extracted number: {number}")
            if pd.isna(number):
                continue
            try:
                if 'k' in temp:
                    total_temp += number - 273.15
                elif 'f' in temp:
                    total_temp += (number - 32) * 5 / 9
                elif 'c' in temp or '°' in temp or '掳' in temp:
                    total_temp += number
                else:
                    total_temp += number
                count += 1
            except:
                continue

    if count == 0:
        return np.nan

    return total_temp / count

def convert_time(time_str):
    if pd.isna(time_str):
        return np.nan

    time_str = time_str.lower()
    times = re.split(r'[;,]\s*', time_str)
    total_time = 0

    time_dict = {
        'second': 1/3600, 'min': 1/60, 'hour': 1, 'day': 24, 'week': 168, 'month': 730, 'year': 8760,
        'several': 5, 'few': 5, 'overnight': 12
    }
    number_dict = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
        'ten': 10, 'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15, 'sixteen': 16,
        'seventeen': 17, 'eighteen': 18, 'nineteen': 19, 'twenty': 20
    }

    for t in times:
        # print(f"Processing time segment: {t}")
        if 'overnight' in t:
            total_time += 12
            continue
        value = extract_number(t)
        if pd.isna(value):
            for word, num in number_dict.items():
                if word in t:
                    value = num
                    break
        if pd.isna(value):
            continue

        matched_unit = False
        for unit, factor in time_dict.items():
            if unit in t:
                total_time += value * factor
                matched_unit = True
                break
        
        if not matched_unit:
            # If no unit is matched, assume the unit is hours
            total_time += value

        # print(f"Value: {value}, Total Time: {total_time}")

    if total_time == 0:
        return np.nan

    return total_time

table = Table('MOF', metadata, autoload_with=engine)

columns_to_add = [
    Column('active_time_value', Float),
    Column('active_temperature_value', Float),
    Column('reaction_time_value', Float),
    Column('reaction_temperature_value', Float)
]
updated = False
with engine.connect() as conn:
    for column in columns_to_add:
        if column.name not in table.columns:
            updated = True
            try:
                conn.execute(f'ALTER TABLE `MOF` ADD COLUMN `{column.name}` FLOAT')
                print(f"Added column: {column.name}")
            except IntegrityError as e:
                print(f"Failed to add column {column.name}: {str(e)}")

if updated:
    metadata = MetaData(bind=engine)
    table = Table('MOF', metadata, autoload_with=engine)

df = pd.read_sql_table('MOF', engine)

df['active_time_value'] = df['active_time_str'].apply(convert_time)
df['active_temperature_value'] = df['active_temperature_str'].apply(convert_temperature)
df['reaction_time_value'] = df['reaction_time_str'].apply(convert_time)
df['reaction_temperature_value'] = df['reaction_temperature_str'].apply(convert_temperature)
df = df.where(pd.notnull(df), None)

records = []
for row in df.to_dict(orient='records'):
    cleaned_row = {k: (None if pd.isna(v) else v) for k, v in row.items()}
    records.append(cleaned_row)

# print(records[:5])

with engine.connect() as conn:
    for row in tqdm(records):
        stmt = table.update().where(table.c.identifier == row['identifier']).values(
            active_time_value=row['active_time_value'],
            active_temperature_value=row['active_temperature_value'],
            reaction_time_value=row['reaction_time_value'],
            reaction_temperature_value=row['reaction_temperature_value']
        )
        conn.execute(stmt)

