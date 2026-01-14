# QR Code Label Generator

Generate sequential QR codes for tracking labels using the SL655 label template (4x6 grid, 24 labels per sheet).

## Project Structure

```
 BarcodePrinter/
├── src/
│   └── generate_labels.py    # Main script
├── templates/
│   └── SL655.pdf              # Label template
├── output/                    # Generated PDFs (created automatically)
├── requirements.txt           # Python dependencies
└── README.md
```

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Generate 24 labels starting from ITEM-0001:
```bash
python3 src/generate_labels.py --base-url "https://example.com/item/" --count 24
```

Output will be saved to `output/labels.pdf`

### Generate Without Template

Generate QR codes without overlaying on the template (plain labels):
```bash
python3 src/generate_labels.py --base-url "https://example.com/item/" --count 24 --no-template
```

### Custom Prefix

Generate keg labels with KEG- prefix:
```bash
python3 src/generate_labels.py --base-url "https://example.com/keg/scan/" --prefix "KEG-" --count 24
```

### Specify Starting Number

Generate 48 labels starting from KEG-0100:
```bash
python3 src/generate_labels.py --base-url "https://example.com/keg/scan/" --prefix "KEG-" --start 100 --count 48
```

### Custom Output Filename

```bash
python3 src/generate_labels.py --base-url "https://example.com/item/" --count 24 --output output/my_labels.pdf
```

### All Options

```bash
python3 src/generate_labels.py --base-url "https://example.com/item/" --prefix "ITEM-" --start 1 --count 24 --output output/labels.pdf --template templates/SL655.pdf
```

## Command Line Arguments

- `--base-url`: Base URL for QR codes (required, e.g., https://example.com/item/)
- `--prefix`: Prefix for item IDs (default: ITEM-)
- `--start`: Starting item number (default: 1)
- `--count`: Number of labels to generate (required)
- `--output`: Output PDF filename (default: output/labels.pdf)
- `--template`: Path to label template (default: templates/SL655.pdf)
- `--no-template`: Generate QR codes without merging with template

## Examples

**Generate one full sheet (24 labels) for inventory tracking:**
```bash
python3 src/generate_labels.py --base-url "https://mycompany.com/inventory/" --prefix "INV-" --count 24
```

**Generate keg tracking labels KEG-0050 through KEG-0099:**
```bash
python3 src/generate_labels.py --base-url "https://brewery.com/keg/scan/" --prefix "KEG-" --start 50 --count 50
```

**Generate 100 asset labels (will create 5 sheets):**
```bash
python3 src/generate_labels.py --base-url "https://company.com/asset/" --prefix "ASSET-" --start 1 --count 100
```

**Generate QR codes without template (plain labels on blank paper):**
```bash
python3 src/generate_labels.py --base-url "https://example.com/item/" --count 24 --no-template
```

## Output

The script will:
- Generate QR codes for each sequential item number
- Overlay them onto the SL655.pdf template (unless `--no-template` is used)
- Add the item ID text below each QR code
- Output a print-ready PDF file

Each QR code encodes a URL in the format:
```
{base-url}{prefix}{number}
```

For example, with `--base-url "https://example.com/item/"` and `--prefix "ITEM-"`:
```
https://example.com/item/ITEM-0001
https://example.com/item/ITEM-0002
...
```

## Notes

- The template supports 24 labels per sheet (4 columns x 6 rows)
- Multiple sheets will be generated automatically if count > 24
- QR codes are centered within each label area
- The script uses exact SL655 specifications (38mm x 38mm labels) for accurate printing
- Works with any URL and prefix - perfect for inventory, asset tracking, keg management, etc.
- Use `--no-template` to print on blank label sheets or other templates
