import os
from loguru import logger
from argparse import ArgumentParser
from pathlib import Path

import sienna
from dotenv import load_dotenv

from src.tldrbot.overview_summary import generate_overview
from src.tldrbot.utils import get_latest, get_n_papers, post

load_dotenv()
URL = os.environ.get("URL")
assert isinstance(URL, str)

USED_URLS_PATH = Path("./used_urls_path.txt")

if not os.path.exists("./logs"):
    os.mkdir("./logs")
logger.add("./logs/file_{time}.log")


if not USED_URLS_PATH.exists():
    USED_URLS_PATH.touch()


def run_single_tldr():
    """Make a TLDR post"""
    used_urls = sienna.load(str(USED_URLS_PATH))

    paper = get_latest()

    if paper.url in used_urls:
        return

    post(URL, paper.to_markdown())

    assert isinstance(used_urls, list)
    used_urls.append(paper.url)
    sienna.save(used_urls, str(USED_URLS_PATH))


@logger.catch
def run_newsletter(n: int = 3):
    """Make a newsletter looking post with N papers

    Parameters
    ----------
    n : int
        Number of papers to be included in the post
    """
    papers = get_n_papers(n)
    overview_summary = generate_overview(papers)
    overview_summary = overview_summary.rstrip()

    content = f"""Hello The Token.
Today, we have papers about {overview_summary}"""
    post(URL, content)

    for paper in papers:
        post(URL, paper.to_markdown())


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--do-news-letter", action="store_true")
    parser.add_argument("--news-letter-paper-n", type=int, deefault=3)
    args = parser.parse_args()

    if args.do_news_letter:
        run_newsletter(n=args.news_letter_paper_n)
    else:
        run_single_tldr()
