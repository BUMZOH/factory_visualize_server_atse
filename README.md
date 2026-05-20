## 実行方法
フォルダ内の"run.bat"をダブルクリックする。
以下の2つのプログラムが並行して実行される。
- disp_realtime_gsp.py
- user_request_monitoring.py


## 準備
共通モジュール"common_lib_mw"を以下のコマンドでインストールする  
```
git clone https://github.com/BUMZOH/common_lib_mw.git
```
"common_lib_mw"フォルダの中に".git"フォルダが作成されるが、不要なので削除すること。

上記フォルダ"common_lib_mw"の中に以下のSpreadSheet、GoogleDriveの認証用jsonファイル、
yamlファイルを格納すること。
認証用のファイルは別途保管してある。
- bumzoh.json
- client_secrets.json
- mtwa.kogyo.json
- saved_credentials.json
- settings.yaml


## 【更新履歴】
2025.10.12
    disp_monthly_opdata.pyでSpreadSheet貼り付け用変数data_pasteが
    グローバル変数であり、毎回空リストを入れていなかったため、データが
    積み重なるという不具合あり。
    グローバル変数からローカル変数に変更し、さらに使用前初期化した。

2025.10.11
    disp_realtime_gsp.pyのSpreadSheetへの書き込み処理に対して例外処理を
    追加。ログ出力、20秒待機後に再開するプログラムへ変更した。
    (Internal roor encounteredが1日数回レベルで発生するため)

2025.10.8
    SpreadSheetは空文字''を入力すると表示形式(%やカンマ区切りなど)が
    リセットされる。
    対策として入力範囲すべてをClearメソッドで消去し、入力しないセルには
    空文字ではなく、Noneを入れる。
    Noneは元々値がある場合は、それを残す（つまり何もしない）
    デメリットはAPI使用回数が増える

2025.10.6
    pingによる疎通確認時、戻り値resが0.0(float)になることがあり、
    res==Flaseが成立する場合があった。
    そのため、pingが通っているにもかかわらず、不通として処理される
    不具合が発生した。
    kv_com.pyのconnect_check関数を修正した

2025.10.5
    GoogleSpreadSheetのエラー発生(今後対応)
    gspread.exceptions.APIError: APIError: 
    [500]: Internal error encountered.

2025.10.5
    工場監視用PC(HP製ノートPC)通信不安定
    PLCとの通信が不安定になっていたため、LANからWi-Fiに変更した。
    しばらく調子が良かったが、同様の現象が発生した。
    (TeamViewer接続中は改善されるという謎現象も見られた)
    文博用デスクトップPCでは見られないのでPC個別の不具合と判断。
    → 杉産業佐多さんに相談、またはPC入れ替え
    → 上記2025.10.6で不具合解消した

2025.10.5 
    GoogleSpreadSheetのエラー発生(今後対応)
    gspread.exceptions.APIError: APIError: 
    [503]: The service is currently unavailable.

2025.10.4
    自作モジュールkv_com.py不具合解消
    モジュール先頭でワーキングディレクトリ変更の命令を入れてしまい。
    呼び出し元のワーキングディレクトリを変えてしまっていた。

2025.10.4
    pingによる疎通確認で不具合
    ping失敗時の戻り値をNoneだけを想定していた
    実際はFalseの場合もあり、その時にPLCにSocket通信してしまっていた

2025.9.25
    dl_alarm_comment_from_plc.pyの修正
    IPアドレスが192.21.0.10で固定されていた不具合解消

2025.9.20
    SpreadSheet APIリクエスト数制限
    GoogleSpreadSheetはAPIリクエストが多すぎるとエラーが発生する。
    そのため、List形式データを一気に張り付ける必要がある(バッチ処理)。
    値の更新や取得以外はバッチ処理ができないため、Pythonから実行するべきではない。
    セルの塗りつぶしやフォント色変更は「条件付き書式」を利用した方がよい。




## 残作業・アップデート予定
・disp_detail_opdata.pyの改良
　→ データエリアと表示エリアを分ける
　→ 時系列グラフを作成し、GoogleDriveにアップロードする

・user_request_monitoring.pyから呼び出されるモジュールの
　エラー検知部にreturnではなく、exitになっている可能性が
　ある。チェックして修正すること。

・稼働率データダウンロード処理(dl_opdata_from_plc.py)の
　実行タイミングを決める
　user_request_monitoring.py実行時(初回)とwhileループ
　カウンタで一定のカウント数にする。
　例えば、１回のループが約3秒なので1000回＝3000秒＝50分
　で実行するとか。

・PLC時計合わせ処理
　非定期処理でよい（管理者が必要に応じて実施）

・アラームコメントダウンロード処理
　非定期処理でよい（管理者が必要に応じて実施）

・各プロセス開始用GUIインターフェース
　 BUTTON1 : リアルタイム表示
　 BUTTON2 : 集計シート要求監視
　 BUTTON3 : アラームコメントDL
　 BUTTON4 : PLC時計合わせ

・月別集計処理、開始日を1日以外にした時の処理












