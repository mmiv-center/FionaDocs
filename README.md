# FionaDocs

FIONA (Flash-based Input/Output Network Appliance) - a secure research data gateway for medical imaging. It provides DICOM anonymization, quarantine management, and automated transfer from clinical to research PACS systems while ensuring GDPR compliance.

This repository contains the Sphinx sources of the FIONA documentation (HTML and PDF).


## Repository layout

```
FionaDocs/
├── source/                  # Documentation sources
│   ├── conf.py              # Sphinx configuration
│   ├── index.rst            # Main page
│   ├── EndUser/             # End user documentation
│   ├── SystemAdmin/         # System administration documentation
│   ├── Developer/           # Developer documentation
│   │   └── scripts/         # One .rst page per Fiona script + setup.sh
│   ├── config/links.json    # URLs and names used as RST substitutions
│   ├── helpers/             # Loader that turns links.json into substitutions
│   ├── _static/             # Images, custom CSS/JS
│   └── titlepage.tex        # PDF title page
├── build/                   # Generated output (not tracked by git)
├── requirements.txt         # Python packages needed for the build
├── Makefile                 # Unix build entry point (make html, make latexpdf)
└── make.bat                 # Windows build entry point
```


## Workflow

The documentation is edited on any machine, pushed to GitHub, and the **final HTML and PDF are built on the Fiona server**.

The developer pages (`source/Developer/scripts/*.rst`) include the docstrings of the Fiona scripts (`.py`, `.sh`, `.php`). These scripts are **not tracked by git** (see `.gitignore`), so they must be provided on every machine before building:

- **Fiona server:** run `setup.sh`, which creates symbolic links to the live scripts.
- **Any other machine:** manually copy the current scripts from the Fiona server into `source/Developer/scripts/` before each build.


## One-time installation

The steps below are the same on the Fiona server and on a workstation (tested on Ubuntu 24.04, Python 3.12).

### 1. System packages

```bash
# Python virtual environments
sudo apt install -y python3-venv

# LaTeX (only needed for the PDF)
sudo apt install -y texlive-latex-recommended texlive-latex-extra \
                    texlive-fonts-recommended tex-gyre latexmk
```

Optional: Mermaid diagrams require the Mermaid CLI (`mmdc`):

```bash
sudo npm install -g @mermaid-js/mermaid-cli
```

### 2. Clone the repository

```bash
git clone git@github.com:mmiv-center/FionaDocs.git
cd FionaDocs
```

### 3. Python environment

```bash
python3 -m venv .venv --prompt fionadocs
source .venv/bin/activate          # the prompt now starts with (fionadocs)
pip install -r requirements.txt
```

### 4. Fiona scripts (Fiona server only)

```bash
cd source/Developer/scripts
./setup.sh --dry-run               # show which links would be created
./setup.sh                         # create symbolic links to the Fiona scripts
cd -
```

`setup.sh` must be run from inside `source/Developer/scripts/`. Check that the Fiona version set in `FIONA_VERSION` (e.g. `fiona_v20250919`) matches the version installed under `/var/www/html/`.


## Building the documentation

```bash
cd FionaDocs

# 1. Update the Fiona scripts in source/Developer/scripts/
#    - Fiona server: links from setup.sh are always current
#    - other machines: copy the current scripts from the Fiona server

# 2. Activate the Python environment
source .venv/bin/activate

# 3. Remove the previous output
make clean

# 4. HTML  ->  build/html/index.html
make html

# 5. PDF   ->  build/latex/fiona.pdf
make latexpdf

# 6. Leave the Python environment
deactivate
```

### Checking the result

- `make html` should end with `build succeeded.` - look for lines containing `WARNING` or `ERROR`.
- `make latexpdf` runs LaTeX several times. Warnings like `Rerun LaTeX` or `longtable ... Column widths have changed` are normal. The build is fine if `build/latex/fiona.pdf` is created.
- If you see `sphinx-build: command not found`, the Python environment is not activated (step 2).

To view the output:

```bash
xdg-open build/html/index.html
xdg-open build/latex/fiona.pdf
```


## Updating the Python packages

```bash
source .venv/bin/activate
pip install --upgrade sphinx sphinx_rtd_theme sphinxcontrib-mermaid
pip freeze | grep -iE "^(sphinx|sphinx.rtd.theme|sphinxcontrib-mermaid)=="
```

Copy the new versions into `requirements.txt`, commit, and run `pip install -r requirements.txt` on the Fiona server.
