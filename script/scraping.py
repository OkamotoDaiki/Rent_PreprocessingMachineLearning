from bs4 import BeautifulSoup
import requests
import sys
import time
import pandas as pd
import numpy as np

def GetHTML(url, mode="Download"):
    """
    HTMLをBeautifulSoupで取得するための関数
    Get HTML with BeautifulSoup module.

    Attributes:
        url:URL
        mode: Switching debug mode. Specified 'text' when debuging mode.

    returns:
        soup: beautifulsoup object.
        When error: int zero.
    """
    if mode=="Download":
       response = requests.get(url)
       if response.status_code == requests.codes.ok:
           #Generate a object based on HTML
           print("Downloads...\n{0}".format(url))
           soup = BeautifulSoup(response.text, 'html.parser')
           return soup
       else:
           print("[Error] status code error.")
           sys.exit()
           return 0

    elif mode=="text":
        """
        Debug Mode
        """
        txtfpath = "./HTML/suumo.html"
        with open(txtfpath, 'r') as f:
            s = f.read()
        soup = BeautifulSoup(s, 'html.parser')
        return soup

    else:
        print("[Error] mode argument error.")
        sys.exit()
        return 0


def GenerateURLs(url):
    """
    ターゲットを検索するためのリストの生成
    Generate URL list to sereach target.
    ---structure---
        Inital URL + "&page=" + Any number of target.
    --------------- 

    Attributes:
        url: url to read the city list of suumo.

    returns:
        urls: a list of urls that separated read url.
    """
    soup = GetHTML(url, "Download")
    pages = soup.find("body").find("div", {"class":"pagination pagination_set-nav"})
    last_num = int(str(pages).split('</li>')[-2].split('</a>')[-2].split('>')[-1].replace(' ', '').replace('\n',''))
    print(last_num)
    urls = [url + '&page=' + str(i+2) for i in range(last_num-1)]
    urls.insert(0, url)
    return urls


def GetDataFromHTML(urls, mode="Download"):
    """
    生成されたURL群を展開して、HTMLを解析し、データフレーム化する。
    
    Attirbutes:
        urls: Detected URLs
        mode: Choice of parsing only text in debug mode or downloading. Choices are "Download" or "text".
    returns:
        suumo_df: Object converted to data frame from acquired data
    """
    #初期化
    name = [] #マンション名
    address = [] #住所
    location0 = [] #立地条件1
    location1 = [] #立地条件2
    location2 = [] #立地条件3
    BuildingYear = [] #築年数
    height = [] #建物高さ
    floor = [] #階層
    rent = [] #賃料
    admin = [] #共益費
    deposit = [] #敷金
    gratuity = [] #礼金
    floor_plan = [] #間取り
    area = [] #専有面積

    for url in urls:
        soup = GetHTML(url, mode)
        summary = soup.find('div', {'id':'js-bukkenList'})
        #物件情報
        cassetteitems = summary.find_all("div", {'class':'cassetteitem'})

        for i in range(len(cassetteitems)):
            #マンション名の取得
            title = str(cassetteitems[i].find_all('div', {'class':'cassetteitem_content-title'})).replace('[<div class="cassetteitem_content-title">', '').replace('</div>]', '').replace('\n', '').replace(' ', '')
            name.append(title)
            #住所の取得
            col1 = str(cassetteitems[i].find_all('li',{'class':'cassetteitem_detail-col1'})).replace('[<li class="cassetteitem_detail-col1">', '').replace('</li>]', '').replace('\n', '').replace(' ', '')
            address.append(col1)
            #立地の取得
            col2 = cassetteitems[i].find_all('li', {'class':'cassetteitem_detail-col2'})[0].find_all('div', {'class':'cassetteitem_detail-text'}, limit=3)
            location0.append(str(col2[0].find(text=True)))
            location1.append(str(col2[1].find(text=True)))
            location2.append(str(col2[2].find(text=True)))

            #築年数、建物の高さを取得
            col3 = cassetteitems[i].find_all('li', {'class':'cassetteitem_detail-col3'})
            BuildingYear.append(str(col3[0].find_all('div')[0]).replace('<div>', '').replace('</div>', ''))
            height.append(str(col3[0].find_all('div')[1]).replace('<div>', '').replace('</div>', ''))
            
            #[Bug]以下、一つの建物に対してのみ。複数は取得できない
            #階層のデータを取得
            floor.append(str(cassetteitems[i].find_all('td', limit=3)[2]).replace('<td>', '').replace('</td>', '').replace('\n', '').replace(' ', '').replace('\r', '').replace('\t', ''))
            #賃料のデータを取得
            rent.append(str(cassetteitems[i].find_all('span', {'class':'cassetteitem_price cassetteitem_price--rent'})[0].find_all('span', {'class':'cassetteitem_other-emphasis ui-text--bold'})[0].find(text=True)).replace('\n', '').replace(' ', ''))
            #共益費のデータを取得
            admin.append(str(cassetteitems[i].find_all('span', {'class':'cassetteitem_price cassetteitem_price--administration'})[0].find(text=True)))
            #敷金のデータを取得
            deposit.append(str(cassetteitems[i].find_all('span', 'cassetteitem_price cassetteitem_price--deposit')[0].find(text=True)))
            #礼金のデータを取得
            gratuity.append(str(cassetteitems[i].find_all('span', {'class':'cassetteitem_price cassetteitem_price--gratuity'})[0].find(text=True)))
            #間取りのデータを取得
            floor_plan.append(str(cassetteitems[i].find_all('span', {'class':'cassetteitem_madori'})[0].find(text=True)))
            #専有面積のデータを取得
            area.append(str(cassetteitems[i].find_all('span', {'class':'cassetteitem_menseki'})[0].find(text=True))
            +str(cassetteitems[i].find_all('span', {'class':'cassetteitem_menseki'})[0].find('sup')).replace('<sup>', '').replace('</sup>', ''))

        #スクレイピングマナー
        sleepnum = np.random.randint(10, 60)
        time.sleep(sleepnum)

    #各リストのシリーズ化
    name = pd.Series(name) #マンション名
    address = pd.Series(address) #住所
    location0 = pd.Series(location0) #立地条件1
    location1 = pd.Series(location1) #立地条件2
    location2 = pd.Series(location2) #立地条件3
    BuildingYear = pd.Series(BuildingYear) #築年数
    height = pd.Series(height) #建物高さ
    floor = pd.Series(floor) #階層
    rent = pd.Series(rent) #賃料
    admin = pd.Series(admin) #共益費
    deposit = pd.Series(deposit) #敷金
    gratuity = pd.Series(gratuity) #礼金
    floor_plan = pd.Series(floor_plan) #間取り
    area = pd.Series(area) #専有面積

    #各リストをデータフレーム化
    suumo_df = pd.concat([name, address, location0, location1, location2, BuildingYear, height, floor, rent, admin, deposit, gratuity, floor_plan, area], axis=1)
    suumo_df.columns=['マンション名','住所','立地1','立地2','立地3','築年数','建物高さ','階','賃料','管理費','敷金','礼金','間取り','専有面積']
    return suumo_df


def main():
    outputfpath = sys.argv[1]
    InputURL = sys.argv[2]
    mode = "Download"

    #全ページの取得
    urls = GenerateURLs(InputURL)
    suumo_df = GetDataFromHTML(urls, mode=mode)

    #csvファイルとして保存
    suumo_df.to_csv(outputfpath, sep = ',',encoding='utf-16', index=False)
    return 0


if __name__=="__main__":
    #タイマー
    start = time.time()
    main()
    elapsed_time = time.time() - start

    elapsed_hour = elapsed_time // 3600
    elapsed_minute = (elapsed_time % 3600) // 60
    elapsed_second = elapsed_time % 3600 % 60

    print(str(int(elapsed_hour)).zfill(2) + ":" + str(int(elapsed_minute)).zfill(2) + ":" + str(int(elapsed_second)).zfill(2))