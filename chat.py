import os
import wave
import datetime
import openai
import requests
import json
import whisper
from pydub import AudioSegment

# 日本時間を設定
t_delta = datetime.timedelta(hours=9)
JST = datetime.timezone(t_delta, 'JST')

# 環境変数からAPI_KEYを読込
openai.organization = os.getenv("ORG_ID")
openai.api_key = os.getenv("OPENAI_API_KEY")

# VOICEVOX用の設定
host = '172.18.0.3'  # VOICEVOXのプライベートIPアドレス
port = 50021  # VOICEVOXのポート
way_to_voice_num = 14  # VOICEVOXのイントネーション指定
voice_num = 14  # VOICEVOXの音声指定
punctuations = ["、", "。", "！", "？"]  # 処理効率化のための分割要素

# 中間ファイルを吐き出すファイルパス
env_pass = '/home/user/env/'


# 現在時間を取得
def now():
    return datetime.datetime.now(JST).strftime('%Y%m%d%H%M%S')


# ChatGPTとの過去のやり取りを形式化
def generate_past(past_content, req, res):
    if len(past_content) == 0:
        return 'You:' + req + '\nAI:' + res
    else:
        return past_content + '\nYou:' + req + '\nAI:' + res


# ChatGPTにリクエストを送信する。
def generate_chat(content, past_content):
    if len(past_content) == 0:  # 初会話
        msg = [
            {"role": "system",
             "content": "以下の条件を守って回答してください。AIアシスタントとして振る舞ってください。"},
            {"role": "user", "content": content}
        ]
    else:  # 2回目以降の会話
        msg = [
            {"role": "system",
             "content": "以下の条件を守って回答してください。AIアシスタントとして振る舞ってください。また、過去に以下のようなやり取りを行っています。" + past_content},
            {"role": "user", "content": content}
        ]
    res_chatgpt = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=msg,
        temperature=1
    )
    return res_chatgpt


# テキストをVOICEVOXのjson形式に変換する。
def generate_json(text, speaker=way_to_voice_num):
    params = (
        ('text', text),
        ('speaker', speaker),
    )
    res_json = requests.post(
        f'http://{host}:{port}/audio_query',
        params=params
    )
    raw_json = json.dumps(res_json.json())
    processed_json1 = raw_json.replace('"speedScale": 1.0', '"speedScale": 1.2')
    processed_json2 = processed_json1.replace('。', '！')
    return processed_json2


# 入力した音声を保存する。
def generate_request_wav(input_wav):
    filepath = env_pass + "input_" + now() + ".wav"
    wf = wave.open(filepath, 'wb')
    wf.setnchannels(2)  # モノラル
    wf.setsampwidth(2)  # 2バイト
    wf.setframerate(44100)  # 44.1kHz
    wf.writeframesraw(input_wav)
    wf.close()
    return filepath


# VOICEVOXのjson形式を音声に変換する。
def generate_response_wav(json_file, filepath, speaker=voice_num):
    headers = {'Content-Type': 'application/json', }
    params = (
        ('speaker', speaker),
    )
    res_wav = requests.post(
        f'http://{host}:{port}/synthesis',
        headers=headers,
        params=params,
        data=json_file
    )
    wf = wave.open(filepath, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(24000)
    wf.writeframes(res_wav.content)
    wf.close()
    return filepath


# WHISPERモデルをロードする。
def load_model():
    model = whisper.load_model("medium", device="cpu")
    _ = model.half()
    _ = model.cuda()

    # exception without following code
    # reason : model.py -> line 31 -> super().forward(x.float()).type(x.dtype)
    for m in model.modules():
        if isinstance(m, whisper.model.LayerNorm):
            m.float()
    return model


# WHISPERで音声ファイルをテキストに変換する。
def speech_to_text(filepath, model):
    result = model.transcribe(
        filepath, verbose=True, language='japanese', beam_size=5, fp16=True, without_timestamps=True)
    print(result["text"])  # debug
    return result["text"]


# 分割要素でテキストを分割する。性能のため。
def split_sentence(sentence):
    words = []
    start = 0
    for i in range(len(sentence)):
        if sentence[i] in punctuations:
            words.append(sentence[start:i + 1].strip())
            start = i + 1
    if start < len(sentence):
        words.append(sentence[start:].strip())
    return words


# 音声を平坦化させる。
def normalize(file_name, duration=10):
    sound = AudioSegment.from_wav(file_name)
    normalized_sound = sound.normalize()
    silence = AudioSegment.silent(duration=duration)
    sound = normalized_sound[1:] + silence
    return sound


# 音声を連結する。
def concatenate_wav(file_names, output_file_name):
    concatenated_sound = AudioSegment.silent(duration=0)
    normalized_wave_lst = list(map(normalize, file_names))
    for elem in normalized_wave_lst:
        concatenated_sound = concatenated_sound + elem
    concatenated_sound.export(output_file_name, format="wav")
    return output_file_name


# ファイル名のINDEXを作成する。
def generate_index(lst):
    nw = now()
    lst1 = list((range(len(lst))))
    lst2 = map(str, lst1)
    lst3 = list(map(lambda x: env_pass + "audio_" + nw + "_" + x + ".wav", lst2))
    return lst3


# 型変換
def to_str(lst):
    lst1 = list(map(str, lst))
    return lst1


# 入力テキストを、VOICEVOX音声およびテキストとして出力する。過去のやり取りも持っていく。
def generate_response(input_word, past_content):
    res = generate_chat(input_word, past_content)
    chat = res["choices"][0]["message"]["content"].replace('\n', '')
    past_content = generate_past(past_content, input_word, chat)
    split_chat = split_sentence(chat)
    split_json = list(map(generate_json, split_chat))
    index = generate_index(split_json)
    list(map(generate_response_wav, split_json, index))
    concatenated_wav = concatenate_wav(index, env_pass + "comb_" + now() + ".wav")
    list(map(os.remove, to_str(index)))
    return [concatenated_wav, chat, past_content]
