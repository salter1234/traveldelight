import sys,os
import pandas as pd
project_dir = "/projectname/"
sys.path.append(project_dir)
os.environ['DJANGO_SETTINGS_MODULE'] = 'projectname.settings'
import django
django.setup()
import json
from django.core.management import call_command

# Open the output file in write mode with UTF-8 encoding
with open('data.json', 'w', encoding='utf-8') as f:
    # Call dumpdata and write to the file
    call_command('dumpdata', stdout=f)