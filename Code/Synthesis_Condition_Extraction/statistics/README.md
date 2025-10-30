# Usage
Import `get_result_of_one_file` from `result_statistic.py`
```python
from result_statistic import get_result_of_one_file
print(get_result_of_one_file("../extraction_results.json"))
```
It will output the scores of extraction, such as "avg_F1", "avg_acc". 

**Note**: each item of result file should have annotated conditions, like "Compound_Name" and "Metal_Source". 