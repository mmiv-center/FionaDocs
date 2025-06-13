#!/usr/bin/env python3

"""
Extract docstring from the beginning of the bsh (*.sh) file and generate Sphinx documentation (*.rst) file.

Created: 2025.06.12
Updated: 2025.06.12
"""

from pathlib import Path

def extract_docstring_from_single_file(file_path):
    """Extract docstring from the beginning of the .sh file."""

    file_path = Path(file_path)
    if not file_path.exists():
        print(f"File {file_path} does not exist!")
        return None
    
    if not file_path.is_file():
        print(f"File {file_path} is not a file!")
        return None
    
    # Read file
    with open(file_path, 'r') as f:
        lines = f.readlines()

    # Initialize empty list for docstring
    docstring = []
    
    # Process each line
    for line in lines:
        line = line.strip()
        
        # Skip shebang and empty lines
        if line.startswith('#!') or line == '':
            continue
            
        # If line starts with #
        if line.startswith('#'):
            # Remove # and add to docstring
            clean_line = line[1:].strip()
            docstring.append(clean_line)
        else:
            # First non-comment => end of docstring
            break    

    # Join docstring lines with newlines
    return '\n'.join(docstring)


def generate_rst_for_single_file(script_name: str, docstring: str, saved_rst_folder: Path = Path('.'), verbose: bool = False):
    """Generate and save RST file in the saved_rst folder"""

    # Create RST file
    # WARNING: Should we save the extention .sh in an .rst file?
    title = f"{script_name}"
    rst = f"""{title}
{'=' * len(title)}

{docstring}
"""
    # Create folder and file pahts
    saved_rst_file = saved_rst_folder / f'{script_name}.rst'
    # Save RST file
    with open(saved_rst_file, 'w') as f:
        f.write(rst)
    
    if verbose:
        print(f"Created: {saved_rst_file}")
        

def main(): 
    """Process bunch of *.sh files from txt file."""

    bunch_of_sh_files_to_process = 'script_paths_2.txt'



    files_to_process = []
    with open(bunch_of_sh_files_to_process, 'r') as f:
        for line in f:
            # Remove whitespace
            path = line.strip()
            if path:  # Check if line is not empty
                files_to_process.append(path)

    for file in files_to_process:
        if file.endswith('.sh'):
            print(f'Processing: {file}')
            docstring = extract_docstring_from_single_file(file)
            if docstring:
                rst_content = generate_rst_for_single_file(file, docstring, verbose=True)
            else:
                print(f"No docstring found for {file}")
            #print(rst_content)

if __name__ == "__main__":
    main()


    





