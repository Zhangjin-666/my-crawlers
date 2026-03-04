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

def main():
    parser = argparse.ArgumentParser(description="Generic Web Crawler CLI")
    parser.add_argument("--config", help="Path to the JSON configuration file", required=True)
    parser.add_argument("--output", help="Path to save the output JSON (optional)")
    parser.add_argument("--search", help="Keyword to search on the site (will be sent to search_url template)")
    parser.add_argument("--search-field", default="name", help="Field to further filter results after fetch (default: name)")
    parser.add_argument("--category", help="Fetch a specific category defined in the config (e.g. handgun)")

    args = parser.parse_args()

    try:
        with open(args.config, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: Config file '{args.config}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from '{args.config}'.")
        sys.exit(1)

    crawler = GenericCrawler(config)

    # compute crawl parameters and delegate to the engine
    print(f"Starting crawler: {config.get('name', 'Unnamed Crawler')}...")
    if args.category:
        print(f"Fetching category '{args.category}'")
    if args.search:
        print(f"Searching remote with keyword: '{args.search}'")

    try:
        results = crawler.run(query=args.search, category=args.category)
        print(f"Successfully crawled {len(results)} items.")

        # local filtering tokens
        if args.search:
            tokens = tokenize_search(args.search, config.get('categories'))
            print(f"Applying local filter for tokens: {tokens} (field: {args.search_field})")
            results = filter_results(results, tokens, args.search_field)
            print(f"{len(results)} items remain after local filtering.")

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
                print(f"No matches found; falling back to category '{cat_choice}' and re-filtering without the category term.")
                cat_results = crawler.run(query=None, category=cat_choice)
                # recompute tokens excluding the category word
                tokens = tokenize_search(args.search, {cat_choice: True})
                cat_results = filter_results(cat_results, tokens, args.search_field)
                print(f"{len(cat_results)} items found in category after filtering.")
                results = cat_results

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=4)
            print(f"Results saved to {args.output}")
        else:
            print(json.dumps(results, indent=4))

    except Exception as e:
        print(f"An error occurred during crawling: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
