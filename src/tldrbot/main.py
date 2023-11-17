from argparse import ArgumentParser
from pathlib import Path

import sienna

from src.tldrbot.overview_summary import generate_overview
from src.tldrbot.utils import get_latest, get_n_papers, post


def run_single_tldr(discord_url: str, used_url_fpath: Path, keywords: list[str] | None):
    """Make a TLDR post"""
    used_urls = sienna.load(str(used_url_fpath))

    paper = get_latest(keywords)

    if paper.url in used_urls:
        return

    post(discord_url, paper.to_markdown())

    assert isinstance(used_urls, list)
    used_urls.append(paper.url)
    sienna.save(used_urls, str(used_url_fpath))


def run_newsletter(discord_url: str, n: int = 3):
    """Make a newsletter looking post with N papers

    Parameters
    ----------
    n : int
        Number of papers to be included in the post
    """
    papers = get_n_papers(n, keywords=None)
    overview_summary = generate_overview(papers)
    overview_summary = overview_summary.rstrip()

    content = f"""Hello The Token.
Today, we have papers about {overview_summary}"""
    post(discord_url, content)

    for paper in papers:
        post(discord_url, paper.to_markdown())


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--bot-name", type=str, required=True)
    parser.add_argument("--discord-url", type=str, required=True)
    parser.add_argument("--do-news-letter", action="store_true")
    parser.add_argument("--news-letter-paper-n", type=int, default=3)
    parser.add_argument("--keywords", nargs="+", type=str, default=None)
    args = parser.parse_args()

    used_url_fpath = Path(f"./used-urls.{args.bot_name}.txt")
    if not used_url_fpath.exists():
        used_url_fpath.touch()

    if args.do_news_letter:
        run_newsletter(args.discord_url, n=args.news_letter_paper_n)
    else:
        run_single_tldr(args.discord_url, used_url_fpath, args.keywords)
