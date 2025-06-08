# FionaDocs
FIONA (Flash-based Input/Output Network Appliance) - A secure research data gateway for medical imaging. Provides DICOM anonymization, quarantine management, and automated transfer from clinical to research PACS systems while ensuring GDPR compliance.


## Sphinx
1. [Installation](https://www.sphinx-doc.org/en/master/usage/installation.html)
2. Check the installed sphinx verskon: 
```
sphinx-build --version
```
3. Folder structure:
```
FionaDocs/
└── docs/
    ├── build/          # Generated documentation output
    ├── source/         # Source files for documentation
    │   ├── conf.py     # Sphinx configuration file
    │   └── index.rst   # Main documentation file
    ├── make.bat        # Windows batch file for building
    └── Makefile        # Unix makefile for building
```
4. Build the HTML documentation
   ```
   cd docs
   make html
   ```
5. Generate PDF documentation
   ```
   cd docs
   make latex
   ```
6. Generate PDF from LaTeX
```
cd build/latex
pdflatex fionadocs.tex
```
