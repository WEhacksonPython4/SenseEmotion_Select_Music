from watson_developer_cloud import SpeechToTextV1
import json
from os.path import join, dirname
# APIキーをconfig.pyに書いて参照
import config

speech_to_text = SpeechToTextV1(
    iam_apikey='config.API_KEY_TONEANALYZER',
    url='https://gateway-tok.watsonplatform.net/speech-to-text/api'
)

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


def speech():
    for i in data["results"]:
        text = i["alternatives"][0]["transcript"]
        print(text)


speech()
