'使用Bing进行语音识别, 可以自动转换mp3'
import re
import os
import speech_recognition as sr
from pydub import AudioSegment

def spech_recognize(path):
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
        print(recognizer.recognize_bing(audio, key, language='zh-cn'))
    except LookupError:
        print("Could not understand audio")
    finally:
        if re.match(r'^.*\.mp3\.wav$', path):
            os.remove(path)

def main():
    '测试主函数'
    path = ''
    spech_recognize(path)

if __name__ == '__main__':
    main()
