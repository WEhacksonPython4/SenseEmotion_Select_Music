import json
from watson_developer_cloud import ToneAnalyzerV3
from TranslateText import translate_text
from watson_developer_cloud import WatsonApiException
# APIキーをconfig.pyに書いて参照
import config

def analyze_emotion_from_text(text):
    """
    テキスト（日本語不可）から感情を分析する
    Watson - ToneAnalyzer
    """
    API_KEY = config.API_KEY_TONEANALYZER
    URL = "https://gateway-tok.watsonplatform.net/tone-analyzer/api"
    try:
        # Invoke a Tone Analyzer method
        tone_analyzer = ToneAnalyzerV3(
            version='2017-09-21',
            iam_apikey=API_KEY,
            url=URL
        )

        tone_analysis = tone_analyzer.tone(
            {'text': text},
            'application/json'
        ).get_result()
        
        return json.dumps(tone_analysis, indent=4, ensure_ascii=False)

    except WatsonApiException as ex:
        print("Method failed with status code " + str(ex.code) + ": " + ex.message)

if __name__ == "__main__":
    # textに、Speech-to-Textの結果が渡される
    # サンプルのテキスト
    text = 'Team, I know that times are tough! Product '\
        'sales have been disappointing for the past three '\
        'quarters. We have a competitive product, but we '\
        'need to do a better job of selling it!'
    
    # Google翻訳で、日本語を英語に翻訳する
    print("Translate Japanese -> English")
    orig_text = "これめっちゃ面白いな。これ何円で買える？"
    print("inputted text = {}".format(orig_text))
    translate_response = translate_text(orig_text)

    # JSON文字列をプログラムで使用可能な形式に変換（デコード）
    # 参考サイト：http://programming-study.com/technology/python-json-dumps/
    decoded_json = json.loads(translate_response)
    # JSONから翻訳結果の文のみを抽出
    translate_result = decoded_json["translations"][0]["translation"]
    print("translate_result = {}".format(translate_result))
    print()

    ### 英訳したテキストを感情分析する
    print("Tone Analyze translated text")
    print("inputted text = {}".format(translate_result))
    analyze_response = analyze_emotion_from_text(translate_result)
    
    # JSONをデコード
    decoded_json = json.loads(analyze_response)
    # 分析結果を抽出
    analyze_result = decoded_json["document_tone"]
    print("analyze_result = {}".format(analyze_result))