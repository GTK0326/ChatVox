# ChatVox
You can talk with the VOICEVOX character.

※工事中


本ツールはStreamlitを介して、ChatGPTと音声で会話するWEBアプリです。

環境
Docker Engine
 -CentOS7
  -Python3.10.9
 -VOICEVOX


使い方
・Linux環境の環境変数にChatGPTのAPI_KEYとORG_KEYを記載します。
・環境に合わせてchat.py内のいくつかのパラメータを変更します。(IPアドレスやVOICEVOX音声指定など)
・Python3.10.9のLinux環境の同じディレクトリに、web.pyとchat.pyを配置します。
・右記を実行します。:streamlit run web.py


処理内容
ユーザーがWEB上でマイクを通して音声を入力する。
↓Python (Streamlit)
Linuxに音声ファイルを保存
↓Python (Whisper)
音声ファイルを入力テキストに変換する。
↓Python (ChatGPT API)
入力テキストをChatGPTに通して、結果テキストを取得する。
↓Python
並行処理を実現するために、テキストを句読点で分割する。
↓Python (VOICEVOX API)
テキストからVOICEVOX発音用のJSONファイルを作成する。
↓Python (VOICEVOX API)
JSONファイルから音声ファイルを作成する。
↓Python
分割された音声ファイルを統合する。
↓Python (Streamlit)
WEBアプリ上で音声ファイルを再生する。
