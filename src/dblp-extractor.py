import re
import lorem
import pandas as pd
from textblob import TextBlob

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

SOURCE_PATH='./dumps'
OUTPUT_PATH='./main/resources'


def extract_keywords_from_sentence(title):
    """
    Tries it's best to generate keywords from the title of a paper
    :param title: title of the paper
    :return: processed_string of keywords
    """
    blob = TextBlob(title)
    keywords = blob.noun_phrases
    return '|'.join(keywords)


def extract_conference_details(raw_string):
    """
    Extracts conference details from the raw string
    :param raw_string: with conference details like workshop/conference, venue, part of the year etc.
    :return: string that represents coded information about conference
    """
    processed_string = [re.sub("$[\s.]", '', token) for token in raw_string.split(',')]
    is_workshop = 'workshop' in raw_string.lower()
    if len(processed_string) < 5:
        return None
    else:
        if not processed_string[-2].strip().isdigit():
            return None
        if not re.search(".+-.+", processed_string[-3]):
            return None
        return f'{processed_string[0]}{processed_string[1]}|{processed_string[-5]}' \
               f'|{processed_string[-4]}|{processed_string[-3]}|{processed_string[-2]}|{is_workshop}'


def extract_file_header(path):
    """
    Returns list of header names from the header csv file
    :param path: path to the header csv file
    :return: list of headers
    """
    try:
        raw_data = open(path)
        raw_data = raw_data.read().split(sep=';')
        headers = []
        for item in raw_data:
            headers.append(item.split(sep=':')[0])
        return headers
    except IOError as io_error:
        print("Input/Output Exception => ", io_error)


def extract_coauthors(authors_raw):
    """
    Extract co-authors of a paper
    :param authors_raw: string of authors
    :return: co-authors of the paper
    """
    authors = authors_raw.split('|')
    if len(authors) > 1:
        authors.pop(0)
        return '|'.join(authors)
    else:
        return None


def extract_journal_papers(path):
    """
    Extracts papers that have been published in journals
    :param path: path to the file that contains papers that have been published in journals (output_articles)
    :return: data frame of journal papers
    """
    try:
        print(f'Extracting journal papers from the {path}.csv ...')
        headers = extract_file_header(f'{path}_header')
        df = pd.read_csv(path, names=headers, delimiter=';', nrows=5000, low_memory=False, error_bad_lines=False)
        # take only journals - documentation: key is the unique key of the record. `conf/*` is used
        # for conference or workshop papers and `journals/*` is used for articles which are published in journals.
        df = df[df.key.str.contains('journals')]
        df = df[['author', 'title', 'pages', 'key', 'ee', 'journal', 'volume', 'year']]
        # if some of these fields is empty drop that row
        df.dropna(subset=['key', 'title', 'journal', 'year', 'volume', 'author'], inplace=True)
        # add abstract as lorem and infer keywords from the title
        df['abstract'] = df.apply(lambda _: lorem.paragraph(), axis=1)
        df['keywords'] = df.apply(lambda x: extract_keywords_from_sentence(x['title']), axis=1)
        df['coauthors'] = df.apply(lambda x: extract_coauthors(x['author']), axis=1)
        df['author'] = df.apply(lambda x: x['author'].split('|')[0], axis=1)
        df['title'] = df.apply(lambda x: re.sub('[\\|"]', '', x['title']), axis=1)

        return df.reset_index(drop=True)
    except IOError as io_error:
        print("Input/Output Exception => ", io_error)


def extract_conference_papers(inproceedings_path, proceedings_path):
    """
    Extracts papers that have been published in conferences
    :param inproceedings_path: path to the inproceedings file
    :param proceedings_path: path to the proceedings file
    :return: data frame of conference papers
    """
    try:
        print(f'Extracting conference papers from the {inproceedings_path}.csv ...')
        headers = extract_file_header(f'{inproceedings_path}_header')
        df = pd.read_csv(inproceedings_path, names=headers, delimiter=';', nrows=20000, low_memory=False,
                         error_bad_lines=False)
        df = df[df.key.str.contains('conf')]
        df = df[['author', 'title', 'pages', 'key', 'ee', 'crossref', 'year']]
        df.dropna(subset=['key', 'title', 'year', 'author', 'crossref'], inplace=True)

        headers_conf = extract_file_header(f'{proceedings_path}_header')
        conf = pd.read_csv(proceedings_path, names=headers_conf, delimiter=';', error_bad_lines=False, low_memory=False)

        final_df = pd.merge(df, conf, left_on='crossref', right_on='key', how='inner')
        final_df = final_df[['author_x', 'title_x', 'pages_x', 'key_x', 'ee_x', 'editor', 'ee_y', 'isbn', 'key_y',
                             'publisher', 'series', 'title_y', 'year_y']]
        final_df['abstract'] = final_df.apply(lambda _: lorem.paragraph(), axis=1)
        final_df['keywords'] = final_df.apply(lambda x: extract_keywords_from_sentence(x['title_x']), axis=1)
        final_df['title_y'] = final_df.apply(lambda x: extract_conference_details(x['title_y']), axis=1)
        final_df.dropna(subset=['title_y'], inplace=True)

        return final_df
    except IOError as io_error:
        print("Input/Output Exception => ", io_error)


df_journals = extract_journal_papers(f"{SOURCE_PATH}/output_article")
df_conferences = extract_conference_papers(f"{SOURCE_PATH}/output_inproceedings", f"{SOURCE_PATH}/output_proceedings")

df_conferences.to_csv(f'{OUTPUT_PATH}/conferences.csv')
df_journals.to_csv(f'{OUTPUT_PATH}/journals.csv')