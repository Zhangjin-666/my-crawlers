import json
import argparse
import sys
import re
import urllib.parse
from src.crawler.engine import GenericCrawler

def tokenize_search(search_term: str, categories: dict | None = None) -> list:
    """Convert a raw search string into a set of tokens, optionally stripping
    out any words that correspond to configured categories.

    Returns a list of lower‑cased tokens.
    """
    if not search_term:
        return []
    tokens = [tok for tok in re.findall(r"\w+", search_term.lower()) if tok]
    if categories:
        # remove tokens that exactly match any category key
        tokens = [t for t in tokens if t not in categories.keys()]
    return tokens


def filter_results(results, tokens: list, search_field="name"):
    """Keep only items where **all** tokens appear in ``search_field``.

    ``tokens`` should already be normalized to lowercase.
    """
    if not tokens:
        return results
    filtered = []
    for item in results:
        value = str(item.get(search_field, "")).lower()
        if all(tok in value for tok in tokens):
            filtered.append(item)
    return filtered

def compute_deal_score(item: dict) -> float:
    """Calculate a heuristic score for "good deal" items.

    - high absolute price * discount ratio
    - recent model year (parsed from name)
    """
    price_text = item.get("price", "") or ""
    # find all dollar amounts
    amounts = re.findall(r"\$([0-9,]+\.?\d*)", price_text)
    current = 0.0
    original = 0.0
    if amounts:
        current = float(amounts[-1].replace(',', ''))
        if len(amounts) >= 2:
            original = float(amounts[0].replace(',', ''))
    discount = 0.0
    if original > 0:
        discount = (original - current) / original
    score = current * discount
    # year bonus
    year_match = re.search(r"20(1[5-9]|2[0-9])", item.get("name", ""))
    if year_match:
        year = int(year_match.group(0))
        score += (year - 2015)
    item["deal_score"] = score
    return score


def main():
    parser = argparse.ArgumentParser(description="Generic Web Crawler CLI")
    parser.add_argument("--config", help="Path to the JSON configuration file", required=True)
    parser.add_argument("--output", help="Path to save the output JSON (optional)")
    parser.add_argument("--search", help="Keyword to search on the site (will be sent to search_url template)")
    parser.add_argument("--search-field", default="name", help="Field to further filter results after fetch (default: name)")
    parser.add_argument("--category", help="Fetch a specific category defined in the config (e.g. handgun)")
    parser.add_argument("--brand", help="Filter results by brand name (case-insensitive)")
    parser.add_argument("--score", action="store_true", help="Compute and sort results by deal score (good deals first)")
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Keep stdout as JSON-only output and write progress logs to stderr",
    )

    args = parser.parse_args()

    def log(message: str):
        stream = sys.stderr if args.json_only else sys.stdout
        print(message, file=stream)

    try:
        with open(args.config, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: Config file '{args.config}' not found.", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from '{args.config}'.", file=sys.stderr)
        sys.exit(1)

    crawler = GenericCrawler(config)

    # compute crawl parameters and delegate to the engine
    log(f"Starting crawler: {config.get('name', 'Unnamed Crawler')}...")
    if args.category:
        log(f"Fetching category '{args.category}'")
    if args.search:
        log(f"Searching remote with keyword: '{args.search}'")

    try:
        results = crawler.run(query=args.search, category=args.category)
        log(f"Successfully crawled {len(results)} items.")

        # local filtering tokens
        if args.search:
            tokens = tokenize_search(args.search, config.get('categories'))
            log(f"Applying local filter for tokens: {tokens} (field: {args.search_field})")
            results = filter_results(results, tokens, args.search_field)
            log(f"{len(results)} items remain after local filtering.")

        # brand filter
        if args.brand:
            b = args.brand.lower()
            log(f"Applying brand filter: '{args.brand}'")
            results = [r for r in results if r.get('brand') and b in r.get('brand','').lower()]
            log(f"{len(results)} items remain after brand filtering.")

        # fallback: if nothing found and categories exist, try crawling category page
        if args.search and not results and config.get('categories'):
            # pick first category whose key appears in the original search string
            cat_choice = None
            lower = args.search.lower()
            for key in config['categories'].keys():
                if key in lower:
                    cat_choice = key
                    break
            if cat_choice:
                log(f"No matches found; falling back to category '{cat_choice}' and re-filtering without the category term.")
                cat_results = crawler.run(query=None, category=cat_choice)
                # recompute tokens excluding the category word
                tokens = tokenize_search(args.search, {cat_choice: True})
                cat_results = filter_results(cat_results, tokens, args.search_field)
                log(f"{len(cat_results)} items found in category after filtering.")
                results = cat_results

        # compute deal score and optionally sort
        if args.score:
            for item in results:
                compute_deal_score(item)
            results.sort(key=lambda r: r.get('deal_score', 0), reverse=True)
            log("Results sorted by deal score.")

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=4)
            log(f"Results saved to {args.output}")
        else:
            print(json.dumps(results, indent=4))

    except Exception as e:
        print(f"An error occurred during crawling: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
