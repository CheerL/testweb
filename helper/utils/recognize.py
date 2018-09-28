'使用Bing进行语音识别, 可以自动转换mp3'
import re
import os
import sys
import speech_recognition as sr
from pydub import AudioSegment

def spech_recognize(path, mode=0):
    '使用Bing进行语音识别, 可以自动转换mp3'
    if not path:
        return
    if not os.path.isfile(path):
        return
    key = '9bbefdf7174c40b9a6657e762f43801a'

    #如果是mp3, 转换为wav
    if re.match(r'^.*\.mp3$', path):
        AudioSegment.from_mp3(path).export(path + '.wav', format="wav")
        path = path + '.wav'

    recognizer = sr.Recognizer()
    with sr.WavFile(path) as source:
        audio = recognizer.record(source)

    try:
        if mode is 0:
            return recognizer.recognize_bing(audio, key, language='zh-cn')
        elif mode is 1:
            return recognizer.recognize_google(audio, language='zh-cn')
        else:
            return
    except (LookupError, sr.UnknownValueError):
        return False
    finally:
        if re.match(r'^.*\.mp3\.wav$', path):
            os.remove(path)

def main():
    '测试主函数'
    path = ''
    if len(sys.argv) > 1:
        path = sys.argv[1]
    if len(sys.argv) > 2:
        text = spech_recognize(path, sys.argv[2])
    else:
        text = spech_recognize(path)
    print(text)

if __name__ == '__main__':
    main()
