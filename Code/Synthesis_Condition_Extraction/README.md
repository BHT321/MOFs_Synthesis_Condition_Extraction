# Synthesis Condition Extraction Using Few-shot LLM
This code is used to extract synthesis condition from MOFs paragraphs.
## Requirement
**Operation system**: Ubuntu 20.04  
**GPU**: NVIDIA GeForce RTX 3090  
**CUDA version**: 11.4  
**Python version**: 3.8.18   
**Packages**:  
- openai==1.30.3
- python-dotenv==0.21.1
- langchain==0.1.15
- transformers==4.28.0
- sentence-transformers==2.2.2
- torch==2.1.2
- numpy==1.24.4
- scipy==1.10.1
- pandas==1.5.3
- ipykernel==6.29.0
- tqdm==4.66.1
- rank-bm25==0.2.2
## Usage
### Env Setting
First you need to create an `.env` file in this folder, and write `OPENAI_API_KEY=xxx` to it. Here you should get an openai api key to access the model. You can refer to [Openai Documentaion](https://platform.openai.com/) to get an api key.

### Synthesis Condition Extraction        
**Note**: if you run the code for the first time, it might take a few minutes to download Bert and SBert models.   
You can use the following code to extract one synthesis paragraph or use the code in `example.ipynb` to extract synthesis conditions for paragraphs.    
Import the `extract_synthesis_parameters` in your code.   
```python
# The following code is in `example.ipynb`.
from llm import extract_synthesis_parameters

results = extract_synthesis_parameters(
    paragraph=paragraph,
    example_size=4, 
    model='gpt-3.5-turbo', 
    rag_method="BM25", 
    temperature=0
    )
print(results)
```
`paragraph` is the string of synthesis text.  
`example_size` is the number of examples used in few-shot algorithm. If `example_size` is 0, then use zero-shot algorithm.   
`model` is the openai model used to extract synthesis conditions.  
`rag_method` is the algorithm used to retrieve examples from annotated MOF data. Can be "BM25", "bert", "sbert" or "random".   
`temperature` is the randomness of output. Set to 0 to make the output more stable. You can refer to openai document for more information.

### Metrics of Results
1. Run the code in `example.ipynb`. It will generate an `example_output.json` file, containing the extraction result of each paragraph in `example_input.json`
2. Run the code in `statistics/example.ipynb`. It will read `example_output.json` and calculate the scores of extraction.

**Time**: it will take 1 to 3 minutes to run extraction   
**Result**: the result is calculated in `statistics/example.ipynb`. The F1 score will be about 0.91 to 0.93.