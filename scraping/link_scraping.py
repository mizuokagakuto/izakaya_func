# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import time
from retrying import retry
from requests.exceptions import HTTPError


class Tabelog:
    
    #食べログスクレイピングクラス
    #test_mode=Trueで動作させると、最初のページの３店舗のデータのみを取得できる
    

    def __init__(
        self, base_url, test_mode=False, p_ward="福岡市内", begin_page=1, end_page=20
    ):

        # 変数宣言
        self.store_id = ""
        self.store_id_num = 0
        self.store_name = ""
        self.link_url = "NaN"#####################################
        self.ward = p_ward
        self.columns = [
            "store_id",
            "store_name",
            "link_url",
        ]
        self.df = pd.DataFrame(columns=self.columns)
        self.__regexcomp = re.compile(r"\n|\s")  # \nは改行、\sは空白

        page_num = begin_page  # 店舗一覧ページ番号

        if test_mode:
            list_url = (
                base_url + str(page_num) + "/?Srt=D&SrtT=rt&sort_mode=1"
            )  # 食べログの点数ランキングでソートする際に必要な処理
            self.scrape_list(list_url, mode=test_mode)
        else:
            while True:
                list_url = (
                    base_url + str(page_num) + "/?Srt=D&SrtT=rt&sort_mode=1"
                )  # 食べログの点数ランキングでソートする際に必要な処理
                if self.scrape_list(list_url, mode=test_mode) != True:
                    break

                # INパラメータまでのページ数データを取得する
                if page_num >= end_page:
                    break
                page_num += 1
        return

    def scrape_list(self, list_url, mode):
        
        #店舗一覧ページのパーシング

        @retry(stop_max_attempt_number=5, wait_fixed=2000)
        def safe_get(url):
            r = requests.get(url)
            r.raise_for_status()  # Raise an error for bad responses
            return r
        
        r = safe_get(list_url)
        if r.status_code != requests.codes.ok:
            return False

        soup = BeautifulSoup(r.content, "html.parser")
        soup_a_list = soup.find_all("a", class_="list-rst__rst-name-target")  # 店名一覧
        # print(soup_a_list)#確認ok

        if len(soup_a_list) == 0:
            return False

        if mode:
            for soup_a in soup_a_list[:2]:
                item_url = soup_a.get("href")  # 店の個別ページURLを取得
                print(item_url)
                self.link_url = item_url
                self.store_id_num += 1
                self.scrape_item(item_url, mode)
        else:
            for soup_a in soup_a_list:
                item_url = soup_a.get("href")  # 店の個別ページURLを取得
                print(item_url)
                self.link_url = item_url
                self.store_id_num += 1
                # print(item_url)#こっちで実行できてる
                self.scrape_item(item_url, mode)

        return True

    def scrape_item(self, item_url, mode):

        # 個別店舗情報ページのパーシング

        start = time.time()

        @retry(stop_max_attempt_number=5, wait_fixed=2000)
        def safe_get(url):
            r = requests.get(url)
            r.raise_for_status()  # Raise an error for bad responses
            return r
        
        r = safe_get(item_url)

        if r.status_code != requests.codes.ok:
            print(f"error:not found{ item_url }")
            return

        soup = BeautifulSoup(r.content, "html.parser")

        store_name_tag = soup.find("h2", class_="display-name")
        store_name = store_name_tag.span.string
        print("{}→店名:{}\n".format(self.store_id_num, store_name.strip()), end="")
        self.store_name = store_name.strip()

        self.make_df()
        return

    def make_df(self):
        self.store_id = str(self.store_id_num).zfill(8)  # 0パディング
        se = pd.Series(
            [
                self.store_id,
                self.store_name,
                self.link_url
            ],
            index=self.columns,
        )  # 行を作成
        self.df = pd.concat(
            [self.df, se.to_frame().T], ignore_index=True
        )  # 行を追加#################################################################################################
        return
    
fukuokacity_izakaya_review = Tabelog(
    #base_url="https://tabelog.com/fukuoka/A4001/A400102/rstLst/RC21/",#中州
    base_url="https://tabelog.com/fukuoka/A4001/A400103/rstLst/RC21/",#天神
    #base_url="https://tabelog.com/fukuoka/C40133/C106028/rstLst/RC21/",#大名
    #https://tabelog.com/miyagi/A0401/rstLst/RC21/#仙台？
    test_mode=False,
    p_ward="中州",
)

fukuokacity_izakaya_review.df.to_csv(".//output//fukuokacity_izakaya_link.csv", index=False, encoding="utf-8-sig")