import json
import pandas as pd
import sys
from sqlalchemy import create_engine, MetaData, Table, Column, String, Text, Integer, ForeignKey, Float
import os
from dotenv import load_dotenv
load_dotenv()
mysql_path = os.getenv("SQL_URL")

version = sys.argv[1]
filename = 'extraction_result.json'
with open(f'{version}/{filename}', 'r') as file:
    data = json.load(file)

mof_data = []
metal_source_data = []
modulator_data = []
organic_linker_data = []
solvent_data = []

import re

def classify_compound_name(name):
    if re.search(r'[\[\(]', name) and re.search(r'[\]\)]\s*[\d\[\(n\?]', name):
        return 'formula'
    
    if re.search(r'([A-Z][a-z]?\s+\d+)', name):
        return 'composition'
    
    return 'name'

for item in data:
    identifier = item.get('identifier')
    txt = item.get('txt')
    paragraph = item.get('paragraph')
    replaced_result = item.get('replaced_result', [])

    mof_record = {
        "identifier": identifier,
        "txt": txt,
        "paragraph": paragraph,
        "name": "",
        "formula": "",
        "composition": ""
    }
    if replaced_result != None:
        if len(replaced_result) != 1:
            continue
        for result in replaced_result:
            compound_names = result.get('Compound_Name', [])
            for name in compound_names:
                name_type = classify_compound_name(name)
                if mof_record[name_type]:
                    mof_record[name_type] += '; ' + name
                else:
                    mof_record[name_type] = name
                # if name_type == 'name' and not mof_record["name"]:
                #     mof_record["name"] = name
                # elif name_type == 'formula' and not mof_record["formula"]:
                #     mof_record["formula"] = name
                # elif name_type == 'composition' and not mof_record["composition"]:
                #     mof_record["composition"] = name
                # else:
                #     print(f'duplicated {name_type}: {name}', mof_record)

            mof_record['active_time_str'] = '; '.join(result.get('Active_Time', []))
            mof_record['active_temperature_str'] = '; '.join(result.get('Active_Temperature', []))
            mof_record['reaction_time_str'] = '; '.join(result.get('Reaction_Time', []))
            mof_record['reaction_temperature_str'] = '; '.join(result.get('Reaction_Temperature', []))

            for metal_source in result.get('Metal_Source', []):
                metal_source_data.append({
                    "mof_identifier": identifier,
                    "amount": metal_source.get('amount', ""),
                    "precursor_name": metal_source.get('precursor_name', "")
                })

            for modulator in result.get('Modulator', []):
                try:
                    modulator_data.append({
                        "mof_identifier": identifier,
                        "amount": modulator.get('amount', ""),
                        "precursor_name": modulator.get('precursor_name', "")
                    })
                except:
                    print('not formated modulater:', modulator)

            for organic_linker in result.get('Organic_Linker', []):
                organic_linker_data.append({
                    "mof_identifier": identifier,
                    "amount": organic_linker.get('amount', ""),
                    "precursor_name": organic_linker.get('precursor_name', "")
                })

            for solvent in result.get('Solvent', []):
                solvent_data.append({
                    "mof_identifier": identifier,
                    "amount": solvent.get('amount', ""),
                    "precursor_name": solvent.get('precursor_name', "")
                })

        mof_data.append(mof_record)

df_mof = pd.DataFrame(mof_data)
df_metal_source = pd.DataFrame(metal_source_data)
df_modulator = pd.DataFrame(modulator_data)
df_organic_linker = pd.DataFrame(organic_linker_data)
df_solvent = pd.DataFrame(solvent_data)


DATABASE_URI = mysql_path
engine = create_engine(DATABASE_URI)
engine.execute(f"CREATE DATABASE IF NOT EXISTS synthethis_condition_{version} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")

DATABASE_URI = f'{mysql_path}/synthethis_condition_{version}?charset=utf8mb4'
engine = create_engine(DATABASE_URI)
metadata = MetaData()

mof_table = Table('MOF', metadata,
    Column('identifier', String(255), primary_key=True),
    Column('txt', String(255)),
    Column('paragraph', Text),
    Column('name', String(1023)),
    Column('formula', String(1023)),
    Column('composition', String(1023)),
    Column('active_time_str', String(255)),
    Column('active_temperature_str', String(255)),
    Column('reaction_time_str', String(255)),
    Column('reaction_temperature_str', String(255))
)

metal_source_table = Table('MOF_MetalSource', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('mof_identifier', String(255), ForeignKey('MOF.identifier')),
    Column('amount', String(255)),
    Column('precursor_name', String(255))
)

modulator_table = Table('MOF_Modulator', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('mof_identifier', String(255), ForeignKey('MOF.identifier')),
    Column('amount', String(255)),
    Column('precursor_name', String(255))
)

organic_linker_table = Table('MOF_OrganicLinker', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('mof_identifier', String(255), ForeignKey('MOF.identifier')),
    Column('amount', String(255)),
    Column('precursor_name', String(255))
)

solvent_table = Table('MOF_Solvent', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('mof_identifier', String(255), ForeignKey('MOF.identifier')),
    Column('amount', String(255)),
    Column('precursor_name', String(255))
)

with engine.connect() as connection:
    connection.execute("SET FOREIGN_KEY_CHECKS = 0;")
    connection.execute("DROP TABLE IF EXISTS MOF_MetalSource;")
    connection.execute("DROP TABLE IF EXISTS MOF_Modulator;")
    connection.execute("DROP TABLE IF EXISTS MOF_OrganicLinker;")
    connection.execute("DROP TABLE IF EXISTS MOF_Solvent;")
    connection.execute("DROP TABLE IF EXISTS MOF;")
    connection.execute("SET FOREIGN_KEY_CHECKS = 1;")

metadata.create_all(engine)

with engine.connect() as connection:
    connection.execute("CREATE INDEX idx_metal_source_mof_identifier ON MOF_MetalSource (mof_identifier);")
    connection.execute("CREATE INDEX idx_modulator_mof_identifier ON MOF_Modulator (mof_identifier);")
    connection.execute("CREATE INDEX idx_organic_linker_mof_identifier ON MOF_OrganicLinker (mof_identifier);")
    connection.execute("CREATE INDEX idx_solvent_mof_identifier ON MOF_Solvent (mof_identifier);")

df_mof.to_sql('MOF', engine, if_exists='append', index=False)
df_metal_source.to_sql('MOF_MetalSource', engine, if_exists='append', index=False)
df_modulator.to_sql('MOF_Modulator', engine, if_exists='append', index=False)
df_organic_linker.to_sql('MOF_OrganicLinker', engine, if_exists='append', index=False)
df_solvent.to_sql('MOF_Solvent', engine, if_exists='append', index=False)