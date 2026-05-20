""" GoogleSpreadSheet(検査NG数入力シート)からNGデータを取得し、
    特定の設備・日付の検査NG数を返す
"""

import os
import sys
from datetime import datetime, timedelta
import pprint as p

# 共通モジュールインポート
import common_lib_mw.gspread_com as gs


# --- Definition of Constant --------------------------------------------------
# GoogleSpreadSheetID(検査NG数入力シート)
SPREAD_SHEET_ID = '18qV3meZBB_-coQNM2aw43WEsgil6PwMi9ZrHx4GvJx8' # URLから取得する

# --- Definition of Function --------------------------------------------------

def get_ng_data(mc_name:str, year_month:str)->list:
    """ 対象の機械と年月を指定してGoogleSpreadSheetから
        NG数(検査時NG判定数)リストを取得する
        (DATAシートから抽出する)

    Args:
        mc_name (str): 機械名(例：MC067)
        yearmonth (str): 年月(例：2025/10)

    Returns:
        list: 引数の機械・年月のNG数リスト
    """
    # SpreadSheetオブジェクト取得
    spreadsheet = gs.connect_gspread(SPREAD_SHEET_ID, 'mtwa.kogyo')
    # シートオブジェクト取得
    sht = spreadsheet.worksheet('DATA')

    # シート内全データ取得
    # ---<データ定義 (全てstr型で取得)>-----
    # 検査日 - 検査機 - 加工機 - NG数 - 記入者
    data = sht.get_all_values()
    # 機械Noによる絞り込み
    data_mc = [x for x in data if x[2][:5]==mc_name]
    # 年月による絞り込み
    data_ym = [x for x in data_mc if x[0][0:7]==year_month]

    return data_ym


def get_oneday_ng_num(ng_table:list, date:str)->int:
    """ 特定の日付のNG数を集計する
        (get_ng_data関数によって範囲が絞られていることを
         前提とする)

    Args:
        ng_table (list): NG数テーブル
        date (str): 日付(例：2025/10/05)

    Returns:
        int: NG数合計
    """
    if len(ng_table)==0: return 0

    data_oneday = [ n for n in ng_table if n[0]==date]
    # p.pprint(data_oneday) # ForDebug

    # NG数集計
    if len(data_oneday)==0: return 0
    sum = 0
    for x in data_oneday:
        if x[3].isdigit():  # 数字の時だけ集計
            sum = sum + int(x[3])
        else:
            continue
    
    return sum


# テストコード(動作確認用) -------------------------------------------------------
if __name__=='__main__':

    mc_name = 'MC056'         # 集計対象の加工機
    year_month = '2025/10'  # 集計対象の年月

    data_ym = get_ng_data(mc_name, year_month)
    p.pprint(data_ym)

    date = '2025/10/07'
    ng_num = get_oneday_ng_num(data_ym, date)
    print(ng_num)
