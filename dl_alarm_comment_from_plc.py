#####################################################################
#   KV-5000 アラームデータ受信PG Ver.1.0
#   Last Update on 2023.9.22
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
#   LR10.00-LR29.15のアラーム用デバイス(320点分)のコメントをPLCから
#   ダウンロードする
#   ダウンロード先は共有ファイルサーバ内とする
#   既にダウンロードされている場合(ファイルがある場合)は上書きする
#####################################################################
import os
import sys
import socket
import csv
from ping3 import ping        # 要インストール
from tkinter import messagebox
import configparser
import time

os.chdir(os.path.dirname(__file__)) # ワーキングディレクトリ変更(VSCode時必要)
sys.path.append(os.pardir)          # 独自モジュールPATH追加        
import common.kv_com as kv

# 関数定義 --------------------------------------------------------------


# 定数定義 ------------------------------------------------------------------------
SVR_IP_ADD = '192.168.2.1'      # ファイルサーバIPアドレス
BASE_FOLDER = r'\\192.168.2.1\共有ファイル\M-光和共有ファイル\P_ProductControl\alarm_comment' + '\\'


# メインプロセス ---------------------------------------------------------------------
print('-----Starting initial process -----')
# ファイルサーバ疎通確認
res = ping(SVR_IP_ADD,timeout=0.5)
if res==None or res==False:
    messagebox.showwarning('ERROR', 'ファイルサーバ通信異常(ABEND)')
    exit()
# 保存フォルダ存在確認
if os.path.isdir(BASE_FOLDER)==False:
    messagebox.showwarning('ERROR', 'データ格納フォルダなし(ABEND)')
    exit()

# setting.ini読み込み
cfg = configparser.ConfigParser()
cfg.read('setting.ini')
mc_list = cfg.sections()    # 対象機械リスト取得
print(mc_list)    # ForDebug


# メインループ --------------------
print('-----Starting main-loop process -----')
for mc_name in mc_list:
    ip_add = cfg[mc_name]['IpAddress']

    # PLC疎通確認 
    if kv.connect_check(ip_add)==False:
        print(f'{mc_name}:Connectivity-check is false')
        continue

    # デバイスコメント読み出し(LR10.00-LR29.15の320点) 
    print(f'{mc_name}:Receiving Comments from PLC')
    alarm_info = kv.dl_alarm_comment(ip_add)

    # CSVファイル出力(Excelで確認するため、文字コードはshift-jisにした)
    file_name = mc_name + '_alarm_comment.csv'
    file_path = BASE_FOLDER + file_name
    with open(file_path,'w',newline='',encoding='shift-jis') as f:
        writer = csv.writer(f)
        writer.writerows(alarm_info)
    print(f'{mc_name}:Alarm-comment is downloaded normaly')


# 終了メッセージ
print('===== Process completed successfully =====')
time.sleep(5)   # 目視確認用タイマ

