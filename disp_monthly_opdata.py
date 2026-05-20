##################################################################################
#   月間稼働データ 表示プログラム Ver.1.0
#
#   Last Update on 2025.10.8
##################################################################################
import os
import sys
import configparser
import datetime as dt
from ping3 import ping
import time
import pprint
import calendar

# 独自モジュールのインポート
import common_lib_mw.gspread_com as gs


# 関数定義 ------------------------------------------------------------------------
def preparation_mcop_data(mc_name, cfg)->list:
    '''
    3行x34列のマトリックスを準備
    機械名、型式、項目名は入力する
    '''
    data = []
    for i in range(3):
        d = [None for n in range(34) ]
        data.append(d)

    data[0][0] = mc_name
    data[1][0] = cfg[mc_name]['McType']

    data[0][1] = '生産数'
    data[1][1] = '稼働率'
    data[2][1] = 'ｱﾗｰﾑ数'

    data[1][2] = 0.85
    data[2][2] = 10

    return data
    

def get_op_data(mc_name, op_date)->list:
    '''
    mc_name : 機械名 例:MC067
    op_date : 稼働日 例:2025/09/25
    '''
    op_date = op_date.replace('/', '')  # /除去
    fname = 'op_data' + op_date[2:] + '.CSV'
    fpath = BASE_FOLDER_OP + mc_name + '/' + fname
    # print(fpath)  # ForDebug
    if os.path.isfile(fpath)==False:
        print(f'{mc_name}/{op_date}:Operation-data file is not found')
        return []
    
    # CSVファイル読み込み(1列データ)
    with open(fpath, 'r') as f:
        data = f.readlines()
    data = [x.rstrip('\n') for x in data]   # CR除去
    data = [int(x) for x in data]           # str→int変換

    # データサイズチェック
    if len(data)!=3330:
        print(f'{mc_name}/{op_date}:Operation-data-size is abnormal(!=3330)')
        return []

    return data

def get_prod_num(op_data)->int:
    '''
    生産数実績 index=4
    '''
    if len(op_data)==0:return None
    return op_data[4]

def get_prod_goal(op_data)->int:
    '''
    生産数目標 index=7
    '''
    if len(op_data)==0:return None
    return op_data[7]

def get_alarm_num(op_data)->int:
    '''
    アラーム発生数 index=5
    '''
    if len(op_data)==0:return None
    return op_data[5]

def get_op_rate(op_data)->int:
    '''
    定時間稼働率の算出(定時間=9h=540min)
    自動中ステータス=15
    '''
    if len(op_data)==0:return None
    auto_time = op_data[250:(250+540)].count(15)
    op_rate = (auto_time / 540)
    return op_rate

def connectivity_check(ipadd)->bool:
    '''
    与えられたIPアドレス(ipadd)に対しPINGテストを実施する。
    PING成功時True、失敗時にFalseを返す。
    社内ネットワークなのでタイムアウト時間は短くする(0.2sec)
    '''    
    # pingで疎通確認
    result = ping(ipadd,timeout=0.2)
    if result==None or result==False:
        print(f'PING({ipadd}):Connectivity False')
        return False
    else:
        print(f'PING({ipadd}):ReplyTime={result}')
        return True


# 定数 ----------------------------------------------
FILE_SERVER_IP_ADD = '192.168.2.1'
BASE_FOLDER_OP = r'\\192.168.2.1\共有ファイル\M-光和共有ファイル\P_ProductControl\operation_data' + '\\'
# GoogleSpreadSheett関連
SPREAD_SHEET_ID = '1_vy216XmrivXZLFosfxT3TLmpHHnyX2lgbhk3f7P-DY' # URLから取得する(光和工場モニタ)


# グローバル変数 -------------------------------------
cfg = None  # setting.ini操作用オブジェクト


# メインプロセス -------------------------------------------------------------------
def main_proc(): 
    # 接続対象設備名の取得(INIファイルより)
    cfg = configparser.ConfigParser()
    cfg.read('setting.ini')
    mc_list = cfg.sections()
    print('M/C list in setting.ini is ',mc_list)    # ForDebug
    # time.sleep(1)   # 目視確認用

    # サーバ(共有ファイル)疎通チェック
    if connectivity_check(FILE_SERVER_IP_ADD)==False:
        print('ファイルサーバが応答しません(終了します)')
        exit()

    # SpreadSheet準備(接続等)
    spreadsheet = gs.connect_gspread(SPREAD_SHEET_ID, 'mtwa.kogyo')
    sht = spreadsheet.worksheet('Monthly')
    str_date = sht.acell('I1').value    # SpreadSheet入力値取得(開始日)

    # リクエストフラグOFF
    sht.update_acell('M1', 'OFF')   # API-Request(write)
    # Spreadシートクリア
    spreadsheet.values_clear("'Monthly'!B4:AI78")  # API-Request(write)

    # -----------------------------
    start_date = dt.datetime.strptime(str_date, '%Y/%m/%d')
    start_date = start_date.replace(day=1)    # 月初格納(念のため)
    # 月日数取得
    # https://note.nkmk.me/python-datetime-first-last-date-last-week/#_3
    days = calendar.monthrange(start_date.year,start_date.month)[1] # 月の日数

    data_paste = []   # SpreadSheet貼り付け用
    # 機械ブロックデータ(3行x34列データ)作成-----------------------------
    for mc_name in mc_list:
        # 機械ブロックデータ(SpreadSheet表示用データ)準備
        mcop_data = preparation_mcop_data(mc_name, cfg)
        # print(mcop_data)  # ForDebug

        # 稼働データ取得
        for i in range(days):
            op_date = dt.datetime.strftime(start_date+dt.timedelta(days=i),'%Y/%m/%d')
            op_data = get_op_data(mc_name, op_date)
            mcop_data[0][i+3] = get_prod_num(op_data)
            mcop_data[1][i+3] = get_op_rate(op_data)
            mcop_data[2][i+3] = get_alarm_num(op_data)
            # 生産数目標はデータがある場合のみ入力
            if get_prod_goal(op_data)!=None:
                mcop_data[0][2] = get_prod_goal(op_data)
        # print(mcop_data)  # ForDebug

        for i in range(3):
            data_paste.append(mcop_data[i])

    print(data_paste)

    # SpreadSheetへデータ貼り付け
    sht.update(data_paste, 'B4')

# 単体動作用
if __name__=='__main__':
    main_proc()


















