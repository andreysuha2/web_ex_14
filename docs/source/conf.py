import sys
import os
from datetime import datetime

year = datetime.now().year
copy_years = year if year > 2024 else f"2024 - {year}"

sys.path.append(os.path.abspath('../..'))
project = 'Contacts App'
author = 'Andrii Sukhenko'
copyright = f'{copy_years}, {author}'

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templaes']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'nature'
html_static_path = ['_static']