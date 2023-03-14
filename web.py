import base64
import time
import os
import streamlit as st
import chat
from audio_recorder_streamlit import audio_recorder

# WEB上で音声ファイルを自動再生する。
def play_audio(path):
    audio_placeholder = st.empty()

    file_ = open(path, "rb")
    contents = file_.read()
    file_.close()

    audio_str = "data:audio/ogg;base64,%s" % (base64.b64encode(contents).decode())
    audio_html = """
                    <audio autoplay=True>
                    <source src="%s" type="audio/ogg" autoplay=True>
                    Your browser does not support the audio element.
                    </audio>
                """ % audio_str

    audio_placeholder.empty()
    time.sleep(0.1)
    audio_placeholder.markdown(audio_html, unsafe_allow_html=True)


# 事前設定
input_wav = False
if 'past_content' not in st.session_state:
    st.session_state.past_content = ''
if 'content' not in st.session_state:
    st.session_state.content = ''
model = chat.load_model()

# UI
st.title('ChatVox')
st.header('You can talk with VOICEVOX character.')

# UI writing
with st.form("input", clear_on_submit=False):
    sentence = st.text_area("自由に話しかけてください。")
    submitted = st.form_submit_button("送信")

# UI speaking
input_wav = audio_recorder()
if input_wav:
    generated_request_wav = chat.generate_request_wav(input_wav)
    sentence = chat.speech_to_text(generated_request_wav, model)
    submitted = sentence
    st.markdown(submitted)
    os.remove(generated_request_wav)


# submit
if submitted:
    result = chat.generate_response(sentence, st.session_state.past_content)
    play_audio(result[0])
    st.markdown(result[1])
    st.session_state.past_content = result[2]
    os.remove(result[0])
