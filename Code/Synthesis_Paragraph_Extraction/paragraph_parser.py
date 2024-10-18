
import pandas as pd
from bs4 import BeautifulSoup
import json
import statistics
import nltk
from nltk.tokenize import TextTilingTokenizer

NLTKTextTokenizer = TextTilingTokenizer()




def paragraph_dict(paragraph_text, start, end, first_row, file_name, is_syn=True, creator_id=None):
    """
    :return: A single paragraph dictionary
    """
    return {
        'paragraph': paragraph_text.replace("\n"," "),
        'startPosition': start,
        'endPosition': end,
        'doi': first_row['doi'],
        'mof-id': first_row['mof-id'],
        'fileName': file_name,
        'is_synthesis_paragraph': is_syn,
        'marker': creator_id,
        'twice_marked': False,
    }


def judge_overlap(paragraph1, paragraph2):
    """
    Judge whether two paragraph is overlap or not.
    Condition: s1 >= s2,which means the sequence should be sorted before judge.
    If overlapped part is fewer than 5 characters, they are considered as not overlapped.
    :return:
        - 1 if paragraph1 contains paragraph2;
        - -1 if paragraph2 contains paragraph1;
        - 0 if they do not totally contain each.
    """
    if paragraph1['endPosition'] <= (paragraph2['startPosition'] + 5):
        return 0
    if paragraph1['endPosition'] >= paragraph2['endPosition']:
        return 1
    return -1


def find_and_mark_overlaps(paragraphs):
    """
    Record twice marked paragraph and delete duplicated paragraph. Remain once marked paragraph.
    :param paragraphs: Marked paragraphs in one paper.
    :return: Parsed overlaps paragraphs.
    """
    paragraphs.sort(key=lambda x: x['startPosition'])
    to_remove = set()
    for i, paragraph1 in enumerate(paragraphs):
        for j, paragraph2 in enumerate(paragraphs[i + 1:], start=i + 1):
            overlap_result = judge_overlap(paragraph1, paragraph2)
            if overlap_result == 1:
                paragraph1['twice_marked'] = True
                to_remove.add(j)
            elif overlap_result == -1:
                paragraph2['twice_marked'] = True
                to_remove.add(i)
                break  # No need to compare paragraph1 with others as it will be removed
            elif overlap_result == 0:
                break

    for index in sorted(to_remove, reverse=True):  # Reverse sort to remove from the end
        del paragraphs[index]

    return paragraphs


def populate_marker_dict(single_paper_markers):
    """
    Step 2: Split marker. Create a dictionary to store start and end positions with creator-id as the key
    :param single_paper_markers: All lines of markings
    :return: A dictionary split by marker, recording start and end position.
    """
    marker_dict = {}
    for _, row in single_paper_markers.iterrows():
        if row['creator-id'] not in marker_dict:
            marker_dict[row['creator-id']] = {'start': [], 'end': []}
        marker_dict[row['creator-id']][row['class'].split(' ')[-1]].append(
            row['start pos' if row['class'] == 'syns start' else 'end pos'])
    return marker_dict


def extract_non_synthesis_paragraphs(text, marked_paragraphs, first_row, file_name):
    non_synthesis_paragraphs = []

    # Step 1: Prepare list of start and end positions for all marked paragraphs
    positions = [(para['startPosition'], para['endPosition']) for para in marked_paragraphs]
    positions.sort()

    # Step 2: Remove marked paragraphs
    new_text = ""
    last_end = 0
    for start, end in positions:
        new_text += text[last_end:start]
        last_end = end
    new_text += text[last_end:]

    # Step 3: Tokenize the remaining text into paragraphs (Commented out for now)
    paragraphs = NLTKTextTokenizer.tokenize(new_text.replace("\n","\n\n"))

    # Step 4: Create dictionary for each non-synthesis paragraph
    # paragraphs = new_text.split('\n')  # If you want to disable nltk, uncomment this line and comment the above line.
    paragraphs = [para for para in paragraphs if para.strip()]
    for idx, paragraph in enumerate(paragraphs):
        start = new_text.find(paragraph)  #
        end = start + len(paragraph)
        non_synthesis_paragraphs.append(paragraph_dict(paragraph.replace('\n',''), start, end, first_row, file_name, is_syn=False))

    return non_synthesis_paragraphs


def extract_synthesis_paragraphs(csv_file):
    """
    Extract synthesis and non-synthesis paragraph from a marking csv file.
    :param csv_file: synthesis paragraph records
    :return: a list of dictionary including all synthesis paragraph.
    """
    marking_information = pd.read_csv('data/' + csv_file)
    synthesis_paragraphs = []  # Final output
    for file_name, single_paper_markers in marking_information.groupby('txt-name'):
        try:
            with open('txt/' + file_name, 'r', encoding='utf-8') as f:
                paragraph_text = f.read()
        except FileNotFoundError:
            print(f"File {file_name} not found.")
            continue

        single_paper_markers = single_paper_markers.reset_index(drop=True)  # Reset the index for the current group
        first_row = single_paper_markers.iloc[0]  # For extracting doi and mof-id, which remain unchanged in a paper.
        marker_dict = populate_marker_dict(single_paper_markers)
        print(f"Extracting file with file name : {file_name}\n")

        # add recorded paragraphs into the repository
        synthesis_paragraphs_single_paper = []
        for creator_id, positions in marker_dict.items():
            for start, end in zip(positions['start'], positions['end']):
                synthesis_paragraphs_single_paper.append(
                    paragraph_dict(paragraph_text[start:end], start, end, first_row, file_name,True, creator_id))

        overlapped_paragraph = find_and_mark_overlaps(synthesis_paragraphs_single_paper)
        synthesis_paragraphs.extend(overlapped_paragraph)

        # 5. extract non-synthesis paragraph
        non_synthesis_paragraphs = extract_non_synthesis_paragraphs(paragraph_text, synthesis_paragraphs_single_paper,first_row, file_name)

        synthesis_paragraphs.extend(non_synthesis_paragraphs)

    return synthesis_paragraphs


# start Parsing
test_csv_file = 'testDataPara.csv'  # two samples
single_csv_file = 'singleDataPara.csv'  # one samples
test_middle_csv_file = '2-syns_para.csv'
test_total_csv_file = 'totalDataPara.csv'
csv_file_name = test_total_csv_file

extracted_paragraphs = extract_synthesis_paragraphs(csv_file_name)

statistics.count_parsed_csv_result(extracted_paragraphs)

def read_dict_from_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


write_path = 'parsed_synthesis_paragraphs_' + csv_file_name + '.txt'

with open(write_path, 'w', encoding='utf-8') as synthesis_paragraph_output:
    for single_paragraph in extracted_paragraphs:
        # synthesis_paragraph_output.write(str(single_paragraph) + '\n')
        json.dump(single_paragraph, synthesis_paragraph_output)
        synthesis_paragraph_output.write('\n')
    print("write into:\n" + synthesis_paragraph_output.name)



