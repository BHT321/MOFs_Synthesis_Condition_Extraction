import csv
import sys

version = sys.argv[1]
classified_csv_path = 'classified_data.csv'
target_csv_path = f'{version}/merged_features.csv'
output_csv_path = f'{version}/merged_data.csv'

classified_data = {}
with open(classified_csv_path, 'r', encoding='utf-8') as file:
    reader = csv.reader(file)
    next(reader)
    for row in reader:
        custom_id = row[0].replace('.txt', '') 
        synthesis_method = row[1]
        classification = row[2]
        classified_data[custom_id] = (synthesis_method, classification)

with open(target_csv_path, 'r', encoding='utf-8') as file:
    reader = csv.reader(file)
    target_data = list(reader)

output_data = [target_data[0] + ['synthesis_method', 'classification']]

for row in target_data[1:]:
    custom_id = row[0]
    if custom_id in classified_data:
        synthesis_method, classification = classified_data[custom_id]
        row += [synthesis_method, classification]
    else:
        row += ["", ""] 
    output_data.append(row)

with open(output_csv_path, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerows(output_data)

