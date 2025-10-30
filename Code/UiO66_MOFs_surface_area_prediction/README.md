# Data preparation for UiO-66 MOFs SA Prediction
This code is used to process the extaction result of UiO-66 MOFs and generate a formated input for surface area prediction.   
## Requirement
**Operation system**: Ubuntu 20.04  
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
## Usage
1. Config    
    You need to create a `.env` file in this directory and put`SQL_URL=xxx` in it.     
    The `SQL_URL` should be like `mysql+pymysql://mysql_user_name:mysql_password@host_url:url_port`.    
    For example, if the MySQL database is run in the local computer, and the name and password of user is `root` and `pass`, the `SQL_URL` should be `mysql+pymysql://root:pass@127.0.0.1:3306`

2. Data preparation    
    If the `run.sh` file is not excutable, use `chmod +x run.sh`.   
    Use `./run.sh` to dump the extraction result to mysql database and generate a model input for SA prediction in `uio66_few_shot` and `uio66_zero_shot` folder. The model input file will be named `model_input.csv`

**Time**: it will takes about 30 minutes to prepare data.
