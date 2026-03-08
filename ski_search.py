#!/usr/bin/env python3
import argparse
import json
import os
import re
import subprocess
import sys
from typing import Dict, Optional, List


def normalize_token(token: str) -> str:
    token = token.strip().lower()
    if not token:
        return ""
    if len(token) == 1 and token.isalpha():
        return ""
    if re.fullmatch(r"(19|20)\d{2}", token):
        return ""
    if len(token) > 3 and token.endswith("ies"):
        token = token[:-3] + "y"
    elif len(token) > 3 and token.endswith("s"):
        token = token[:-1]
    return token


def build_search_query(brand: str, model: str) -> str:
    b = brand.strip()
    m = model.strip()
    if b.lower() in m.lower():
        return m
    return f"{b} {m}".strip()


def select_category(categories: Dict[str, str], brand: str, model: str) -> Optional[str]:
    if not categories:
        return None

    keys = list(categories.keys())
    b = brand.strip().lower()

    # Most specific signal first: explicit brand category.
    for key in keys:
        kl = str(key).lower()
        if kl == b or kl in b or b in kl:
            return key

    # Then token matching from model text.
    model_tokens = {normalize_token(t) for t in re.findall(r"\w+", model.lower())}
    model_tokens.discard("")
    ranked_keys = sorted(keys, key=lambda k: len(str(k)), reverse=True)
    for key in ranked_keys:
        nk = normalize_token(str(key))
        if nk and nk in model_tokens:
            return key
    return None


def build_main_cmd(
    python_bin: str,
    main_script: str,
    config_path: str,
    brand: str,
    model: str,
    output: str,
    category: str = "auto",
    no_score: bool = False,
    json_only: bool = False,
) -> List[str]:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"config not found: {config_path}")
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(f"cannot read config {config_path}: {e}") from e

    search_query = build_search_query(brand, model)
    if category.lower() == "auto":
        category = select_category(config.get("categories", {}), brand, search_query) or ""

    command = [
        python_bin,
        main_script,
        "--config",
        config_path,
        "--search",
        search_query,
        "--brand",
        brand,
        "--output",
        output,
    ]
    if category:
        command.extend(["--category", category])
    if not no_score:
        command.append("--score")
    if json_only:
        command.append("--json-only")
    return command


def run_search(
    brand: str,
    model: str,
    config_path: str = "configs/evo_skis_config.json",
    category: str = "auto",
    output: str = "output/evo_latest.json",
    python_bin: str = sys.executable,
    main_script: str = "main.py",
    no_score: bool = False,
    json_only: bool = False,
    dry_run: bool = False,
) -> int:
    try:
        command = build_main_cmd(
            python_bin=python_bin,
            main_script=main_script,
            config_path=config_path,
            brand=brand,
            model=model,
            output=output,
            category=category,
            no_score=no_score,
            json_only=json_only,
        )
    except Exception as e:  # noqa: BLE001
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print("Running:", " ".join(f"'{c}'" if " " in c else c for c in command))
    if dry_run:
        return 0

    completed = subprocess.run(command)
    return int(completed.returncode)


def main() -> int:
    parser = argparse.ArgumentParser(description="Search EVO skis by brand and model with a short command.")
    parser.add_argument("--brand", required=True, help="Brand name (e.g. Blizzard)")
    parser.add_argument("--model", required=True, help="Model keywords (e.g. Zero 105)")
    parser.add_argument("--config", default="configs/evo_skis_config.json", help="Crawler config path")
    parser.add_argument("--category", default="auto", help="Category key from config (default: auto)")
    parser.add_argument("--output", default="output/evo_latest.json", help="Output JSON path")
    parser.add_argument("--python", default=sys.executable, help="Python interpreter to run main.py")
    parser.add_argument("--main-script", default="main.py", help="Path to main crawler CLI")
    parser.add_argument("--no-score", action="store_true", help="Disable deal-score sorting")
    parser.add_argument("--json-only", action="store_true", help="Forward --json-only to main.py")
    parser.add_argument("--dry-run", action="store_true", help="Print command and exit")
    args = parser.parse_args()
    return run_search(
        brand=args.brand,
        model=args.model,
        config_path=args.config,
        category=args.category,
        output=args.output,
        python_bin=args.python,
        main_script=args.main_script,
        no_score=args.no_score,
        json_only=args.json_only,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    raise SystemExit(main())
