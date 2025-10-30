#! /bin/bash
set -e

python to_database.py uio66_few_shot
python to_database.py uio66_zero_shot
python replace_precursor_names.py uio66_few_shot '' merge1  --remove-whitespace
python replace_precursor_names.py uio66_zero_shot '' merge1  --remove-whitespace
python deal_time.py uio66_few_shot
python deal_time.py uio66_zero_shot
python deal_amount.py uio66_few_shot
python deal_amount.py uio66_zero_shot

# python select_training_mofs.py uio66_few_shot uio66_zero_shot
python training_data_preparation2.py uio66_few_shot
python training_data_preparation2.py uio66_zero_shot

python get_synthesis_method.py uio66_few_shot
python get_synthesis_method.py uio66_zero_shot

python data_preparation.py uio66_few_shot
python data_preparation.py uio66_zero_shot
