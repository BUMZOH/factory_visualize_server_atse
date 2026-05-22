##################################################################################
#   工場稼働状況リアルタイム表示プログラム Ver.1.1
#
#   Last Update on 2025.10.8
##################################################################################
import os
import sys
import time
import datetime as dt
import configparser
from ping3 import ping
from tkinter import messagebox
import keyboard
import logging

# 独自モジュールPATH追加 
import common_lib_mw.kv_com as kv
import common_lib_mw.gspread_com as gs


# ロギング設定
logging.basicConfig(filename='log(disp_realtime_gsp).txt',encoding='UTF-8',
                    format='%(asctime)s - %(levelname)s - %(message)s')


# 関数定義 ------------------------------------------------------------------------
def prepare_op_table(mc_list, config)->list:
    '''
    ＜データ構造＞
    機械番号, 型式, ステータス, 生産数実績, 生産数目標, アラーム数
    '''
    op_table = []
    for mc_name in mc_list:
        x = [mc_name,'','',0,0,0]
        op_table.append(x)

    # 機械型式入力
    for x in op_table:
        x[1] = config[x[0]]['McType']

    return op_table


def get_op_data(op_data, config)->list:
    '''
    ＜op_data データ構造＞
    機械番号, 型式, ステータス, 生産数実績, 生産数目標, アラーム数
    '''
    data = op_data
    
    # Updateフラグ確認
    update_flg = config[data[0]]['Update']
    if update_flg=='False':
        print(f'{data[0]}:UpdateFlag is False')
        for i in range(2,6): data[i] = ''
        return data
    
    # PING疎通確認
    ip_add = config[data[0]]['IpAddress']
    if kv.connect_check(ip_add)==False:
        print(f'{data[0]}:Connectivity False')
        for i in range(2,6): data[i] = ''
        return data

    # 設備ステータス 取得
    res = kv.read_device_u(ip_add, DEVICE_MC_STATUS)
    data[2] = get_status_string(int(res))
    # 生産数実績
    res = kv.read_device_u(ip_add, DEVICE_PROD_RESULT)
    data[3] = int(res)
    # 生産数目標
    res = kv.read_device_u(ip_add, DEVICE_PROD_GOAL)
    data[4] = int(res)
    # アラーム数
    res = kv.read_device_u(ip_add, DEVICE_ALARM_NUM)
    data[5] = int(res)
    print((f'{data[0]}:Getting op-data was successful'))
    return data


def get_status_string(status_no)->str:
    if status_no==1:
        return '刃具交換'
    elif status_no==2:
        return '段替え'
    elif status_no==3:
        return '故障停止'
    elif status_no==4:
        return '材料切れ'
    elif status_no==15:
        return '自動中'
    elif status_no==16:
        return '停止中'
    elif status_no==20:
        return '異常中'
    elif status_no==0:
        return '---'
    else:
        return 'unknown'


def wait_and_keystop(time_sec,key)->None:
  for i in range(time_sec*10):
    if keyboard.is_pressed(key):  # 'q'キーが押されているかチェック
      print(f"{key}キーが押されました。プログラムを終了します。")
      exit()
    time.sleep(0.1)


def get_present_datetime()->str:
    dt_now = dt.datetime.now()
    now_str = dt_now.strftime('%Y/%m/%d %H:%M:%S')
    return now_str


# 定数定義 ------------------------------------------------------------------------
# GoogleSpreadSheett関連
SPREAD_SHEET_ID = '1_vy216XmrivXZLFosfxT3TLmpHHnyX2lgbhk3f7P-DY' # URLから取得する

DEVICE_MC_STATUS = 'EM10006'      # 設備ステータス用PLCデバイス
DEVICE_PROD_RESULT = 'EM10004'    # 生産数実績用PLCデバイス
DEVICE_PROD_GOAL = 'EM10007'      # 生産数実目標PLCデバイス
DEVICE_ALARM_NUM = 'EM10005'      # アラーム発生数用PLCデバイス


# グローバル変数定義 ---------------------------------------------------------------
mc_list = []        # 機械IDリスト(setting.iniのセクション名)
op_table = []       # 稼働データテーブル
spreadsheet = None  # SpreadSheet操作用


# メインプロセス -------------------------------------------------------------------
print('-----Starting initial process -----')
# setting.ini読み込み
cfg = configparser.ConfigParser()
cfg.read('setting.ini')

# 対象機械リスト取得
mc_list = cfg.sections()
# print(mc_list)    # ForDebug

# データテーブルの準備
op_table = prepare_op_table(mc_list, cfg)
print(op_table)

# SpreadSheet準備(接続等)
spreadsheet = gs.connect_gspread(SPREAD_SHEET_ID, 'bumzoh')
if spreadsheet==None: exit()

# メインループ --------------------
print('-----Starting main-loop process -----')
while True:
    try:
        # 稼働データ取得
        for data in op_table:
            data = get_op_data(data, cfg)
        print(op_table)
    except Exception as e:
        logging.error(e)
        time.sleep(1)
        continue


    # APIリクエスト数対策として1つの表にまとめる
    # (APIリクエスト制限 分間60リクエスト以下、但しReadとWrite別カウント)
    data_paste = [] # 貼り付け用データ
    data_paste.append([None,None,None,get_present_datetime()])  # 2行目(現在時刻)
    data_paste.append([])   # 3行目
    data_paste.append([])   # 4行目
    for x in op_table:  # 5行目以降(データ領域)
        data_paste.append(x)

    try:
        sht = spreadsheet.worksheet('RtTable')
        sht.update(data_paste, 'B2')                      # データ貼り付け
    except Exception as e:
        # SpreadSheet APIエラー発生時(30秒待ってから再開)
        logging.error(e)
        time.sleep(30)
        continue
    
    print('(途中で停止したい場合はqキーを押してください)')
    wait_and_keystop(3, 'q')    # 3secの場合 APIリクエスト=20/min(write)



######################################################################################################
#   MEMO
#-----------------------------------------------------------------------------------------------------
#
#


