# ChatVox
You can talk with the VOICEVOX character.<br>
<br>
※工事中<br>
<br>
<br>
本ツールはStreamlitを介して、ChatGPTと音声で会話するWEBアプリです。<br>
<br>
環境<br>
Docker Engine<br>
 -CentOS7<br>
  -Python3.10.9<br>
 -VOICEVOX<br>
<br>
<br>
使い方<br>
・Linux環境の環境変数にChatGPTのAPI_KEYとORG_KEYを記載します。<br>
・環境に合わせてchat.py内のいくつかのパラメータを変更します。(IPアドレスやVOICEVOX音声指定など)<br>
・Python3.10.9のLinux環境の同じディレクトリに、web.pyとchat.pyを配置します。<br>
・右記を実行します。:streamlit run web.py<br>
<br>
<br>
処理内容<br>
ユーザーがWEB上でマイクを通して音声を入力する。<br>
↓Python (Streamlit)<br>
Linuxに音声ファイルを保存<br>
↓Python (Whisper)<br>
音声ファイルを入力テキストに変換する。<br>
↓Python (ChatGPT API)<br>
入力テキストをChatGPTに通して、結果テキストを取得する。<br>
↓Python<br>
並行処理を実現するために、テキストを句読点で分割する。<br>
↓Python (VOICEVOX API)<br>
テキストからVOICEVOX発音用のJSONファイルを作成する。<br>
↓Python (VOICEVOX API)<br>
JSONファイルから音声ファイルを作成する。<br>
↓Python<br>
分割された音声ファイルを統合する。<br>
↓Python (Streamlit)<br>
WEBアプリ上で音声ファイルを再生する。<br>


手順書
この通りにやったら絶対に成功します。<br>
ChatVox環境構築手順書.xlsx<br>
