# helpers/config_loader.py

import json
from operator import sub
import os


def load_config(config_file='config/links.json'):
    """
    Load configuration from JSON file

    Args:
        config_file: path to JSON file (related to the main folder)

    Returns:
        dict: dictionary with confituration
    """

    try:
        # path related to the main folder, that contains conf.py
        base_dir = os.path.dirname(os.path.dirname(__file__))
        config_path = os.path.join(base_dir, config_file)

        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
        
    except FileNotFoundError:
        print(f"No such file: {config_file}")
        return {}
    
    except json.JSONDecodeError as e:
        print(f"Error in JSON file: {config_file}: {e}")
        return {}


# helpers/config_loader.py

def generate_substitutions(config):
    """
    Generuje substitutions z obsługą niestandardowych nazw
    """
    substitutions = []
    
    # URLs
    urls = config.get('urls', {})
    for key, data in urls.items():
        if isinstance(data, dict):
            # A new structure with name i url
            url = data.get('url', '')
            name = data.get('name', url)
            substitutions.append(f".. |{key}_url| replace:: {url}")
            substitutions.append(f".. |{key}_link| replace:: `{name} <{url}>`__")
        else:
            # Structure only with url
            substitutions.append(f".. |{key}_url| replace:: {data}")
            substitutions.append(f".. |{key}_link| replace:: `{data} <{data}>`__")
    
    # Contacts  
    contacts = config.get('contacts', {})
    for key, data in contacts.items():
        if isinstance(data, dict):
            # New structure
            email = data.get('email', '')
            name = data.get('name', email)
            substitutions.append(f".. |{key}_email| replace:: {email}")
            substitutions.append(f".. |{key}_contact| replace:: `{name} <mailto:{email}>`__")
        else:
            # Old structure - only email
            substitutions.append(f".. |{key}_email| replace:: {data}")
            substitutions.append(f".. |{key}_contact| replace:: `{data} <mailto:{data}>`__")
    
    return '\n'.join(substitutions)


