import urllib
import requests
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException 
from tencentcloud.aai.v20180522 import aai_client, models
from helper.setting import VOICE_HOST

SECRET_ID = 'AKIDByZwBHyk7E6h3Uo7JI3atxnOjpeHZnkR'
SECRET_KEY = 'av0pOm27pMh05vXx99uQjncDZgX8SWJq'
PROJECT_ID = '0'
ENDPOINT = 'aai.tencentcloudapi.com'
REGION = 'ap-guangzhou'

def voice_recognize_remote(voice_url, eng_type='tencent_ai'):
    para = {
        'url': voice_url,
        'eng_type': eng_type
    }
    response = requests.post(VOICE_HOST, para)
    result = response.json()
    return result['msg'], result['result']

def voice_recognize(voice_url):
    comment = 'voice'
    params_dict = {
        'ProjectId': PROJECT_ID,
        'SubServiceType': '2',
        'EngSerViceType': '8k',
        'SourceType': '0',
        'Url': urllib.parse.quote(voice_url, safe=''),
        'VoiceFormat': 'mp3',
        'UsrAudioKey': comment
    }

    try:
        cred = credential.Credential(SECRET_ID, SECRET_KEY)
        http_profile = HttpProfile()
        http_profile.endpoint = ENDPOINT

        client_profile = ClientProfile()
        client_profile.httpProfile = http_profile
        client = aai_client.AaiClient(cred, REGION, client_profile)

        req = models.SentenceRecognitionRequest()
        params = str(params_dict).replace("'", '"')
        req.from_json_string(params)

        resp = client.SentenceRecognition(req)
        assert resp.Result != '', '音频不存在或无内容, 识别失败'
        return resp.Result, True
    except TencentCloudSDKException as error:
        return str(error), False

def auto_chat(text, user):
    params_dict = {
        'ProjectId': PROJECT_ID,
        'Text': text,
        'User': '{"id": "%s"}' % user
    }
    try:
        cred = credential.Credential(SECRET_ID, SECRET_KEY)
        http_profile = HttpProfile()
        http_profile.endpoint = ENDPOINT

        client_profile = ClientProfile()
        client_profile.httpProfile = http_profile
        client = aai_client.AaiClient(cred, REGION, client_profile)

        req = models.ChatRequest()
        params = str(params_dict).replace('"', r'\"').replace("'", '"')
        req.from_json_string(params)

        resp = client.Chat(req)
        return resp.Answer if resp.Answer != '' else '我不知道该怎么接', True

    except TencentCloudSDKException as error:
        return str(error), False
