from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import feedparser
from PyPDF2 import PdfReader
import io

class ContentParser:
    @staticmethod
    def parse_html(content: str, url: str):
        soup = BeautifulSoup(content, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()

        title = soup.title.string if soup.title else urlparse(url).netloc
        text = soup.get_text(separator=" ", strip=True)
        links = [urljoin(url, a.get("href", "")) for a in soup.find_all("a", href=True)]

        return {
            "title": title,
            "content": text[:5000],
            "links": links[:50],
            "content_type": "html",
        }

    @staticmethod
    def parse_xml(content: str, url: str):
        soup = BeautifulSoup(content, "xml")
        text = soup.get_text(separator=" ", strip=True)
        return {
            "title": urlparse(url).path.split("/")[-1] or urlparse(url).netloc,
            "content": text[:5000],
            "links": [],
            "content_type": "xml",
        }

    @staticmethod
    def parse_rss(url: str):
        feed = feedparser.parse(url)
        items = []
        for entry in feed.entries[:20]:
            items.append(
                {
                    "title": entry.get("title", "N/A"),
                    "content": entry.get("summary", entry.get("description", ""))[:5000],
                    "url": entry.get("link", url),
                    "links": [entry.get("link", "")],
                    "content_type": "rss",
                    "published": entry.get("published", None),
                }
            )
        return items

    @staticmethod
    def parse_pdf(content: bytes, url: str):
        pdf = PdfReader(io.BytesIO(content))
        text = ""
        for page in pdf.pages[:10]:
            extracted = page.extract_text() or ""
            text += extracted + " "
        return {
            "title": urlparse(url).path.split("/")[-1] or urlparse(url).netloc,
            "content": text[:5000],
            "links": [],
            "content_type": "pdf",
        }

    @staticmethod
    def parse_text(content: str, url: str):
        return {
            "title": urlparse(url).path.split("/")[-1] or urlparse(url).netloc,
            "content": content[:5000],
            "links": [],
            "content_type": "txt",
        }
