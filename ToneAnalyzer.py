import json
from watson_developer_cloud import ToneAnalyzerV3
from watson_developer_cloud import WatsonApiException

API_KEY = 'OxDiHyOmIJbkIpAuewHPSb_oHWSP76TaMobdYVrYp--8'
URL = 'https://gateway-tok.watsonplatform.net/tone-analyzer/api'

try:
    # Invoke a Tone Analyzer method
    tone_analyzer = ToneAnalyzerV3(
        version='2017-09-21',
        iam_apikey=API_KEY,
        url=URL
    )

    # textに、Speech-to-Textの結果が渡される
    text = 'Team, I know that times are tough! Product '\
        'sales have been disappointing for the past three '\
        'quarters. We have a competitive product, but we '\
        'need to do a better job of selling it!'

    tone_analysis = tone_analyzer.tone(
        {'text': text},
        'application/json'
    ).get_result()
    
    print(json.dumps(tone_analysis, indent=4))

except WatsonApiException as ex:
    print("Method failed with status code " + str(ex.code) + ": " + ex.message)