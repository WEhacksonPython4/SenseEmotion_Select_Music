# 事前に、コマンドプロンプトでpip install spotipy
# 参考サイト：
# https://spotipy.readthedocs.io/en/latest/
# https://githubja.com/plamere/spotipy

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import config
from pathlib import Path
from TranslateText import translate_text
from ToneAnalyzer import analyze_emotion_from_text
import json

CLIENT_ID = config.CLIENT_ID_SPOTIFY
CLIENT_SECRET = config.CLIENT_SECRET_SPOTIFY
client_credentials_manager = spotipy.oauth2.SpotifyClientCredentials(CLIENT_ID, CLIENT_SECRET)

sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def translate_and_store_lyrics():
    """
    歌詞データ400個を英訳し、./json_files/translated_lyrics直下に保存する
    """
    p_lyrics_dir = Path("./json_files/lyrics_files") # 歌詞ディレクトリのパス
    lyrics_data = list(p_lyrics_dir.iterdir()) # 歌詞JSONデータ400個のリスト
    lyrics_json = None # 歌詞データのJSONを読み込んで保存する変数
    p_translated_lyrics = Path("./json_files/translated_lyrics") # 歌詞の英訳データを保存するディレクトリ

    for i, data in enumerate(lyrics_data):
        print("{}th lyrics".format(i + 1))
        
        # 歌詞データを読み込んで英訳
        with Path(data).open("r", encoding="utf-8") as f:
            lyrics_json = json.load(f)
        translated_result = translate_text(lyrics_json["lyrics"]) # JSON形式の文字列が格納される

        # 翻訳結果の文のみを抽出
        decoded_result = json.loads(translated_result)
        translated_lyrics = decoded_result["translations"][0]["translation"]
        # 歌詞データの辞書に英訳結果の情報を追加
        lyrics_json["translated_lyrics"] = translated_lyrics

        # ディレクトリp_translated_lyricsに新しく保存
        with Path(p_translated_lyrics).open(mode="w", encoding="utf-8") as f:
            json.dump(lyrics_json, f, indent=2, ensure_ascii=False)

def analyze_and_choose_emotion():
    """
    英訳済みの歌詞データを感情分析APIに入力する
    結果から、document_tone内のリストを取得する
    
    感情分析結果が"Analytical", "Confident", "Tentative"だったら、2番目の候補の感情を見る。
    全部該当しなかったらスキップ
    """
    p_translated_lyrics_dir = Path("./json_files/translated_lyrics")
    translated_lyrics_data = list(p_translated_lyrics_dir.iterdir()) # 英訳済み歌詞JSONデータ400個のリスト
    translated_lyrics_json = None # 英訳済み歌詞データのJSONを読み込んで保存する変数
    emotion_dirs = ["Anger", "Fear", "Joy", "Sadness"] # 感情ディレクトリ名のリスト

    for i, data in enumerate(translated_lyrics_data):
        chosen_emotion = None # 選択された感情を保存する変数

        print("{}th lyrics".format(i + 1))

        # 英訳済みの歌詞データを読み込む
        with Path(data).open(mode="r", encoding="utf-8") as f:
            translated_lyrics_json = json.load(f)
        translated_lyrics = translated_lyrics_json["lyrics"]

        # 読み込んだ歌詞データを感情分析APIに入力する
        analyze_response = analyze_emotion_from_text(translated_lyrics)
        # 分析結果のJSON文字列をデコード
        decoded_json = json.loads(analyze_response)
        # テキスト全体の分析結果のリストを抽出し、scoreで降順ソート
        lyrics_emotions = decoded_json["document_tone"]["tones"]
        decoded_json.sort(key=lambda x: x["score"], reverse=True)
        
        for emotion_candidate in decoded_json["document_tone"]["tones"]:
            # emotion_candidate -> {"score": score, "tone_id": tone_id, "tone_name": tone_name}
            if emotion_candidate["tone_name"] in emotion_dirs:
                # Anger, Fear, Joy, Sadnessのどれかに当てはまるなら、その歌詞の感情として選択
                chosen_emotion = emotion_candidate ["tone_name"]
                break
        
        # 感情分析結果のどれか1つでもemotion_dirs内の感情を含んでいたら
        if chosen != None:
            # 英訳済みの歌詞データに感情情報を追加
            translated_lyrics_json["tone_name"] = chosen_emotion
            # 感情情報付き&英訳済みの歌詞データの保存
            p_emotion_lyrics = Path("./json_files").joinpath(chosen_emotion)
            with Path(p_emotion_lyrics).open("w", encoding="utf-8") as f:
                json.dump(translated_lyrics_json, f, indent=2, ensure_ascii=False)

# ディレクトリ内のファイルを順に見ていく
# "title"（曲名）でAPI検索かける
# 検索した曲があれば、曲を持ってくる
# 取得したら曲を再生

# ※Spotifyで曲を再生（playback）できるか？

"""
# サンプルコード1
results = sp.search(q='weezer', limit=20)
for lyrics, t in enumerate(results['tracks']['items']):
    print(' ', lyrics, t['name'])

# サンプルコード2
playlists = sp.user_playlists('spotify')
while playlists:
    for lyrics, playlist in enumerate(playlists['items']):
        print("%4d %s %s" % (lyrics + 1 + playlists['offset'], playlist['uri'],  playlist['name']))
    if playlists['next']:
        playlists = sp.next(playlists)
    else:
        playlists = None
"""

if __name__ == "__main__":
    translate_and_store_lyrics()
    print("Finished translating and storing lyrics.")
    analyze_and_choose_emotion()
    print("Finished analyzing and choosing emotion.")