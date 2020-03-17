import os
import re
import nltk
import lorem
import random
import settings
import numpy as np
import pandas as pd
from faker import Faker
from textblob import TextBlob
from database.neo4j_loader import Neo4JLoader

nltk.download('brown')
nltk.download('punkt')


class DblpExtracor(object):

    def __init__(self):
        """
        DblpExtractor constructor
        """
        # pick up configuration parameters
        self._SOURCE_PATH = os.getenv('DBLP_SOURCE')
        self._JOURNALS_NUMBER = os.getenv('JOURNALS_NUMBER')
        self._CONFERENCES_NUMBER = os.getenv('CONFERENCES_NUMBER')

    def _extract_keywords_from_sentence(self, title):
        """
        Tries it's best to generate keywords from the title of a paper
        :param title: title of the paper
        :return: string keywords
        """
        keywords = []
        blob = TextBlob(title)
        db_keywords = ['data management', 'indexing', 'data modeling', 'big data',
                       'data processing', 'data storage', 'data querying']

        val = np.random.choice([1, 2], p=[0.20, 0.80])

        if val == 1:
            keywords += random.sample(db_keywords, random.randint(1, 3))

        keywords += blob.noun_phrases
        return '|'.join(keywords)

    def _extract_conference_details(self, raw_string):
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

    def _extract_file_header(self, path):
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

    def _extract_coauthors(self, authors_raw):
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

    def extract_journal_papers(self, path):
        """
        Extracts papers that have been published in journals
        :param path: path to the file that contains papers that have been published in journals (output_articles)
        :return: data frame of journal papers
        """
        try:
            path = f'{self._SOURCE_PATH}/{path}'
            print(f'Extracting journal papers from the {path}.csv ...')

            headers = self._extract_file_header(f'{path}_header')
            journal_papers = pd.DataFrame(columns=['author', 'title', 'pages', 'key', 'ee', 'journal', 'volume',
                                                   'year', 'abstract', 'keywords', 'coauthors'])

            for df in pd.read_csv(path, names=headers, delimiter=';', nrows=100000, low_memory=False,
                                  error_bad_lines=False, chunksize=20000):

                if len(journal_papers) > int(self._JOURNALS_NUMBER):
                    break

                # take only journals - documentation: key is the unique key of the record. `conf/*` is used for
                # conference or workshop papers and `journals/*` is used for articles which are published in journals.
                df = df[df.key.str.contains('journals')]
                df = df[['author', 'title', 'pages', 'key', 'ee', 'journal', 'volume', 'year']]
                # if some of these fields is empty drop that row
                df.dropna(subset=['key', 'title', 'journal', 'year', 'volume', 'author', 'ee', 'pages'], inplace=True)
                # add abstract as lorem and infer keywords from the title
                df['abstract'] = df.apply(lambda _: lorem.paragraph(), axis=1)
                df['keywords'] = df.apply(lambda x: self._extract_keywords_from_sentence(x['title']), axis=1)
                df['coauthors'] = df.apply(lambda x: self._extract_coauthors(x['author']), axis=1)
                df['author'] = df.apply(lambda x: x['author'].split('|')[0], axis=1)
                df['title'] = df.apply(lambda x: re.sub('[\\|"]', '', x['title']), axis=1)

                journal_papers = journal_papers.append(df)

            journal_papers = journal_papers.sample(n=int(self._JOURNALS_NUMBER))
            journal_papers.to_csv(f'{self._SOURCE_PATH}/journals.csv')
        except IOError as io_error:
            print("Input/Output Exception => ", io_error)

    def extract_conference_papers(self, inproceedings_path, proceedings_path):
        """
        Extracts papers that have been published in conferences
        :param inproceedings_path: path to the inproceedings file
        :param proceedings_path: path to the proceedings file
        :return: data frame of conference papers
        """
        try:
            inproceedings_path = f'{self._SOURCE_PATH}/{inproceedings_path}'
            proceedings_path = f'{self._SOURCE_PATH}/{proceedings_path}'
            print(f'Extracting conference papers from the {inproceedings_path}.csv ...')

            headers = self._extract_file_header(f'{inproceedings_path}_header')
            confwork_papers = pd.DataFrame(columns=['author_x', 'title_x', 'pages_x', 'key_x', 'ee_x', 'editor', 'ee_y',
             'isbn', 'key_y', 'publisher', 'series', 'title_y', 'abstract', 'keywords', 'coauthors'])

            for df in pd.read_csv(inproceedings_path, names=headers, delimiter=';', nrows=100000, low_memory=False,
                                  error_bad_lines=False, chunksize=20000):

                if len(confwork_papers) > int(self._CONFERENCES_NUMBER):
                    break

                df = df.sample(frac=1).reset_index(drop=True)
                df = df[df.key.str.contains('conf')]
                df = df[['author', 'title', 'pages', 'key', 'ee', 'crossref', 'year']]
                df.dropna(subset=['key', 'title', 'author', 'crossref'], inplace=True)

                headers_conf = self._extract_file_header(f'{proceedings_path}_header')
                conf = pd.read_csv(proceedings_path, names=headers_conf, delimiter=';', error_bad_lines=False,
                                   low_memory=False)

                final_df = pd.merge(df, conf, left_on='crossref', right_on='key', how='inner')
                final_df = final_df[['author_x', 'title_x', 'pages_x', 'key_x', 'ee_x', 'editor', 'ee_y', 'isbn', 'key_y',
                                     'publisher', 'series', 'title_y']]

                final_df.dropna(subset=['author_x', 'title_x', 'pages_x', 'key_x', 'ee_x', 'editor', 'ee_y',
                                        'isbn', 'key_y', 'publisher', 'series', 'title_y'], inplace=True)

                final_df['abstract'] = final_df.apply(lambda _: lorem.paragraph(), axis=1)
                final_df['keywords'] = final_df.apply(lambda x: self._extract_keywords_from_sentence(x['title_x']), axis=1)
                final_df['title_y'] = final_df.apply(lambda x: self._extract_conference_details(x['title_y']), axis=1)
                final_df['coauthors'] = final_df.apply(lambda x: self._extract_coauthors(x['author_x']), axis=1)
                final_df['author_x'] = final_df.apply(lambda x: x['author_x'].split('|')[0], axis=1)
                final_df.dropna(subset=['title_y'], inplace=True)

                confwork_papers = confwork_papers.append(final_df)

            confwork_papers = confwork_papers.sample(n=int(self._CONFERENCES_NUMBER))
            confwork_papers.to_csv(f'{self._SOURCE_PATH}/conferences.csv')
        except IOError as io_error:
            print("Input/Output Exception => ", io_error)

    def genrate_random_reviews_(self):
        """
        Generate random reviews with comments and decisions
        :return: void
        """
        print("Generating random reviews information ... ")

        neo4j = Neo4JLoader()
        author_paper_pair = neo4j.evolver_helper()

        faker = Faker()
        universities = pd.read_csv('resources/universities', names=['Short', 'OName', 'URL'])

        for i in range(0, len(author_paper_pair)):
            choice = np.random.choice(['Company', 'University'], p=[0.3, 0.7])

            if choice == 'Company':
                picked = faker.company()
            if choice == 'University':
                picked = list(universities.sample(1)['OName'])[0]

            author_paper_pair[i].append(lorem.paragraph()),
            author_paper_pair[i].append(np.random.choice([True, False], p=[0.7, 0.3]))
            author_paper_pair[i].append(picked)
            author_paper_pair[i].append(choice)

        df = pd.DataFrame(author_paper_pair, columns=['author', 'paper', 'comment',
                                                      'decision', 'affiliation', 'organization'])

        df.to_csv(f'{self._SOURCE_PATH}/reviews.csv')
