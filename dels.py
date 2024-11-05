from members.models import Tour, Site, Company, Region
Company.objects.filter(id=5).delete()