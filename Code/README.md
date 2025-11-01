# Documentation
## Overview
1.  Synthesis_Paragraph_Extraction    
    The code is used to extract synthesis paragraphs from MOFs literature using a fine-tuned BERT classification model.
    
    More details in `Synthesis_Paragraph_Extraction/README.md`
    
3.  Synthesis_Condition_Extraction    
    The code uses GPT LLM to extract synthesis conditions.    
    K similar paragraphs are retrieved based on BM25, Bert, SBert similarity or random selection for input paragraph. The K similar paragraphs and corresponding annotation data are used as examples to guide the LLM to find synthesis conditions from the input paragraph.     
    More details in `Synthesis_Condition_Extraction/README.md` 

4. CSD_MOFs_density_prediction    
    The code processes the extraction results of 5269 CSD MOFs. After data cleansing and embedding, the extraction results are used to train xgboost model to predict MOFs density.    
    More details in `CSD_MOFs_density_predition/README.md`

5. UiO66_MOFs_surface_area_prediction     
    The code is used to process the extraction results of 261 WoS-UiO66 MOFs and prepare formatted data for surface area prediction.    
    More details in `UiO66_MOFs_surface_area_prediction/README.md`
## Requirement
**Operation system**: Ubuntu 20.04  
**GPU**: NVIDIA GeForce RTX 3090  
**Packages**:  
- openai
- python-dotenv1
- langchain
- transformers
- sentence-transformers
- torch
- numpy
- scipy
- pandas
- ipykernel
- tqdm
- rank-bm25

## Usage
Using LLM to synthesis conditions, you need to prepare and run the code in  `Synthesis_Condition_Extraction`.   
1. you need to create an `.env` file in the folder, and write `OPENAI_API_KEY=xxx` to it.   
2. Import the `extract_synthesis_parameters` in your code.      
    ```python
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
    The `results` will contains the 10 synthesis conditions extracted from `paragraph`.

    More detailed usage of extraction and other codes are in the `README.md` in each folder.
