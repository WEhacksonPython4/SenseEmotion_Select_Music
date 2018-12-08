from watson_developer_cloud import SpeechToTextV1
import json
from os.path import join, dirname
speech_to_text = SpeechToTextV1(
    iam_apikey='J0AZx8Ht05j4MdxhMBW58BiwW8OmlSX2_0XsxMoStxtj',
    url='https://gateway-tok.watsonplatform.net/speech-to-text/api'
)


files = ['asano.wav']
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
    a = json.dumps(speech_recognition_results,
                   indent=2, ensure_ascii=False)

    b = json.loads(a)

for i in b["results"]:
    text = i["alternatives"][0]["transcript"]
    print(text)
