from typing import Optional

try:
    from readability import Document  # type: ignore
    from bs4 import BeautifulSoup  # type: ignore
    HAVE_READABILITY = True
except Exception:
    HAVE_READABILITY = False
    try:
        from bs4 import BeautifulSoup  # type: ignore
    except Exception:  # pragma: no cover
        BeautifulSoup = None  # type: ignore


def html_to_text(html: str) -> str:
    if BeautifulSoup is None:
        return ""
    if HAVE_READABILITY:
        try:
            doc = Document(html)
            summary_html = doc.summary(html_partial=True)
            soup = BeautifulSoup(summary_html, "lxml")
            _strip(soup)
            return soup.get_text("\n")
        except Exception:
            pass
    # Fallback: basic soup clean
    soup = BeautifulSoup(html, "lxml")
    _strip(soup)
    return soup.get_text("\n")


def _strip(soup):
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "aside"]):
        tag.decompose()

