from bs4 import BeautifulSoup
import requests
import time
import re
from datetime import datetime
import json

# 検索語と曲リストページのURL
QUERY_WORD = "xmas"

list_page_url = f"https://www.uta-net.com/search/?Aselect=2&Bselect=3&Keyword={QUERY_WORD}&sort=4"

# ファイル名を固有名にするために現在時刻を取得
now_datetime = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")


# 上記ページのHTMLを取ってくる
response = requests.get(list_page_url)
response.encoding = response.apparent_encoding

soup = BeautifulSoup(response.text, "html.parser")

# 各曲の詳細歌詞ページへのURLをリストで取得
detail_urls = []
td_td1 = soup.select("td.td1")
for i in range(30):
    one_of_td1 = td_td1[i]
    a_tag = one_of_td1.find_all("a")[0]
    detail_urls.append(a_tag["href"])

# 各曲の詳細歌詞ページへアクセス
for j in range(len(detail_urls)):
    # 各曲の詳細歌詞ページのHTMLを取ってくる
    response = requests.get("https://www.uta-net.com" + detail_urls[j])
    response.encoding = response.apparent_encoding

    soup = BeautifulSoup(response.text, "html.parser")

    # 歌詞を取ってくる
    lyrics_areas = soup.select("#kashi_area")
    lyrics_area = lyrics_areas[0]
    lyrics = lyrics_area.text.strip()

    # 歌詞の間の改行を削除
    lyrics = re.sub("\n", "", lyrics)

    # 曲名を取ってくる
    title_area = soup.select("div.title")[0]
    song_name = title_area.find("h2").text.strip()

    # 歌手名を取ってくる
    artist_area = soup.select("div.kashi_artist")[0]
    singer = artist_area.find("span").text.strip()

    # Json用の辞書を作成
    song_dict = {"song_name": song_name, "singer": singer, "lyrics": lyrics}

    # 歌詞をファイルに書き込み
    with open(f"lyrics_files/songs_lyrics{j}_{now_datetime}.json", mode="w", encoding="utf-8") as f:
        json.dump(song_dict, f, indent=4, ensure_ascii=False)
    time.sleep(1)
