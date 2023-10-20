import os
from pathlib import Path

import sienna
from dotenv import load_dotenv

from src.tldrbot.overview_summary import generate_overview
from src.tldrbot.utils import get_latest, get_n_papers, post

load_dotenv()
URL = os.environ.get("URL")
assert isinstance(URL, str)

USED_URLS_PATH = Path("./used_urls_path.txt")


if not USED_URLS_PATH.exists():
    USED_URLS_PATH.touch()


def run():
    used_urls = sienna.load(str(USED_URLS_PATH))

    paper = get_latest()

    if paper.url in used_urls:
        return

    post(URL, paper.to_markdown())

    assert isinstance(used_urls, list)
    used_urls.append(paper.url)
    sienna.save(used_urls, str(USED_URLS_PATH))


def run_newsletter():
    papers = get_n_papers(5)
    overview_summary = generate_overview(papers)

    content = f"""Hello The Token.
Today, {overview_summary}

{'\n\n'.join([paper.to_markdown() for paper in papers])}"""

    post(URL, content)


if __name__ == "__main__":
    run()
