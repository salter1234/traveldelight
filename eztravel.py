
"""
易遊網
"""
import os
import math
import threading
import queue
# import requests
# from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import Select
# from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time

user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
chrome_options = webdriver.ChromeOptions()
# chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless=old") #無頭模式
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument(f"user-agent={user_agent}")
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--no-sandbox")

#佈署所需要的設定
from selenium.webdriver.chrome.service import Service
service = Service(executable_path=os.environ.get("CHROMEDRIVER_PATH"))

ArriveID={
    # "台灣":"",
    "台北":"PLCCITYTPE",
    "基隆":"PLCCITYKEE",
    "宜蘭":"PLCCITYYI0",
    "新北":"PLCCITYTP2",
    "桃園":"PLCCITYTA1",
    "新竹":"PLCCITYHSZ",
    "苗栗":"PLCCITYMI1",
    "台中":"PLCCITYTXG",
    "彰化":"PLCCITYZH1",
    "南投":"PLCCITYNA0",
    "雲林":"PLCCITYYU1",
    "嘉義":"PLCCITYCYI",
    "台南":"PLCCITYTNN",
    "高雄":"PLCCITYKHH",
    "屏東":"PLCCITYPIF",
    # "小琉球":"B3-55-9,",
    "花蓮":"PLCCITYHUN",
    "台東":"PLCCITYTTT",
    "蘭嶼":"PLCCITYKYD",
    "綠島":"PLCCITYGNI",
    "澎湖":"PLCCITYMZG",
    "金門":"PLCCITYKNH",
    "馬祖":"PLCCITYMFK" 
 }

Arrivelist=list(ArriveID.keys())
# print(Arrivelist)
# print("="*20)
# Arrive=input('地點:')
# GoDateStart=input('去日(ex.2024-12-23):')
# GoDateEnd=input('返日(ex.2024-12-23):')
# Arrivelist=["台北"]

"""
設定年月日
"""
GoDateStart=datetime.now().strftime("%Y-%m-%d")
GoDateEnd=datetime.today().date()-relativedelta(months=-2)
GoDateEnd=GoDateEnd.strftime("%Y-%m-%d")
GoDateStart1=GoDateStart.replace("-", "")
GoDateEnd1=GoDateEnd.replace("-", "")
GoDateStart2=GoDateStart.replace("-", "/")
GoDateEnd2=GoDateEnd.replace("-", "/")

#更新data用的暫存欄位
indexes=[]
earlierGoDatevalues=[]
GoDatevalues=[]      ####
renew_datevalues=[]
AttractionSet=set()



"""
擷取
"""
def eztravel(Arrive, df, driver, retries=3):
    retry_count = 0
    while retry_count < retries:
        try:
            """
            設定欄位
            """
            NormGroupIDList=[]#
            TourNamelist=[]#
            TourSitelist=[]#
            CompanyList=[]#
            TourLinklist=[]#
            GoSitelist=[]#
            TourImagelist=[]#
            TourDaylist=[]#
            Pricelist=[]#
            EarliGoDatelist=[]#
            CreateDateList=[]#
            RenewDateList=[]#
            TourSpecialList=[]#
            GoDatelist=[]#
            Attractionlist=[]#
            Breakfastlist=[]#
            Dinnerlist=[]#
            Lunchlist=[]#
            Daylist=[]#
            TravelPointlist=[]#
            Hotellist=[]#
            
            link='https://trip.eztravel.com.tw/domestic/keywords?depart=&viewList='+ArriveID[Arrive]+'&avaliableOnly=true&depDateFrom='+GoDateStart1+'&depDateTo='+GoDateEnd1
            # driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_window_size(1920,1080)
            driver.implicitly_wait(15)
            driver.get(link)
            # time.sleep(0.5)
            WebDriverWait(driver,30,0.5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.SearchResult_orange__4td0o')))
            num=int(driver.find_element(By.CSS_SELECTOR, 'div.SearchResult_orange__4td0o').text)
        
            for page in range(1,math.ceil(num/15)+1):
                #每一頁共15個行程一起抓
                nextlink='https://trip.eztravel.com.tw/domestic/keywords?depart=&viewList='+ArriveID[Arrive]+'&avaliableOnly=true&depDateFrom='+GoDateStart1+'&depDateTo='+GoDateEnd1+'&orderBy=1&page='+str(page)
                driver.get(nextlink)
                time.sleep(1)
                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
                time.sleep(1)
                tournames=[t.text for t in driver.find_elements(By.CSS_SELECTOR, 'div.SearchResult_prod__0VaY2 div.SearchResult_prodNm__Twsev')]
                images=[im.get_attribute('src') for im in driver.find_elements(By.CSS_SELECTOR, 'div.SearchResult_prod__0VaY2 div.lazyload-wrapper img')]
                prices=[p.text.replace(',','') for p in driver.find_elements(By.CSS_SELECTOR, 'div.SearchResult_prod__0VaY2 div.SearchResult_final__Vg___')]
                gosites=[lo.text for lo in driver.find_elements(By.CSS_SELECTOR, 'div.SearchResult_prod__0VaY2 div.SearchResult_prodNm__Twsev')]
                tourDays=[td.text for td in driver.find_elements(By.CSS_SELECTOR, 'div.SearchResult_prod__0VaY2 div.SearchResult_day__rtzOB')]
                links=[li.get_attribute('href') for li in driver.find_elements(By.CSS_SELECTOR, 'div.SearchResult_prod__0VaY2 a')]
                for x, link in enumerate(links):
                    NormGroupID="ez"+link.lstrip("https://trip.eztravel.com.tw/domestic/introduction/").split('/')[0]        
                    if NormGroupID in list(df["NormGroupID"]):
                        try:
                            ids=df[(df.NormGroupID == NormGroupID)&(df.toursite == Arrive)].index[0]
                            indexes.append(ids)       
                            renew_datevalues.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                            driver.get(link)
                            time.sleep(1)
                            try:
                                WebDriverWait(driver,20,0.5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.DescDetail_date__ySvMg.text-h5')))
                                x=driver.find_element(By.CSS_SELECTOR, 'div.DescDetail_date__ySvMg.text-h5').text.split('(')[0].replace(' / ', '/')
                                earlierGoDatevalues.append(x[:10])
                            except:
                                earlierGoDatevalues.append("")
        
                            GoDate=[]
                            go=True
                            n=0
                            while go:
                                try:
                                    WebDriverWait(driver,24,0.5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.Calendar_column__I2zk5')))
                                    year=driver.find_element(By.CSS_SELECTOR, 'div.Calendar_column__I2zk5').text.split(" ")[1]
                                    WebDriverWait(driver,20,0.5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.Calendar_column__I2zk5')))
                                    month=driver.find_element(By.CSS_SELECTOR, 'div.Calendar_column__I2zk5').text.split("月 ")[0]
                                    WebDriverWait(driver,20,0.5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.Calendar_row__nY4G_ a.Calendar_column__I2zk5.Calendar_cell__u32_d.Calendar_none__p25cR div.Calendar_number__OksZ2')))
                                    days=driver.find_elements(By.CSS_SELECTOR, 'div.Calendar_row__nY4G_ a.Calendar_column__I2zk5.Calendar_cell__u32_d.Calendar_none__p25cR div.Calendar_number__OksZ2')                       
                                    for day in days:
                                        if len(day.text)==1:
                                            GoDate.append(year+'/'+month+'/0'+day.text)
                                        else:
                                            GoDate.append(year+'/'+month+'/'+day.text)
                                except:
                                    pass
                                if n == 2:
                                    go=False
                                else:
                                    try:
                                        driver.find_element(By.CSS_SELECTOR, 'div.Calendar_next__S26u8').click()   
                                        n+=1
                                    except:
                                        go=False
                            GoDatevalues.append(GoDate)
                        except:
                            continue
                        
                    else:
                        GoSite=[]
                        if "出發" not in gosites[x]:
                            GoSite=["台北","台中","高雄","宜蘭","花蓮","台東"]
                        else:
                            if "各站可" in gosites[x]:
                                GoSite=["台北","新北","基隆","桃園","新竹","苗栗","台中","彰化","南投","雲林","嘉義","台南","高雄","屏東","宜蘭","花蓮","台東"]
                            elif '北中南可' in gosites[x]:
                                GoSite=["台北","新北","基隆","桃園","新竹","苗栗","台中","彰化","南投","雲林","嘉義","台南","高雄","屏東"]
                            elif len(gosites[x].split('出發')[0].split('(')[gosites[x].split('出發')[0].count('(')].rstrip('可'))>2:
                                if "桃竹" in gosites[x].split('出發')[0].split('(')[gosites[x].split('出發')[0].count('(')].rstrip('可'):
                                    GoSite=["桃園","新竹"]
                                elif "北部" in gosites[x].split('出發')[0].split('(')[gosites[x].split('出發')[0].count('(')].rstrip('可'):
                                    GoSite=["台北","新北","基隆","桃園","新竹"]
                                elif "中部" in gosites[x].split('出發')[0].split('(')[gosites[x].split('出發')[0].count('(')].rstrip('可'):
                                    GoSite=["苗栗","台中","彰化","南投","雲林"]
                                elif "南部" in gosites[x].split('出發')[0].split('(')[gosites[x].split('出發')[0].count('(')].rstrip('可'):
                                    GoSite=["嘉義","台南","高雄","屏東"]
                                else:
                                    # Locationlist.append(lo.text.split('出發')[0].split('(')[lo.text.split('出發')[0].count('(')][:2])
                                    continue
                            else:
                                if "桃竹" in gosites[x].split('出發')[0].split('(')[gosites[x].split('出發')[0].count('(')].rstrip('可'):
                                    GoSite=["桃園","新竹"]
                                elif "北部" in gosites[x].split('出發')[0].split('(')[gosites[x].split('出發')[0].count('(')].rstrip('可'):
                                    GoSite=["台北","新北","基隆","桃園","新竹"]
                                elif "中部" in gosites[x].split('出發')[0].split('(')[gosites[x].split('出發')[0].count('(')].rstrip('可'):
                                    GoSite=["苗栗","台中","彰化","南投","雲林"]
                                elif "南部" in gosites[x].split('出發')[0].split('(')[gosites[x].split('出發')[0].count('(')].rstrip('可'):
                                    GoSite=["嘉義","台南","高雄","屏東"]
                                else:
                                    GoSite=[gosites[x].split('出發')[0].split('(')[gosites[x].split('出發')[0].count('(')].rstrip('可')]
                        NormGroupIDList.append(NormGroupID)
                        TourLinklist.append(link)
                        GoSitelist.append(GoSite)
                        TourNamelist.append(tournames[x])
                        TourSitelist.append(Arrive)
                        CompanyList.append('易遊網')
                        TourImagelist.append(images[x])
                        TourDaylist.append(tourDays[x])
                        Pricelist.append(prices[x]) 
                        CreateDateList.append(datetime.now().strftime("%Y-%m-%d")) 
                        RenewDateList.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        
                        driver.get(link)
                        time.sleep(1)
                        try:
                            WebDriverWait(driver,20,0.5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.DescDetail_date__ySvMg.text-h5')))
                            x=driver.find_element(By.CSS_SELECTOR, 'div.DescDetail_date__ySvMg.text-h5').text.split('(')[0].replace(' / ', '/')
                            EarliGoDatelist.append(x[:10])   
                        except:
                            EarliGoDatelist.append("")
                        try:
                            WebDriverWait(driver,20,0.5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.TourFeature_content__zz2Gu')))
                            TourSpecialList.append(driver.find_element(By.CSS_SELECTOR, 'div.TourFeature_content__zz2Gu').text)
                        except:
                            TourSpecialList.append("")
                        GoDate=[]
                        go=True
                        n=0
                        while go:
                            try:
                                WebDriverWait(driver,24,0.5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.Calendar_column__I2zk5')))
                                year=driver.find_element(By.CSS_SELECTOR, 'div.Calendar_column__I2zk5').text.split(" ")[1]
                                WebDriverWait(driver,20,0.5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.Calendar_column__I2zk5')))
                                month=driver.find_element(By.CSS_SELECTOR, 'div.Calendar_column__I2zk5').text.split("月 ")[0]
                                WebDriverWait(driver,20,0.5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.Calendar_row__nY4G_ a.Calendar_column__I2zk5.Calendar_cell__u32_d.Calendar_none__p25cR div.Calendar_number__OksZ2')))
                                days=driver.find_elements(By.CSS_SELECTOR, 'div.Calendar_row__nY4G_ a.Calendar_column__I2zk5.Calendar_cell__u32_d.Calendar_none__p25cR div.Calendar_number__OksZ2')                       
                                for day in days:
                                    if len(day.text)==1:
                                            GoDate.append(year+'/'+month+'/0'+day.text)
                                    else:
                                        GoDate.append(year+'/'+month+'/'+day.text)
                            except:
                                pass
                            if n == 2:
                                go=False
                            else:
                                try:
                                    driver.find_element(By.CSS_SELECTOR, 'div.Calendar_next__S26u8').click()   
                                    n+=1
                                except:
                                    go=False    
                        GoDatelist.append(GoDate)
                        try:
                            WebDriverWait(driver,20,0.5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.DescDetail_travelDays__0tHN9')))
                            Days=[i for i in range(1,int(driver.find_element(By.CSS_SELECTOR, 'div.DescDetail_travelDays__0tHN9').text.split(" ")[0])+1)]
                        except:
                            Days=[]
                        Daylist.append(Days)
                        try:
                            WebDriverWait(driver,20,0.5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'article.ScheduleDay_scheduleDay__odBC9 h2')))
                            TravelPoint=[i.text.split(" 天")[1] for i in driver.find_elements(By.CSS_SELECTOR, 'article.ScheduleDay_scheduleDay__odBC9 h2')]
                        except:
                            TravelPoint=[]
                        TravelPointlist.append(TravelPoint)
                        try:
                            WebDriverWait(driver,20,0.5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'article.ScheduleDay_scheduleDay__odBC9 h2 ts')))
                            Attractions=[i.text for i in driver.find_elements(By.CSS_SELECTOR, 'article.ScheduleDay_scheduleDay__odBC9 h2 ts')]
                            for a in Attractions:
                                AttractionSet.add(a)
                        except:
                            Attractions=[]
                        Attractionlist.append(Attractions)
                        Breakfasts=[]
                        Lunchs=[]
                        Dinners=[]
                        try:
                            WebDriverWait(driver,20,0.5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'article.ScheduleDay_scheduleDay__odBC9 div.HotelAndMeals_hotelAndMeals__Q6BPP div.HotelAndMeals_meals__3xaQZ ul')))
                            meals=[i.text for i in driver.find_elements(By.CSS_SELECTOR, 'article.ScheduleDay_scheduleDay__odBC9 div.HotelAndMeals_hotelAndMeals__Q6BPP div.HotelAndMeals_meals__3xaQZ ul')]
                            for m in meals:
                                Breakfasts.append(m.split("\n")[0].lstrip("早餐："))
                                Lunchs.append(m.split("\n")[1].lstrip("午餐："))
                                Dinners.append(m.split("\n")[2].lstrip("晚餐："))
                        except:
                            pass
                        Breakfastlist.append(Breakfasts)
                        Lunchlist.append(Lunchs)
                        Dinnerlist.append(Dinners)
                        try:
                            WebDriverWait(driver,20,0.5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'article.ScheduleDay_scheduleDay__odBC9 div.HotelAndMeals_hotelAndMeals__Q6BPP div.HotelAndMeals_htl__AIyx9')))
                            Hotels=[i.text for i in driver.find_elements(By.CSS_SELECTOR, 'article.ScheduleDay_scheduleDay__odBC9 div.HotelAndMeals_hotelAndMeals__Q6BPP div.HotelAndMeals_htl__AIyx9')]
                        except:
                            Hotels=[]
                        Hotellist.append(Hotels)
            
            
            """
            回傳新擷取結果
            """    
            data = pd.DataFrame({"NormGroupID":NormGroupIDList,"tourname":TourNamelist,"toursite":TourSitelist,"company":CompanyList,
                                  "tourlink":TourLinklist,"gosite":GoSitelist,"tourimage":TourImagelist,"tourday":TourDaylist,"price":Pricelist,
                                  "earlierGoDate":EarliGoDatelist,"create_date":CreateDateList,"renew_date":RenewDateList,"tourSpecial":TourSpecialList,
                                  'GoDate':GoDatelist, 'Attraction':Attractionlist, 'Day':Daylist, 'TravelPoint':TravelPointlist, 
                                  'Breakfast':Breakfastlist, 'Lunch':Lunchlist, 'Dinner':Dinnerlist, 'Hotel':Hotellist})
        
            return data
            break  # 成功后退出循环
        except TimeoutException:
            retry_count += 1
            print(f"TimeoutException encountered. Retrying {retry_count}/{retries}...")
            if retry_count == retries:
                print("Maximum retries reached. Moving to the next task.")
                return None  # 或者返回一个默认值继续流程
            time.sleep(2)  # 可选择添加延迟以避免频繁请求
    

"""
多工+貯列
"""    
class Worker(threading.Thread):
    def __init__(self, queue, lock, df):
        threading.Thread.__init__(self)
        self.queue = queue
        self.lock = lock
        self.df = df
        # 初始化 WebDriver
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def run(self):
        while self.queue.qsize() > 0:
          # 取得新的資料
            Arrive=self.queue.get()
            
            result_data = eztravel(Arrive, self.df, self.driver)
            """
            取得資料(鎖)
            """
            if not result_data.empty:
                self.lock.acquire()  # 鎖住寫檔操作
                try:
                    df=pd.read_csv('eztravel.csv', encoding='utf-8', index_col=0)
                    con = pd.concat([df,result_data],ignore_index=True)
                    con.to_csv('eztravel.csv', encoding='utf-8',errors='ignore')
                finally:
                    self.lock.release()  # 釋放鎖
                    
    # 在程式結束時，確保 WebDriver 被正確關閉                
    def quit_driver(self):
        self.driver.quit()


               
"""
擷取各旅遊地點資訊+存檔
"""
lock = threading.Lock()
my_queue = queue.Queue()
    
# 將任務放入佇列（每個地點的工作）
for Arrive in Arrivelist:
    my_queue.put(Arrive)

# 建立10個工作者執行緒
num_threads = 1
workers = []

df=pd.read_csv('eztravel.csv', encoding='utf-8', index_col=0)
for _ in range(num_threads):
    worker = Worker(my_queue, lock, df)
    worker.start()
    workers.append(worker)
   
    
# 等待所有工作者完成
for worker in workers:
    worker.join()
    
for worker in workers:
    worker.quit_driver()

df1=pd.read_csv('eztravel.csv', encoding='utf-8', index_col=0)
for idx, ev, rv, gv in zip(indexes, earlierGoDatevalues, renew_datevalues, GoDatevalues):
    df1.at[idx, "earlierGoDate"]=ev
    df1.at[idx, "renew_date"]=rv
    df1.at[idx, "GoDate"]=gv
df1.to_csv('eztravel.csv', encoding='utf-8',errors='ignore')

#清理掉earlierGoDate和GoDate無法同步的tour
df3=pd.read_csv('eztravel.csv', encoding='utf-8')
ids=df3[(df3.GoDate != "['此行程目前暫告一段落，敬請期待下一季精彩行程！']")&(df3.GoDate != "[]")]
num=[]
NormGroupID=list(ids.NormGroupID)
earlierGoDate=list(ids.earlierGoDate)
for n, eg,i in zip(NormGroupID, earlierGoDate,ids.GoDate):
    GoDatelist=i.lstrip("['").rstrip("']").split("', '")
    if eg.strip(' ') in GoDatelist:
        num.append(n)
numdf=df[df.NormGroupID.isin(num)]
numdf.to_csv('eztravel.csv', encoding='utf-8', errors='ignore')

if len(AttractionSet)>0:       
    df2=pd.read_csv('attraction.csv', encoding='utf-8', index_col=0)
    df2_Attract=set(df2['Attraction'])
    Attract=df2_Attract|AttractionSet
    Attractdata = pd.DataFrame({"Attraction":list(Attract)})
    Attractdata.to_csv('attraction.csv', encoding='utf-8',errors='ignore')
  
