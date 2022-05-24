from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time
from time import sleep
import csv
import requests
from bs4 import BeautifulSoup
# from selenium.webdriver.common.keys import Keys
#%%
driver = webdriver.Chrome("C:/Users/LAK/Desktop/chromedriver.exe")
driver.get("https://www.104.com.tw/jobs/main/") # 104首頁
actions = ActionChains(driver)
stop = 2 # 步驟間隔秒數
scroll_count = 1 # 滾輪滾動次數，1頁30筆資料
#%%  以公司名稱搜尋
actions.click(driver.find_element_by_link_text("找公司")).perform() # 點擊"找公司"
sleep(stop)
actions.click(driver.find_element_by_class_name("btn.btn-sm.btn-block.d-flex.justify-content-between.align-items-center")).perform() # 點擊區域篩選選項
sleep(stop)
actions.click(driver.find_element_by_xpath("/html/body/div[3]/div/div[2]/div/div[2]/div[2]/div/li[8]/a/span[1]/input")).perform() # 選擇"台中市"
actions.click(driver.find_element_by_xpath("/html/body/div[3]/div/div[2]/div/div[3]/button")).perform() # 點擊"確定"
sleep(stop)
actions.click(driver.find_element_by_xpath('//*[@id="index"]/div[1]/div[1]/div[1]/div/div/form/div/div[2]/button')).perform() # 點擊"搜尋"
sleep(stop)
#%% 以關鍵字搜尋
# keyword = driver.find_element_by_name("ikeyword")
# sleep(stop)
# keyword.send_keys("有公務門號") # 輸入關鍵字
# sleep(stop)
# actions.click(driver.find_element_by_xpath('//*[@id="icity"]')).perform() # 篩選區域
# sleep(stop)
# actions.click(driver.find_element_by_xpath("/html/body/div[12]/div/div[2]/div/div[2]/div[2]/div/li[8]/a/span[1]/input")).perform() # 選取台中市
# sleep(stop)
# actions.click(driver.find_element_by_class_name("category-picker-btn-primary")).perform() # 點擊"確定"
# sleep(stop)
# actions.click(driver.find_element_by_class_name("btn.btn-primary.js-formCheck")).perform() # 搜尋

# titles = driver.find_elements_by_partial_link_text("有限公司")
# sleep(stop)
#%% 加入滾輪操作
for i in range(scroll_count): 
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") # excute scroll 滾動網頁
    sleep(stop)

titles = driver.find_elements_by_class_name("info-job__text.jb-link.jb-link-blue.jb-link-blue--visited.text-truncate.d-inline-block.h2") # 空白要改成.
sleep(stop)
#%% 創建資料蒐集List
name = ["公司名稱", ]
vat = ["統一編號", ]
keyman = ["聯絡人"]
phone_num = ["聯絡電話", ]
add = ["公司地址", ]
#%% 進入每個公司名稱
for title in titles: 
    # print(title.get_attribute("href"))
    actions.click(title).perform()
    sleep(stop)
    driver.switch_to.window(driver.window_handles[1]) # 切換分頁
    name.append(driver.find_element_by_class_name("h1.d-inline").text)
    phone_num.append(driver.find_element_by_xpath('//*[@id="intro"]/div[2]/div/div[2]/div[4]/p').text)
    keyman.append(driver.find_element_by_xpath('//*[@id="intro"]/div[2]/div/div[1]/div[4]/p').text)
    add.append(driver.find_element_by_xpath('//*[@id="intro"]/div[2]/div/div[4]/div[4]/p').text)
    sleep(stop)
    driver.close()
    driver.switch_to.window(driver.window_handles[0]) # 回到主頁
print("-----------------------")
print("總共 %d 筆資料" % (len(titles)))
#%% 離開webdriver
sleep(stop)
driver.quit()
#%% 使用商工行政資料平臺所提供的API介接，查詢統一編號
for i in name:
    if i == "公司名稱":
        continue
    URL = ("https://data.gcis.nat.gov.tw/od/data/api/6BBA2268-1367-4B42-9CCA-BC17499EBE8C?$format=xml&$filter=Company_Name like %s and Company_Status eq 01&$skip=0&$top=50" % i)
    response = requests.get(URL)
    root = BeautifulSoup(response.text, "lxml")
    vat_num = root.find("business_accounting_no")
    try:
      vat.append(vat_num.text)
    except AttributeError:
      vat.append(0) # 若查詢不到值，則鍵入0
#%% 匯出至CSV檔
data = []   
with open("104_data.csv", "w", encoding="utf-8-sig", newline="") as file:
    w = csv.writer(file, delimiter = ",")
    for i in range(len(add)):
        data.append([])
        data[i].append(name[i])
        data[i].append(vat[i])
        data[i].append(keyman[i])
        data[i].append(phone_num[i])
        data[i].append(add[i])
        w.writerow(data[i])

print(time.ctime(time.time()))
