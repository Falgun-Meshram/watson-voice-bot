import json
import os
import requests

from dotenv import load_dotenv
from flask import Flask
from flask import jsonify
from flask import request
from flask_socketio import SocketIO
from watson_developer_cloud import AuthorizationV1
from watson_developer_cloud import AssistantV1
from watson_developer_cloud import SpeechToTextV1
from watson_developer_cloud import TextToSpeechV1
from os.path import join, dirname

# speech_to_text = SpeechToTextV1('https://gateway-wdc.watsonplatform.net/speech-to-text/api',
#                                 None, None,                                '63f2322b-141b-4ba5-8b46-3d81dd8ee181')

# print('speech to text')
# print(dir(speech_to_text))

app = Flask(__name__)
socketio = SocketIO(app)


if 'VCAP_SERVICES' in os.environ:
    vcap = json.loads(os.getenv('VCAP_SERVICES'))
    print('Found VCAP_SERVICES')
    if 'conversation' in vcap:
        conversationCreds = vcap['conversation'][0]['credentials']
        assistantUsername = conversationCreds['username']
        assistantPassword = conversationCreds['password']

    if 'text_to_speech' in vcap:
        textToSpeechCreds = vcap['text_to_speech'][0]['credentials']
        textToSpeechUser = textToSpeechCreds['username']
        textToSpeechPassword = textToSpeechCreds['password']
    if 'speech_to_text' in vcap:
        speechToTextCreds = vcap['speech_to_text'][0]['credentials']
        speechToTextUser = speechToTextCreds['username']
        speechToTextPassword = speechToTextCreds['password']
    if "WORKSPACE_ID" in os.environ:
        workspace_id = os.getenv('WORKSPACE_ID')

    if "ASSISTANT_IAM_APIKEY" in os.environ:
        assistantIAMKey = os.getenv('ASSISTANT_IAM_APIKEY')

else:
    print('Found local VCAP_SERVICES')
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
    assistantUsername = os.environ.get('ASSISTANT_USERNAME')
    assistantPassword = os.environ.get('ASSISTANT_PASSWORD')
    assistantIAMKey = os.environ.get('ASSISTANT_IAM_APIKEY')
    assistantUrl = os.environ.get('ASSISTANT_URL')
    TTSAPIKey = os.environ.get('TTS_API_KEY')
    STTAPIKey = os.environ.get('STT_API_KEY')

    textToSpeechUser = os.environ.get('TEXTTOSPEECH_USER')
    textToSpeechPassword = os.environ.get('TEXTTOSPEECH_PASSWORD')
    workspace_id = os.environ.get('WORKSPACE_ID')

    print(assistantUsername,
          assistantPassword,
          assistantIAMKey,
          assistantUrl,
          textToSpeechUser,
          workspace_id,
          textToSpeechPassword)

    # speechToTextUser = os.environ.get('SPEECHTOTEXT_USER')
    # speechToTextPassword = os.environ.get('SPEECHTOTEXT_PASSWORD')


@app.route('/')
def Welcome():
    return app.send_static_file('index.html')


@app.route('/api/conversation', methods=['POST', 'GET'])
def getConvResponse():
    # Instantiate Watson Assistant client.
    # only give a url if we have one (don't override the default)
    try:
        print("inside api/conversation")
        assistant_kwargs = {
            'version': '2018-11-04',
            'username': assistantUsername,
            'password': assistantPassword,
        }
        # 'iam_api_key': assistantIAMKey

        print("Running auth now with args")
        print(assistant_kwargs)
        assistant = AssistantV1(**assistant_kwargs)
        print("Auth ran")
        print("assistant is: ")
        print(assistant)

        convText = request.form.get('convText')
        convContext = request.form.get('context')

        if convContext is None:
            convContext = "{}"
        print("convContext" + convContext)
        jsonContext = json.loads(convContext)

        response = assistant.message(workspace_id=workspace_id,
                                     input={'text': convText},
                                     context=jsonContext)
    except Exception as e:
        print("95 error is: " + e)

    print("res is: ")
    print(response)
    reponseText = response["output"]["text"]
    responseDetails = {'responseText': reponseText[0],
                       'context': response["context"]}
    return jsonify(results=responseDetails)


@app.route('/api/speech-to-text/token', methods=['POST', 'GET'])
def getSttToken():
    try:
        # authorization = AuthorizationV1(username=speechToTextUser,
        #                                 password=speechToTextPassword)
        # retvalue = authorization.get_token(url=SpeechToTextV1.default_url)
        import requests

        url = "https://iam.bluemix.net/identity/token"

        payload = "apikey=" + STTAPIKey + \
            "&grant_type=urn%3Aibm%3Aparams%3Aoauth%3Agrant-type%3Aapikey"
        headers = {
            'Content-Type': "application/x-www-form-urlencoded",
            'Cache-Control': "no-cache",
            'Postman-Token': "679f6c97-b8ee-5ef6-153b-1af40ed0094e"
        }

        response = requests.request("POST", url, data=payload, headers=headers)

        print("STT token responce is")
        res = json.loads(response.text)
    except Exception as e:
        print(e)
    return res['access_token']


@app.route('/api/text-to-speech/token', methods=['POST', 'GET'])
def getTtsToken():
    print("getTtstoken ran")
    try:
        # print("inside try of geTtstoken with default url")
        # authorization = AuthorizationV1(
        #     "https://stream-fra.watsonplatform.net/text-to-speech/api")
        # username = textToSpeechUser,
        # password = textToSpeechPassword
        # print("authorisation in text to speech is")
        # print(authorization)
        # print("before retvalue")
        # retvalue = authorization.get_token(
        #     "https://gateway-fra.watsonplatform.net/text-to-speech/api")
        # print("text to speech token is :")
        import requests

        url = "https://iam.bluemix.net/identity/token"

        payload = "apikey=" + TTSAPIKey + \
            "&grant_type=urn%3Aibm%3Aparams%3Aoauth%3Agrant-type%3Aapikey"
        headers = {
            'Content-Type': "application/x-www-form-urlencoded",
            'Cache-Control': "no-cache",
            'Postman-Token': "679f6c97-b8ee-5ef6-153b-1af40ed0094e"
        }

        response = requests.request("POST", url, data=payload, headers=headers)

        print("TTS token responce is")
        res = json.loads(response.text)
    except Exception as e:
        print("122 error is: " + e)

    return res['access_token']


port = os.getenv('PORT', '5001')
if __name__ == "__main__":
    app.run(ssl_context='adhoc')
    socketio.run(app, host='0.0.0.0', port=int(port))


# from watson_developer_cloud import TextToSpeechV1
# from watson_developer_cloud import SpeechToTextV1
# from watson_developer_cloud import AssistantV1
# from watson_developer_cloud import AuthorizationV1
# from flask_socketio import SocketIO
# from flask import request
# from flask import jsonify
# from flask import Flask
# import json
# # from dotenv import load_dotenv
# import os
# # from dotenv import load_dotenv
# import dotenv

# path = dotenv.find_dotenv()
# print("The path is " + path)
# # from dotenv import Dotenv
# # Of course, replace by your correct path
# dotenv = dotenv.load_dotenv(path)
# # os.environ.update(dotenv)


# app = Flask(__name__)
# socketio = SocketIO(app)


# if 'VCAP_SERVICES' in os.environ:
#     vcap = json.loads(os.getenv('VCAP_SERVICES'))
#     print('Found VCAP_SERVICES')
#     if 'conversation' in vcap:
#         conversationCreds = vcap['conversation'][0]['credentials']
#         assistantUsername = conversationCreds['username']
#         assistantPassword = conversationCreds['password']

#     if 'text_to_speech' in vcap:
#         textToSpeechCreds = vcap['text_to_speech'][0]['credentials']
#         textToSpeechUser = textToSpeechCreds['username']
#         textToSpeechPassword = textToSpeechCreds['password']
#     if 'speech_to_text' in vcap:
#         speechToTextCreds = vcap['speech_to_text'][0]['credentials']
#         speechToTextUser = speechToTextCreds['username']
#         speechToTextPassword = speechToTextCreds['password']
#     if "WORKSPACE_ID" in os.environ:
#         workspace_id = os.getenv('WORKSPACE_ID')

#     if "ASSISTANT_IAM_APIKEY" in os.environ:
#         assistantIAMKey = os.getenv('ASSISTANT_IAM_APIKEY')

# else:
#     print('Found local VCAP_SERVICES')
#     # load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
#     assistantUsername = os.environ.get('ASSISTANT_USERNAME')
#     assistantPassword = os.environ.get('ASSISTANT_PASSWORD')
#     assistantIAMKey = os.environ.get('ASSISTANT_IAM_APIKEY')
#     assistantUrl = os.environ.get('ASSISTANT_URL')

#     textToSpeechUser = os.environ.get('TEXTTOSPEECH_USER')
#     textToSpeechPassword = os.environ.get('TEXTTOSPEECH_PASSWORD')

#     speechToTextUser = os.environ.get('SPEECHTOTEXT_USER')
#     speechToTextPassword = os.environ.get('SPEECHTOTEXT_PASSWORD')
#     workspace_id = os.environ.get('WORKSPACE_ID')


# @app.route('/')
# def Welcome():
#     return app.send_static_file('index.html')


# @app.route('/api/conversation', methods=['POST', 'GET'])
# def getConvResponse():
#     # Instantiate Watson Assistant client.
#     # only give a url if we have one (don't override the default)
#     try:
#         assistant_kwargs = {
#             'version': '2018-07-06',
#             'username': assistantUsername,
#             'password': assistantPassword,
#             'iam_api_key': assistantIAMKey
#         }

#         assistant = AssistantV1(**assistant_kwargs)

#         convText = request.form.get('convText')
#         convContext = request.form.get('context')

#         if convContext is None:
#             convContext = "{}"
#         print(convContext)
#         jsonContext = json.loads(convContext)

#         response = assistant.message(workspace_id=workspace_id,
#                                      input={'text': convText},
#                                      context=jsonContext)
#     except Exception as e:
#         print(e)

#     print(response)
#     reponseText = response["output"]["text"]
#     responseDetails = {'responseText': reponseText[0],
#                        'context': response["context"]}
#     return jsonify(results=responseDetails)


# @app.route('/api/speech-to-text/token', methods=['POST', 'GET'])
# def getSttToken():
#     try:
#         authorization = AuthorizationV1(username=speechToTextUser,
#                                         password=speechToTextPassword)
#         retvalue = authorization.get_token(url=SpeechToTextV1.default_url)
#     except Exception as e:
#         print(e)
#     return retvalue


# @app.route('/api/text-to-speech/token', methods=['POST', 'GET'])
# def getTtsToken():
#     try:
#         authorization = AuthorizationV1(username=textToSpeechUser,
#                                         password=textToSpeechPassword)
#         retvalue = authorization.get_token(url=TextToSpeechV1.default_url)
#     except Exception as e:
#         print(e)
#     return retvalue


# port = os.getenv('PORT', '5000')
# if __name__ == "__main__":
#     socketio.run(app, host='0.0.0.0', port=int(port))
