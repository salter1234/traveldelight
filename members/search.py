from django.db.models import Q
from .models import Tour
from datetime import datetime

# 搜尋的條件判斷function
def searchTour(startDate, endDate, tour_toursite, tour_tourday, tour_company, options):
    # 所有的tour 物件
    tours = Tour.objects.all()
    toursite_filter = Q() # 目的地的查詢條件集
    tourday_filter = Q() # 旅遊天數的查詢條件集
    company_filter = Q() # 旅遊公司的查詢條件集

# 設定出團日的查詢條件集
    goDateIDlist=[] #出團日有在'出發日期區間'當中的TourID
    for inx, godate in zip(Tour.objects.all().values("id"), Tour.objects.all().values("goDate")): #每個行程的godate list
        for date in godate["goDate"].split(", "): #每個行程的godate list的date
            #將date轉換datetime型態
            try:
                date=datetime.strptime(date.replace("'", "").replace("/", "-"),"%Y-%m-%d").date()
            except:
                continue
        #判斷每個行程的godate list的date 是否在搜尋篩選的'出發日期區間'
            if date >= startDate and date <= endDate: 
                goDateIDlist.append(inx["id"])
                break 
    goDate_filter = Q(id__in=goDateIDlist)

# 設定 目的地、旅遊天數、旅遊公司 的查詢條件
    # 判斷 目的地 的查詢條件
    if tour_toursite!=None: #如果有選擇 目的地
        toursite_filter=Q(toursite=tour_toursite)

        if tour_tourday!=None and tour_company!=None: #如果有選擇 旅遊天數 和 旅遊公司
        #判斷勾選什麼 旅遊天數
            for t in range(len(tour_tourday)):
                if "4" in tour_tourday: #4天以上
                    tourday_filter |= Q(tourday__gte=int(tour_tourday[t]))
                else: #1、2、3天
                    tourday_filter |= Q(tourday=int(tour_tourday[t]))
        #判斷勾選什麼 旅遊公司
            for c in range(len(tour_company)):
                company_filter |= Q(company=tour_company[c]) 
            
        # 依據以上條件篩選tour 物件
            tours = Tour.objects.filter(goDate_filter &toursite_filter & tourday_filter & company_filter)
        # 設定排序
            if options == "P":
                tours = tours.order_by('price') # 依價位排序
            else:
                tours = tours.order_by('earlierGoDate') # 依最早出發日排序 
        
        else: #如果沒有選擇 旅遊天數 和 旅遊公司
            tours = 'None'
    else: #如果沒有選擇目的地

        if (tour_tourday!=None) and (tour_company!=None): #如果有選擇 旅遊天數 和 旅遊公司
        #判斷勾選什麼 旅遊天數   
            for t in range(len(tour_tourday)):
                if "4" in tour_tourday: #4天以上
                    tourday_filter |= Q(tourday__gte=int(tour_tourday[t]))
                else: #1、2、3天
                    tourday_filter |= Q(tourday=int(tour_tourday[t]))
        #判斷勾選什麼 旅遊公司
            for c in range(len(tour_company)):
                company_filter |= Q(company=tour_company[c])
        # 依據以上條件篩選tour 物件
            tours = Tour.objects.filter(goDate_filter & tourday_filter & company_filter) 
        # 設定排序
            if options == "P":
                tours = tours.order_by('price') # 依價位排序
            else:
                tours = tours.order_by('earlierGoDate') # 依最早出發日排序 
        else: #如果沒有選擇 旅遊天數 和 旅遊公司
            tours = 'None'
    return tours


     
    