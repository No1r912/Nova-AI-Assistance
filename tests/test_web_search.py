import unittest

from core.web_search import _ResultParser, _unique_results, _unwrap_url


class WebSearchTests(unittest.TestCase):
    def test_parser_extracts_title_url_and_snippet(self):
        parser = _ResultParser()
        parser.feed('''
            <a class="result__a" href="/l/?uddg=https%3A%2F%2Fexample.com%2Fguide%23top">
              Example <b>guide</b>
            </a>
            <div class="result__snippet">A useful <em>summary</em>.</div>
        ''')
        self.assertEqual(
            parser.results,
            [("Example guide", "https://example.com/guide", "A useful summary.")],
        )

    def test_parser_accepts_newer_result_markup(self):
        parser = _ResultParser()
        parser.feed(
            '<a data-testid="result-title-a" href="https://example.org">Title</a>'
            '<div data-testid="result-snippet">Details</div>'
        )
        self.assertEqual(parser.results[0], ("Title", "https://example.org", "Details"))

    def test_unwrap_rejects_unsafe_urls_and_removes_fragments(self):
        self.assertEqual(_unwrap_url("javascript:alert(1)"), "")
        self.assertEqual(_unwrap_url("https://example.com/path#section"), "https://example.com/path")

    def test_unique_results_preserves_first_result(self):
        results = [("First", "https://example.com", "one"), ("Duplicate", "https://EXAMPLE.com", "two")]
        self.assertEqual(_unique_results(results, 5), [results[0]])


if __name__ == "__main__":
    unittest.main()
