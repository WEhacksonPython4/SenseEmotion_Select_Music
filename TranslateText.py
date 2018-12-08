import json
from watson_developer_cloud import LanguageTranslatorV3
from watson_developer_cloud import WatsonApiException
# APIキーをconfig.pyに書いて参照
import config

def translate_text(text):
    """
    感情分析の前準備として、入力された日本語のテキストを英語に翻訳する
    Watson - Language Translator
    """
    API_KEY = config.API_KEY_TRANSLATE
    URL = "https://gateway-tok.watsonplatform.net/language-translator/api"
    source = "ja" # 入力となるテキストの言語
    target = "en" # テキストの翻訳先の言語
    try:
        # Invoke a Language Translator method
        language_translator = LanguageTranslatorV3(
            version="2018-05-01",
            iam_apikey=API_KEY,
            url=URL
        )

        # 日本語を英訳
        translation = language_translator.translate(
            text=text,
            source=source,
            target=target
        ).get_result()

        return json.dumps(translation, indent=4, ensure_ascii=False)
    except WatsonApiException as ex:
        print("Method failed with status code " + str(ex.code) + ": " + ex.message)