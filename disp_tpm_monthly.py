##################################################################################
#   機械別TPMデータ表示プログラム Ver.1.0
#
#   Last Update on 2025.10.5
##################################################################################
import os
import sys
import pprint as pp
from datetime import datetime, timedelta

# 同一フォルダ内モジュール
import get_ng_info as ng    

# 共通モジュールインポート
import common_lib_mw.opdata_generator as opg
import common_lib_mw.gspread_com as gs



# Constant ---------------------------------------------------------------------------
ITEM_NUM = 21   # TMPデータ数(日ごとに生成されるデータ数)
# GoogleSpreadSheett関連
SPREAD_SHEET_ID = '1_vy216XmrivXZLFosfxT3TLmpHHnyX2lgbhk3f7P-DY' # URLから取得する(光和工場モニタ)

# Functions ---------------------------------------------------------------------------
def update_ng_info(op_data:list, ng_info:list, date:str)->list:
    """ TPM稼働データ(21項目)中の不良数を格納する処理。
        不良数格納に際し、良品率と設備総合効率も修正する。
        
    
    Args:
        op_data (list): TPM稼働データ(dateで指定されたもの)
        ng_info (list): NG数データ(SpreadSheetから取得)
        date (str): 対象年月日

    Returns:
        list: 更新されたTPM稼働データ
    """
   
    tmp = op_data # 稼働データ受け取り

    ng_num = ng.get_oneday_ng_num(ng_info, date)
    # 不良数更新
    tmp[15][1]= ng_num

    # 良品率更新
    prod_num = tmp[13][1]    # 生産数実績
    if prod_num!=0:
        ok_rate =  (1 - ng_num/prod_num)
        tmp[16][1] = ok_rate
    else:
        ok_rate = 0         # 生産数0の時は強制的に0
        tmp[16][1] = ok_rate

    # OEE(設備総合効率)更新 (時間稼働率×性能稼働率×良品率)
    oee = tmp[9][1] * tmp[14][1] * ok_rate
    tmp[17][1] = oee
    #print(ng_num, ok_rate, oee)    # ForDebug
    return tmp


# Global Variables --------------------------------------------------------------------


# --- MainProcess ---------------------------------------------------------------------
def main_proc()->None:
    
    # SpreadSheet準備(接続等)
    spreadsheet = gs.connect_gspread(SPREAD_SHEET_ID, 'mtwa.kogyo')
    sht = spreadsheet.worksheet('TPM')
    # 稼働日、機械No、更新フラグの取得
    val = sht.row_values(2) # 2行目全体を取得(list)  # API-Request(Read)
    mc_name = val[5]        # str型
    start_date = val[8]     # str型


    # リクエストフラグOFF
    sht.update_acell('M2', 'OFF')   # API-Request(write)
    # Spreadシートクリア
    spreadsheet.values_clear("'TPM'!B5:AG25")  # API-Request(write)

    #　31日分の日付用意→1日であることを確認した方がよい
    dates = []
    st_date = datetime.strptime(start_date,'%Y/%m/%d')
    for i in range(31):
        date = st_date + timedelta(days=i)
        str_date = datetime.strftime(date, '%Y/%m/%d')
        dates.append(str_date)

    # 対象設備・年月の不良数データ取得
    ng_info = ng.get_ng_data(mc_name, start_date[:7])   # 年月は「2025/10」形式

    # TPMデータを対象日時分だけresult(list)に格納する
    # (各日付に対し、タイトル列とデータ列 21行x2列)
    results = []
    for d in dates:
        data = opg.get_op_data(mc_name, d)  # サーバから稼働データDL
        if len(data)!=0:
            tmp = opg.get_opdata_list(data)
            # 不良数・不良データ格納(初期値からの更新)
            tmp = update_ng_info(tmp,ng_info,d)
            results.append(tmp)
        else:
            tmp = [[None,None] for n in range(ITEM_NUM) ] # 21x2の空リスト
            results.append(tmp)


    # タイトル列の取得(有効データがあれば1列目を格納する)
    title_col = ['' for x in range(ITEM_NUM)]   # 空リスト
    for x in results:
        if x[0][0]!=None: # 有効データ条件
            title_col = [x[i][0] for i in range(ITEM_NUM)]
            break
    # print(title_col)


    # 貼り付け用テーブル(全データ)の作成
    # (なかなか分かりにくい。結果オーライで・・・)
    data_paste = [[x] for x in title_col]   # appendで追加できるようlistとして生成
    for i in range(ITEM_NUM):
        for j in range(len(dates)):
            data_paste[i].append(results[j][i][1])

    print(data_paste)

    # データ領域クリア

    # データ貼り付け
    sht.update(data_paste, 'B5')


# 単体動作用
if __name__=='__main__':
    main_proc()
