
"""
東南旅遊
"""
from requests.cookies import RequestsCookieJar
from datetime import datetime
from dateutil.relativedelta import relativedelta
import threading
import queue
import os
# import requests
# from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import Select
# from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time



user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.3'
chrome_options = webdriver.ChromeOptions()
# chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless=old") #無頭模式
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument(f"user-agent={user_agent}")
# chrome_options.add_argument("--disable-notifications")

chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument("--disable-dev-shm-usage")

#以下是為了解決--headless=new跳出白框問題
chrome_options.add_argument("--disable-gpu")  # 測試是否與 GPU 設置有關
chrome_options.add_argument("--no-sandbox")  #禁用沙盒模式
# chrome_options.add_argument("--disable-software-rasterizer")  #禁用軟件渲染列表
# #禁用背景加載
# chrome_options.add_argument("--disable-background-timer-throttling")
# chrome_options.add_argument("--disable-backgrounding-occluded-windows")
# chrome_options.add_argument("--disable-renderer-backgrounding")


#佈署所需要的設定
from selenium.webdriver.chrome.service import Service
service = Service(executable_path=os.environ.get("CHROMEDRIVER_PATH"))



"""
設定旅遊地點
"""
ArriveID={
    # "台灣":"",
    "台北":"TPE_2",
    # "基隆":"TPE_2",
    "宜蘭":"ILN_2",
    # "新北":"TPE_2",
    "桃園":"TYU_2",
    "新竹":"HSZ_2",
    "苗栗":"MAL_2",
    "台中":"TXG_2",
    "彰化":"CWH_2",
    "南投":"NTO_2",
    "雲林":"YUN_2",
    "嘉義":"CHY_2",
    "台南":"TNN_2",
    "高雄":"KHH_2",
    "屏東":"PIF_2",
    "小琉球":"HLI_2",
    "花蓮":"HUN_2",
    "台東":"TTT_2",
    "蘭嶼":"KYD_2",
    "綠島":"GNI_2",
    "澎湖":"MZG_2",
    "金門":"KNH_2",
    "馬祖":"MFK_2" 
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
GoDateEnd=datetime.today().date()-relativedelta(months=-3)
GoDateEnd=GoDateEnd.strftime("%Y-%m-%d")
# GoDateEnd=datetime.today().date()-relativedelta(months=-3)
# GoDateEnd=GoDateEnd.strftime("%Y-%m-%d")
GoDateStart1=GoDateStart.replace("-", "")
GoDateEnd1=GoDateEnd.replace("-", "")


#更新data用的暫存欄位
indexes=[]
earlierGoDatevalues=[]
GoDatevalues=[]
renew_datevalues=[]
AttractionSet=set()

"""
擷取
"""
def settour(Arrive, df, driver, retries=3):
    retry_count = 0
    while retry_count < retries:
        try:
            """
            設定欄位
            """
            NormGroupIDList=[]
            TourNamelist=[]
            TourSitelist=[]
            CompanyList=[]
            TourLinklist=[]
            GoSitelist=[]
            TourImagelist=[]
            TourDaylist=[]
            Pricelist=[]
            EarliGoDatelist=[]
            CreateDateList=[]
            RenewDateList=[]
            TourSpecialList=[]
            GoDatelist=[]
            Attractionlist=[]
            Breakfastlist=[]
            Dinnerlist=[]
            Lunchlist=[]
            Daylist=[]
            TravelPointlist=[]
            Hotellist=[]
            
            link='https://trip.settour.com.tw/taiwan/search?tourDays=&departure=&startDate='+GoDateStart1+'&endDate='+GoDateEnd1+'&keyWord=&destination='+ArriveID[Arrive]+'&isOrder=true'
            
            """
            開始擷取
            """
            # driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_window_size(1920, 1080)
            driver.implicitly_wait(15)
            driver.get(link)
            time.sleep(1)
            objects=driver.find_elements(By.CSS_SELECTOR, 'article.product-item.trip')
            num1=len(objects)
            num0=0
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            time.sleep(1)
            while num1!=num0:
                time.sleep(1)
                objects=driver.find_elements(By.CSS_SELECTOR, 'article.product-item.trip')
                num0=len(objects)
                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
                time.sleep(1)
                objects=driver.find_elements(By.CSS_SELECTOR, 'article.product-item.trip')
                num1=len(objects)
            
            for obj in objects:
                TourName=obj.find_element(By.CSS_SELECTOR, 'h4.product-name a').text
                TourSite=Arrive
                Company='東南旅遊'
                GoSite=[]
                GoSite.append(obj.find_element(By.CSS_SELECTOR, 'div.product-info-tag-area').text.split(' ')[0].rstrip('出發'))
                TourImage=obj.find_element(By.CSS_SELECTOR, 'div.serach-img.col-md-4.col-sm-5 a').get_attribute('style').split(' ')[1].lstrip('url("').rstrip('",)')
                TourDay=list(obj.find_element(By.CSS_SELECTOR, 'div.price div.ori-price').text)[0]
                Price=obj.find_element(By.CSS_SELECTOR, 'div.price div.ori-price-offer').text.lstrip('$').rstrip('起').replace(',', '')
                EarliGoDate='2024/'+obj.find_elements(By.CSS_SELECTOR, 'div.product-info-bottom div')[0].text.split('(')[0]
                CreateDate=datetime.now().strftime("%Y-%m-%d")
                RenewDate=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                obj.find_element(By.CSS_SELECTOR, 'div.price-btn.col-md-12.col-xs-4 button.btn-order').send_keys(Keys.PAGE_UP)
                time.sleep(0.5)
                #點進分頁
                obj.find_element(By.CSS_SELECTOR, 'div.price-btn.col-md-12.col-xs-4 button.btn-order').click()       
                driver.switch_to.window(driver.window_handles[-1]) 
                time.sleep(2)
                detaillink=driver.current_url
                NormGroupID=detaillink.split('/')[-1]
                if NormGroupID in list(df["NormGroupID"]):
                    try:
                        ids=df[(df.NormGroupID == NormGroupID)&(df.toursite == TourSite)].index[0]
                    except:
                        try:
                            driver.close()
                        except:
                            print("關閉分頁錯誤1")
                        time.sleep(2)
                        driver.switch_to.window(driver.window_handles[0])
                        continue
                    indexes.append(ids)
                    earlierGoDatevalues.append(EarliGoDate)
                    renew_datevalues.append(RenewDate)
                    try:
                        WebDriverWait(driver,40,4).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.month-list.clearfix div ul li div.year")))
                        Ybtnall=driver.find_elements(By.CSS_SELECTOR, "div.month-list.clearfix div ul li div.year") ##
                        Mbtnall=driver.find_elements(By.CSS_SELECTOR, "div.month-list.clearfix div ul li div.month")
                        GoDate=[]
                        for i, y, m in zip([j for j in range(len(Mbtnall))], Ybtnall, Mbtnall):
                            driver.find_elements(By.CSS_SELECTOR, "div.month-list.clearfix div ul li div.month")[i]
                            time.sleep(0.5)
                            driver.find_elements(By.CSS_SELECTOR, "div.month-list.clearfix div ul li div.month")[i].click()
                            WebDriverWait(driver,40,4).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.st-calendar div.date-list-area.clearfix div.date-list.clearfix div.date.has-remark")))
                            try:
                                DPbtnall=driver.find_elements(By.CSS_SELECTOR, "div.st-calendar div.date-list-area.clearfix div.date-list.clearfix div.date.has-remark") ##
                            except:
                                DPbtnall=''
                            for d in DPbtnall:
                                GoDate.append(y.text+'/'+m.text.rstrip('月')+'/'+d.text.split('\n')[0])
                    except:
                        GoDate=['此行程目前暫告一段落，敬請期待下一季精彩行程！']
                    GoDatevalues.append(GoDate)
                    try:
                        driver.close()
                    except:
                        print("關閉分頁錯誤2")
                    time.sleep(2)
                    driver.switch_to.window(driver.window_handles[0])
                else:
                    TourLinklist.append(detaillink)
                    NormGroupIDList.append(NormGroupID)
                    TourNamelist.append(TourName)
                    TourSitelist.append(TourSite)
                    CompanyList.append(Company)
                    GoSitelist.append(GoSite)
                    TourImagelist.append(TourImage)
                    TourDaylist.append(TourDay)
                    Pricelist.append(Price)
                    EarliGoDatelist.append(EarliGoDate)
                    CreateDateList.append(CreateDate)
                    RenewDateList.append(RenewDate)
                    try:
                        WebDriverWait(driver,40,4).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.product-features-text.editor-area.show ul li')))
                        TourSpecialList.append(''.join([i.text+'\n' for i in driver.find_elements(By.CSS_SELECTOR, 'div.product-features-text.editor-area.show ul li')])) ##
                    except:
                        TourSpecialList.append([''])
        
                    try:
                        WebDriverWait(driver,40,4).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.product-info-list-area div[name='schedule'] div.stroke-item-area div.stroke-item div.container div.indent-type")))
                        DailyLists = driver.find_elements(By.CSS_SELECTOR, "div.product-info-list-area div[name='schedule'] div.stroke-item-area div.stroke-item div.container div.indent-type")  # 存取DailyList欄位            
                        Days=[]
                        TravelPoints=[]
                        Attractions=[]
                        Breakfasts=[]
                        Lunchs=[]
                        Dinners=[]
                        Hotels=[]
                        for Daily in DailyLists:
                            try:
                                Day=Daily.find_element(By.CSS_SELECTOR, 'div.stroke-item-tit-day').text.lstrip('第').rstrip('天')
                            except:
                                Day=''
                            Days.append(Day)
                            try:
                                TravelPoint=Daily.find_element(By.CSS_SELECTOR, 'div.stroke-item-tit-stroke').text
                            except:
                                TravelPoint=''
                            TravelPoints.append(TravelPoint)
                            try:
                                Attraction=[d.text for d in Daily.find_elements(By.CSS_SELECTOR, 'div.stroke-item-tit-stroke a.tit-link')] ##
                            except:
                                Attraction=''
                            for i in Attraction:
                                Attractions.append(i)
                            try:
                                Breakfast=Daily.find_elements(By.CSS_SELECTOR, 'div.stroke-item-eat ul li')[0].text.lstrip('早餐：') ##
                            except:
                                Breakfast=''
                            Breakfasts.append(Breakfast)
                            try:
                                Lunch=Daily.find_elements(By.CSS_SELECTOR, 'div.stroke-item-eat ul li')[1].text.lstrip('午餐：')
                            except:
                                Lunch=''
                            Lunchs.append(Lunch)
                            try:
                                Dinner=Daily.find_elements(By.CSS_SELECTOR, 'div.stroke-item-eat ul li')[2].text.lstrip('晚餐：') 
                            except:
                                Dinner=''
                            Dinners.append(Dinner)
                            try:
                                Hotel=Daily.find_element(By.CSS_SELECTOR, 'div.stroke-item-room span').text
                            except:
                                Hotel=''
                            Hotels.append(Hotel)
                           
                            for a in Attraction:
                                AttractionSet.add(a)
                        Attractionlist.append(Attractions)
                        Breakfastlist.append(Breakfasts)
                        Dinnerlist.append(Dinners)
                        Lunchlist.append(Lunchs)
                        Daylist.append(Days)
                        TravelPointlist.append(TravelPoints)
                        Hotellist.append(Hotels)
                        
                    except:
                        TravelPointlist.append('本行程詳細內容請洽服務人員')
                        Attractionlist.append(Attractions)
                        Breakfastlist.append(Breakfasts)
                        Dinnerlist.append(Dinners)
                        Lunchlist.append(Lunchs)
                        Daylist.append(Days)
                        Hotellist.append(Hotels)
        
                    try:
                        WebDriverWait(driver,40,4).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.month-list.clearfix div ul li div.year")))
                        Ybtnall=driver.find_elements(By.CSS_SELECTOR, "div.month-list.clearfix div ul li div.year") ##
                        Mbtnall=driver.find_elements(By.CSS_SELECTOR, "div.month-list.clearfix div ul li div.month")
                        GoDate=[]
                        for i, y, m in zip([j for j in range(len(Mbtnall))], Ybtnall, Mbtnall):
                            driver.find_elements(By.CSS_SELECTOR, "div.month-list.clearfix div ul li div.month")[i]
                            time.sleep(0.5)
                            driver.find_elements(By.CSS_SELECTOR, "div.month-list.clearfix div ul li div.month")[i].click()
                            WebDriverWait(driver,40,4).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.st-calendar div.date-list-area.clearfix div.date-list.clearfix div.date.has-remark")))
                            try:
                                DPbtnall=driver.find_elements(By.CSS_SELECTOR, "div.st-calendar div.date-list-area.clearfix div.date-list.clearfix div.date.has-remark") ##
                            except:
                                DPbtnall=''
                            for d in DPbtnall:
                                GoDate.append(y.text+'/'+m.text.rstrip('月')+'/'+d.text.split('\n')[0])
                    except:
                        GoDate=['此行程目前暫告一段落，敬請期待下一季精彩行程！']
                    GoDatelist.append(GoDate)
                    try:
                        driver.close()
                    except:
                        print("關閉分頁錯誤3")
                    time.sleep(2)
                    driver.switch_to.window(driver.window_handles[0])
            
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
        try:
            # # 在線程開始時初始化 WebDriver
            # self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            while not self.queue.empty():  # 使用 empty() 替代 qsize() > 0
                try:
                    # 取得新的資料
                    arrive = self.queue.get_nowait()  # 使用 get_nowait() 避免阻塞
                except queue.Empty:
                    break
                    
                try:
                    result_data = settour(arrive, self.df, self.driver)
                    
                    if not result_data.empty:
                        with self.lock:  # 使用 context manager 自動處理鎖的獲取和釋放
                            try:
                                df = pd.read_csv('settour.csv', encoding='utf-8', index_col=0)
                                con = pd.concat([df, result_data], ignore_index=True)
                                con.to_csv('settour.csv', encoding='utf-8', errors='ignore')
                            except Exception as e:
                                print(f"Error saving data: {e}")
                                
                finally:
                    self.queue.task_done()  # 標記任務完成
                    
        except Exception as e:
            print(f"Thread error: {e}")
            
        finally:
            # 確保在線程結束時關閉 WebDriver
            if self.driver:
                try:
                    self.driver.quit()
                except Exception as e:
                    print(f"Error closing WebDriver: {e}")


               
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

df=pd.read_csv('settour.csv', encoding='utf-8', index_col=0)
for _ in range(num_threads):
    worker = Worker(my_queue, lock, df)
    worker.start()
    workers.append(worker)
   
    
# 等待所有工作者完成
for worker in workers:
    worker.join()
    
# for worker in workers:
#     worker.quit_driver()

df1=pd.read_csv('settour.csv', encoding='utf-8', index_col=0)
for idx, ev, rv, gv in zip(indexes, earlierGoDatevalues, renew_datevalues, GoDatevalues):
    df1.at[idx, "earlierGoDate"]=ev
    df1.at[idx, "renew_date"]=rv
    df1.at[idx, "GoDate"]=gv
df1.to_csv('settour.csv', encoding='utf-8',errors='ignore')

#清理掉earlierGoDate和GoDate無法同步的tour
df3=pd.read_csv('settour.csv', encoding='utf-8')
ids=df3[(df3.GoDate != "['此行程目前暫告一段落，敬請期待下一季精彩行程！']")&(df3.GoDate != "[]")]
num=[]
NormGroupID=list(ids.NormGroupID)
earlierGoDate=list(ids.earlierGoDate)
for n, eg,i in zip(NormGroupID, earlierGoDate,ids.GoDate):
    GoDatelist=i.lstrip("['").rstrip("']").split("', '")
    if eg.strip(' ') in GoDatelist:
        num.append(n)
numdf=df[df.NormGroupID.isin(num)]
numdf.to_csv('settour.csv', encoding='utf-8', errors='ignore')

if len(AttractionSet)>0:       
    df2=pd.read_csv('attraction.csv', encoding='utf-8', index_col=0)
    df2_Attract=set(df2['Attraction'])
    Attract=df2_Attract|AttractionSet
    Attractdata = pd.DataFrame({"Attraction":list(Attract)})
    Attractdata.to_csv('attraction.csv', encoding='utf-8',errors='ignore')
  