##################################################################################
#   設備アラームデータ集計プログラム Ver.1.0
#   Last Update on 2026.1.19
#
#   ※GoogleSpreadSheetは制約が多いため、Excelに貼り付ける
##################################################################################
import os
import sys
import csv
import xlwings as xw
from datetime import datetime, timedelta
sys.path.append(os.pardir)          # 独自モジュールPATH追加        
import common.opdata_generator as opg


# ----- Definition of Constant -----------------------------------------------------------
BASE_FOLDER_OP = r'\\192.168.2.1\共有ファイル\M-光和共有ファイル\P_ProductControl\operation_data' + '\\'
BASE_FOLDER_AL = r'\\192.168.2.1\共有ファイル\M-光和共有ファイル\P_ProductControl\alarm_comment' + '\\'


# ----- Definition of Function -----------------------------------------------------------
def get_alarminfo_1day(mcname: str, op_date: str) -> list:
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
  alm_comment.insert(0,['Device','Comment'])  # ヘッダ行追加
  # print(alm_comment)    # ForDebug

  # 稼働データ取得(共有ファイルサーバから)
  all_opedata = opg.get_op_data(mc_name, op_date)
  if len(all_opedata)==0:
    # データなしの場合(0を代入)
    # print(f'ERROR:size of opedata is ZERO ({op_date})')
    alarm_num_data = [ 0 for x in range(320)]
  else:
    # アラーム発生回数データ格納
    alarm_num_data = all_opedata[3010:(3010+320)]
  
  alarm_num_data.insert(0, op_date) # ヘッダ行追加

  # データ結合
  for i,x in enumerate(alm_comment):
      x.append(alarm_num_data[i])
  # print(alm_comment)
  return alm_comment


def get_alarminfo_all(mc_name:str, st_date:str, days:int)-> list:
    alm_tbl = get_alarminfo_1day(mc_name,st_date) # 開始日データを格納

    # 2日目以降はデータを結合
    for i in range(1, days):
        op_date = get_date_str(st_date,i) # 対象日付
        alm_tbl_add = get_alarminfo_1day(mc_name,op_date) # 結合するデータ(1列、2列は不要)
        # データ結合
        for i,x in enumerate(alm_tbl):
          x.append(alm_tbl_add[i][2])
        print(f'{op_date} : 処理完了')  # 進捗確認用の表示

    return alm_tbl


def get_date_str(st_date:str, days:int)->str:
    '''
    指定した日数だけ経過した日付を取得
    
    :param st_date: 起点日(yyyy/mm/dd形式で指定)
    :param days: 経過日数(int型で指定)
    :return: 指定した日数経過した日付(yyyy/mm/dd形式)
    '''
    calc_date = datetime.strptime(st_date,'%Y/%m/%d') + timedelta(days=days)
    return calc_date.strftime('%Y/%m/%d')


# ----- MainProcess -----------------------------------------------------------
print('''==========================================================
   アラームデータ集計プログラム
   Ver.1.0 / Last Modified on 2026.1.19
==========================================================''')
mc_name = input('対象設備ナンバー(例:MC055) = ')
op_date = input('集計開始日(例:2025/12/01) = ')
days = int(input('集計日数(例:31) = '))

if False: # For Debug
  mc_name = 'MC058'
  op_date = '2025/12/01'
  days = 31


data = get_alarminfo_all(mc_name,op_date,days)
# print(data)

# 合計列の追加
col_num = len(data[0])
row_num = len(data)
data[0].append('TOTAL') # ヘッダ行
for i in range(1,row_num):
   total = sum(data[i][2:])  # アラーム別合計
   data[i].append(total)
# print(data) # ForDebug

# 合計列で並べ替え
header = data.pop(0)  # ヘッダを除去しておく
print(f'len(data[0])={len(data[0])}')
sorted_data = sorted(data, key=lambda row: row[len(data[0])-1],reverse=True)
sorted_data.insert(0,header)  # ヘッダを基に戻す
print(data) # ForDebug

# Excelへデータ貼り付け
wb = xw.Book()
ws = wb.sheets[0]
ws.range('A1').value = sorted_data

