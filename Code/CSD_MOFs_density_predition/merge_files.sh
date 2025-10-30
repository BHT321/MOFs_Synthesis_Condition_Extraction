#! /bin/bash
set -e

version1=$1
version2=$2

python disambiguation.py $version1
python disambiguation.py $version2
python disambiguation2.py $version1
python disambiguation2.py $version2
python merge_files.py $version1 $version2 disambiguation_v2


python  replace_precursor_names.py $version1 '' disambiguation  --remove-whitespace
python  replace_precursor_names.py $version2 '' disambiguation  --remove-whitespace
python  replace_precursor_names.py $version1 disambiguation disambiguation_v2  --remove-whitespace
python  replace_precursor_names.py $version2 disambiguation disambiguation_v2  --remove-whitespace

python  replace_precursor_names.py $version1 disambiguation_v2 merge  --remove-whitespace
python  replace_precursor_names.py $version2 disambiguation_v2 merge  --remove-whitespace

python deal_amount.py $version1 merge
python deal_amount.py $version2 merge
python deal_time.py $version1
python deal_time.py $version2