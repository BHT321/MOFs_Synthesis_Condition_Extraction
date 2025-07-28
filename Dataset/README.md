# Files

- `extract_results_all.csv`: The CSD-MOFs extracted using the few-shot LLM method.

- `Supplementary_Data.xlsx`: This file contains the extracted synthesis conditions and the few-shot and zero-shot model training data for both the CSD-MOFs and WoS-UiO-66 datasets.

  In the CSD-MOFs dataset, an additional tab labeled **“MOFs Literature (CSD)”** provides a one-to-one correspondence between the DOI and the MOF-ID (`mof_identifier`). The MOF-ID serves as the primary key in the training data, while the DOI is used as the key for synthesis condition extraction from the papers.

  Below are descriptions of each tab. Tabs related to the CSD-MOFs dataset include:

  **Tabs related to the CSD-MOFs dataset include:**

  - **Annotated Conditions (CSD):** Our annotations of 123 CSD-MOFs papers, where the synthesis paragraphs are obtained by human annotation, and the synthesis conditions are obtained by the human-AI joint data curation method.

  - **Extracted Conditions (all CSD):** Results extracted from the synthesis paragraphs of 36,177 papers in the CSD-MOFs database, where the synthesis paragraphs are obtained via model extraction and the parameters are extracted using GPT.

  - **MOFs Literature (CSD):** DOI list of the CSD-MOFs dataset.

  - **Density Inference (Few-shot):** Extraction results obtained using few-shot extraction. After data cleaning and feature engineering, the density inference dataset is constructed. The density values are in the last column.

  - **Density Inference (Zero-shot):** Extraction results obtained using zero-shot extraction. After data cleaning and feature engineering, the density inference dataset is constructed. The density values are in the last column.

  **Tabs related to the WoS-UiO-66 dataset include:**

  - **Annotated Conditions (WoS):** Our annotations of 102 WoS-UiO-66 papers, where the synthesis paragraphs are obtained by human annotation, and the synthesis conditions are obtained following the human-AI joint data curation method.

  - **MOFs Literature (WoS):** The wosID list for each paper retrieved from the web of science for the WoS-UiO-66 dataset.

  - **Extracted Conditions (WoS):** Results extracted from the synthesis paragraphs of 260 papers in the WoS-UiO-66 database, where the synthesis paragraphs are obtained via model extraction and the parameters are extracted using GPT.

  - **SA Inference (Few-shot):** Extraction results obtained using few-shot extraction. After data cleaning and feature engineering, the surface area inference dataset is constructed. The surface area values are in the last column.

  - **SA Inference (Zero-shot):** Extraction results obtained using zero-shot extraction. After data cleaning and feature engineering, the surface area inference dataset is constructed. The surface area values are in the last column.

  **Tabs related to the SIMM dataset include:**

  - **Annotated Conditions (SIMM):** The cleaned 573 MOFs from SIMM datasets. In order to align the two manually annotated datasets, the original train and test datasets of SIMM are filtered and converted to JSON format using our human-AI annotation protocol.

  **Tabs related to the Bayesian optimization iterations:**
  
  - **Bayesian Round 1 Synthesis:** The conditions infered by the model and lab synthesis result in the first round of Bayesian optimization, comprising five recommended synthesis routes and their corresponding measured specific surface area values. The model are trained from few-shot extraction. The surface area values are in the last column.
  
  - **Bayesian Round 2 Synthesis:** The conditions infered by the model and lab synthesis result in the second round of Bayesian optimization, comprising five recommended synthesis routes and their corresponding measured specific surface area values. The model are trained from few-shot extraction. The surface area values are in the last column.
  
  - **Bayesian Round 3 Synthesis:** The conditions infered by the model and lab synthesis result in the third round of Bayesian optimization, comprising five recommended synthesis routes and their corresponding measured specific surface area values. The model are trained from few-shot extraction. The surface area values are in the last column.
  
  - **Bayesian_Round_1_result.pdf:** (See file in this folder) Detailed report of the test results for the synthesized UiO‑66 material product in first round.
  
  - **Bayesian_Round_2_result.pdf:** (See file in this folder) Detailed report of the test results for the synthesized UiO‑66 material product in second round.
  
  - **Bayesian_Round_3_result.pdf:** (See file in this folder) Detailed report of the test results for the synthesized UiO‑66 material product in third round.

  
  **Tabs related to the inorganic solid state(ISS) dataset:**

  - **Extracted Condition (BiLSTM ISS):** Selected 217 papers' extraction data from Kononova et al.'s work ([link](https://www.nature.com/articles/s41597-019-0224-1)) and their latest updated dataset ([link](https://github.com/CederGroupHub/text-mined-synthesis_public))
  
  - **Annotated Conditions (ISS):** Our 20 annotated paragraphs from 217 inorganic solid state papers . Mixing operations including mixing media and mixing device are annotated by the human-AI joint data curation method.
  
  - **Extracted Condition (LLM ISS):**  Extracted mixing operations extracted from the synthesis paragraphs of 217 papers in the inorganic solid-state database using FS-ICL with BM25 4-shot GPT-4.
