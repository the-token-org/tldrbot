from dataclasses import dataclass, field

from schnitsum import SchnitSum


@dataclass
class Paper:
    title: str
    abstract: str
    url: str
    authors: list[str]
    summarizer: SchnitSum
    tldr: str = field(init=False)

    def __post_init__(self):
        self.tldr = self.generate_tldr()

    def generate_tldr(self) -> str:
        return self.summarizer([self.abstract])[0]

    def to_markdown(self) -> str:
        return f"""[{self.title}]({self.url})
**TLDR**: {self.tldr}"""
