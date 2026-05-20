""""1日分の設備ステータスデータを基に帯グラフを描画する

"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont


os.chdir(os.path.dirname(__file__)) # ワーキングディレクトリ変更(VSCode時必要)
# 独自モジュールPATH追加 
sys.path.append(os.pardir)
import common.opdata_generator as opg

# ----- Definition of Constant --------------------------------------------
COLOR_DIC = {0:'black',      # データなし
             1:'skyblue',    # 刃具交換
             2:'blue',       # 段替え
             3:'red',        # 故障停止
             4:'yellow',     # 材料切れ
             15:'limegreen', # 自動中
             16:'gray',      # 単純停止
             20:'deeppink',  # 異常中
             }


# ----- Definition of Function --------------------------------------------
def get_ope_graph(op_data:list, title:str)->object:
    """ 1日分の稼働データ(1440個)から帯グラフを作成する

    Args:
        op_data (list): 稼働データ(int型/1440個)
        title (list): グラフタイトル
        
    Returns:
        object: PILLOW IMAGEオブジェクト
    """
    # データ数チェック
    if len(op_data)!=1440:
        print('Number of OpeData is not 1440.')
        return None

    # 使用するフォント
    font_path = 'msgothic.ttc'
    font_L = ImageFont.truetype(font=font_path, size=22)
    font_M = ImageFont.truetype(font=font_path, size=16)

    # 背景用画像データ生成(Imageオブジェクト生成)
    img = Image.new('RGB',(1600,400),'white')
    # ImageDrawオブジェクトの生成
    draw = ImageDraw.Draw(img)
    
    basex = 80  # X方向の描画基準位置

    # タイトル描画
    draw.text((basex-50, 25),title,'black', font=font_L) # 目盛りタイトル

    # 帯グラフ描画
    i = 0
    for d in op_data:
        draw.line([(basex+i,100),(basex+i,200)],fill=COLOR_DIC[d],width=1)
        i += 1

  # 時間目盛り描画(1時間は60pixel)
    for i in range(0,25):
        posx = basex + i * 60
        draw.line([(posx,200),(posx,205)],fill='black',width=1) # 目盛り線
        draw.text((posx-4,210),str(i+4),'black',align='center', font=font_M) # 目盛り文字
    draw.text((basex-50,210),'Time','black', font=font_M) # 目盛りタイトル

    # 定時間(8:00-17:00)描画(黒矩形)
    start_posx = basex + (60*4) # 8:00
    end_posx = basex + (60*13)  # 17:00
    draw.rectangle([(start_posx,80),(end_posx,200)],fill=None,outline='black',width=1)
    label = '定時稼働時間 (8:00 - 17:00 = 540分)'
    draw.text((start_posx,60),label,'black', font=font_M)

    # 凡例画像貼り付け
    img_legend = Image.open('legend.png')
    img.paste(img_legend,(basex+0,240))

    # 結果確認　ForDebug
    # img.show()

    return img


def save_img(f_name:str, img:object)->bool:
    """ PILLOW IMAGEオブジェクトを保存する。
        保存先フォルダは「C:/my_data」で固定

    Args:
        f_name (str): 保存ファイル名
        img (object): 保存するIMAGEオブジェクト

    Returns:
        bool: 成功時True / 失敗時False
    """
    FOLDER_PATH = 'C:/my_data/'
    # フォルダ存在確認
    if os.path.isdir(FOLDER_PATH)==False:
        os.mkdir(FOLDER_PATH)
        print('Created new folder "my_data"')
   
    f_path = FOLDER_PATH + f_name
    img.save(f_path)


# テストコード(動作確認用) -----------------------------------------------------------------
if __name__=='__main__':
    
    # 稼働データ取得(ファイルサーバより)
    all_data = opg.get_op_data('MC067', '2025/09/10')
    op_data = opg.get_all_status_data(all_data)  # ステータスデータのみ格納(1440個)

    img = get_ope_graph(op_data, 'SAMPLE GRAPH')
    save_img('img_opdata.png', img)





