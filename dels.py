import sys,os
import pandas as pd
project_dir = "/projectname/"
sys.path.append(project_dir)
os.environ['DJANGO_SETTINGS_MODULE'] = 'projectname.settings'
import django
django.setup()

from members.models import Tour, Site, Company, Region
Company.objects.filter(id=5).delete()