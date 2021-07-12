# -*- coding: utf-8 -*-
"""
Created on Thu Jul  8 21:24:21 2021

@author: Dennis
"""

import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import re
from datetime import datetime

# 一次撈取八卦版、表特版、股票版、python版、資料科學版
gossiping_url = "https://www.ptt.cc/bbs/Gossiping/index.html"
beauty_url = "https://www.ptt.cc/bbs/Beauty/index.html"
stock_url = "https://www.ptt.cc/bbs/Stock/index.html"
python_url = "https://www.ptt.cc/bbs/Python/index.html"
dataSci_url = "https://www.ptt.cc/bbs/DataScience/index.html"

urls = [gossiping_url, beauty_url, stock_url, python_url, dataSci_url]

# 繞過未滿18歲的警告
cookies = {"over18": "1"}

ptt_articleInfo = []
now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print("Start Time =", current_time)
for j in range(len(urls)):
    # 抓版面名稱
    pattern_label = "bbs/(\w+)/index.html"
    find_label = re.search(pattern_label, urls[j]).groups()[0]
    
    data = requests.get(urls[j], cookies = cookies).text
    soup = bs(data,'lxml')
    
    # 找頁碼
    # https://www.ptt.cc/bbs/Gossiping/index38982.html 格式
    get_Newest = soup.select('div.btn-group.btn-group-paging a.btn.wide')[1]["href"]
    pattern = "/index(\d+)"
    page_num = int(re.search(pattern, get_Newest).groups()[0]) + 1 # retrieve page number from the link of second newest page
    start_page = page_num - 50 # look for articels within 50 pages
    
    # 如果起始頁面(start_page)等於或少於0時, 則從第1頁到最新一頁
    if start_page <= 0:
        start_page = 1
        
    # 抓取各版最新的50頁內文章資料
    for i in range(start_page, page_num+1):
        article_url = "https://www.ptt.cc/bbs/{}/index{}.html".format(find_label,start_page)
        data = requests.get(article_url, cookies = cookies)
        soup = bs(data.text,'lxml')
        if data.status_code == requests.codes.ok:       
            divs = soup.find_all("div","r-ent")
            
            for div in divs:
                if div.find("a"):   # 如果文章被刪除,則不會出現a標籤 (無法找到文章url)
                    ptt_author = div.find('div','author')
                    ptt_articleDate = div.find('div','date')
                    ptt_title = div.find('div','title')
                    ptt_url = div.find('a')["href"] # get article ID
                    pattern = "/bbs/{}/(\w.+).html".format(find_label)
                    ptt_id = re.search(pattern, str(ptt_url)).groups()[0]
                    ptt_articleInfo.append({
                        'category': find_label.strip(),
                        'title': ptt_title.text.strip(),
                        'date': ptt_articleDate.text.strip(),
                        'author': ptt_author.text.strip(),
                        'article_ID': ptt_id.strip(),
                        'aritcle_URL': "https://www.ptt.cc" + ptt_url.strip(),
                    })
            start_page = start_page + 1
        else:
            print("Failed to retrieve webpage")
            
end = datetime.now()
end_time = end.strftime("%H:%M:%S")
print("End Time =", end_time)
df = pd.DataFrame(ptt_articleInfo)
