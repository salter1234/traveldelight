"""
定時擷取各家旅行社+匯入Django資料庫(多工)
"""
import pandas as pd
import threading
from django.db.models import Q

region_mapping={
    '台北':'北部',
    '新北':'北部',
    '基隆':'北部',
    '桃園':'北部',
    '新竹':'北部',
    '苗栗':'中部',
    '台中':'中部',
    '彰化':'中部',
    '南投':'中部',
    '雲林':'中部',
    '嘉義':'南部',
    '台南':'南部',
    '高雄':'南部',
    '屏東':'南部',
    '宜蘭':'東部',
    '花蓮':'東部',
    '台東':'東部',
    '小琉球':'離島',
    '蘭嶼':'離島',
    '綠島':'離島',
    '澎湖':'離島',
    '金門':'離島',
    '馬祖':'離島',
    }

"""
自動化擷取各家旅遊網站資料(多工)
"""
# # 載入雄獅旅遊(liontravel.py)
# def liontravelGet():
#     import liontravel    
# #東南旅遊(settour.py)
# def settourGet():
#     import settour
# #五福旅遊(domestic.py)
# def domesticGet():
#     import domestic
# #易遊網(eztravel.py)
# def eztravelGet():
#     import eztravel

# #建立執行序
# liontravel_thread=threading.Thread(target=liontravelGet)
# settour_thread=threading.Thread(target=settourGet)
# domestic_thread=threading.Thread(target=domesticGet)
# eztravel_thread=threading.Thread(target=eztravelGet)
# # 讓開始擷取資料
# liontravel_thread.start()
# settour_thread.start()
# domestic_thread.start()
# eztravel_thread.start()
# # 等待所有執行緒結束
# liontravel_thread.join()
# settour_thread.join()
# domestic_thread.join()
# eztravel_thread.join()

"""
合併成一個gettour.csv檔案
""" 
import pandas as pd                       
# 合併所有旅遊網擷取儲存的csv檔
liontravel_df=pd.read_csv('liontravel.csv', encoding='utf-8', index_col=0)
settour_df=pd.read_csv('settour.csv', encoding='utf-8', index_col=0)
domestic_df=pd.read_csv('domestic.csv', encoding='utf-8', index_col=0)
eztravel_df=pd.read_csv('eztravel.csv', encoding='utf-8', index_col=0)
con = pd.concat([liontravel_df,settour_df, domestic_df, eztravel_df],ignore_index=True)
con.to_csv('gettour.csv',encoding='utf-8',errors='ignore')


"""
將gettour.csv檔案匯入Django資料庫
"""    
# import sys,os
# project_dir = "/projectname/"
# sys.path.append(project_dir)
# os.environ['DJANGO_SETTINGS_MODULE'] = 'projectname.settings'
# import django
# django.setup()


from members.models import Tour, Site, Company, Region, TourSite, Attraction, TourAttraction
df=pd.read_csv('./gettour.csv', encoding='utf-8')
for i in range(len(list(df.iloc[:,0]))):
    row=list(df.iloc[i,:])
    try:
        if not Tour.objects.filter(NormGroupID = row[1]).exists(): #如果資料庫 沒有 該筆資料的狀況
            comp_name = row[4] #旅遊公司處理
            try:
                company, _ = Company.objects.get_or_create(company_name=comp_name)
            except:
                continue        
            site_name = row[3] #旅遊目的地處理
            region_name = region_mapping[site_name]
            if region_name: 
                region, _ = Region.objects.get_or_create(region_name=region_name)
                toursite, _ = Site.objects.get_or_create(site_name=site_name, region=region)
            tour, created = Tour.objects.get_or_create(
                    NormGroupID = row[1], #旅遊行程編號
                    tourname = row[2], #旅遊標題名稱
                    toursite = toursite,  #旅遊目的地
                    company = company,  #旅行社
                    tourlink = row[5],  # 旅遊行程連結
                    tourimage = row[7], # 旅遊行程圖片
                    tourday = int(row[8]), # 旅遊天數
                    price = float(row[9]),  # 費用   
                    earlierGoDate = row[10],   # 最早可出發日期 
                    create_date = row[11].replace('/', '-'),   #建立行程時間
                    renew_date = row[12].replace('/', '-'), #更新可出發日期時間                       
                    tourSpecial = row[13], #旅遊行程特色描述
                    goDate = row[14].lstrip('[').rstrip(']'), # 可出團日
                    day = row[16], # 行程第幾天
                    travelPoint = row[17], # 參考行程
                    breakfast = row[18],  # 早餐
                    lunch = row[19], # 午餐
                    dinner = row[20], # 晚餐
                    hotel = row[21]  # 住宿
                    ) 
            #出發地點處理       
            gosites = row[6].replace("'","").replace(" ","").lstrip('[').rstrip(']').split(',')
            for sit in gosites:
                r_name = region_mapping.get(sit)
                if r_name:
                    r, _ = Region.objects.get_or_create(region_name=r_name)
                    gosite, _ = Site.objects.get_or_create(site_name=sit, region=r)                   
                TourSite.objects.create(tour=Tour.objects.get(NormGroupID = row[1]),site=gosite) #新增行程縣市關聯物件
            #景點處理
            attractions = row[15].replace("'","").replace(" ","").lstrip('[').rstrip(']').split(',')
            attractions = list(set(attractions))
            for attract in attractions:
                if Attraction.objects.filter(attraction_name = attract).exists():
                    attractionid, _ = Attraction.objects.get_or_create(attraction_name=attract)   #新增行程景點關聯物件                 
                    TourAttraction.objects.create(tour=Tour.objects.get(NormGroupID = row[1]),attraction=attractionid)
                else: 
                    continue
        else:   #如果資料庫 已經有 該筆資料的狀況(更新 最早出發日期earlierGoDate & 更新時間renew_date 
            site_name = row[3] #旅遊目的地                                     & 更新出團日期goDate)
            region_name = region_mapping[site_name]
            if region_name:
                region, _ = Region.objects.get_or_create(region_name=region_name)
                toursite, _ = Site.objects.get_or_create(site_name=site_name, region=region)
            tour=Tour.objects.get(Q(NormGroupID = row[1])&Q(toursite = toursite))
            tour.earlierGoDate=row[10]  #更新 最早出發日期
            tour.renew_date=row[12].replace('/', '-') #更新時間
            tour.goDate=row[14].lstrip('[').rstrip(']') #更新出團日期
            tour.save()
    except Exception as e:
        print(e)
        continue



"""
**下面這段通常 註解 掉**

如何通過 Django shell 插入資料的範例：

如果資料庫當中的Region, Site, Company, Site, Attraction的資料表還沒建立，
請跑這一段程式，如果已經有表格，就註解掉。
"""

# from members.models import Tour, Site, Company, Region

# # 插入商家
# liontravel = Company.objects.create(company_name='雄獅旅遊')
# domestic = Company.objects.create(company_name='五福旅遊')
# settour = Company.objects.create(company_name='東南旅遊')
# eztravel = Company.objects.create(company_name='易遊網')

# # 插入區域
# north = Region.objects.create(region_name='北部')
# central = Region.objects.create(region_name='中部')
# south = Region.objects.create(region_name='南部')
# east = Region.objects.create(region_name='東部')
# island = Region.objects.create(region_name='離島')

# # 插入城市並與區域建立關聯
# Site.objects.create(site_name='台北', region=north)
# Site.objects.create(site_name='新北', region=north)
# Site.objects.create(site_name='基隆', region=north)
# Site.objects.create(site_name='桃園', region=north)
# Site.objects.create(site_name='新竹', region=north)

# Site.objects.create(site_name='苗栗', region=central)
# Site.objects.create(site_name='台中', region=central)
# Site.objects.create(site_name='彰化', region=central)
# Site.objects.create(site_name='南投', region=central)
# Site.objects.create(site_name='雲林', region=central)

# Site.objects.create(site_name='嘉義', region=south)
# Site.objects.create(site_name='台南', region=south)
# Site.objects.create(site_name='高雄', region=south)
# Site.objects.create(site_name='屏東', region=south)

# Site.objects.create(site_name='宜蘭', region=east)
# Site.objects.create(site_name='花蓮', region=east)
# Site.objects.create(site_name='台東', region=east)

# Site.objects.create(site_name='小琉球', region=island)
# Site.objects.create(site_name='蘭嶼', region=island)
# Site.objects.create(site_name='綠島', region=island)
# Site.objects.create(site_name='澎湖', region=island)
# Site.objects.create(site_name='金門', region=island)
# Site.objects.create(site_name='馬祖', region=island)

"""
**下面這段通常 註解 掉**
Attraction的資料表還沒建立，
請跑這一段程式，如果已經有表格，就註解掉。
"""
# # 插入景點
# import sys,os
# import pandas as pd
# project_dir = "/projectname/"
# sys.path.append(project_dir)
# os.environ['DJANGO_SETTINGS_MODULE'] = 'projectname.settings'
# import django
# django.setup()
from members.models import Attraction
df=pd.read_csv('./attraction.csv', encoding='utf-8')
for a in list(df['Attraction']):
    try:
        if not Attraction.objects.filter(attraction_name=a).exists():
            Attraction.objects.create(attraction_name=a)
        else:
            continue
    except Exception as e:
        print(e)
        continue