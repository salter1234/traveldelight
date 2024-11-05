import sys,os
import pandas as pd
project_dir = "/projectname/"
sys.path.append(project_dir)
os.environ['DJANGO_SETTINGS_MODULE'] = 'projectname.settings'
import django
django.setup()

import json

def split_fixtures(input_file, batch_size=1000):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        with open(f'fixture_batch_{i//batch_size}.json', 'w', encoding='utf-8') as f:
            json.dump(batch, f, ensure_ascii=False, indent=2)

# 使用方法
split_fixtures('data.json')