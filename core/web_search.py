"""Private, user-triggered web search with no API key or account access."""

from html.parser import HTMLParser
from urllib.error import URLError
from urllib.parse import parse_qs, quote_plus, unquote, urlparse, urlunparse
from urllib.request import Request, urlopen


_SEARCH_ENDPOINTS = (
    "https://html.duckduckgo.com/html/?q={query}",
    "https://lite.duckduckgo.com/lite/?q={query}",
)
_USER_AGENT = "Mozilla/5.0 (Nova local assistant; web search)"


class _ResultParser(HTMLParser):
    """Extract DuckDuckGo result links and snippets without extra dependencies."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.results = []
        self._href = None
        self._title = []
        self._snippet = []
        self._collecting_snippet = False
        self._snippet_depth = 0
        self._snippet_result_index = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = attributes.get("class", "").split()
        test_id = attributes.get("data-testid", "")
        is_result_link = tag == "a" and (
            "result__a" in classes
            or "result-link" in classes
            or test_id in {"result-title-a", "result-title"}
        )
        if is_result_link and self._href is None:
            self._href = attributes.get("href", "")
            self._title = []
            self._snippet = []

        is_snippet = (
            "result__snippet" in classes
            or "result-snippet" in classes
            or test_id == "result-snippet"
        )
        if is_snippet and self.results:
            self._collecting_snippet = True
            self._snippet_depth = 1
            self._snippet = []
            self._snippet_result_index = len(self.results) - 1
        elif self._collecting_snippet:
            self._snippet_depth += 1

    def handle_data(self, data):
        if self._collecting_snippet:
            self._snippet.append(data)
        elif self._href is not None:
            self._title.append(data)

    def handle_endtag(self, tag):
        if self._collecting_snippet:
            self._snippet_depth -= 1
            if self._snippet_depth == 0:
                self._collecting_snippet = False
                index = self._snippet_result_index
                if index is not None:
                    title, url, _ = self.results[index]
                    self.results[index] = (title, url, _clean_text(self._snippet))
                self._snippet_result_index = None

        if tag == "a" and self._href is not None:
            title = _clean_text(self._title)
            url = _unwrap_url(self._href)
            if title and url:
                self.results.append((title, url, ""))
            self._href = None
            self._title = []
            self._snippet = []
            self._collecting_snippet = False
            self._snippet_depth = 0
            self._snippet_result_index = None


def _clean_text(parts):
    return " ".join("".join(parts).split())


def _unwrap_url(url):
    """Return a safe destination from a DuckDuckGo redirect or direct URL."""
    parsed = urlparse(url)
    is_redirect = (
        parsed.netloc.endswith("duckduckgo.com") and parsed.path.startswith("/l/")
    ) or url.startswith("/l/")
    if is_redirect:
        url = unquote(parse_qs(parsed.query).get("uddg", [""])[0])

    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return ""
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, parsed.query, ""))


def _unique_results(results, limit):
    unique, seen = [], set()
    for title, url, snippet in results:
        if url.lower() in seen:
            continue
        seen.add(url.lower())
        unique.append((title, url, snippet))
        if len(unique) == limit:
            break
    return unique


def _search_endpoint(endpoint, query):
    request = Request(
        endpoint.format(query=quote_plus(query)),
        headers={"User-Agent": _USER_AGENT, "Accept": "text/html"},
    )
    with urlopen(request, timeout=12) as response:
        page = response.read().decode("utf-8", errors="replace")
    parser = _ResultParser()
    parser.feed(page)
    return parser.results


def search(query, limit=5):
    """Return DuckDuckGo results with source URLs and concise snippets."""
    query = query.strip()
    if not query:
        raise ValueError("Enter a search query.")
    if len(query) > 300:
        raise ValueError("Search queries must be 300 characters or fewer.")
    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 10:
        raise ValueError("Search result limit must be between 1 and 10.")

    last_error = None
    results = []
    for endpoint in _SEARCH_ENDPOINTS:
        try:
            results = _unique_results(_search_endpoint(endpoint, query), limit)
        except (OSError, URLError) as error:
            last_error = error
            continue
        if results:
            break

    if not results:
        if last_error:
            raise OSError("The search service could not be reached. Check your internet connection and try again.") from last_error
        return "No results found. Try a more specific search."

    formatted = []
    for index, (title, url, snippet) in enumerate(results, 1):
        item = f"{index}. {title}\n   {url}"
        if snippet:
            item += f"\n   {snippet[:240]}"
        formatted.append(item)
    return "Web results for: " + query + "\n\n" + "\n\n".join(formatted)
