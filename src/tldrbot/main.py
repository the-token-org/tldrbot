import os
from dataclasses import dataclass, field
from pathlib import Path

import discord
import feedparser
import requests
import sienna
from dotenv import load_dotenv
from schnitsum import SchnitSum

load_dotenv()
URL = os.environ.get("URL")
assert isinstance(URL, str)

USED_URLS_PATH = Path("./used_urls_path.txt")
ARXIV_QUERY_URL = "http://export.arxiv.org/api/query?search_query=cat:cs.CL&max_results=1&sortBy=lastUpdatedDate&sortOrder=descending"


if not USED_URLS_PATH.exists():
    USED_URLS_PATH.touch()


@dataclass
class Paper:
    title: str
    abstract: str
    url: str
    authors: list[str]
    tldr: str = field(init=False)

    def __post_init__(self):
        self.tldr = self.generate_tldr()

    def generate_tldr(self) -> str:
        model = SchnitSum("sobamchan/bart-large-scitldr")
        return model([self.abstract])[0]

    @classmethod
    def get_latest(cls):
        res = feedparser.parse(ARXIV_QUERY_URL)
        paper = res["entries"][0]
        return cls(
            paper["title"],
            paper["summary"],
            paper["link"],
            [author["name"] for author in paper["authors"]],
        )

    def to_markdown(self) -> str:
        return f"""[{self.title}]({self.url})
**TLDR**: {self.tldr}"""


def post(paper: Paper):
    session = requests.Session()
    webhook = discord.webhook.SyncWebhook.from_url(URL, session=session)
    webhook.send(paper.to_markdown())


def run():
    used_urls = sienna.load(str(USED_URLS_PATH))

    paper = Paper.get_latest()

    if paper.url in used_urls:
        return

    post(paper)

    assert isinstance(used_urls, list)
    used_urls.append(paper.url)
    sienna.save(used_urls, str(USED_URLS_PATH))


if __name__ == "__main__":
    run()
