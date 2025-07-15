# Files

- `extract_results_all.csv`: The CSD-MOFs extracted using the few-shot LLM method.

- `Supplementary_Data.xlsx`: This file contains the extracted synthesis conditions and the few-shot and zero-shot model training data for both the CSD-MOFs and WoS-UiO-66 datasets.

  In the CSD-MOFs dataset, an additional tab labeled **“MOFs Literature (CSD)”** provides a one-to-one correspondence between the DOI and the MOF-ID (`mof_identifier`). The MOF-ID serves as the primary key in the training data, while the DOI is used as the key for synthesis condition extraction from the papers.

  Below are descriptions of each tab. In summary, all tabs are divided into two parts, corresponding to the two datasets.

  **Tabs related to the CSD-MOFs dataset include:**

  - **Annotated Conditions (CSD):** Our annotations of 123 CSD-MOFs papers, where the synthesis paragraphs and all synthesis parameters are obtained through manual annotation.

  - **Extracted Conditions (all CSD):** Results extracted from the synthesis paragraphs of 36,177 papers in the CSD-MOFs database, where the synthesis paragraphs are obtained via model extraction and the parameters are extracted using GPT.

  - **MOFs Literature (CSD):** DOI list of the CSD-MOFs dataset.

  - **Density Inference (Few-shot):** Extraction results obtained using few-shot extraction. After data cleaning and feature engineering, the density inference dataset is constructed. The density values are in the last column.

  - **Density Inference (Zero-shot):** Extraction results obtained using zero-shot extraction. After data cleaning and feature engineering, the density inference dataset is constructed. The density values are in the last column.

  **Tabs related to the WoS-UiO-66 dataset include:**

  - **Annotated Conditions (WoS):** Our annotations of 87 WoS-UiO-66 papers, where the synthesis paragraphs and all synthesis parameters are obtained through manual annotation.

  - **MOFs Literature (WoS):** DOI list of the WoS-UiO-66 dataset.

  - **Extracted Conditions (WoS):** Results extracted from the synthesis paragraphs of 261 papers in the WoS-UiO-66 database, where the synthesis paragraphs are obtained via model extraction and the parameters are extracted using GPT.

  - **SA Inference (Few-shot):** Extraction results obtained using few-shot extraction. After data cleaning and feature engineering, the surface area inference dataset is constructed. The surface area values are in the last column.

  - **SA Inference (Zero-shot):** Extraction results obtained using zero-shot extraction. After data cleaning and feature engineering, the surface area inference dataset is constructed. The surface area values are in the last column.

  **Tabs related to the SIMM dataset include:**

  - **Annotated Conditions (SIMM):** The cleaned 573 MOFs from SIMM datasets. In order to align the two manually annotated datasets, the original train and test datasets of SIMM are filtered and converted to JSON format using our human-AI annotation protocol.

- `inorganic_solid_state_extraction_experiment`: This folder contains the files of mixing operation synthesis condition extraction experiments on inorganic solid-state dataset.  

  - **BiLSTM_extracted_conditions_inorganic_solid_state.json:** Selected 217 papers' extraction data from Kononova et al.'s work ([link](https://www.nature.com/articles/s41597-019-0224-1)) and their latest updated dataset ([link](https://github.com/CederGroupHub/text-mined-synthesis_public))
  
  - **annotated_conditions_inorganic_solid_state.json:** Our 20 annotated paragraphs from 217 inorganic solid state papers. Mixing operations including mixing media and mixing device are annotated.
  
  - **FSICL_extracted_conditions_inorganic_solid_state.json:**  Results extracted from the synthesis paragraphs of 217 papers in the inorganic solid-state database using FS-ICL with BM25 4-shot GPT-4.
