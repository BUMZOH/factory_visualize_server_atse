import os
import sys

os.chdir(os.path.dirname(__file__)) # ワーキングディレクトリ変更(VSCode時必要)
# 独自モジュールPATH追加 
sys.path.append(os.pardir)
import common.gdrive_com as gd


fpath = "C:/my_data/img_opdata.png"
# フォルダ：マイドライブ\K_共有ファイル\共有ファイル(全体)\IMAGE
# https://drive.google.com/drive/folders/1Bu-KASatQAinYbR7hW0zUXEWz2YsWrO0
folder_id = '1Bu-KASatQAinYbR7hW0zUXEWz2YsWrO0'
gd.upload_to_gdrive(fpath, folder_id)
print('Upload to Google-Drive complete!')




