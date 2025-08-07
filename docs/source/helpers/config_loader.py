# helpers/config_loader.py

import json
from operator import sub
import os

from matplotlib.pylab import f


def load_config(config_file='config/urls.json'):
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


def generate_substitutions(config):
    """
    Generates substitutions for Sphinx base on configuration

    Args:
        config: configuration dictionary

    Returns:
        str: generated susbstitutions
    
    """

    substitutions = []

    # URLs
    urls = config.get('urls', {})
    for key, url in urls.items():
        substitutions.append(f".. |{key}_url| replace:: {url}")
        substitutions.append(f".. |{key}_link| replace:: `{key} <{url}>`__")

    # Contacts
    contacts = config.get('contacts', {})
    for key, email in contacts.items():
        substitutions.append(f".. |{key}_email| replace:: {email}")
        substitutions.append(f".. |{key}_contact| replace:: `{email} <mailto:{email}>`__")

    # Internal
    internal = config.get('internal', {})
    for key, url in internal.items():
        substitutions.append(f".. |{key}_url| replace:: {url}")
        substitutions.append(f".. |{key}_link| replace:: `{key} <{url}>`__")

    # Bergen
    internal = config.get('bergen', {})
    for key, url in internal.items():
        if key =="hus":
            new_key = "Haukeland University Hospital"
            substitutions.append(f".. |{key}_url| replace:: {url}")
            substitutions.append(f".. |{key}_link| replace:: `{new_key} <{url}>`__")        
        else:
            substitutions.append(f".. |{key}_url| replace:: {url}")
            substitutions.append(f".. |{key}_link| replace:: `{key} <{url}>`__")

    return '\n'.join(substitutions)



