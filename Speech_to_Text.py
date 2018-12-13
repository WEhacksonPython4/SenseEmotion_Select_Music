from watson_developer_cloud import SpeechToTextV1
import json
from os.path import join, dirname
# APIキーをconfig.pyに書いて参照
import config
from ToneAnalyzer import analyze_emotion_from_text
from TranslateText import translate_text
import time
import threading
import Speech_Input
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

    # 音声入力したファイル
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
    # 音声テキストのみ抽出

    for i in data["results"]:
        text = i["alternatives"][0]["transcript"]

    t = translate_text(text)

    dic_English = json.loads(t)

    p = dic_English["translations"]

    for i in p:
        a = i['translation']
    json_emotion = analyze_emotion_from_text(a)
    emotion_dict = json.loads(json_emotion)
    a = emotion_dict['document_tone']['tones'][0]['tone_name']
    print(a)


# rangeに何回レコーディングをループさせるか
funcs = [Speech_Input.timekeep, Speech_Input.recoding, speech_text]
threads = []
current_time = time.time()

for i in range(1, 3):
    for func in funcs:
        t = threading.Thread(target=func)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
