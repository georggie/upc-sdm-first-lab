import lorem
import pandas as pd
from textblob import TextBlob

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


# from articles get authors, journal -> extract volume and year and title and after merge with other journals
# from inproceedings -> use key: conf/.... then use db/conf/nooj/nooj2018.html#BlancheteMMM18
# reduc it to db/conf/nooj/nooj2018.html and search that in output_proceedings for details
# run python -m textblob.download_corpora


def extract_keywords_from_sentence(title):
    """
    Tries it's best to generate keywords from the title of a paper
    :param title: title of the paper
    :return: array of keywords
    """
    blob = TextBlob(title)
    return blob.noun_phrases


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


def extract_journal_papers(path):
    """
    Extracts papers that have been published in journals
    :param path: path to the file that contains papers that have been published in journals (output_articles)
    :return: data frame of journal papers
    """
    try:
        print(f'Extracting journal papers from the {path}.csv ...')
        headers = extract_file_header(f'{path}_header')
        df = pd.read_csv(path, names=headers, delimiter=';', nrows=20000, low_memory=False, error_bad_lines=False)
        # take only journals - documentation: key is the unique key of the record. `conf/*` is used
        # for conference or workshop papers and `journals/*` is used for articles which are published in journals.
        df = df[df.key.str.contains('journals')]
        df = df[['author', 'title', 'pages', 'key', 'ee', 'journal', 'volume', 'year']]
        # if some of these fields is empty drop that row
        df.dropna(subset=['key', 'title', 'journal', 'year', 'volume', 'author'], inplace=True)
        # add abstract as lorem and infer keywords from the title
        df['abstract'] = df.apply(lambda _: lorem.paragraph(), axis=1)
        df['keywords'] = df.apply(lambda x: extract_keywords_from_sentence(x['title']), axis=1)
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
        df = pd.read_csv(inproceedings_path, names=headers, delimiter=';', nrows=30000, low_memory=False, error_bad_lines=False)
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

        return final_df
    except IOError as io_error:
        print("Input/Output Exception => ", io_error)


# df_journals = extract_journal_papers("output_article")
df_conferences = extract_conference_papers("output_inproceedings", "output_proceedings")

# print(df_journals)
print(df_conferences)