import requests as req
import json
from bs4 import BeautifulSoup
import pandas as pd

def crawler_104(keywordStr, areaNum):
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36",
    "Referer": "https://www.104.com.tw/jobs/search/?ro=0&kwop=7&keyword=%E5%85%AC%E5%8B%99%E6%89%8B%E6%A9%9F&expansionType=area%2Cspec%2Ccom%2Cjob%2Cwf%2Cwktm&area=6001008000&order=12&asc=0&page=7&mode=s&jobsource=2018indexpoc&langFlag=0&langStatus=0&recommendJob=1&hotJob=1"
        } # 測試後, 須附上Referer才能抓到資料
    
    roots = []
    rootsNew = []
    
    url = "https://www.104.com.tw/company/ajax/list?&jobsource=checkc&mode=s"
    keyword = "&keyword=%s" % keywordStr # 搜尋列關鍵字
    area = "&area=%s" % areaNum # 搜尋區域, 台中: 6001008000
    response = req.get(url + keyword + area, headers= headers )
    roots.append(json.loads(response.text)) 
    maxNum = roots[0]["metadata"]["pagination"]["lastPage"] # 找出總共有幾頁資料
    
    for num in range(maxNum-2):
        page = "&page=%s" % (num+2)
        response = req.get(url + keyword + area+ page, headers= headers ) 
        roots.append(json.loads(response.text))
        
    for i in range(len(roots)):
        for j in range(len(roots[i]["data"])):
            encodedCustNo = roots[i]["data"][j]["encodedCustNo"]+"?"
            url = "https://www.104.com.tw/company/ajax/content/"
            response = req.get(url + encodedCustNo, headers= headers)
            rootsNew.append(json.loads(response.text))
        
    return rootsNew
        
def data_arrange(roots):
    companyName = ["公司名稱", ]
    vat = ["統一編號"]
    phone = ["聯絡電話", ]
    address = ["公司地址", ]
    data = []
    for i in range(len(roots)):
        companyName.append(roots[i]["data"]["custName"])
        phone.append(roots[i]["data"]["phone"])
        address.append(roots[i]["data"]["address"])
        
    for i in companyName:
        if i == "公司名稱":
            continue
        URL = ("https://data.gcis.nat.gov.tw/od/data/api/6BBA2268-1367-4B42-9CCA-BC17499EBE8C?$format=xml&$filter=Company_Name like %s and Company_Status eq 01&$skip=0&$top=50" % i)
        response = req.get(URL)
        root = BeautifulSoup(response.text, "lxml")
        vat_num = root.find("business_accounting_no")
        try:
          vat.append(vat_num.text)
        except AttributeError:
          vat.append(0) # 若查詢不到值，則鍵入0
    
    for i in range(len(companyName)):
        data.append([])
        data[i].append(companyName[i])
        data[i].append(vat[i])
        data[i].append(phone[i])
        data[i].append(address[i])
        
    return companyName, vat, phone, address

def csv_Outfile(companyName, vat, phone, address):
    df = pd.DataFrame()
    df["公司名稱"] = companyName
    df["統一編號"] = vat
    df["聯絡電話"] = phone
    df["公司地址"] = address
    df.to_csv("104.csv", index=True, encoding="utf-8-sig")
        
    return len(companyName)

root = crawler_104(" ", 6001008000)
count = csv_Outfile(data_arrange(root))
print("資料筆數:", count)

    

