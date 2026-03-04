# my-crawlers
Crawlers for my daily life

## Setup

### macOS / Linux (General)

1. Create a virtual environment:
```bash
python3 -m venv venv
```

2. Activate the virtual environment:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
playwright install
```

### Ubuntu 22 LTS

#### System Prerequisites

First, install Python3 and required system packages:

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv
```

For Playwright to work properly, install additional system dependencies:

```bash
sudo apt install -y libgconf-2-4 libnss3 libxss1 libappindicator1 libindicator7 libgbm1 libxss1 fonts-liberation xdg-utils
```

#### Project Setup

1. Clone the repository and navigate to the project:
```bash
cd my-crawlers
```

2. Create a virtual environment:
```bash
python3 -m venv venv
```

3. Activate the virtual environment:
```bash
source venv/bin/activate
```

4. Upgrade pip:
```bash
pip install --upgrade pip
```

5. Install Python dependencies:
```bash
pip install -r requirements.txt
```

6. Install Playwright browsers:
```bash
playwright install
```

This will download the necessary browser binaries (Chromium, Firefox, WebKit).

#### Running the Crawler on Ubuntu

Once setup is complete, you can run the crawler:

```bash
source venv/bin/activate
python main.py --config configs/gundeals_config.json
```

Or search for specific items:
```bash
source venv/bin/activate
python main.py --config configs/gundeals_config.json --search "Beretta"
```

#### Troubleshooting on Ubuntu

- **Permission denied errors**: Make sure you're in the correct directory and have read permissions
- **Playwright headless issues**: Ensure all system dependencies are installed with the commands above
- **Memory issues**: On low-memory systems, consider running one crawler at a time

## Usage

### Quick Shortcuts

**Gun Deals Crawler:**
```bash
source venv/bin/activate && python main.py --config configs/gundeals_config.json
```

**News Crawler:**
```bash
source venv/bin/activate && python main.py --config configs/news_config.json
```

**Price Crawler:**
```bash
source venv/bin/activate && python main.py --config configs/price_config.json
```

### General Usage

Run the crawler with a configuration file:
```bash
python main.py --config <config_file_path> [--output <output_file_path>] [--search <keyword>]
```

**Arguments:**
- `--config` (required): Path to the JSON configuration file
- `--output` (optional): Path to save the output JSON file. If not specified, results are printed to stdout
- `--search` (optional): Search for items by keyword (searches in name field by default)
- `--search-field` (optional): Field to search in (default: name)

### Examples

Run gun.deals crawler and save output:
```bash
source venv/bin/activate
python main.py --config configs/gundeals_config.json --output gun_deals_results.json
```

Search for a specific gun (e.g., Beretta):
```bash
source venv/bin/activate
python main.py --config configs/gundeals_config.json --search "Beretta"
```

Search with multiple keywords – the crawler will tokenize and match all terms:
```bash
source venv/bin/activate
python main.py --config configs/gundeals_config.json --search "Beretta M9 9mm handgun"
```
(This query will internally strip the generic word "handgun" and return Beretta M9 results.)

---

### EVO skis

A new configuration is provided at `configs/evo_skis_config.json` for scraping
ski deals from the EVO website.  Because EVO’s Cloudflare protection is strict,
Playwright must be used, and you may need to run the crawler from an IP that’s
not blocked.

You can search by brand and rank results by a simple “good deal” score:

```bash
source venv/bin/activate
python main.py --config configs/evo_skis_config.json \
    --search "fischer" --brand "Fischer" --score
```

**Deal metric:**
1. Higher price with a larger discount ratio produces a higher score.
2. Newer model years (looks for 2015+ in the product name) add bonus points.
3. Brand filtering is supported via `--brand`.

Results will include a `deal_score` field and are sorted when `--score` is used.

Search for Beretta M9 and save results:
```bash
source venv/bin/activate
python main.py --config configs/gundeals_config.json --search "Beretta M9" --output beretta_m9_deals.json
```

## Configuration

Each crawler has a corresponding JSON configuration file in the `configs/` directory. Customize the URL and extraction rules in these files to suit your needs.
