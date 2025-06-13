#!/usr/bin/env python3
"""
Creates basic Sphinx (*.rst) file structure for a bash (*.sh) script.

Usage:
	python generate_rst.py <bash-file-name>

(C) MMIV, mk & hb.

Created: 2025.06.13
Updated: 2025.06.13
"""

import sys
import os

def generate_rst(script_name):
    """
    Generates RST file for bash script
    
    Args:
        script_name: script name without extension (e.g. 'test')
    """
    # Capitalize first letter
    title = script_name.capitalize() + " Script"
    
    # Header line length
    header_line = "=" * len(title)
    
    # RST file content
    rst_content = f"""{title}
{header_line}

.. literalinclude:: {script_name}.sh
   :start-after: # docs-start
   :end-before: # docs-end
   :language: text
"""
    
    # Output file name
    output_file = f"{script_name}.rst"
    
    # Save file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(rst_content)
    
    print(f"Generated: {output_file}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python generate_rst.py <script_name>")
        print("Example: python generate_rst.py test")
        sys.exit(1)
    
    script_name = sys.argv[1]
    
    # Remove .sh extension if provided
    if script_name.endswith('.sh'):
        script_name = script_name[:-3]
    
    generate_rst(script_name)

if __name__ == "__main__":
    main()
