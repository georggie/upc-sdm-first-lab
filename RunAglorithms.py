from database.algorithms_executor import AlgorithmsExecutor


if __name__ == "__main__":
    exec = AlgorithmsExecutor()
    # exec.run_page_rank_algorithm()
    exec.run_louvain_algorithm()
