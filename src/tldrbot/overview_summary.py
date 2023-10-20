from transformers import pipeline

from src.tldrbot.main import Paper

MODEL = "meta-llama/Llama-2-7b-chat-hf"
PROMPT_TEMPLATE = "Generate an overview sentence of the following {num_document} documents in one sentence.\n"


def generate_overview(papers: list[Paper]) -> str:
    pipe = pipeline("text-generation", model=MODEL, device_map="auto")

    prompt = (
        PROMPT_TEMPLATE.format(len(papers))
        + "\n".join([f"Document {i}: {paper.tldr}" for i, paper in enumerate(papers)])
        + "\nThere are papers that present"
    )

    out = pipe(prompt, max_new_tokens=512)
    summary = out[0]["generated_text"]
    assert isinstance(summary, str)
    return summary
