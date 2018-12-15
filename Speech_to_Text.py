from watson_developer_cloud import SpeechToTextV1
import json
from os.path import join, dirname
# APIキーをconfig.pyに書いて参照
import config
from ToneAnalyzer import analyze_emotion_from_text
from TranslateText import translate_text
import time
import threading
from Speech_Input import timekeep, recoding
from ToneAnalyzer import analyze_emotion_from_text


speech_to_text = SpeechToTextV1(
    iam_apikey=config.API_KEY_SPEEECH_TO_TEXT,
    url='https://gateway-tok.watsonplatform.net/speech-to-text/api'
)


def speech_text():
    """
    音声ファイルからテキストにする
    Watson - Text to Speech
    """
    try:
        # recodingから録音したファイル
        files = ['Speech.wav']

        for file in files:
            with open(join(dirname(__file__), './.', file),
                      'rb') as audio_file:
                speech_recognition_results = speech_to_text.recognize(
                    audio=audio_file,
                    model='ja-JP_BroadbandModel',
                    content_type='audio/wav',
                    timestamps=True,
                    word_alternatives_threshold=0.9,
                    keywords=['colorado', 'tornado', 'tornadoes'],
                    keywords_threshold=0.5
                ).get_result()
            p = json.dumps(speech_recognition_results,
                           indent=2, ensure_ascii=False)

            data = json.loads(p)
        # 音声テキスト（日本語）のみ抽出

        for i in data["results"]:
            text = i["alternatives"][0]["transcript"]
        # 翻訳APIで英語に変換
        t = translate_text(text)

        dic_English = json.loads(t)

        p = dic_English["translations"]

        for i in p:
            a = i['translation']
        # 英語テキストを感情分析にかける
        json_emotion = analyze_emotion_from_text(a)
        emotion_dict = json.loads(json_emotion)
        result = emotion_dict['document_tone']['tones'][0]['tone_name']
        # リストに追加してみてresultが正しく出力されるか確認
        emotion_list.append(result)
        # [最終結果:感情を表す英単語の文字列]
        return result
    except UnboundLocalError:
        print("もっとはっきりしゃべってください！！")
    except IndexError:
        print("正しく感情が認識されませんでした・・・")


emotion_list = []

# rangeに何回レコーディングをループさせるか

funcs = [timekeep, recoding, speech_text]
threads = []
current_time = time.time()

for i in range(1, 3):
    for func in funcs:
        t = threading.Thread(target=func)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()


emotion_result = emotion_list[0]
# resultが正しく出力されるか確認
print(emotion_list)

print(emotion_result)
