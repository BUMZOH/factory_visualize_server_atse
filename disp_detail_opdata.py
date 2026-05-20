##################################################################################
#   詳細稼働データ 表示プログラム Ver.1.0
#
#   Last Update on 2025.9.21
##################################################################################
import os
import sys
import pprint
import keyboard
import time
import csv

# 共通モジュールインポート
import common_lib_mw.gspread_com as gs
import common_lib_mw.opdata_generator as opg
import common_lib_mw.gdrive_com as gd
import common_lib_mw.create_ope_graph as cog



# 関数定義 ------------------------------------------------------------------------

def wait_and_keystop(time_sec,key)->None:
  for i in range(time_sec*10):
    if keyboard.is_pressed(key):  # 'q'キーが押されているかチェック
      print(f"{key}キーが押されました。プログラムを終了します。")
      exit()
    time.sleep(0.1)


# 定数 ----------------------------------------------
BASE_FOLDER_OP = r'\\192.168.2.1\共有ファイル\M-光和共有ファイル\P_ProductControl\operation_data' + '\\'
BASE_FOLDER_AL = r'\\192.168.2.1\共有ファイル\M-光和共有ファイル\P_ProductControl\alarm_comment' + '\\'
# GoogleSpreadSheett関連
JSON_KEY = 'basic-breaker-471718-j3-01bc813e6f72.json'  # 環境に合わせて変更する
SPREAD_SHEET_ID = '1_vy216XmrivXZLFosfxT3TLmpHHnyX2lgbhk3f7P-DY' # URLから取得する

# グローバル変数 -------------------------------------



# メインプロセス -------------------------------------------------------------------
def main_proc()->None:
    # ワーキングディレクトリ変更(VSCode使用時必要)
    # os.chdir(os.path.dirname(__file__))
    # sys.path.append(os.pardir)          # 独自モジュールPATH追加        
    # import common.gspread_com as gs
    # import common.opdata_generator as opg
    # import common.gdrive_com as gd

    # SpreadSheet準備(接続等)
    spreadsheet = gs.connect_gspread(SPREAD_SHEET_ID,'mtwa.kogyo')
    sht = spreadsheet.worksheet('Detail')


    # 稼働日、機械No、更新フラグの取得
    val = sht.row_values(2) # 2行目全体を取得(list)  # API-Request(Read)
    op_date = val[5]        # 稼働日(str型)
    mc_name = val[7]          # 機械No(str型)

    # SpreadSheet内 リクエストフラグOFF
    sht.update_acell('K2', 'OFF')   # API-Request(write)
    # Spreadシート データ領域クリア
    spreadsheet.values_clear("'Detail'!B42:F62")  # API-Request(write)

    
    #--- 稼働データ表示処理 -----------------------------------
    # 稼働データ取得(共有ファイルサーバから)
    all_opedata = opg.get_op_data(mc_name, op_date)
    if len(all_opedata)==0: return  # データなしの場合
    opedata_list = opg.get_opdata_list(all_opedata)
    # print(opedata_list)   # ForDebug
    
    sht.update(opedata_list, 'B42')    # API-Request(write)


    #--- アラームデータ表示処理 -------------------------------
    # アラーム発生回数データ格納
    alarm_num_data = all_opedata[3010:(3010+320)]
    # print(alarm_num_data)   # ForDebug

    # アラームコメント読み込み
    alm_fpath = BASE_FOLDER_AL + mc_name + '_alarm_comment.csv'
    alm_comment = []
    if os.path.isfile(alm_fpath)==True:
        with open(alm_fpath) as f:
            reader = csv.reader(f)
            alm_comment = [row for row in reader]
    else:
        # アラームコメントファイルがない場合(デバイス名をコメントとする)
        print(f'{mc_name}:Alarm-comment file is not found')
        for i in range(10,30):
            for j in range(16):
                device = 'LR' + str(i) + str(j).zfill(2)
                alm_comment.append([device,device])
    # print(alm_comment)    # ForDebug

    # データサイズチェック
    if len(alm_comment)!=len(alarm_num_data):
        print('ERROR:Alarm-data-size is abnormal')
        return

    # アラーム別発生回数データ生成
    alarm_info = []
    for i,x in enumerate(alm_comment):
        alarm_info.append([x[1], alarm_num_data[i]])

    # 発生回数0データの除去
    alarm_info = [x for x in alarm_info if x[1]!=0]
    # print(alarm_info)

    # 並び替え
    alarm_info.sort(key=lambda x: x[1], reverse=True)
    print(alarm_info)

    # SpreadSheet貼り付け
    sht.update(alarm_info, 'E42') # API-Request(write)


    #--- 稼働グラフ作成&GoogleDriveアップロード処理 -------------------------------
    status_data = opg.get_all_status_data(all_opedata)
    title = 'OperationGraph of' + mc_name + ' on ' + op_date
    graph = cog.get_ope_graph(status_data, title)
    cog.save_img('img_opdata.png', graph)

    # GoogleDrive Upload
    FOLDER_ID = '1Bu-KASatQAinYbR7hW0zUXEWz2YsWrO0'
    f_path = 'C:/my_data/img_opdata.png'
    gd.upload_to_gdrive(f_path, FOLDER_ID)
    print('Upload to Google-Drive complete!')




# 単体動作用
if __name__=='__main__':
    main_proc()


