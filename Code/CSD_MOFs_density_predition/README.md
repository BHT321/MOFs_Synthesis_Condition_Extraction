# Data preparation for CSD MOFs Density Prediction
This code is used to process the extaction result of CSD MOFs and generate a formated input for downstream task. The final output will be used for density prediction.   
The prediction code is in `CSD_density_model_training`.   
## Requirement
**Operation system**: Ubuntu 20.04  
**GPU**: NVIDIA GeForce RTX 3090  
**CUDA version**: 11.4  
**Python version**: 3.8.18   
**Database**: MySQL  
**Packages**:  
- cryptography==42.0.5    
- SQLAlchemy==1.4.46    
- PyMySQL==1.1.0   
- pandas==1.5.3   
- numpy==1.24.4   
- tqdm==4.66.1   
- fuzzywuzzy==0.18.0   
- python-dotenv==0.21.1     
- python-Levenshtein==0.25.1     
- scikit-learn==1.3.2  
- xgboost==1.7.5  
- optuna==3.6.1
## Usage
1. Config    
    You need to create a `.env` file in this directory and put`SQL_URL=xxx` in it.     
    The `SQL_URL` should be like `mysql+pymysql://mysql_user_name:mysql_password@host_url:url_port`.    
    For example, if the MySQL database is run in the local computer, and the name and password of user is `root` and `pass`, the `SQL_URL` should be `mysql+pymysql://root:pass@127.0.0.1:3306`

2. Data preparation    
    If the `run.sh` file is not excutable, use `chmod +x run.sh`.   
    Use `./run.sh` to dump the extraction result to mysql database and generate a model input for density prediction in `few_shot` and `zero_shot` folder. The model input file will be named `merged_features.csv`

3. Train models
    Use `train_xgboost_model.py` to train xgboost models for few-shot and zero-shot data.    
    `python train_xgboost_model.py few_shot` will train xgboost model to predict density for few-shot extraction results.    
    `python train_xgboost_model.py zero_shot` will train xgboost model to predict density for zero-shot extraction results. 
    

**Time**: it will takes about 5 to 10 minutes to prepare data and 2 hours to train models.
**Result**: The output of `Best value` is the test $R^2$ score of xgboost model. The few-shot score will be about **0.42** and zero-shot score will be about **0.34**