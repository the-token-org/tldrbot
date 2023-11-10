import os

import discord
import feedparser
import requests
from dotenv import load_dotenv
from schnitsum import SchnitSum

from src.tldrbot.paper import Paper

load_dotenv()
DEFAULT_ARXIV_QUERY = "http://export.arxiv.org/api/query?search_query=cat:cs.CL{keywords}&max_results={n}&sortBy=lastUpdatedDate&sortOrder=descending"
ARXIV_QUERY_URL = os.environ.get("ARXIV_QUERY_URL", DEFAULT_ARXIV_QUERY)
assert isinstance(ARXIV_QUERY_URL, str)


def get_n_papers(n: int, keywords: list[str] | None) -> list[Paper]:
    """Get N papers via Arxiv API.

    Parameters
    ----------
    n : int
        Number of recent papers to fetch from API
    keywords : list[str] | None
        Use to query Arxiv

    Returns
    -------
    list[Paper]
        A list of fetched papers
    """
    summarizer = SchnitSum("sobamchan/bart-large-scitldr")

    if keywords:
        keywords = [f"ti:{kw}" for kw in keywords]
        keywords_str = f"+AND+{'+OR+'.join(keywords)}"
    else:
        keywords_str = ""

    url = ARXIV_QUERY_URL.format(n=n, keywords=keywords_str)
    res = feedparser.parse(url)

    papers: list[Paper] = []
    for entry in res["entries"]:
        papers.append(
            Paper(
                title=entry["title"],
                abstract=entry["summary"],
                url=entry["link"],
                authors=[author["name"] for author in entry["authors"]],
                summarizer=summarizer,
            )
        )

    return papers


def get_latest(keywords: list[str] | None) -> Paper:
    """Just get one latest paper

    Returns
    -------
    Paper
        The latest paper
    """
    return get_n_papers(1, keywords)[0]


def post(url: str, text: str):
    """Post the given text to the Discord channel

    Parameters
    ----------
    url : str
        URL of the Discord channel, for Webhook
    text : str
        Text to be posted
    """
    session = requests.Session()
    webhook = discord.webhook.SyncWebhook.from_url(url, session=session)
    webhook.send(text)
