##################################################################################
#   工場見える化SpreadSheet監視プログラム Ver.1.1
#
#   Last Update on 2026.5.6
##################################################################################
import os
import sys
import keyboard
import time
import pprint as pp
from pathlib import Path
from datetime import datetime

os.chdir(os.path.dirname(__file__)) # ワーキングディレクトリ変更(VSCode時必要)
import disp_detail_opdata
import disp_tpm_monthly
import disp_monthly_opdata

# 独自モジュールPATH追加 
# sys.path.append(os.pardir)
# import common.gspread_com as gs
# import common.launch as launch
import common_lib_mw.gspread_com as gs
import common_lib_mw.launch as launch


# 定数定義 ------------------------------------------------------------------------
# GoogleSpreadSheett関連
SPREAD_SHEET_ID = '1_vy216XmrivXZLFosfxT3TLmpHHnyX2lgbhk3f7P-DY' # 工場稼働モニタ
DL_EXCUTE_COUNT = 1000   # 稼働データをファイルサーバからDLするカウント数(約1h見込み)

BASE_DIR = Path(__file__).resolve().parent
PARENT_DIR = BASE_DIR.parent

# KVおよびVT稼働データSQLite登録プログラムのパス
VTDL_APP_PATH = PARENT_DIR / "光和_VTアラーム履歴SQLインポートat新江" / "main.py"
KVDL_APP_PATH = PARENT_DIR / "光和_KV稼働データSQLインポートat新江" / "main.py"


# 関数定義 ------------------------------------------------------------------------
def call_module(sheet_name:str)->None:
    """_summary_

    Args:
        sheet_name (str): _description_
    """
    if sheet_name=='Monthly':
        # Montyleシート更新スクリプトの実行
        disp_monthly_opdata.main_proc()
    elif sheet_name=='TPM':
        # TPMシート更新スクリプトの実行
        disp_tpm_monthly.main_proc()
    elif sheet_name=='Detail':
        # Detailシート更新スクリプトの実行
        disp_detail_opdata.main_proc()


def wait_and_keystop(time_sec,key)->None:
  for i in range(time_sec*10):
    if keyboard.is_pressed(key):  # 'q'キーが押されているかチェック
      print(f"{key}キーが押されました。プログラムを終了します。")
      exit()
    time.sleep(0.1)

def log(msg: str):
    """ログ出力用関数 (from datetime import datetimeすること)"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  
    with open("log(user_request).txt", "a", encoding="utf-8") as f:  
	    f.write(f"{now} {msg}\n")


# メインプロセス -------------------------------------------------------------------
loop_cnt = DL_EXCUTE_COUNT  # プログラム起動時にKV/VTのデータDL処理をするため

while True:
    # try範囲が広すぎる(今後改善する)
    try:
        # PLC/KVから稼働データダウンロード
        if loop_cnt>=DL_EXCUTE_COUNT:
            # dl_opdata_from_plc.main_proc()    # 2026.5.6 廃止
            launch.run_outer_app(KVDL_APP_PATH)
            launch.run_outer_app(VTDL_APP_PATH)
            loop_cnt = 0
        else:
            loop_cnt = loop_cnt + 1 # カウンタインクリメント


        # SpreadSheetから取得
        spreadsheet = gs.connect_gspread(SPREAD_SHEET_ID, 'mtwa.kogyo')
        if spreadsheet==None: exit()

        sht = spreadsheet.worksheet('Control')
        cells = sht.range('A1:E4')

        # 制御データ(Control Data)としてリスト格納
        sheet_name = []
        request = []

        for i in range(1,4):
            sheet_name.append(cells[i*5].value)
            request.append(cells[i*5+1].value)

        if True:    # forDebug
            print(sheet_name)
            print(request)

        for req,sht in zip(request, sheet_name):
            if req=='ON':
                print(f'{sht}:process excute')
                call_module(sht)

        print(f'---終了する場合は「q」を押してください(loop_cont={loop_cnt})---')
        wait_and_keystop(2, 'q')

    except Exception as e:
        # 例外発生時(30秒待ってから再開)
        log(e)
        time.sleep(30)
        continue


    """
    ----- 更新履歴 -----

    2026.5.6
    KVとVTからSQLiteファイル登録プロセスを追加
    モジュールとしてではなく外部プログラムとして実行(Subprocess利用)
    KVDL_APP_PATHとVTDL_APP_PATHの設定にあるとおり、一つ上のフォルダに
    あることが前提

    
    """