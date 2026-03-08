#!/usr/bin/env python3
import argparse

from ski_search import run_search


def prompt_value(label: str, default: str = "", required: bool = False) -> str:
    while True:
        suffix = f" [{default}]" if default else ""
        value = input(f"{label}{suffix}: ").strip()
        if not value and default:
            return default
        if value:
            return value
        if not required:
            return ""
        print("Value is required.")


def parse_yes_no(value: str, default: bool = True) -> bool:
    v = value.strip().lower()
    if not v:
        return default
    if v in {"y", "yes", "true", "1", "on"}:
        return True
    if v in {"n", "no", "false", "0", "off"}:
        return False
    return default


def main() -> int:
    parser = argparse.ArgumentParser(description="Interactive CLI for ski brand/model search.")
    parser.add_argument("--config", default="configs/evo_skis_config.json", help="Crawler config path")
    parser.add_argument("--python", default="python", help="Python interpreter for main.py")
    parser.add_argument("--main-script", default="main.py", help="Path to main crawler CLI")
    parser.add_argument("--output-default", default="output/evo_latest.json", help="Default output path")
    parser.add_argument("--category-default", default="auto", help="Default category (auto recommended)")
    parser.add_argument("--no-score-default", action="store_true", help="Disable score sorting by default")
    args = parser.parse_args()

    print("Interactive ski search. Type 'q' at Brand to quit.")
    while True:
        brand = prompt_value("Brand", required=True)
        if brand.lower() in {"q", "quit", "exit"}:
            break

        model = prompt_value("Model", required=True)
        category = prompt_value("Category", default=args.category_default)
        output = prompt_value("Output file", default=args.output_default)
        score_default = "n" if args.no_score_default else "y"
        score_input = prompt_value("Enable score sorting? (y/n)", default=score_default)
        enable_score = parse_yes_no(score_input, default=not args.no_score_default)

        code = run_search(
            brand=brand,
            model=model,
            config_path=args.config,
            category=category,
            output=output,
            python_bin=args.python,
            main_script=args.main_script,
            no_score=not enable_score,
        )
        print(f"Done (exit code: {code})")

        again = prompt_value("Search again? (y/n)", default="y")
        if not parse_yes_no(again, default=True):
            break

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
