#! /bin/bash
set -e

python to_database.py few_shot
python to_database.py zero_shot

./merge_files.sh few_shot zero_shot
python data_preparation.py few_shot merge
python data_preparation.py zero_shot merge