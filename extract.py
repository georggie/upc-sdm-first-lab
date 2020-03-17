from loader.dblp_extractor import DblpExtracor

if __name__ == "__main__":
    dblp_extr = DblpExtracor()
    dblp_extr.extract_journal_papers("output_article")
    dblp_extr.extract_conference_papers("output_inproceedings", "output_proceedings")
    # dblp_extr.genrate_random_reviews_() # uncomment during the evolving