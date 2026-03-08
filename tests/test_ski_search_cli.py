import unittest

from ski_search import build_search_query, select_category


class TestSkiSearchCLI(unittest.TestCase):
    def test_build_search_query_adds_brand_when_missing(self):
        q = build_search_query("Blizzard", "Zero 105")
        self.assertEqual(q, "Blizzard Zero 105")

    def test_build_search_query_avoids_duplicate_brand(self):
        q = build_search_query("Blizzard", "Blizzard Zero 105")
        self.assertEqual(q, "Blizzard Zero 105")

    def test_select_category_prefers_brand(self):
        categories = {
            "ski": "https://www.evo.com/shop/ski/skis",
            "blizzard": "https://www.evo.com/shop/ski/skis/blizzard",
        }
        cat = select_category(categories, "Blizzard", "Blizzard Zero 105")
        self.assertEqual(cat, "blizzard")

    def test_select_category_from_model_tokens(self):
        categories = {
            "ski": "https://www.evo.com/shop/ski/skis",
            "backcountry": "https://www.evo.com/shop/ski/backcountry",
        }
        cat = select_category(categories, "Unknown", "Backcountry 105")
        self.assertEqual(cat, "backcountry")


if __name__ == "__main__":
    unittest.main()
