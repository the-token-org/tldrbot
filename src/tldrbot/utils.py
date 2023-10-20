import discord
import feedparser
import requests
from schnitsum import SchnitSum

from src.tldrbot.paper import Paper

ARXIV_QUERY_URL = "http://export.arxiv.org/api/query?search_query=cat:cs.CL&max_results={n}&sortBy=lastUpdatedDate&sortOrder=descending"


def get_n_papers(n: int) -> list[Paper]:
    """Get N papers via Arxiv API.

    Parameters
    ----------
    n : int
        Number of recent papers to fetch from API

    Returns
    -------
    list[Paper]
        A list of fetched papers
    """
    summarizer = SchnitSum("sobamchan/bart-large-scitldr")

    url = ARXIV_QUERY_URL.format(n=n)
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


def get_latest() -> Paper:
    """Just get one latest paper

    Returns
    -------
    Paper
        The latest paper
    """
    return get_n_papers(1)[0]


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
