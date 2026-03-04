# my-crawlers
Crawlers for my daily life

## Setup

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

Search for Beretta M9 and save results:
```bash
source venv/bin/activate
python main.py --config configs/gundeals_config.json --search "Beretta M9" --output beretta_m9_deals.json
```

## Configuration

Each crawler has a corresponding JSON configuration file in the `configs/` directory. Customize the URL and extraction rules in these files to suit your needs.
