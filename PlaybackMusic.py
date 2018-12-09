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
from pprint import pprint

def translate_and_store_lyrics():
    """
    歌詞データ400個を英訳し、./json_files/translated_lyrics直下に保存する
    """
    p_lyrics_dir = Path("./json_files/lyrics_files") # 歌詞ディレクトリのパス
    lyrics_json = None # 歌詞データのJSONを読み込んで保存する変数
    p_translated_lyrics = Path("./json_files/translated_lyrics") # 歌詞の英訳データを保存するディレクトリ

    for i, data in enumerate(p_lyrics_dir.iterdir()): # 歌詞JSONデータ400個のリスト
        print("{}th lyrics".format(i + 1))
        json_name = str(data).split("\\")[-1] # ディレクトリ階層ごとに区切って末尾のJSONファイル名を取り出す
        
        # 歌詞データを読み込んで英訳
        with Path(str(data)).open("r", encoding="utf-8") as f:
            lyrics_json = json.load(f)
        translated_result = translate_text(lyrics_json["lyrics"]) # JSON形式の文字列が格納される

        # 翻訳結果の文のみを抽出
        decoded_result = json.loads(translated_result)
        translated_lyrics = decoded_result["translations"][0]["translation"]
        # 歌詞データの辞書に英訳結果の情報を追加
        lyrics_json["translated_lyrics"] = translated_lyrics

        # ディレクトリp_translated_lyricsに新しくJSONファイルを保存
        # ファイル名はlyrics_files直下と同じ
        with p_translated_lyrics.joinpath(json_name).open(mode="w", encoding="utf-8") as f:
            json.dump(lyrics_json, f, indent=2, ensure_ascii=False)

def analyze_and_choose_emotion():
    """
    ・英訳済みの歌詞データを感情分析APIに入力する
    ・その結果から感情情報付きの歌詞データを抽出する
    
    どの感情ディレクトリに保存するかを決める
    ・抽出した歌詞データを、scoreが高い順にソートする
    ・感情分析結果が"Analytical", "Confident", "Tentative"だったら、2番目の候補の感情を見る。
      4つの感情と同じ感情ラベルが無ければ、該当する感情ディレクトリは無いと見なし、その歌詞データの保存をスキップする
    """
    p_translated_lyrics_dir = Path("./json_files/translated_lyrics")
    translated_lyrics_json = None # 英訳済み歌詞データのJSONを読み込んで保存する変数
    emotion_dirs = ["Anger", "Fear", "Joy", "Sadness"] # 感情ディレクトリ名のリスト

    for i, data in enumerate(p_translated_lyrics_dir.iterdir()): # 英訳済み歌詞JSONデータ400個のリスト
        print("{}th lyrics".format(i + 1))
        chosen_emotion = None # 選択された感情を保存する変数
        json_name = str(data).split("\\")[-1] # ディレクトリ階層ごとに区切って末尾のJSONファイル名を取り出す
        
        # 英訳済みの歌詞データを読み込む
        with Path(str(data)).open(mode="r", encoding="utf-8") as f:
            translated_lyrics_json = json.load(f)
        translated_lyrics = translated_lyrics_json["translated_lyrics"]

        # 読み込んだ歌詞データを感情分析APIに入力する
        analyze_response = analyze_emotion_from_text(translated_lyrics)
        # 分析結果のJSON文字列をデコード
        decoded_json = json.loads(analyze_response)
        # テキスト全体の分析結果のリストを抽出し、scoreで降順ソート
        lyrics_emotions = decoded_json["document_tone"]["tones"]
        lyrics_emotions.sort(key=lambda x: x["score"], reverse=True)
        
        for emotion_candidate in lyrics_emotions:
            # emotion_candidate -> {"score": score, "tone_id": tone_id, "tone_name": tone_name}
            if emotion_candidate["tone_name"] in emotion_dirs:
                # Anger, Fear, Joy, Sadnessのどれかに当てはまるなら、その歌詞の感情として選択
                chosen_emotion = emotion_candidate["tone_name"]
                break
        
        # 感情分析結果のどれか1つでもemotion_dirs内の感情を含んでいたら
        if chosen_emotion != None:
            # 英訳済みの歌詞データに感情情報を追加
            translated_lyrics_json["tone_name"] = chosen_emotion
            # 感情情報付き&英訳済みの歌詞データの保存
            p_emotion_lyrics = Path("./json_files").joinpath(chosen_emotion)
            with p_emotion_lyrics.joinpath(json_name).open("w", encoding="utf-8") as f:
                json.dump(translated_lyrics_json, f, indent=2, ensure_ascii=False)

def choose_emotion_dir_for_retrieval(emotions):
    """
    英訳済みの会話テキストを感情分析した結果から、どの感情ディレクトリを見るかを決定する

    ・各感情ディレクトリ内のJSONファイル(感情別歌詞データ)を、emotionsの要素のscoreが大きい順に見ていく
    ・JSONファイルから、検索に使う情報を取得する
    ※emotionsの要素が"Analytical", "Confident", "Tentative"だったら、2番目の候補の感情を見る。
      emotionsの要素に4つの感情ラベル(tone_name)が1つも無ければ、該当する曲が無いとする
    
    emotions: 会話データを英訳＆感情分析にかけた結果のリスト
    -> [{"score": score, "tone_id": tone_id, "tone_name": tone_name}, ...]
    """
    emotion_dirs = ["Anger", "Fear", "Joy", "Sadness"] # 感情ディレクトリ名のリスト
    lyrics_json_for_emotion = None # 英訳＆感情情報付き歌詞データを取得して保存する変数
    retrieve_condidates = [] # 検索対象となる情報を保存する変数(return)

    # 会話の感情分析結果を、スコアの高い順にソートする
    emotions.sort(key=lambda x: x["score"], reverse=True)
    # 英訳＆感情情報付き歌詞データを検索する際、どのディレクトリを見るかを決定する
    chosen_emotions = [emotion for emotion in emotions if emotion["tone_name"] in emotion_dirs]

    if chosen_emotions != []:
        for chosen_emotion in chosen_emotions:
            for data in Path("./json_files").joinpath(chosen_emotion["tone_name"]).iterdir():
                json_name = str(data).split("\\")[-1] # ディレクトリ階層ごとに区切って末尾のJSONファイル名を取り出す
                with Path(data).open(encoding="utf-8") as f:
                    # {"song_name": song_name, "singer": singer, "lyrics": lyrics, "translated_lyrics": translated_lyrics, "tone_name": tone_name}
                    lyrics_json_for_emotion = json.load(f)
                    # 各情報を取得
                    song_name = lyrics_json_for_emotion["song_name"]
                    singer = lyrics_json_for_emotion["singer"]
                    # 検索クエリになりそうな曲名と歌手名を検索情報に追加
                    retrieve_condidates.append((song_name, singer))
        return retrieve_condidates
    else: # 感情分析の結果、4つの感情ラベルが無い
        return None # 該当する曲は無し

def choose_playback_music(retrieval_candidates):
    """
    再生する曲を選択する
    ・Anger -> Joy
    ・Sadness -> Joy
    ・Fear -> Anger? Joy
    ・Joy -> Joy

    ・感情別歌詞データから検索クエリを取得し、曲名でSpotifyを検索する
    ・曲が見つかれば、曲を取得する
    ・取得した曲のリストをreturn
    """
    CLIENT_ID = config.CLIENT_ID_SPOTIFY
    CLIENT_SECRET = config.CLIENT_SECRET_SPOTIFY
    client_credentials_manager = spotipy.oauth2.SpotifyClientCredentials(CLIENT_ID, CLIENT_SECRET)

    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    track_id_list = []
    if retrieval_candidates != None:
        for i, candidate in enumerate(retrieval_candidates):
            song_name, singer = candidate[0], candidate[1] # (song_name, singer)
            print("{}th retrival ... song_name, singer = {}, {}".format(i + 1, song_name, singer))

            # 曲名で検索
            result_dict = sp.search(q='track:' + song_name, type='track')

            # 更にアーティスト名で絞り込む
            tracks_items = result_dict["tracks"]["items"]
            for j, item_in_track in enumerate(tracks_items):
                print("{}th track".format(j + 1))
                track_whole_name = item_in_track["name"] # 検索された曲の名前（完全一致バージョン）
                artist_name = item_in_track["artists"][0]["name"] # 検索された曲のアーティスト名
                track_id = item_in_track["id"] # 検索された曲のID（これを曲の再生で使う）
                print("track_whole_name = {}, artist_name = {}, track_id = {}".format(track_whole_name, artist_name, track_id))

                if song_name == track_whole_name and singer == artist_name:
                    # 検索クエリと検索結果の曲名＆アーティスト名が一致したら、再生候補リストに追加
                    # 改善点：この条件指定だと、アレンジ版などが選ばれなかったりする
                    track_id_list.append(track_id)
            print()
        print("track_id_list: {}".format(track_id_list))
        return track_id_list
    else:
        return None # 再生候補無し
            
def playback():
    """
    再生候補となる曲のIDリストからランダムで曲を選択し、再生する
    """
    return None

if __name__ == "__main__":
    # データ作成済みなら以下は実行不要
    # translate_and_store_lyrics()
    # print("Finished translating and storing lyrics.")
    # analyze_and_choose_emotion()
    # print("Finished analyzing and choosing emotion.")

    print("Let's Playback music!")
    print()
    # 会話データの入力
    text = "Hello, I'm happy!"
    
    # 会話データからテキストを抽出
    
    # テキストを日本語から英語に翻訳
    
    # 翻訳されたテキストを感情分析
    decoded_json = json.loads(analyze_emotion_from_text(text))
    conversation_emotions = decoded_json["document_tone"]["tones"]
    
    # 分析結果に基づいて再生する曲を探す
    # 検索クエリの取得
    retrieval_candidates = choose_emotion_dir_for_retrieval(conversation_emotions)
    choose_playback_music(retrieval_candidates)

    # 再生
