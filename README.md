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

1. Use Python 3.11 or newer in a virtual environment, then install the locked dependencies:
```bash
python3 -m venv venv
# Linux/macOS; on Windows use venv\\Scripts\\activate
source venv/bin/activate
python -m pip install --require-hashes -r requirements.txt
```

This is a local command-line tool, not a hosted service. No account or network
connection is needed to generate labels after installation.

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

## Dependency security and regression checks

`requirements.in` records the direct dependency choices. `requirements.txt` is
the installable lock: all runtime dependencies (including transitive packages)
have exact versions and distribution hashes. Keep both files in security PRs.
The Windows-only qrcode dependency `colorama` is locked on every platform so the
same file can be installed with hash checking on Windows and Linux.

The PDF reader uses maintained `pypdf` instead of `PyPDF2`, which has no patched
release for [GHSA-4vvm-4w3v-6mr8](https://github.com/advisories/GHSA-4vvm-4w3v-6mr8).
Pillow is pinned to a security-patched version. Unaffected qrcode and ReportLab
versions are retained rather than routinely upgraded.

To refresh the lock after a reviewed security change, use Python 3.11 and an
isolated tooling environment:

```bash
python3.11 -m venv tooling-venv
# Linux/macOS commands; use the equivalent Scripts paths on Windows.
tooling-venv/bin/python -m pip install pip-tools==7.5.3 pip-audit==2.10.1
tooling-venv/bin/pip-compile --generate-hashes --no-strip-extras --no-emit-index-url --no-emit-trusted-host --output-file=requirements.txt requirements.in
tooling-venv/bin/pip-audit --requirement requirements.txt --require-hashes --disable-pip --strict
python -m pip install --require-hashes -r requirements.txt
python -m pip check
python -W error -m unittest discover -s tests -v
```

The security workflow runs these installation, PDF regression and audit checks on
pull requests, main-branch pushes and a weekly schedule. Tests invoke the actual
CLI, parse generated PDFs, verify page dimensions, sequential label text and
embedded QR images, exercise the real template, and guard against the EOF-comment
PDF-parser hang. Auditing fails on known vulnerabilities or collection errors;
it does not suppress advisories or automatically modify dependencies.

GitHub's dependency graph can read the exact runtime versions from
`requirements.txt`, including the listed transitive packages. See GitHub's
[dependency graph documentation](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependency-graph-data).
Repository-level Dependabot security updates can propose fixes for alerts without
a version-update schedule; see
[Dependabot security updates](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependabot-security-updates).
No routine version-update configuration or paid security service is required.
CodeQL remains managed separately by the repository's default setup.
