import logging
import re
from collections import Counter

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger("rag-app")


def chunk_text(text: str, chunk_size: int = 200, overlap: int = 20) -> list[str]:
    """
    Splits the input text into overlapping chunks of fixed size.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end].strip())
        start += chunk_size - overlap
    return chunks


def auto_tag(text: str, top_n: int = 3) -> list[str]:
    """
    Extracts the top N most common 'important' words (length ≥ 4) from the text.
    """
    words = re.findall(r"\b\w{4,}\b", text.lower())
    common = Counter(words).most_common(top_n)
    return [word for word, _ in common]
