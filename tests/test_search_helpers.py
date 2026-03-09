import unittest
import argparse
from unittest.mock import patch, MagicMock

import main
from main import tokenize_search, compute_deal_score, brand_matches


class TestSearchHelpers(unittest.TestCase):
    def test_tokenize_search_normalizes_and_strips_year_and_category(self):
        categories = {"blizzard": "https://www.evo.com/shop/ski/skis/blizzard"}
        tokens = tokenize_search("Blizzard Zero G 105 Skis 2026", categories)
        self.assertEqual(tokens, ["zero", "105", "ski"])

    def test_tokenize_search_deduplicates_terms(self):
        tokens = tokenize_search("Skis skis SKIS Blizzard", None)
        self.assertEqual(tokens, ["ski", "blizzard"])

    def test_tokenize_search_drops_single_letter_alpha_tokens(self):
        tokens = tokenize_search("Zero G 105", None)
        self.assertEqual(tokens, ["zero", "105"])

    def test_fallback_prefers_brand_category_over_generic_search_term(self):
        args = argparse.Namespace(
            config="configs/evo_skis_config.json",
            output=None,
            search="Blizzard Zero G 105 Skis 2026",
            search_field="name",
            category=None,
            brand="Blizzard",
            score=False,
            json_only=False,
        )
        cfg = {
            "name": "EVO Skis Crawler",
            "categories": {
                "ski": "https://www.evo.com/shop/ski/skis",
                "blizzard": "https://www.evo.com/shop/ski/skis/blizzard",
            }
        }

        crawler = MagicMock()
        # first run: search path returns empty; second run: fallback category returns empty
        crawler.run.side_effect = [[], []]

        with patch.object(main.argparse.ArgumentParser, "parse_args", return_value=args):
            with patch.object(main, "GenericCrawler", return_value=crawler):
                with patch.object(main.json, "load", return_value=cfg):
                    with patch("builtins.open", unittest.mock.mock_open(read_data="{}")):
                        with patch.object(main, "filter_results", side_effect=lambda r, *_: r):
                            main.main()

        self.assertEqual(crawler.run.call_count, 2)
        # fallback call should use brand category instead of generic ski category
        self.assertEqual(crawler.run.call_args_list[1].kwargs, {"query": None, "category": "blizzard"})

    def test_compute_deal_score_uses_sale_and_original_price_from_flattened_evo_text(self):
        item = {
            "name": "Atomic Backland 102 Skis 20265.01 Review$749.95$599.95Sale",
            "brand": "Atomic",
            "price": "$599.95",
            "link": "https://www.evo.com/skis/atomic-backland-102",
        }
        score = compute_deal_score(item)
        self.assertGreater(score, 100.0)
        self.assertAlmostEqual(score, 130.99799986665778)

    def test_brand_matches_falls_back_to_name_when_brand_field_missing(self):
        item = {
            "name": "Beretta M9 9mm Pistol",
            "price": "$499.99",
        }
        self.assertTrue(brand_matches(item, "Beretta"))
        self.assertFalse(brand_matches(item, "Glock"))


if __name__ == "__main__":
    unittest.main()
