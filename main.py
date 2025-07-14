import pyxel as px
import random as rand
import json
import os

#定数
IS_DEBUG        = False
ASSET_FILE      = "assets/assets.pyxres"
JP_FONT         = ""
ENCRYPT_KEY     = b"EzOjl1635"
DATAHEADER      = b"\x7F\x70\x79\x78"
NAME_CHARS      = [
 [["あ","い","う","え","お","　","わ","を","ん","、","。"],
  ["か","き","く","け","こ","　","が","ぎ","ぐ","げ","ご"],
  ["さ","し","す","せ","そ","　","ざ","じ","ず","ぜ","ぞ"],
  ["た","ち","つ","て","と","　","だ","ぢ","づ","で","ど"],
  ["な","に","ぬ","ね","の","　","ば","び","ぶ","べ","ぼ"],
  ["は","ひ","ふ","へ","ほ","　","ぱ","ぴ","ぷ","ぺ","ぽ"],
  ["ま","み","む","め","も","　","ぁ","ぃ","ぅ","ぇ","ぉ"],
  ["や","ゆ","よ","ゔ","　","　","っ","ゃ","ゅ","ょ","ー"],
  ["ら","り","る","れ","ろ","　","　","　","　","ｶﾅ","ED"],
 ],[
  ["ア","イ","ウ","エ","オ","　","ワ","ヲ","ン","、","。"],
  ["カ","キ","ク","ケ","コ","　","ガ","ギ","グ","ゲ","ゴ"],
  ["サ","シ","ス","セ","ソ","　","ザ","ジ","ズ","ゼ","ゾ"],
  ["タ","チ","ツ","テ","ト","　","ダ","ヂ","ヅ","デ","ド"],
  ["ナ","ニ","ヌ","ネ","ノ","　","バ","ビ","ブ","ベ","ボ"],
  ["ハ","ヒ","フ","ヘ","ホ","　","パ","ピ","プ","ペ","ポ"],
  ["マ","ミ","ム","メ","モ","　","ァ","ィ","ゥ","ェ","ォ"],
  ["ヤ","ユ","ヨ","ヴ","　","　","ッ","ャ","ュ","ョ","ー"],
  ["ラ","リ","ル","レ","ロ","　","　","　","　","Aa","ED"],
 ],[
  ["０","１","２","３","４","　","５","６","７","８","９"],
  ["Ａ","Ｂ","Ｃ","Ｄ","Ｅ","　","ａ","ｂ","ｃ","ｄ","ｅ"],
  ["Ｆ","Ｇ","Ｈ","Ｉ","Ｊ","　","ｆ","ｇ","ｈ","ｉ","ｊ"],
  ["Ｋ","Ｌ","Ｍ","Ｎ","Ｏ","　","ｋ","ｌ","ｍ","ｎ","ｏ"],
  ["Ｐ","Ｑ","Ｒ","Ｓ","Ｔ","　","ｐ","ｑ","ｒ","ｓ","ｔ"],
  ["Ｕ","Ｖ","Ｗ","Ｘ","Ｙ","　","ｕ","ｖ","ｗ","ｘ","ｙ"],
  ["Ｚ","　","　","　","　","　","ｚ","　","　","　","　"],
  ["！","？","＃","＄","％","　","＆","（","）","［","］"],
  ["．","＋","－","＝","：","　","；","＊","／","平","ED"],
 ]
]
han             = "0123456789"
zen             = "０１２３４５６７８９"
h2z             = str.maketrans(han,zen)

CHARA_DIR       = [[0,1],[-1,0],[1,0],[0,-1]]  #キャラの向き 0:下（正面）1:左 2:右 3:上（背面）
X,Y             = 0,1 #XY座標を添え字配列で指定する際の可読性
P_BLOCK_SIZE    = 16 #ブロックサイズ（Pixel）
if IS_DEBUG:
    PIXEL_PER_MOVE = 16
else:
    PIXEL_PER_MOVE = 4
P_CHIP_SIZE     = 8 #マップチップサイズ（Pixel）
B_DISP_SIZE     = 15 #画面表示サイズ※中央マスを設定する為、奇数設定が前提（Block）
B_DRAW_OFFSET   = -(-B_DISP_SIZE//2)
P_DRAW_WIDTH    = P_DRAW_HEIGHT = (1 + B_DISP_SIZE + 1) * P_BLOCK_SIZE

WINDOW_WAIT     = 90    #一時表示ウインドウの消去時間（frame）
SCENE_STATUS    = {"Field":0, "EvilField":10 , "Town":1, "Dungeon":2, "Title":3, "NameEntry":4, "Sanctuary":5, "Battle":9, "Ending":999}  #現在処理中のゲーム状況
SNDEFX          = {"Special":55, "run":56, "pi":57, "spell":58, "damage":59, "miss":60, "attack2":61, "attack1":62, "don":63}
IMGIDX_CHIP     = 0
IMGIDX_CHAR     = 1
IMGIDX_MOB      = 2
WEAPONS         = (["なし",0,0],["けやきのぼう",3,10],["せいどうのけん",12,160],["こうてつのおの",21,1080],["まほうのつるぎ",33,9800],["でんせつのけん",50,2])
ARMORS          = (["なし",0,0],["あさのふく",3,20],["かわのよろい",9,220],["ばんきんよろい",23,1880],["しゅごのよろい",28,7700],["むてきのよろい",38,2])
SHIELDS         = (["なし",0,0],["ちいさいたて",5,90],["おおきなたて",12,750],["マジックガード",13,5600],["しんわのたて",30,2])
ITEMS           = (["くすりのくさ",24],["まほうのくさ",240],["りゅうのうろこ",32768],["ランタン",8],["ばんのうかぎ",53],["オリハルコイル",0],["まどうバッテリ",0],["たいようのかぜ",0],["オーロラベール",0],["ゆうきのあかし",0],["ダミー",0])
MAGICS          = (["ヒール",4],["マジックアロー",2],["サンクチュアリ",2],["リターン",8],["グレートヒール",10],["エクスプロード",5])

MONSTERS        =( # id -> ,0Name,1MAXHP,2MAXMP,3ATK,4DEF,5SPD,6MGR,7EXP,8GOLD,9MAGIC ID(-1 is none),10img(ブロック数（img*P_CHIP_SIZE=8）,11ver(カラーバリエーション 0~),12imgtyp(イメージ種別)
    ["スライム",3,0,5,3,1,10,2,3,-1,2,0,0], #0
    ["ブルースライム",4,0,7,3,2,10,3,8,-1,2,1,0], #1
    ["きんぞくゼリー",4,40,40,255,100,99,805,21,1,2,2,0], #2
    ["ゼラチナスアイ",22,0,20,18,9,20,11,24,-1,2,3,0], #3
    ["あくまのひとみ",35,16,47,40,20,50,50,213,0,2,4,0], #4
    ["スコーピオン",20,0,18,52,4,0,9,24,-1,5,0,1], #5
    ["スチールクロー",34,0,36,118,11,0,35,100,-1,5,1,1], #6
    ["アンタレス",48,0,60,160,23,0,91,385,-1,5,2,1], #7
    ["キマイラ",42,0,56,48,36,50,36,150,-1,5,3,1], #8
    ["ダークキマイラ",58,0,78,68,46,70,85,350,-1,5,4,1], #9
    ["しんじゅう",65,20,86,80,60,90,151,560,4,5,5,1], #10
    ["ビッグバット",6,0,9,6,3,10,3,5,-1,3,0,2], #11
    ["メイジバット",15,6,14,10,7,15,13,30,1,3,1,2], #12
    ["ゴールデン",20,8,22,26,19,30,39,70,0,3,2,2], #13
    ["ウルフビースト",34,0,40,30,20,10,24,75,-1,3,3,2], #14
    ["ライカン",38,0,50,36,27,30,50,200,-1,3,4,2], #15
    ["ウェアウルフ",60,0,86,70,53,50,140,543,-1,3,5,2], #16
    ["ゴースト",7,0,11,8,4,30,5,8,-1,4,0,3], #17
    ["ハウント",23,10,18,20,10,50,20,45,1,4,1,3], #18
    ["デスレイス",36,18,38,36,18,80,63,245,1,4,2,3], #19
    ["ドラゴン",65,0,88,74,37,30,68,240,-1,4,3,3], #20
    ["ぎんりゅう",70,0,98,84,42,60,150,375,-1,4,4,3], #21
    ["きんりゅう",100,0,120,90,45,90,350,490,-1,4,5,3], #22
    ["ドルイド",13,8,11,12,6,50,6,18,1,3,0,4], #23
    ["ウィザード",30,16,28,22,11,75,33,88,1,3,1,4], #24
    ["ソーサラー",65,50,80,70,35,99,175,578,5,3,2,4], #25
    ["ふらんしたい",30,0,28,22,6,20,17,45,-1,3,0,5], #26
    ["くずれしかばね",36,8,44,34,9,40,43,150,0,3,1,5], #27
    ["のろわれたもの",46,8,68,56,14,60,98,420,0,3,2,5], #28
    ["グレイナイト",55,6,76,78,20,40,50,195,1,3,3,5], #29
    ["レッドクロス",70,30,94,82,22,50,135,413,4,3,4,5], #30
    ["ロイヤルガード",90,30,105,86,43,60,245,490,5,3,5,5], #31
)
MOB_AREA = [[0,1],[0,1,11],[1,11,17,0],[17,23,11,1],[17,23,12,5],[12,5,23,26],[5,26,24,14],[6,24,14,27],
            [27,6,18,15],[19,27,15,8],[8,28,29,7],[28,29,9,4,2],[29,9,16,10],[16,20,10,25],[18,13,26,24],[19,15,4,28],
            [16,20,10,25,30],[25,30,21],[25,31,22],[3,17,23,5],[1,2]]

BOSS = ( # id -> ,0Name,1MAXHP,2MAXMP,3ATK,4DEF,5SPD,6MGR,7EXP,8GOLD,9MAGIC ID(-1 is none),10img(ブロック数（img*P_CHIP_SIZE=8）,11ver(カラーバリエーション 0~),12imgtyp(イメージ種別)
   ["もりのあらくれ", 34, 0, 38, 30, 15, 0,260,800,-1,2,0,0], 
   ["デューンワーム",225,160, 89, 78, 13,60,1250,3200,1,4,0,1], 
   ["まもののおう"  ,250,100,100,150, 80,90,0,0,5,4,1,1], 
   ["まかいこうてい",520,  0,215,185, 75,99,0,0,-1,6,0,2], 
)

OBJ_CHAR_LIST = []



#******************************************************************************#
# 現在座標ごとの生息モンスター（MOB_AREAを参照）
#******************************************************************************#
def getLivingMobID(x, y):
    tileID = px.tilemaps[0].pget(x * 2, y * 2)
    mobListId = 2

#*****  草原１
    #初心者ゾーン
    if (125 <= x <= 176) and (99 <= y <= 202):
        match tileID:
            case [0,0]: #草原
                mobListId = 1
            case [1,0]: #森
                mobListId = 4
    #最初の試練
    elif (27 <= x <= 124) and (85 <= y <= 129):
        match tileID:
            case [0,0]: #草原
                mobListId = 3
            case [1,0]: #森
                mobListId = 5
    #森の迷路
    elif (28 <= x <= 78) and (191 <= y <= 222):
        match tileID:
            case [1,0]: #森
                mobListId = 7
    #スラ
    elif (21 <= x <= 23) and (126 <= y <= 126):
        match tileID:
            case [0,0]: #森
                mobListId = 20
    #全体
    elif (12 <= x <= 188) and (75 <= y <= 222):
        match tileID:
            case [0,0]: #草原
                mobListId = 19
            case [1,0]: #森
                mobListId = 6
            case [4,0]: #雪
                mobListId = 11
#*****  草原２
    #砂漠への経路
    if (230 <= x <= 279) and (181 <= y <= 222):
        match tileID:
            case [0,0]: #草原
                mobListId = 9
            case [1,0]: #森
                mobListId = 11
            # case [0,3]: #毒沼 #存在しない
            #     mobListId = 12
    #あかしの試練
    elif (245 <= x <= 284) and (75 <= y <= 180):
        match tileID:
            case [0,0]: #草原
                mobListId = 12
            case [1,0]: #森
                mobListId = 13
            case [0,3]: #毒沼
                mobListId = 15
    #全体
    elif (189 <= x <= 286) and (75 <= y <= 222):
        match tileID:
            case [0,0]: #草原
                mobListId = 8
            case [1,0]: #森
                mobListId = 15

#*****  砂漠
    #東砂漠　奥地
    if (129 <= x <= 175) and (223 <= y <= 282):
        match tileID:
            case [2,0]: #砂地
                mobListId = 10
            case [3,0]: #荒地
                mobListId = 12
            case [0,3]: #毒沼
                mobListId = 13
    #全体
    elif (12 <= x <= 286) and (223 <= y <= 289):
        match tileID:
            case [0,0]: #草原
                mobListId = 9
            case [1,0]: #森
                mobListId = 7
            case [2,0]: #砂地
                mobListId = 8
            case [3,0]: #荒地
                mobListId = 9
            case [0,3]: #毒沼
                mobListId = 14

#*****  雪原
    #北東の岬
    if (258 <= x <= 285) and (13 <= y <= 34):
        match tileID:
            case [5,0]: #氷
                mobListId = 17
            case [4,0]: #雪
                mobListId = 16
    #魔王城
    elif (15 <= x <= 76) and (17 <= y <= 69):
        match tileID:
            case [7,0]: #魔回廊
                mobListId = 18
            case [5,0]: #氷
                mobListId = 17
            case [4,0]: #雪
                mobListId = 16
            case [1,3]: #バリア
                mobListId = 17
    #全体
    elif (12 <= x <= 286) and (11 <= y <= 74):
        match tileID:
            case [0,0]: #草原
                mobListId = 0
            case [5,0]: #氷
                mobListId = 16
            case [4,0]: #雪
                mobListId = 13
            case [1,3]: #バリア
                mobListId = 17

    mobList = MOB_AREA[mobListId]
    lenList = len(mobList)
    mobListRating = []
    for i in range(lenList):
        for c in range(lenList - i):
            mobListRating.append(mobList[i])
    
    return mobListRating[px.rndi(0,len(mobListRating)-1)]



#******************************************************************************#
# アイテム新規入手・加算
#******************************************************************************#
def getItem(ItemID):
    chkResult = True
      
    try:
        for i in range(len(OBJ_CHAR_LIST[0].Item)+1):
            if OBJ_CHAR_LIST[0].Item[i][0] == ItemID:
                OBJ_CHAR_LIST[0].Item[i][1] += 1
                chkResult = False
                break
    except IndexError:
        OBJ_CHAR_LIST[0].Item.append([i-1,1])

    if chkResult:
        OBJ_CHAR_LIST[0].Item.append([ItemID,1])
        OBJ_CHAR_LIST[0].Item.sort



#******************************************************************************#
# レベルアップ処理
#******************************************************************************#

def chkLevelUp():
    ParaUP=[]
    lstGetMagic = []
    i=0
    while i <= 30:

        if OBJ_CHAR_LIST[0].st.xp >= 6 and OBJ_CHAR_LIST[0].lvl < 2:
            ParaUP = [8,0,2,1,1,0]
        elif OBJ_CHAR_LIST[0].st.xp >= 21 and OBJ_CHAR_LIST[0].lvl < 3:
            ParaUP = [3,5,2,2,2,1]
            OBJ_CHAR_LIST[0].magic.append(0)
            lstGetMagic.append(0)
        elif OBJ_CHAR_LIST[0].st.xp >= 45 and OBJ_CHAR_LIST[0].lvl < 4:
            ParaUP = [8,11,1,2,1,1]
        elif OBJ_CHAR_LIST[0].st.xp >= 108 and OBJ_CHAR_LIST[0].lvl < 5:
            ParaUP = [5,4,4,2,1,1]
            OBJ_CHAR_LIST[0].magic.append(1)
            lstGetMagic.append(1)
        elif OBJ_CHAR_LIST[0].st.xp >= 210 and OBJ_CHAR_LIST[0].lvl < 6:
            ParaUP = [4,4,4,1,2,2]
        elif OBJ_CHAR_LIST[0].st.xp >= 440 and OBJ_CHAR_LIST[0].lvl < 7:
            ParaUP = [3,2,2,6,3,1]
        elif OBJ_CHAR_LIST[0].st.xp >= 780 and OBJ_CHAR_LIST[0].lvl < 8:
            ParaUP = [7,3,3,3,2,1]
            OBJ_CHAR_LIST[0].magic.append(2)
            lstGetMagic.append(2)
        elif OBJ_CHAR_LIST[0].st.xp >= 1250 and OBJ_CHAR_LIST[0].lvl < 9:
            ParaUP = [5,7,8,1,2,3]
        elif OBJ_CHAR_LIST[0].st.xp >= 1880 and OBJ_CHAR_LIST[0].lvl < 10:
            ParaUP = [5,4,4,8,4,1]
        elif OBJ_CHAR_LIST[0].st.xp >= 2800 and OBJ_CHAR_LIST[0].lvl < 11:
            ParaUP = [9,10,5,4,2,1]
        elif OBJ_CHAR_LIST[0].st.xp >= 4000 and OBJ_CHAR_LIST[0].lvl < 12:
            ParaUP = [2,8,7,5,4,1]
            OBJ_CHAR_LIST[0].magic.append(3)
            lstGetMagic.append(3)
        elif OBJ_CHAR_LIST[0].st.xp >= 5500 and OBJ_CHAR_LIST[0].lvl < 13:
            ParaUP = [8,6,3,7,4,4]
        elif OBJ_CHAR_LIST[0].st.xp >= 7500 and OBJ_CHAR_LIST[0].lvl < 14:
            ParaUP = [10,6,8,6,3,2]
        elif OBJ_CHAR_LIST[0].st.xp >= 9500 and OBJ_CHAR_LIST[0].lvl < 15:
            ParaUP = [10,2,7,8,5,2]
        elif OBJ_CHAR_LIST[0].st.xp >= 12000 and OBJ_CHAR_LIST[0].lvl < 16:
            ParaUP = [8,23,3,6,3,2]
            OBJ_CHAR_LIST[0].magic.append(4)
            lstGetMagic.append(4)
        elif OBJ_CHAR_LIST[0].st.xp >= 14500 and OBJ_CHAR_LIST[0].lvl < 17:
            ParaUP = [10,5,1,7,4,5]
        elif OBJ_CHAR_LIST[0].st.xp >= 17500 and OBJ_CHAR_LIST[0].lvl < 18:
            ParaUP = [17,8,12,5,4,2]
        elif OBJ_CHAR_LIST[0].st.xp >= 20000 and OBJ_CHAR_LIST[0].lvl < 19:
            ParaUP = [17,7,2,2,1,2]
            OBJ_CHAR_LIST[0].magic.append(5)
            lstGetMagic.append(5)
        elif OBJ_CHAR_LIST[0].st.xp >= 23000 and OBJ_CHAR_LIST[0].lvl < 20:
            ParaUP = [10,13,4,2,1,2]
        elif OBJ_CHAR_LIST[0].st.xp >= 26000 and OBJ_CHAR_LIST[0].lvl < 21:
            ParaUP = [13,7,3,2,2,6]
        elif OBJ_CHAR_LIST[0].st.xp >= 29500 and OBJ_CHAR_LIST[0].lvl < 22:
            ParaUP = [11,11,2,1,1,3]
        elif OBJ_CHAR_LIST[0].st.xp >= 33000 and OBJ_CHAR_LIST[0].lvl < 23:
            ParaUP = [9,7,2,3,2,2]
        elif OBJ_CHAR_LIST[0].st.xp >= 37000 and OBJ_CHAR_LIST[0].lvl < 24:
            ParaUP = [7,8,3,4,3,2]
        elif OBJ_CHAR_LIST[0].st.xp >= 41000 and OBJ_CHAR_LIST[0].lvl < 25:
            ParaUP = [6,0,9,2,1,3]
        elif OBJ_CHAR_LIST[0].st.xp >= 45500 and OBJ_CHAR_LIST[0].lvl < 26:
            ParaUP = [8,7,4,4,2,2]
        elif OBJ_CHAR_LIST[0].st.xp >= 50000 and OBJ_CHAR_LIST[0].lvl < 27:
            ParaUP = [11,7,7,2,2,3]
        elif OBJ_CHAR_LIST[0].st.xp >= 55000 and OBJ_CHAR_LIST[0].lvl < 28:
            ParaUP = [8,5,5,7,4,2]
        elif OBJ_CHAR_LIST[0].st.xp >= 60000 and OBJ_CHAR_LIST[0].lvl < 29:
            ParaUP = [7,10,4,5,3,3]
        elif OBJ_CHAR_LIST[0].st.xp >= 65535 and OBJ_CHAR_LIST[0].lvl < 30:
            #MHP,MMP,ATK,DEF,SPD,MGR
            ParaUP = [11,10,6,9,6,5]

        if len(ParaUP) > 0:
            insMsgWnd = Window(16,16,px.width - (P_BLOCK_SIZE*2),104,1)
            insMsgWnd.draw()
            tmpTxt = [OBJ_CHAR_LIST[0].name+"は　つよくなった！",""]
            for i in range(len(lstGetMagic)):
                tmpStr="まほう　"+MAGICS[lstGetMagic[i]][0]+" を　おぼえた！"
                tmpTxt.append(tmpStr)
            
            txtMsg = Message(24, 24, tmpTxt)

            insMsgWnd.drawText(txtMsg.P_x, txtMsg.P_y, txtMsg.msg)
            OBJ_CHAR_LIST[0].lvl += 1
            OBJ_CHAR_LIST[0].st.MHP += ParaUP[0]
            OBJ_CHAR_LIST[0].st.MMP += ParaUP[1]
            OBJ_CHAR_LIST[0].st.ATK += ParaUP[2]
            OBJ_CHAR_LIST[0].st.DEF += ParaUP[3]
            OBJ_CHAR_LIST[0].st.SPD += ParaUP[4]
            OBJ_CHAR_LIST[0].st.MGR += ParaUP[5]
            ParaUP = []

        i+=1


#******************************************************************************#
# ゲーム状態初期化
#******************************************************************************#
def reloadGameStatus():
    global OBJ_CHAR_LIST

    OBJ_CHAR_LIST   = [Character(130,170)]  #id0 主人公
#   デバッグ用
    if IS_DEBUG:
        OBJ_CHAR_LIST[0].st.xp=65535
        OBJ_CHAR_LIST[0].st.gp=65535

    OBJ_CHAR_LIST.append(Character(24,23,9,7)) #id1　魔王
    OBJ_CHAR_LIST.append(Character(118,158,9,2)) #id2 街の王
    OBJ_CHAR_LIST.append(Character(88,223,9,2)) #id3 森の王
    OBJ_CHAR_LIST.append(Character(18,285,9,5)) #id4 海の女王
    OBJ_CHAR_LIST.append(Character(178,236,9,5)) #id5 砂漠の女王
    OBJ_CHAR_LIST.append(Character(159,76,9,6)) #id6 雪原の神官
    #街NPC
    OBJ_CHAR_LIST.append(Character(126,170,9,1)) #id7 商人
    OBJ_CHAR_LIST.append(Character(124,170,9,4)) #id8 宿屋
    OBJ_CHAR_LIST.append(Character(121,170,9,6)) #id9 神官
    OBJ_CHAR_LIST.append(Character(132,158,9,3)) #id10 衛兵１
    OBJ_CHAR_LIST.append(Character(118,170,9,3)) #id11 衛兵２
    #森NPC
    OBJ_CHAR_LIST.append(Character(83,223,9,1)) #id12 商人
    OBJ_CHAR_LIST.append(Character(88,215,9,4)) #id13 宿屋
    OBJ_CHAR_LIST.append(Character(84,220,9,6)) #id14 神官
    OBJ_CHAR_LIST.append(Character(80,223,9,3)) #id15 衛兵３
    #海NPC
    OBJ_CHAR_LIST.append(Character(18,281,9,1)) #id16 商人
    OBJ_CHAR_LIST.append(Character(23,281,9,4)) #id17 宿屋
    OBJ_CHAR_LIST.append(Character(23,285,9,6)) #id18 神官
    #砂漠NPC
    OBJ_CHAR_LIST.append(Character(175,242,9,1)) #id19 商人
    OBJ_CHAR_LIST.append(Character(180,241,9,4)) #id20 宿屋
    OBJ_CHAR_LIST.append(Character(181,236,9,6)) #id21 神官
    #海NPC追加
    OBJ_CHAR_LIST.append(Character(18,283,9,1)) #id22 商人
    #雪原NPC追加
    OBJ_CHAR_LIST.append(Character(160,76,9,4)) #id23 宿屋
    #雪原NPC追加
    OBJ_CHAR_LIST.append(Character(231,87,9,6)) #id24 神官

#******************************************************************************#
# サウンドファイルロード・演奏開始
#******************************************************************************#
def reloadBGM(scene):
    px.stop()
    Merged = []
    match scene:
        case 3: # SCENE_STATUS["Title"]
            with open("assets/Title.json", "rt") as fin:
                Merged = json.loads(fin.read())

        case 4: # SCENE_STATUS["NameEntry"]
            with open("assets/name.json", "rt") as fin:
                Merged = json.loads(fin.read())

        case 0: # SCENE_STATUS["Field"]
            with open("assets/fieldA.json", "rt") as fin:
                PartA = json.loads(fin.read()) 
            with open("assets/fieldB.json", "rt") as fin:
                PartB = json.loads(fin.read()) 
                Merged = PartA
                for i in range(4):
                    Merged[i][0] += PartB[i][0]
                    Merged[i][2] += PartB[i][2]

        case 8: #勝利
            with open("assets/win.json", "rt") as fin:
                Merged = json.loads(fin.read())

        case 9: #SCENE_STATUS["Battle"]
            with open("assets/battleA.json", "rt") as fin:
                PartA = json.loads(fin.read()) 
            with open("assets/battleB.json", "rt") as fin:
                PartB = json.loads(fin.read()) 
                Merged = PartA
                for i in range(4):
                    Merged[i][0] += PartB[i][0]
                    Merged[i][2] += PartB[i][2]
                
        case 90: # Boss
            with open("assets/BossBattle.json", "rt") as fin:
                Merged = json.loads(fin.read())

        case 99: # LastBoss
            with open("assets/LastBoss.json", "rt") as fin:
                PartA = json.loads(fin.read()) 
            with open("assets/LastBoss2.json", "rt") as fin:
                PartB = json.loads(fin.read())
                Merged = PartA
                for i in range(4):
                    Merged[i][0] += PartB[i][0]
                    Merged[i][2] += PartB[i][2]

        case 'Ending':
            with open("assets/ed1.json", "rt") as fin:
                PartA = json.loads(fin.read()) 
            with open("assets/ed2b.json", "rt") as fin:
                PartB = json.loads(fin.read())
            with open("assets/ed3.json", "rt") as fin:
                PartC = json.loads(fin.read())

                Merged = PartA
                for i in range(4):
                    Merged[i][0] += PartB[i][0]
                    Merged[i][2] += PartB[i][2]
                for i in range(4):
                    Merged[i][0] += PartC[i][0]
                    Merged[i][2] += PartC[i][2]

    if px.play_pos(0) is None:
        for ch, sound in enumerate(Merged):
            px.sound(ch).set(*sound)
            px.play(ch, ch, loop=True)


#****#****#****#****#**** manageEvent #****#****#****#****#****
class manageEvent:
    def __init__(self):
        self.flgCoil    = False
        self.flgBattery = False
        self.flgSolar   = False
        self.flgAurora  = False
        self.flgBrave   = False
        self._1stGuard  = False
        self._2ndGuard  = False
        self._3rdGuard  = False
        self.Boss1kill  = False
        self.Boss2kill  = False
        self.Boss3kill  = False
        self.Boss4kill  = False
        self.flgDoor1   = False
        self.flgDoor2   = False
        self.flgDoor3   = False
        self.Events = [self.flgCoil, self.flgBattery, self.flgSolar, self.flgAurora, self.flgBrave,
                        self._1stGuard, self._2ndGuard, self._3rdGuard,
                        self.Boss1kill, self.Boss2kill, self.Boss3kill, self.Boss4kill,
                        self.flgDoor1, self.flgDoor2, self.flgDoor3]

    def get(self, EventId):
        return self.Events[EventId]
    
    def set(self, EventId, flgBool:bool):
        self.Events[EventId] = flgBool
        return self.Events[EventId]

EVENT_STAT = manageEvent()



#****#****#****#****#**** Status #****#****#****#****#****        
class Status:
    def __init__(self, MAXHP:int=0, MAXMP:int=0, Attack:int=0, Defend:int=0, Speed:int=0, MagicResist:int=0, Exp:int=0, Gold:int=0):
        self.MHP=MAXHP
        self.MMP=MAXMP
        self.ATK=Attack
        self.DEF=Defend
        self.SPD=Speed
        self.MGR=MagicResist
        self.HP=self.MHP
        self.MP=self.MMP
        self.xp=Exp
        self.gp=Gold

#****#****#****#****#**** Character #****#****#****#****#****
class Character:
    def __init__(self, x, y, typMv=0, typFg=0):   
        self.B_addr     = [x, y]    #キャラのマップ上座標（Block）
        self.now_dir    = 0         #キャラの向き（CHARA_DIRを指す）
        self.P_offset   = [0,0]     #スクロール用オフセット（Pixel）
        self.SpritePos  = 0
        self.flgMove    = False
        self.chkResult  = False
        self.movType    = typMv         #キャラの種別≒移動タイプ（0:画面中央固定 1:画面内移動 9:非移動）
        self.chrType    = typFg         #キャラ外見種別
        self.TileValue  = ()
        if self.movType == 0:
            self.name = "ゆ〇しゃ"
            self.lvl = 1
            self.st = Status(15,0,3,3,3,0)
            self.eq = [0,0,0]
            self.st.ATK += WEAPONS[self.eq[0]][1]
            self.st.DEF += ARMORS[self.eq[1]][1]
            self.st.DEF += SHIELDS[self.eq[2]][1]
            self.Item = [[0,0],[1,0],[2,0],[3,0],[4,0],[5,0],[6,0],[7,0],[8,0],[9,0]]
            self.magic = []

            self.flgPoison      = False
            self.flgBarria      = False
            self.flgSanctuary   = False
            self.sanctuaryCount = 0
            self.flgLantern     = False
            self.LanternCount   = 0
            self.flgWarp        = [False,[0,0]]
            self.flgYouDied     = False


    def update(self, flgWindowOpen, CharList):
        #スプライトアニメーション（イメージ取得元アドレスの上下位置を15フレーム毎に切替）
        if px.frame_count % 15 == 0:
            self.SpritePos = px.frame_count % 2

        if self.movType == 0:
            if flgWindowOpen:
                return
            elif self.flgWarp[0]:
                self.B_addr = self.flgWarp[1]
                self.flgWarp[0] = False
            elif self.flgMove:
                return self.move(CharList)
            else:
                if px.btn(px.KEY_W) or px.btn(px.GAMEPAD1_BUTTON_DPAD_UP) or px.btn(px.KEY_UP):
                    # px.flip()
                    self.now_dir = 3
                    self.flgMove = True
                if px.btn(px.KEY_A) or px.btn(px.GAMEPAD1_BUTTON_DPAD_LEFT) or px.btn(px.KEY_LEFT):
                    # px.flip()
                    self.now_dir = 1
                    self.flgMove = True
                if px.btn(px.KEY_S) or px.btn(px.GAMEPAD1_BUTTON_DPAD_DOWN) or px.btn(px.KEY_DOWN):
                    # px.flip()
                    self.now_dir = 0
                    self.flgMove = True
                if px.btn(px.KEY_D) or px.btn(px.GAMEPAD1_BUTTON_DPAD_RIGHT) or px.btn(px.KEY_RIGHT):
                    # px.flip()
                    self.now_dir = 2
                    self.flgMove = True
#ロジックは有効だが対象キャラが未実装
        # elif self.movType == 1:
        #     if self.flgMove:
        #         self.move(CharList)
        #         return
        #     else:
        #         if px.frame_count % 60 == 0:
        #             tmpRnd = px.rndi(0,4)
        #             if tmpRnd == 4:
        #                 pass
        #             else:
        #                 self.now_dir = tmpRnd
        #                 self.flgMove = True
        # elif self.movType == 9:
        #     pass

    def draw(self, B_adrStart=None, P_mapOfs=None):
        match self.movType:
            case 0:
                #画面中央に居るバージョン
                px.blt( (B_DISP_SIZE*P_BLOCK_SIZE - P_BLOCK_SIZE) // 2, (B_DISP_SIZE*P_BLOCK_SIZE - P_BLOCK_SIZE) // 2, IMGIDX_CHAR,
                        self.now_dir*P_BLOCK_SIZE,self.SpritePos*P_BLOCK_SIZE, P_BLOCK_SIZE,P_BLOCK_SIZE, colkey=0)
                #デバッグ時は無効
                if IS_DEBUG == False:
                    #ダメージ床：毒沼
                    if self.flgPoison:
                        px.dither(0.5)
                        px.rect(0,0, px.width,px.height, 8)
                        px.play(3,SNDEFX["damage"], resume=True)
                        px.flip
                        px.dither(1)
                        self.flgPoison = False
                    #ダメージ床：バリア
                    if self.flgBarria:
                        px.dither(0.5)
                        px.rect(0,0, px.width,px.height, 10)
                        px.play(3,SNDEFX["damage"], resume=True)
                        px.flip
                        px.dither(1)
                        self.flgBarria = False

#デバッグ用
                if IS_DEBUG:
                    px.text((B_DISP_SIZE*P_BLOCK_SIZE - P_BLOCK_SIZE) // 2, (B_DISP_SIZE*P_BLOCK_SIZE - P_BLOCK_SIZE) // 2 - 6, str(self.B_addr), 0)
            case 1:
                #座標地点へ移動するバージョン
                px.blt( ((self.B_addr[X]-B_adrStart[X]-1)*P_BLOCK_SIZE) - P_mapOfs[X] + self.P_offset[X],
                        ((self.B_addr[Y]-B_adrStart[Y]-1)*P_BLOCK_SIZE) - P_mapOfs[Y] + self.P_offset[Y], IMGIDX_CHAR,
                        self.now_dir*P_BLOCK_SIZE,(self.chrType*2+self.SpritePos)*P_BLOCK_SIZE, P_BLOCK_SIZE,P_BLOCK_SIZE, colkey=0)

            case 9:
                #移動しない
                px.blt( ((self.B_addr[X]-B_adrStart[X]-1)*P_BLOCK_SIZE) - P_mapOfs[X], ((self.B_addr[Y]-B_adrStart[Y]-1)*P_BLOCK_SIZE) - P_mapOfs[Y], IMGIDX_CHAR,
                        self.now_dir*P_BLOCK_SIZE,(self.chrType*2+self.SpritePos)*P_BLOCK_SIZE, P_BLOCK_SIZE,P_BLOCK_SIZE, colkey=0)


    def move(self, CharList):
        chkCollid = True

        #通行可能タイルチェック
        if self.chkResult==False:
            self.TileValue = px.tilemaps[0].pget((self.B_addr[X]+CHARA_DIR[self.now_dir][X])*2, (self.B_addr[Y]+CHARA_DIR[self.now_dir][Y])*2)
            match self.TileValue[1]:
                case 1:
                    chkCollid = False
                case 2:
                    chkCollid = False

            #キャラ同士衝突チェック
            for i in range(len(CharList)):
                if id(CharList[i]) != id(self) :
                    if (CharList[i].B_addr) == ([self.B_addr[X]+CHARA_DIR[self.now_dir][X], self.B_addr[Y]+CHARA_DIR[self.now_dir][Y]]):
                        chkCollid = False
                        break
                    if not chkCollid:
                        break
            
            #イベントオブジェクト衝突チェック
            match [self.B_addr[X]+CHARA_DIR[self.now_dir][X], self.B_addr[Y]+CHARA_DIR[self.now_dir][Y]]:
                case [91,209]:
                    chkCollid = EVENT_STAT.get(7)
                case [52,107]:
                    chkCollid = EVENT_STAT.get(8)
                case [121,226]:
                    chkCollid = EVENT_STAT.get(9)
                case [39,38]:
                    chkCollid = EVENT_STAT.get(12)
                case [276,17]:
                    chkCollid = EVENT_STAT.get(13)
                case [223,66]:
                    chkCollid = EVENT_STAT.get(14)
            self.chkResult=True

#デバッグ用
        if IS_DEBUG:
            chkCollid = True

        if chkCollid:
            #画面中央に居るバージョン
            #座標地点へ移動するバージョン
            if ((self.P_offset[X] == CHARA_DIR[self.now_dir][X] * (P_BLOCK_SIZE-PIXEL_PER_MOVE)) and (self.P_offset[Y] == CHARA_DIR[self.now_dir][Y] * (P_BLOCK_SIZE-PIXEL_PER_MOVE))):
                self.B_addr[X] += CHARA_DIR[self.now_dir][X]
                self.B_addr[Y] += CHARA_DIR[self.now_dir][Y]

                if IS_DEBUG == False:
                    #毒沼ダメージ
                    if self.TileValue == (0,3):
                        #むてきのよろい　で　毒沼スルー
                        if OBJ_CHAR_LIST[0].eq[1] != 5:
                            self.flgPoison = True
                            OBJ_CHAR_LIST[0].st.HP -= 2

                    #バリアダメージ
                    if self.TileValue == (1,3):
                        #むてきのよろい　で　バリア半減
                        self.flgBarria = True
                        damage = 15
                        if OBJ_CHAR_LIST[0].eq[1] == 5:
                            damage = 8
                        OBJ_CHAR_LIST[0].st.HP -= damage

                    #ダメ床で死んだらアウト
                    if OBJ_CHAR_LIST[0].st.HP <= 0:
                        self.flgYouDied = True
                        return

                #しんわのたて　で　HP回復
                if (OBJ_CHAR_LIST[0].eq[2] == 4) and (OBJ_CHAR_LIST[0].st.HP < OBJ_CHAR_LIST[0].st.MHP):
                    OBJ_CHAR_LIST[0].st.HP += 1

                #サンクチュアリ中はカウンタ減産
                if self.sanctuaryCount > 0:
                    self.sanctuaryCount -= 1
                    if self.sanctuaryCount == 0:
                        self.flgSanctuary = True

                #ランタン中はカウンタ減産
                if self.flgLantern:
                    self.LanternCount -= 1
                    if self.LanternCount == 0:
                        self.flgLantern = False

                self.P_offset = [0,0]
                self.flgMove = False
                self.chkResult = False
            else:
                self.P_offset[X] += CHARA_DIR[self.now_dir][X]*PIXEL_PER_MOVE
                self.P_offset[Y] += CHARA_DIR[self.now_dir][Y]*PIXEL_PER_MOVE
            return True
        else:
            if self.movType == 0:
                px.play(3,SNDEFX["don"], resume=True)
                for i in range(16//PIXEL_PER_MOVE):
                    px.flip()
            self.flgMove = False
            self.chkResult = False
            return False

#****#****#****#****#**** Map #****#****#****#****#****
class Map:
    if IS_DEBUG:
        EncountRate = ([SCENE_STATUS["Field"], 0],
                    [SCENE_STATUS["EvilField"],0],
                    [SCENE_STATUS["Town"],     0],
                    [SCENE_STATUS["Dungeon"],  0],
                    )
    else:
        EncountRate = ([SCENE_STATUS["Field"],  7],
                    [SCENE_STATUS["EvilField"],66],
                    [SCENE_STATUS["Town"],      0],
                    [SCENE_STATUS["Dungeon"],  15],
                    )

    def __init__(self, area:int=0):
        self.B_charAddr  = [0,0]    #キャラクタ位置（Block）
        self.B_drawStart = [0,0]    #描画開始位置（Block）
        self.P_offset    = [0,0]    #スクロール用オフセット（Pixel）
        self.areaType    = area     #マップエリア種別 0:ワールドマップ 1:安全地帯（街その他） 2:危険地帯
        self.rndEncount  = self.generateRandom(100)


    def generateRandom(self, num:int):
        rand.seed()
        return iter(rand.sample(range(0,num),k=num))


    def update(self, flgMove, dir, x, y):
        self.B_charAddr  = [x, y]
        self.B_drawStart = [x - B_DRAW_OFFSET, y - B_DRAW_OFFSET]
        if flgMove:
            self.P_offset[X] += CHARA_DIR[dir][X]*PIXEL_PER_MOVE
            self.P_offset[Y] += CHARA_DIR[dir][Y]*PIXEL_PER_MOVE
            return False
        else:
            if self.P_offset != [0,0]:
                self.P_offset = [0,0]
                if (116 <= self.B_charAddr[X] <= 133) and (157 <= self.B_charAddr[Y] <= 172):
                    return False
                if (80 <= self.B_charAddr[X] <= 89) and (215 <= self.B_charAddr[Y] <= 223):
                    return False
                if (18 <= self.B_charAddr[X] <= 23) and (281 <= self.B_charAddr[Y] <= 285):
                    return False
                if (176 <= self.B_charAddr[X] <= 181) and (236 <= self.B_charAddr[Y] <= 242):
                    return False
                try:
                    roll = next(self.rndEncount)
                except StopIteration:
                    self.rndEncount  = self.generateRandom(100)
                    roll = next(self.rndEncount)

                if OBJ_CHAR_LIST[0].eq[1] == 4:
                    #しゅごのよろいは　エンカウント率低減
                    roll *= 2.8

                if (231 <= OBJ_CHAR_LIST[0].B_addr[X] <= 283) and (69 <= OBJ_CHAR_LIST[0].B_addr[Y] <= 180):
                    if IS_DEBUG:
                        print(roll<78, roll*2.8<78 )
                    return ( roll < self.EncountRate[1][1] )
                elif (15 <= OBJ_CHAR_LIST[0].B_addr[X] <= 76) and (17 <= OBJ_CHAR_LIST[0].B_addr[Y] <= 69):
                    return ( roll < self.EncountRate[3][1] )
                else:
                    return ( roll < self.EncountRate[self.areaType][1] )

                
    def draw(self):
        P_drawStart = self.B_drawStart[X] * P_BLOCK_SIZE, self.B_drawStart[Y] * P_BLOCK_SIZE
        px.bltm(-P_BLOCK_SIZE,-P_BLOCK_SIZE, 0, P_drawStart[X]+self.P_offset[X], P_drawStart[Y]+self.P_offset[Y], P_DRAW_WIDTH, P_DRAW_HEIGHT, colkey=0)


#****#****#****#****#**** Window #****#****#****#****#****
class Window:
    def __init__(self, x:int, y:int, w:int, h:int, t:int=0):
        if x + w > px.width:
            self.P_x = px.width - w            
        else:
            self.P_x = x
        self.P_y = y
        self.P_width = w #- x
        self.P_height= h #- y
        self.wType = t #ウインドウタイプ　0:待機メッセージ 1:一時メッセージ 2:選択メニュー 3:外部制御ウインドウ
        self.tTimer = 0


    def update(self):
        match self.wType:
            case 0:
                if px.btnp(px.KEY_Z, 10, 5) or px.btnp(px.GAMEPAD1_BUTTON_A, 10, 5) or px.btnp(px.KEY_RETURN, 10, 5):
                    px.flip()
                    px.play(3,SNDEFX["pi"], resume=True)
                    return False
                if px.btnp(px.KEY_X, 10, 5) or px.btnp(px.GAMEPAD1_BUTTON_B, 10, 5) or px.btnp(px.KEY_SPACE, 10, 5):
                    px.flip()
                    return False
            case 1:
                if self.tTimer == 0:
                    self.tTimer = px.frame_count
                while self.tTimer + WINDOW_WAIT > px.frame_count:
                    px.flip()
                    if ( px.btnp(px.KEY_Z, 10, 5) or px.btnp(px.GAMEPAD1_BUTTON_A, 10, 5) or
                         px.btnp(px.KEY_X, 10, 5) or px.btnp(px.GAMEPAD1_BUTTON_B, 10, 5) or
                         px.btnp(px.KEY_RETURN, 10, 5)) or px.btnp(px.KEY_SPACE, 10, 5):
                        if (px.frame_count-self.tTimer) > 17:
                            px.play(3,SNDEFX["pi"], resume=True)
                            break
                return False
            case 2:
                pass
            case 3:
                if self.tTimer == 0:
                    self.tTimer = px.frame_count
                while self.tTimer + WINDOW_WAIT*4 > px.frame_count:
                    px.flip()
                    if ( px.btnp(px.KEY_Z, 10, 5) or px.btnp(px.GAMEPAD1_BUTTON_A, 10, 5) or
                         px.btnp(px.KEY_X, 10, 5) or px.btnp(px.GAMEPAD1_BUTTON_B, 10, 5) or
                         px.btnp(px.KEY_RETURN, 10, 5)) or px.btnp(px.KEY_SPACE, 10, 5):
                        if (px.frame_count-self.tTimer) > WINDOW_WAIT:
                            px.play(3,SNDEFX["pi"], resume=True)
                            break
                self.wType = 4
                return False
            case 4:
                return True

        return True


    def draw(self):
        chip_cnt_w = self.P_width  // P_CHIP_SIZE 
        chip_cnt_h = self.P_height // P_CHIP_SIZE

        #枠線
        for Ypos in range(chip_cnt_h):
            for Xpos in range(chip_cnt_w):
                #四隅
                if Ypos == 0 and Xpos == 0:
                    px.blt(self.P_x, self.P_y, IMGIDX_CHIP,
                            0, 40, P_CHIP_SIZE,P_CHIP_SIZE, colkey=0) #左上
                elif Ypos == 0 and Xpos == chip_cnt_w-1:
                    px.blt(self.P_x + self.P_width - P_CHIP_SIZE, self.P_y, IMGIDX_CHIP,
                            8, 40, P_CHIP_SIZE,P_CHIP_SIZE, colkey=0) #右上
                elif Ypos == chip_cnt_h-1 and Xpos == 0:
                    px.blt(self.P_x, self.P_y + self.P_height - P_CHIP_SIZE, IMGIDX_CHIP,
                            0, 48, P_CHIP_SIZE,P_CHIP_SIZE, colkey=0) #左下
                elif Ypos == chip_cnt_h-1 and Xpos == chip_cnt_w-1:
                    px.blt(self.P_x + self.P_width - P_CHIP_SIZE, self.P_y + self.P_height - P_CHIP_SIZE, IMGIDX_CHIP,
                            8, 48,  P_CHIP_SIZE,P_CHIP_SIZE, colkey=0) #右下
                #枠線
                elif Ypos == 0: #上端
                    px.blt(self.P_x + (Xpos*P_CHIP_SIZE), self.P_y, IMGIDX_CHIP,
                           16, 48, P_CHIP_SIZE,P_CHIP_SIZE )
                elif Xpos == 0: #左端
                    px.blt(self.P_x, self.P_y + (Ypos*P_CHIP_SIZE), IMGIDX_CHIP,
                           16, 40, P_CHIP_SIZE,P_CHIP_SIZE )
                elif Ypos == chip_cnt_h-1: #下端
                    px.blt(self.P_x + (Xpos*P_CHIP_SIZE), self.P_y + self.P_height - P_CHIP_SIZE, IMGIDX_CHIP,
                           24, 48, P_CHIP_SIZE,P_CHIP_SIZE )
                elif Xpos == chip_cnt_w-1: #右端
                    px.blt(self.P_x + self.P_width - P_CHIP_SIZE, self.P_y + (Ypos*P_CHIP_SIZE), IMGIDX_CHIP,
                           24, 40, P_CHIP_SIZE,P_CHIP_SIZE )
                #塗りつぶし
                else:
                    pass
                    px.blt(self.P_x + (Xpos*P_CHIP_SIZE), self.P_y + (Ypos*P_CHIP_SIZE), IMGIDX_CHIP,
                           32, 40, P_CHIP_SIZE,P_CHIP_SIZE )


    def drawText(self, x:int, y:int, txt:list, fnt=JP_FONT):
        for i in range(len(txt)):
            px.text(x, y + i * (10+2), txt[i], 7, font=JP_FONT)
        return
    

#****#****#****#****#**** Message #****#****#****#****#****
class Message:
    def __init__(self, x:int, y:int, txt:list=["...",]):
        self.P_x = x
        self.P_y = y
        self.msg = txt


#****#****#****#****#**** Menu #****#****#****#****#****
class Menu:
    rofs    = 4 #文字出力 行間(pixel)
    fw,fh   = 8, 8 #フォント幅高
    rowpad  = 2 #オブジェクト上下間調整
    def __init__(self, x:int, y:int, ishape:list, items:list, ilen:int=6, typ:int=0, parent=None):
        self.Parent     = parent    
        self.items      = items     #メニュー項目文字列
        self.wndSize    = ishape    #メニュー項目個数　横,縦
        self.sMnuLen    = ilen      #メニュー項目文字長
        self.mnuType    = typ       #メニュー種別 0:フィールドメニュー 1:バトルメニュー 2:商店 3:タイトル 4:名前入力
        self.posCursor  = [0,0]     #メニューカーソル選択位置
        self.P_adrCursor= [0,0]     #メニューカーソル描画アドレス
        self.selMnu     = ""        #選択メニューの文字列
        wndWidth        = -(-(P_CHIP_SIZE + (P_CHIP_SIZE*self.wndSize[0]) + (self.wndSize[0]*P_CHIP_SIZE) +(self.wndSize[0]*self.sMnuLen*self.fw) + P_CHIP_SIZE )
                            // P_CHIP_SIZE ) * P_CHIP_SIZE #- P_CHIP_SIZE #左枠線+(カーソルｘ横項目数)+(横項目数ｘ項目間余白)+(項目数x文字数xフォントサイズ)+右枠線+1(予備)
        wndHeight       = -(-(P_CHIP_SIZE + (self.wndSize[1]*self.rofs) + (self.wndSize[1]*1*self.fh) + P_CHIP_SIZE)
                            // P_CHIP_SIZE ) * P_CHIP_SIZE #- P_CHIP_SIZE  #上枠線+(縦項目数ｘ項目間余白)+(縦項目数x１項目行数xフォントサイズ)+最終行余白+下枠線+1(予備)
        if (x + wndWidth) > px.width:
            x = px.width - wndWidth
        self.insMnuWnd  = Window(x, y, wndWidth, wndHeight, 2)
        self.insSubMnu  = ""
        self.flgSubMnu  = False
        self.insMsgWnd  = ""
        self.flgMsgWnd  = False
        self.answerYN   = 0 #MenuYesNoからのリターン
        self.insCmd     = None
        self.flgCmd     = False
        self.Msg        = ""
        self.closeMe    = False


    def chkCmdRtn(self):
        flgTmp = self.insCmd.update()
        if flgTmp is not None:
            self.flgCmd = False
            if isinstance(self.Parent, Menu):
                self.Parent.closeMe = True
            return False
        return True

    def update(self):
        if self.closeMe:
            if isinstance(self.Parent, Menu):
                self.Parent.closeMe = True
            return False

        if self.flgCmd:
            return self.chkCmdRtn()
       
        #サブメニュー表示中
        if self.flgSubMnu:
            self.flgSubMnu = self.insSubMnu.update()
            return True
        if self.flgMsgWnd:
            self.flgMsgWnd = self.insMsgWnd.update()
            return True

        # if True:
        #キャンセル
        if px.btnp(px.KEY_X, 10, 5) or px.btnp(px.GAMEPAD1_BUTTON_B, 10, 5) or px.btnp(px.KEY_SPACE, 10, 5):
            px.flip()
            return False
        #決定
        if px.btnp(px.KEY_Z, 10, 5) or px.btnp(px.GAMEPAD1_BUTTON_A, 10, 5) or px.btnp(px.KEY_RETURN, 10, 5):
            px.flip()
            px.play(3,SNDEFX["pi"], resume=True)

            self.selMnu = self.items[self.posCursor[1] % self.wndSize[1]] [self.posCursor[0] % self.wndSize[0]]
#デバッグ用
            if IS_DEBUG:
                print([self.posCursor[1] % self.wndSize[1]], [self.posCursor[0] % self.wndSize[0]], self.selMnu)
            P_x,P_y = self.P_adrCursor[0], self.P_adrCursor[1] + P_CHIP_SIZE + self.rowpad
            match self.mnuType:
                #フィールドメニュー
                case 0:
                    match self.selMnu:
                        #フィールドメニュー一階層
                        case "ステータス":
                            self.insCmd = cmdStatus(P_x, P_y)
                            self.flgCmd = True  
                        case "まほう":
                            menuitem = []
                            for i in range(len(OBJ_CHAR_LIST[0].magic)):
                                menuitem.append([ str(MAGICS[ OBJ_CHAR_LIST[0].magic[i] ][0]).ljust(10,"　")+ str(MAGICS[OBJ_CHAR_LIST[0].magic[i]][1]).translate(h2z) ])

                            if len(menuitem) == 0:
                                self.Msg = ["まほうを　おぼえていない"]
                                self.insMsgWnd = Window(P_x, P_y, P_CHIP_SIZE*15, P_CHIP_SIZE*3, 1)
                                self.flgMsgWnd = True
                            else:
                                self.insSubMnu = Menu(P_x, P_y, [1,len(menuitem)], menuitem, 13, 0, self)
                                self.flgSubMnu = True
                        case "アイテム":
                            menuitem = []
                            for i in range(len(OBJ_CHAR_LIST[0].Item)):
                                if OBJ_CHAR_LIST[0].Item[i][1] > 0:
                                    menuitem.append([ str(ITEMS[OBJ_CHAR_LIST[0].Item[i][0]][0]).ljust(10,"　")+ str(OBJ_CHAR_LIST[0].Item[i][1]).translate(h2z) ])

                            if len(menuitem) == 0:
                                self.Msg = ["なにも　もっていない"]
                                self.insMsgWnd = Window(P_x, P_y, P_CHIP_SIZE*13, P_CHIP_SIZE*3, 1)
                                self.flgMsgWnd = True
                            else:
                                self.insSubMnu = Menu(P_x, P_y, [1,len(menuitem)], menuitem, 13, 0, self)
                                self.flgSubMnu = True
                        case "システム":
                            self.insSubMnu = Menu(P_x, P_y, [1,3], [["セーブ"],["ロード"],["しゅうりょう"]], 6, 0, self)
                            self.flgSubMnu = True

                        #フィールドメニュー二階層（システム）
                        case "セーブ":
                            self.insCmd = cmdSave()
                            self.insSubMnu = MenuYesNo(P_x, P_y, ["じょうたいを　ほぞんしますか？"], self.insCmd, self)
                            self.flgSubMnu = True
                        case "ロード":
                            self.insCmd = cmdLoad()
                            self.insSubMnu = MenuYesNo(P_x, P_y, ["じょうたいを　よびだしますか？"], self.insCmd, self)
                            self.flgSubMnu = True
                        case "しゅうりょう":
                            self.insCmd = cmdQuit()
                            self.insSubMnu = MenuYesNo(P_x, P_y, ["ゲームを　しゅうりょうします"], self.insCmd, self)
                            self.flgSubMnu = True

                        #アイテム・魔法使用
                        case _:
                            itemname = str(self.selMnu).split("　")
                            if itemname[0] == ITEMS[0][0]: #["くすりのくさ",0],
                                self.insCmd = cmdHPherb(P_x, P_y)
                                self.flgCmd = True  
                            elif itemname[0] == ITEMS[1][0]: #["まほうのくさ",1],
                                self.insCmd = cmdMPherb(P_x, P_y)
                                self.flgCmd = True  
                            elif itemname[0] == ITEMS[2][0]: #["おおきなうろこ",2],
                                self.insCmd = cmdScale(P_x, P_y, self.mnuType)
                                self.flgCmd = True  
                            elif itemname[0] == ITEMS[3][0]: #["ランタン",3],
                                self.insCmd = cmdLantern(P_x, P_y, self.mnuType)
                                self.flgCmd = True  
                            elif itemname[0] == ITEMS[4][0]: #["ばんのうかぎ",4],
                                self.insCmd = cmdKeys(P_x, P_y)
                                self.flgCmd = True  
                            elif itemname[0] == ITEMS[5][0]: #["オリハルコイル",5],
                                self.insCmd = cmdOriCoil(P_x, P_y)
                                self.flgCmd = True  
                            elif itemname[0] == ITEMS[6][0]: #["まりょくでんち",6],
                                self.insCmd = cmdMagBattery(P_x, P_y)
                                self.flgCmd = True  
                            elif itemname[0] == ITEMS[7][0]: #["たいようのかぜ",7],
                                self.insCmd = cmdSolarWind(P_x, P_y)
                                self.flgCmd = True  
                            elif itemname[0] == ITEMS[8][0]: #["オーロラベール",8],
                                self.insCmd = cmdAuroraBail(P_x, P_y, self.mnuType)
                                self.flgCmd = True  
                            elif itemname[0] == ITEMS[9][0]: #["ゆうきのあかし",9]
                                self.insCmd = cmdBraveHeart(P_x, P_y)
                                self.flgCmd = True  
                            elif itemname[0] == MAGICS[0][0]: # "ヒール"
                                self.insCmd = cmdHeal(P_x, P_y, OBJ_CHAR_LIST[0], self.mnuType)
                                self.flgCmd = True  
                            elif itemname[0] == MAGICS[1][0]: # "マジックアロー"
                                self.insCmd = cmdMagicArrow(P_x, P_y, self.mnuType)
                                self.flgCmd = True  
                            elif itemname[0] == MAGICS[3][0]: # "リターン"
                                self.insCmd = cmdReturn(P_x, P_y, self.mnuType)
                                self.flgCmd = True  
                            elif itemname[0] == MAGICS[2][0]: # "サンクチュアリ"
                                self.insCmd = cmdSanctuary(P_x, P_y, self.mnuType)
                                self.flgCmd = True  
                            elif itemname[0] == MAGICS[4][0]: # "グレートヒール"
                                self.insCmd = cmdGreatHeal(P_x, P_y, OBJ_CHAR_LIST[0], self.mnuType)
                                self.flgCmd = True  
                            elif itemname[0] == MAGICS[5][0]: # "エクスプロード"
                                self.insCmd = cmdExprode(P_x, P_y, self.mnuType)
                                self.flgCmd = True
                    return True
                #戦闘メニュー
                case 1:
                    return self.menuBattle(P_x, P_y)
                #商店メニュー
                case 2:
                    return self.menuShop()
                #タイトルメニュー
                case 3:
                    return self.menuTitle()
                #名前入力メニュー
                case 4:
                    return self.menuNameEntry()
                case _:
                    raise SystemError

            return True
        
        self.moveCursor()

        return True


    def moveCursor(self):
        if px.btnp(px.KEY_W, 10, 5) or px.btnp(px.GAMEPAD1_BUTTON_DPAD_UP, 10, 5) or px.btnp(px.KEY_UP, 10, 5):
            px.flip()
            self.posCursor[1] -= 1
        if px.btnp(px.KEY_A, 10, 5) or px.btnp(px.GAMEPAD1_BUTTON_DPAD_LEFT, 10, 5) or px.btnp(px.KEY_LEFT, 10, 5):
            px.flip()
            self.posCursor[0] -= 1
        if px.btnp(px.KEY_S, 10, 5) or px.btnp(px.GAMEPAD1_BUTTON_DPAD_DOWN, 10, 5) or px.btnp(px.KEY_DOWN, 10, 5):
            px.flip()
            self.posCursor[1] += 1
        if px.btnp(px.KEY_D, 10, 5) or px.btnp(px.GAMEPAD1_BUTTON_DPAD_RIGHT, 10, 5) or px.btnp(px.KEY_RIGHT, 10, 5):
            px.flip()
            self.posCursor[0] += 1        


    def draw(self):
        self.drawMenu()

        if self.flgCmd:
            self.insCmd.draw(self.P_adrCursor)

        if self.flgSubMnu:
            self.insSubMnu.draw()

        if self.flgMsgWnd:
            self.insMsgWnd.draw()
            self.insMsgWnd.drawText(self.P_adrCursor[0] +8 ,self.P_adrCursor[1] + 16, self.Msg, JP_FONT)


    def drawMenu(self):
        #メニューウインドウ枠表示
        self.insMnuWnd.draw()
        #メニュー項目文字表示
        for r in range(self.wndSize[1]):
            for c in range(self.wndSize[0]):
                px.text(self.insMnuWnd.P_x + P_CHIP_SIZE + (P_CHIP_SIZE*(c+1)) + (c*P_CHIP_SIZE) + (c*self.sMnuLen*self.fw),
                        self.insMnuWnd.P_y + P_CHIP_SIZE + self.rofs//2 + (r*self.rofs) + (r*1*self.fh),
                        self.items[r][c], 7, JP_FONT)
        #メニューカーソル表示
        cursorOffset = self.posCursor[0] % self.wndSize[0], self.posCursor[1] % self.wndSize[1]
        self.P_adrCursor = [self.insMnuWnd.P_x + P_CHIP_SIZE + (P_CHIP_SIZE*(cursorOffset[0]+1)-P_CHIP_SIZE) + (cursorOffset[0]*P_CHIP_SIZE) + (cursorOffset[0]*self.sMnuLen*self.fw),
                            self.insMnuWnd.P_y + P_CHIP_SIZE + self.rofs//2  + (cursorOffset[1]*self.rofs) + (cursorOffset[1]*1*self.fh) ] #+ 2 ]
        px.blt(self.P_adrCursor[0], self.P_adrCursor[1], IMGIDX_CHIP, 0,56, P_CHIP_SIZE,P_CHIP_SIZE, colkey=0)


    #オーバーライド用
    def menuBattle(self):
        pass
    def menuShop(self):
        pass
    def menuTitle(self):
        pass
    def menuNameEntry(self):
        pass


#****#****#****#****#**** MenuYesNo #****#****#****#****#****
class MenuTitle(Menu):
    def __init__(self, Parent):
        super().__init__(px.width//4, px.height - px.height//3,[1,2],[["あたらしい　ぼうけん"],["ぼうけんの　つづき"]],13, 0)
        self.insCmd     = cmdLoad()
        self.Parent = Parent
        self.flgNewGame = False
        self.cnt = 1
        self.flgFin = False

    def update(self):
        if self.flgCmd:
            return self.chkCmdRtn()
        
        if self.flgFin == False:
            if px.btnp(px.KEY_Z, 10, 5) or px.btnp(px.GAMEPAD1_BUTTON_A, 10, 5) or px.btnp(px.KEY_RETURN, 10, 5):
                px.flip()
                px.play(3,SNDEFX["pi"], resume=True)
                match self.posCursor[1] % self.wndSize[1]:
                    case 0:
                        self.flgFin = self.flgNewGame = True
                        return True
                    case 1:
                        self.insCmd.exec()
                        if self.insCmd.flgNoPath:
                            self.flgFin = self.flgCmd = True
                            return False
                        else:
                            self.Parent.now_scene = SCENE_STATUS["Field"]
                            self.Parent.music = reloadBGM(self.Parent.now_scene)
                            self.flgFin = self.flgCmd = True
                            return True
                return True

        if px.btnp(px.KEY_X, 10, 5) or px.btnp(px.GAMEPAD1_BUTTON_B, 10, 5) or px.btnp(px.KEY_SPACE, 10, 5):
            px.flip()
            return False

        self.moveCursor()

        return None


    def draw(self):
        if self.flgNewGame:
            if self.cnt > 0:
                px.dither(self.cnt)
                self.cnt -= 0.04
            else:
               self.Parent.flgMenu = False
               px.dither(1)
               self.Parent.now_scene = SCENE_STATUS["NameEntry"]
            return 

        if self.flgCmd:
            self.insCmd.draw()
            if self.insCmd.flgNoPath:
                self.flgNewGame = False
                self.cnt = 1
                self.flgFin = False
                return False
            else:
            # self.insCmd.draw()
                self.Parent.now_scene = SCENE_STATUS["Field"]
        else:
            self.drawMenu()


#****#****#****#****#**** BattleMenu #****#****#****#****#****
class MenuShop(Menu):
    def __init__(self, x, y, insWnd, shoptype=0):
        menuitem = []
        match shoptype:
            case 0:
                for i in range(5):
                    menuitem.append([ str(ITEMS[i][0]).ljust(10,"　")+ str(ITEMS[i][1]).translate(h2z) ])
                for i in range(1,len(WEAPONS)-1):
                    menuitem.append([ str(WEAPONS[i][0]).ljust(10,"　")+ str(WEAPONS[i][2]).translate(h2z) ])
                for i in range(1,len(ARMORS)-1):
                    menuitem.append([ str(ARMORS[i][0]).ljust(10,"　")+ str(ARMORS[i][2]).translate(h2z) ])
                for i in range(1,len(SHIELDS)-2):
                    menuitem.append([ str(SHIELDS[i][0]).ljust(10,"　")+ str(SHIELDS[i][2]).translate(h2z) ])
            case 1:
                menuitem.append([ str(SHIELDS[3][0]).ljust(10,"　")+ str(SHIELDS[3][2]).translate(h2z) ])

        super().__init__(insWnd.P_x + 8, insWnd.P_y + 16, [1,len(menuitem)], menuitem, 18, 2)
        self.insMsgWnd = insWnd
        self.insGpWnd = Window(px.width - P_CHIP_SIZE*13, px.height - P_CHIP_SIZE*3, P_CHIP_SIZE*13,P_CHIP_SIZE*3, 3)


    def menuShop(self):
        itemname = str(self.selMnu).split("　")
        self.Msg = [itemname[0]+"をかうんだね","","そいつのねだんは　"+itemname[len(itemname)-1]+"　だ"]
        self.insCmd = cmdBuy(self.insMsgWnd.P_x, self.insMsgWnd.P_y, self.insMsgWnd, itemname)
        self.insSubMnu = MenuYesNo(self.insMsgWnd.P_x +16, self.insMsgWnd.P_y +P_CHIP_SIZE*7, ["かいますか？"], self.insCmd, self)
        self.flgSubMnu = True

        return True


    def draw(self):
        self.drawMenu()
        self.insGpWnd.draw()
        self.insGpWnd.drawText(self.insGpWnd.P_x+P_CHIP_SIZE,self.insGpWnd.P_y+P_CHIP_SIZE, ["しょじきん："+str(OBJ_CHAR_LIST[0].st.gp).translate(h2z)], JP_FONT)

        if self.flgSubMnu:
            self.insMsgWnd.draw()
            self.insMsgWnd.drawText(self.insMsgWnd.P_x + 8  ,self.insMsgWnd.P_y + 16, self.Msg, JP_FONT)
            self.insSubMnu.draw()


#****#****#****#****#**** MenuYesNo #****#****#****#****#****
class MenuNameEntry(Menu):
    def __init__(self, Parent):
        super().__init__(px.width//2 -96 ,8, [11,9],  NAME_CHARS[0], 0, 4)
        self.prefix     = "なまえ　：　"
        self.InputName  = ""
        self.insMsgWnd  = Window(px.width//2 - (P_CHIP_SIZE*17)//2, px.height//1.5, P_CHIP_SIZE*17, P_CHIP_SIZE*5, 0)
        self.txtMsg     = Message(self.insMsgWnd.P_x+P_CHIP_SIZE, self.insMsgWnd.P_y+P_CHIP_SIZE*2, [self.prefix + self.InputName])
        self.insCmd     = cmd

        self.flgMsgWnd2 = False
        self.Parent = Parent

    def update(self):
        if self.flgMsgWnd2:
            self.flgMsgWnd2 = self.insMsgWnd2.update()
            return True
        
        if self.flgCmd:
            return self.chkCmdRtn()
    
        if px.btnp(px.KEY_Z, 10, 5) or px.btnp(px.GAMEPAD1_BUTTON_A, 10, 5) or px.btnp(px.KEY_RETURN, 10, 5):
            px.flip()
            px.play(3,SNDEFX["pi"], resume=True)
            self.selMnu = self.items[self.posCursor[1] % self.wndSize[1]] [self.posCursor[0] % self.wndSize[0]]
#デバッグ用
            if IS_DEBUG:
                print([self.posCursor[1] % self.wndSize[1]], [self.posCursor[0] % self.wndSize[0]], self.selMnu)
            match self.selMnu:
                case "ED":
                    if len(self.InputName) <= 0:
                        self.insMsgWnd2 = Window(16,16,px.width - (P_BLOCK_SIZE*2),104, 1)
                        self.flgMsgWnd2 = True
                        self.Msg2 = ["なまえが　にゅうりょく　されていません"]
                        return True
                    else:
                        reloadGameStatus()
                        OBJ_CHAR_LIST[0].name = self.InputName
                        return False

                case "ｶﾅ":
                    self.items = NAME_CHARS[1]
                    return True
                case "Aa":
                    self.items = NAME_CHARS[2]
                    return True
                case "平":
                    self.items = NAME_CHARS[0]
                    return True

            tmpStr = self.InputName + self.selMnu
            if len(tmpStr) > 8:
                self.insMsgWnd2 = Window(16,16,px.width - (P_BLOCK_SIZE*2),104, 1)
                self.flgMsgWnd2 = True
                self.Msg2 = ["なまえは　８もじ　まで"]
                px.play(3, SNDEFX["don"], resume=True)
                return True
            else:
                self.InputName += self.selMnu

        if px.btnp(px.KEY_X, 10, 5) or px.btnp(px.GAMEPAD1_BUTTON_B, 10, 5) or px.btnp(px.KEY_SPACE, 10, 5):
            px.flip()
            tmpStr = self.InputName[:-1]
            self.InputName = tmpStr
            return True

        
        self.txtMsg.msg = [self.prefix + self.InputName]
        
        self.moveCursor()
        return True


    def draw(self):
        if self.flgCmd:
            self.insCmd.draw()
        else:
            self.drawMenu()
            self.insMsgWnd.draw()
            self.insMsgWnd.drawText(self.txtMsg.P_x, self.txtMsg.P_y, self.txtMsg.msg)
            if self.flgMsgWnd2:
                self.insMsgWnd2.draw()
                self.insMsgWnd2.drawText(self.insMsgWnd2.P_x + 
                                         ( self.insMsgWnd2.P_width//2 - (P_CHIP_SIZE*len(self.Msg2[0]))//2 ),
                                         self.insMsgWnd2.P_height//2, self.Msg2)


#****#****#****#****#**** MenuYesNo #****#****#****#****#****
class MenuYesNo(Menu):
    def __init__(self, x, y, msg:list, cmd, Parent):
        super().__init__(x + P_CHIP_SIZE*2, y + P_CHIP_SIZE*2 + self.rowpad, [1,2],  [["はい"],["いいえ"]], 4, 3)
        if x + P_CHIP_SIZE*17 > px.width:
            x = px.width - P_CHIP_SIZE*17
        self.insMsgWnd  = Window(x, y, P_CHIP_SIZE*17, P_CHIP_SIZE*2+P_CHIP_SIZE, 0)
        self.txtMsg     = Message(x+P_CHIP_SIZE, y+P_CHIP_SIZE, msg)
        self.insCmd     = cmd
        self.answerYN   = 0 # 0:Yes 1:No
        self.Parent = Parent

    def update(self):
        if self.flgCmd:
            return self.chkCmdRtn()
        
        if px.btnp(px.KEY_Z, 10, 5) or px.btnp(px.GAMEPAD1_BUTTON_A, 10, 5) or px.btnp(px.KEY_RETURN, 10, 5):
            px.flip()
            px.play(3,SNDEFX["pi"], resume=True)
            match self.posCursor[1] % self.wndSize[1]:
                case 0:
                    self.insCmd.exec()
                    self.flgCmd = True
                case 1:
                    return False
            return True
            
        if px.btnp(px.KEY_X, 10, 5) or px.btnp(px.GAMEPAD1_BUTTON_B, 10, 5) or px.btnp(px.KEY_SPACE, 10, 5):
            px.flip()
            if self.flgCmd:
                return True
            else:
                return False

        self.moveCursor()
        return True


    def draw(self):
        if self.flgCmd:
            self.insCmd.draw()
        else:
            self.drawMenu()
            self.insMsgWnd.draw()
            self.insMsgWnd.drawText(self.txtMsg.P_x, self.txtMsg.P_y, self.txtMsg.msg)


#****#****#****#****#**** cmdFunc #****#****#****#****#****
class cmd:
    def __init__(self, x=0, y=0):
        self.insMsgWnd  = None
        self.drawData   = None
        self.flgFin     = False
        self.flgDispFin = False
        self.msg        = []
    def keycheck(self):
        if px.btnp(px.KEY_Z, 10, 5) or px.btnp(px.GAMEPAD1_BUTTON_A, 10, 5) or px.btnp(px.KEY_RETURN, 10, 5):
            px.flip()
            px.play(3,SNDEFX["pi"], resume=True)
            return True
        if px.btnp(px.KEY_X, 10, 5) or px.btnp(px.GAMEPAD1_BUTTON_B, 10, 5) or px.btnp(px.KEY_SPACE, 10, 5):
            px.flip()
            return False
        return None
    def update(self):
        self.flgFin = True
        return self.keycheck()
    def draw(self):
        raise NotImplementedError
    def exec(self):
        raise NotImplementedError

#****#****#****#****#**** ->cmdFunc #****#****#****#****#****
class cmdStatus(cmd):
    def __init__(self, x, y):
        super().__init__(self)
        self.insMsgWnd = Window(x, y, P_CHIP_SIZE*17,P_CHIP_SIZE*24,0)
    def update(self):
        if not self.flgFin:
            self.drawData = [OBJ_CHAR_LIST[0].name,
                "レベル　　　："+str(OBJ_CHAR_LIST[0].lvl).translate(h2z),
                "さいだいＨＰ："+str(OBJ_CHAR_LIST[0].st.MHP).translate(h2z),
                "げんざいＨＰ："+str(OBJ_CHAR_LIST[0].st.HP ).translate(h2z),
                "さいだいＭＰ："+str(OBJ_CHAR_LIST[0].st.MMP).translate(h2z),
                "げんざいＭＰ："+str(OBJ_CHAR_LIST[0].st.MP ).translate(h2z),
                "こうげき　　："+str(OBJ_CHAR_LIST[0].st.ATK).translate(h2z),
                "ぼうぎょ　　："+str(OBJ_CHAR_LIST[0].st.DEF).translate(h2z),
                "すばやさ　　："+str(OBJ_CHAR_LIST[0].st.SPD).translate(h2z),
                "ていこう　　："+str(OBJ_CHAR_LIST[0].st.MGR).translate(h2z),
                "けいけんち　："+str(OBJ_CHAR_LIST[0].st.xp).translate(h2z),
                "おかね　　　："+str(OBJ_CHAR_LIST[0].st.gp).translate(h2z),
                "ぶき　　　　："+WEAPONS[OBJ_CHAR_LIST[0].eq[0]][0],
                "よろい　　　："+ARMORS[OBJ_CHAR_LIST[0].eq[1]][0],
                "たて　　　　："+SHIELDS[OBJ_CHAR_LIST[0].eq[2]][0]
                ]
            self.flgFin = True
        return self.keycheck()
    def draw(self, P_adrCursor):
        if self.flgFin:
            self.insMsgWnd.draw()
            self.insMsgWnd.drawText(P_adrCursor[0] +8 ,P_adrCursor[1] + 16, self.drawData, JP_FONT)

#****#****#****#****#**** ->cmdFunc #****#****#****#****#****
class cmdHeal(cmd):
    def __init__(self, x, y, Caster, mnuType, insW = None):
        super().__init__(self)
        if isinstance(insW,Window):
            self.insMsgWnd=insW
        else:
            self.insMsgWnd = Window(x, y, P_CHIP_SIZE*24,P_CHIP_SIZE*5,0)
        self.insCaster  = Caster
        self.mnuType    = mnuType
        self.Spell = MAGICS[0]

    def update(self):
        if not self.flgFin:
            if self.Spell[1] > self.insCaster.st.MP:
                self.flgFin = True
                self.msg = ["ＭＰが　たりない！"]
                px.play(3, SNDEFX["miss"], resume=True)
                return None

            self.drawData = px.rndi(13,19)+ self.insCaster.st.MHP//16
            if self.insCaster.st.HP + self.drawData >= self.insCaster.st.MHP:
                self.drawData = self.insCaster.st.MHP - self.insCaster.st.HP
            self.insCaster.st.HP += self.drawData
            self.insCaster.st.MP -= self.Spell[1]
            if self.mnuType == 0:
                self.msg = [self.Spell[0]+"！　ＨＰが"+str(self.drawData).translate(h2z)+"かいふくした"]
            else:
                self.msg = [self.insCaster.name+"　の　"+self.Spell[0]+"！","","　ＨＰが"+str(self.drawData).translate(h2z)+"かいふくした"]
            px.play(3, SNDEFX["spell"], resume=True)
            self.flgFin = True

        if self.keycheck() != None:
            return True
        return None

    def draw(self, P_adrCursor):
        if self.flgFin:
            self.insMsgWnd.draw()
            self.insMsgWnd.drawText(self.insMsgWnd.P_x +16 ,self.insMsgWnd.P_y + 16, self.msg, JP_FONT)
            self.flgDispFin = True


#****#****#****#****#**** ->cmdFunc #****#****#****#****#****
class cmdMagicArrow(cmd):
    def __init__(self, x, y, mnuType, iOfs=None, iDfs=None, insW=None):
        super().__init__(self)
        self.Spell = MAGICS[1]
        
        if isinstance(insW,Window):
            self.insMsgWnd=insW
        else:
            self.insMsgWnd = Window(x, y, P_CHIP_SIZE*25,P_CHIP_SIZE*5,0)

        if mnuType == 0:
            self.msg = [self.Spell[0]+"は　ここでは　つかえない"]
            px.play(3, SNDEFX["miss"], resume=True)
            self.flgFin = True
            self.flgDispFin = True
        else:
            self.insCaster = iOfs
            self.insTarget = iDfs

    def update(self):
        if not self.flgFin:
            if self.Spell[1] > self.insCaster.st.MP:
                self.flgFin = True
                self.msg = ["ＭＰが　たりない！"]
                px.play(3, SNDEFX["miss"], resume=True)
                return None
        
            self.drawData = max(0, int( (9 + px.rndi(-2,5) + ( self.insCaster.st.MP / 8 )) * ( 1 - (self.insTarget.st.MGR / 100) ) ))
            if isinstance(self.insTarget, Character):
                if OBJ_CHAR_LIST[0].eq[2] == 3:
                    self.drawData //= 2
            self.insTarget.st.HP -= self.drawData
            self.insCaster.st.MP -= self.Spell[1]
            self.msg = [self.insCaster.name+"　の　"+self.Spell[0]+"！","","　" + self.insTarget.name + "に " + str(self.drawData).translate(h2z)+"の　ダメージを　あたえた"]
            px.play(3, [SNDEFX["spell"],SNDEFX["attack1"]], resume=True)
            self.flgFin = True

        if self.keycheck() != None:
            return True
        return None

    def draw(self, P_adrCursor):
        if self.flgFin:
            self.insMsgWnd.draw()
            self.insMsgWnd.drawText(self.insMsgWnd.P_x +16 ,self.insMsgWnd.P_y + 16, self.msg, JP_FONT)
            self.flgDispFin = True


#****#****#****#****#**** ->cmdFunc #****#****#****#****#****
class cmdReturn(cmd):
    def __init__(self, x, y, mnuType, insW = None):
        super().__init__(self)
        
        if isinstance(insW,Window):
            self.insMsgWnd=insW
        else:
            self.insMsgWnd = Window(x, y, P_CHIP_SIZE*25,P_CHIP_SIZE*5,0)

        if mnuType == 1:
            self.msg = [MAGICS[3][0]+"は　ここでは　つかえない"]
            px.play(3, SNDEFX["miss"], resume=True)
            self.flgFin = True
            self.flgDispFin = True

    def update(self):
        if not self.flgFin:
            if MAGICS[3][1] > OBJ_CHAR_LIST[0].st.MP:
                self.flgFin = True
                self.msg = ["ＭＰが　たりない！"]
                px.play(3, SNDEFX["miss"], resume=True)
            else:
                OBJ_CHAR_LIST[0].flgWarp = [ True, [125,163] ]
                OBJ_CHAR_LIST[0].now_dir = 0

                OBJ_CHAR_LIST[0].st.MP -= MAGICS[3][1]
                self.msg = ["まちまで　ひとっとび！"]
                px.play(3, SNDEFX["spell"], resume=True)
                self.flgFin = True

        if self.keycheck() != None:
            return True
        return None

    def draw(self, P_adrCursor):
        if self.flgFin:
            self.insMsgWnd.draw()
            self.insMsgWnd.drawText(self.insMsgWnd.P_x +16 ,self.insMsgWnd.P_y + 16, self.msg, JP_FONT)
            self.flgDispFin = True


#****#****#****#****#**** ->cmdFunc #****#****#****#****#****
class cmdSanctuary(cmd):
    def __init__(self, x, y, mnuType, insW = None):
        super().__init__(self)
        
        if isinstance(insW,Window):
            self.insMsgWnd=insW
        else:
            self.insMsgWnd = Window(x, y, P_CHIP_SIZE*25,P_CHIP_SIZE*5,0)

        if mnuType == 1:
            self.msg = [MAGICS[2][0]+"は　ここでは　つかえない"]
            px.play(3, SNDEFX["miss"], resume=True)
            self.flgFin = True
            self.flgDispFin = True

    def update(self):
        if not self.flgFin:
            if MAGICS[2][1] > OBJ_CHAR_LIST[0].st.MP:
                self.flgFin = True
                self.msg = ["ＭＰが　たりない！"]
                px.play(3, SNDEFX["miss"], resume=True)
            else:
                OBJ_CHAR_LIST[0].sanctuaryCount = 350
                OBJ_CHAR_LIST[0].flgSanctuary = False
                OBJ_CHAR_LIST[0].st.MP -= MAGICS[2][1]
                self.msg = ["まもののけはいが　とおざかった"]
                px.play(3, SNDEFX["spell"], resume=True)
                self.flgFin = True

        if self.keycheck() != None:
            return True
        return None

    def draw(self, P_adrCursor):
        if self.flgFin:
            self.insMsgWnd.draw()
            self.insMsgWnd.drawText(self.insMsgWnd.P_x +16 ,self.insMsgWnd.P_y + 16, self.msg, JP_FONT)
            self.flgDispFin = True

#****#****#****#****#**** ->cmdFunc #****#****#****#****#****
class cmdGreatHeal(cmd):
    def __init__(self, x, y, Caster, mnuType, insW = None):
        super().__init__(self)
        if isinstance(insW,Window):
            self.insMsgWnd=insW
        else:
            self.insMsgWnd = Window(x, y, P_CHIP_SIZE*24,P_CHIP_SIZE*5,0)
        self.insCaster  = Caster
        self.mnuType    = mnuType
        self.Spell = MAGICS[4]

    def update(self):
        if not self.flgFin:
            if self.Spell[1] > self.insCaster.st.MP:
                self.flgFin = True
                self.msg = ["ＭＰが　たりない！"]
                px.play(3, SNDEFX["miss"], resume=True)
                return None

            self.drawData = 100 + px.rndi(-5,10) + self.insCaster.st.MHP//8
            if self.insCaster.st.HP + self.drawData >= self.insCaster.st.MHP:
                self.drawData = self.insCaster.st.MHP - self.insCaster.st.HP
            self.insCaster.st.HP += self.drawData
            self.insCaster.st.MP -= self.Spell[1]
            if self.mnuType == 0:
                self.msg = [self.Spell[0]+"！　ＨＰが"+str(self.drawData).translate(h2z)+"かいふくした"]
            else:
                self.msg = [self.insCaster.name+"　の　"+self.Spell[0]+"！","","　ＨＰが"+str(self.drawData).translate(h2z)+"かいふくした"]
            px.play(3, SNDEFX["spell"], resume=True)
            self.flgFin = True

        if self.keycheck() != None:
            return True
        return None

    def draw(self, P_adrCursor):
        if self.flgFin:
            self.insMsgWnd.draw()
            self.insMsgWnd.drawText(self.insMsgWnd.P_x +16 ,self.insMsgWnd.P_y + 16, self.msg, JP_FONT)
            self.flgDispFin = True


#****#****#****#****#**** ->cmdFunc #****#****#****#****#****
class cmdExprode(cmd):
    def __init__(self, x, y, mnuType, iOfs=None, iDfs=None, insW=None):
        super().__init__(self)
        self.Spell = MAGICS[5]
        
        if isinstance(insW,Window):
            self.insMsgWnd=insW
        else:
            self.insMsgWnd = Window(x, y, P_CHIP_SIZE*25,P_CHIP_SIZE*5,0)

        if mnuType == 0:
            self.msg = [self.Spell[0]+"は　ここでは　つかえない"]
            px.play(3, SNDEFX["miss"], resume=True)
            self.flgFin = True
            self.flgDispFin = True
        else:
            self.insCaster = iOfs
            self.insTarget = iDfs

    def update(self):
        if not self.flgFin:
            if self.Spell[1] > self.insCaster.st.MP:
                self.flgFin = True
                self.msg = ["ＭＰが　たりない！"]
                px.play(3, SNDEFX["miss"], resume=True)
                return None

            self.drawData = max(0, int( (65 + px.rndi(-2,5) + ( self.insCaster.st.MP / 8 )) * ( 1 - (self.insTarget.st.MGR / 100) ) ))
            if isinstance(self.insTarget, Character):
                if OBJ_CHAR_LIST[0].eq[2] == 3:
                    self.drawData //= 2
                if OBJ_CHAR_LIST[0].eq[2] == 5:
                    self.drawData //= 1.25
            self.insTarget.st.HP -= self.drawData
            self.insCaster.st.MP -= self.Spell[1]
            self.msg = [self.insCaster.name+"　の　"+self.Spell[0]+"！","","　"+self.insTarget.name + "に " + str(self.drawData).translate(h2z)+"の　ダメージを　あたえた"]
            px.play(3, [SNDEFX["spell"],SNDEFX["attack2"]], resume=True)
            self.flgFin = True

        if self.keycheck() != None:
            return True
        return None

    def draw(self, P_adrCursor):
        if self.flgFin:
            self.insMsgWnd.draw()
            self.insMsgWnd.drawText(self.insMsgWnd.P_x +16 ,self.insMsgWnd.P_y + 16, self.msg, JP_FONT)
            self.flgDispFin = True


#****#****#****#****#**** ->cmdFunc #****#****#****#****#****
class cmdHPherb(cmd):
    def __init__(self, x, y, insW = None):
        super().__init__(self)
        if isinstance(insW,Window):
            self.insMsgWnd=insW
        else:
            self.insMsgWnd = Window(x, y, P_CHIP_SIZE*25,P_CHIP_SIZE*5,0)
    def update(self):
        if not self.flgFin:
            self.drawData = 17 + px.rndi(OBJ_CHAR_LIST[0].st.MHP//4, OBJ_CHAR_LIST[0].st.MHP//2)
            if OBJ_CHAR_LIST[0].st.HP + self.drawData >= OBJ_CHAR_LIST[0].st.MHP:
                self.drawData = OBJ_CHAR_LIST[0].st.MHP - OBJ_CHAR_LIST[0].st.HP
            OBJ_CHAR_LIST[0].st.HP += self.drawData
            OBJ_CHAR_LIST[0].Item[0][1] -= 1
            px.play(3, SNDEFX["spell"], resume=True)

            self.flgFin = True
        if self.keycheck() != None:
            return True
        return None
    def draw(self, P_adrCursor):
        if self.flgFin:
            msg = ["ＨＰが"+str(self.drawData).translate(h2z)+"かいふくした"]
            self.insMsgWnd.draw()
            self.insMsgWnd.drawText(self.insMsgWnd.P_x +16 ,self.insMsgWnd.P_y + 16, msg, JP_FONT)
            self.flgDispFin = True


#****#****#****#****#**** ->cmdFunc #****#****#****#****#****
class cmdMPherb(cmd):
    def __init__(self, x, y, insW = None):
        super().__init__(self)
        if isinstance(insW,Window):
            self.insMsgWnd=insW
        else:
            self.insMsgWnd = Window(x, y, P_CHIP_SIZE*25,P_CHIP_SIZE*5,0)
    def update(self):
        if not self.flgFin:
            self.drawData = 9 + px.rndi(OBJ_CHAR_LIST[0].st.MHP//6, OBJ_CHAR_LIST[0].st.MHP//3)
            if OBJ_CHAR_LIST[0].st.MP + self.drawData >= OBJ_CHAR_LIST[0].st.MMP:
                self.drawData = OBJ_CHAR_LIST[0].st.MMP - OBJ_CHAR_LIST[0].st.MP
            OBJ_CHAR_LIST[0].st.MP += self.drawData
            OBJ_CHAR_LIST[0].Item[1][1] -= 1
            px.play(3, SNDEFX["spell"], resume=True)

            self.flgFin = True
        if self.keycheck() != None:
            return True
        return None
    def draw(self, P_adrCursor):
        if self.flgFin:
            msg = ["ＭＰが"+str(self.drawData).translate(h2z)+"かいふくした"]
            self.insMsgWnd.draw()
            self.insMsgWnd.drawText(self.insMsgWnd.P_x +16 ,self.insMsgWnd.P_y + 16, msg, JP_FONT)
            self.flgDispFin = True


#****#****#****#****#**** ->cmdFunc #****#****#****#****#****
class cmdScale(cmd):
    def __init__(self, x, y, mnuType, insW = None):
        super().__init__(self)
        
        if isinstance(insW,Window):
            self.insMsgWnd=insW
        else:
            self.insMsgWnd = Window(x, y, P_CHIP_SIZE*25,P_CHIP_SIZE*7,0)

        if mnuType == 1:
            self.msg = [ITEMS[2][0]+"は　ここでは　つかえない"]
            px.play(3, SNDEFX["miss"], resume=True)
            self.flgFin = True
            self.flgDispFin = True

    def update(self):
        if not self.flgFin:
            OBJ_CHAR_LIST[0].st.ATK +=2
            OBJ_CHAR_LIST[0].st.DEF +=2
            OBJ_CHAR_LIST[0].st.SPD +=2
            OBJ_CHAR_LIST[0].st.MGR +=2
            OBJ_CHAR_LIST[0].Item[2][1] -= 1
            self.msg = ["うろこに　やどされた　りゅうのちからが","からだじゅうに　みなぎってきた！！"]
            px.play(3, SNDEFX["Special"], resume=True)
            self.flgFin = True

        if self.keycheck() != None:
            return True
        return None

    def draw(self, P_adrCursor):
        if self.flgFin:
            self.insMsgWnd.draw()
            self.insMsgWnd.drawText(self.insMsgWnd.P_x +16 ,self.insMsgWnd.P_y + 16, self.msg, JP_FONT)
            self.flgDispFin = True

#****#****#****#****#**** ->cmdFunc #****#****#****#****#****
class cmdLantern(cmd):
    def __init__(self, x, y, mnuType, insW = None):
        super().__init__(self)
        
        if isinstance(insW,Window):
            self.insMsgWnd=insW
        else:
            self.insMsgWnd = Window(x, y, P_CHIP_SIZE*25,P_CHIP_SIZE*5,0)

        if mnuType == 1:
            self.msg = [ITEMS[3][0]+"は　ここでは　つかえない"]
            px.play(3, SNDEFX["miss"], resume=True)
            self.flgFin = True
            self.flgDispFin = True


    def update(self):
        if not self.flgFin:
            OBJ_CHAR_LIST[0].LanternCount = 180
            OBJ_CHAR_LIST[0].flgLantern = True
            OBJ_CHAR_LIST[0].Item[3][1] -= 1
            self.msg = ["しゅういが　あかるく　てらしだされた"]
            px.play(3, SNDEFX["damage"],tick=17, resume=True)
            self.flgFin = True

        if self.keycheck() != None:
            return True
        return None

    def draw(self, P_adrCursor):
        if self.flgFin:
            self.insMsgWnd.draw()
            self.insMsgWnd.drawText(self.insMsgWnd.P_x +16 ,self.insMsgWnd.P_y + 16, self.msg, JP_FONT)
            self.flgDispFin = True


#****#****#****#****#**** ->cmdFunc #****#****#****#****#****
class cmdKeys(cmd):
    def __init__(self, x, y):
        self.insMsgWnd = Window(x, y, P_CHIP_SIZE*25,P_CHIP_SIZE*5,0)
        px.play(3, SNDEFX["miss"], resume=True)

    def draw(self, P_adrCursor):
        self.insMsgWnd.draw()
        self.insMsgWnd.drawText(self.insMsgWnd.P_x +16 ,self.insMsgWnd.P_y + 16, [ITEMS[4][0]+"は　ここでは　つかえない"], JP_FONT)
        self.flgDispFin = True
#****#****#****#****#**** ->cmdFunc #****#****#****#****#****
class cmdOriCoil(cmd):
    def __init__(self, x, y):
        self.insMsgWnd = Window(x, y, P_CHIP_SIZE*25,P_CHIP_SIZE*5,0)
        px.play(3, SNDEFX["miss"], resume=True)

    def draw(self, P_adrCursor):
        self.insMsgWnd.draw()
        self.insMsgWnd.drawText(self.insMsgWnd.P_x +16 ,self.insMsgWnd.P_y + 16, [ITEMS[5][0]+"は　ここでは　つかえない"], JP_FONT)
        self.flgDispFin = True
#****#****#****#****#**** ->cmdFunc #****#****#****#****#****
class cmdMagBattery(cmd):
    def __init__(self, x, y):
        self.insMsgWnd = Window(x, y, P_CHIP_SIZE*25,P_CHIP_SIZE*5,0)
        px.play(3, SNDEFX["miss"], resume=True)

    def draw(self, P_adrCursor):
        self.insMsgWnd.draw()
        self.insMsgWnd.drawText(self.insMsgWnd.P_x +16 ,self.insMsgWnd.P_y + 16, [ITEMS[6][0]+"は　ここでは　つかえない"], JP_FONT)
        self.flgDispFin = True
#****#****#****#****#**** ->cmdFunc #****#****#****#****#****
class cmdSolarWind(cmd):
    def __init__(self, x, y):
        self.insMsgWnd = Window(x, y, P_CHIP_SIZE*25,P_CHIP_SIZE*5,0)
        px.play(3, SNDEFX["miss"], resume=True)

    def draw(self, P_adrCursor):
        self.insMsgWnd.draw()
        self.insMsgWnd.drawText(self.insMsgWnd.P_x +16 ,self.insMsgWnd.P_y + 16, [ITEMS[7][0]+"は　ここでは　つかえない"], JP_FONT)
        self.flgDispFin = True
#****#****#****#****#**** ->cmdFunc #****#****#****#****#****
class cmdAuroraBail(cmd):
    def __init__(self, x, y, mnuType, insW = None):
        super().__init__(self)
        
        if isinstance(insW,Window):
            self.insMsgWnd=insW
        else:
            self.insMsgWnd = Window(x, y, P_CHIP_SIZE*25,P_CHIP_SIZE*5,0)

        if mnuType == 1:
            self.msg = [ITEMS[8][0]+"は　ここでは　つかえない"]
            px.play(3, SNDEFX["miss"], resume=True)
            self.flgFin = True
            self.flgDispFin = True

    def update(self):
        if not self.flgFin:
            OBJ_CHAR_LIST[0].flgWarp = [ True, [24,65] ]
            OBJ_CHAR_LIST[0].now_dir = 0
            self.msg = ["まものたちの　ほんきょちへ！"]
            px.play(3, SNDEFX["Special"], resume=True)
            self.flgFin = True

        if self.keycheck() != None:
            return True
        return None

    def draw(self, P_adrCursor):
        if self.flgFin:
            self.insMsgWnd.draw()
            self.insMsgWnd.drawText(self.insMsgWnd.P_x +16 ,self.insMsgWnd.P_y + 16, self.msg, JP_FONT)
            self.flgDispFin = True


#****#****#****#****#**** ->cmdFunc #****#****#****#****#****
class cmdBraveHeart(cmd):
    def __init__(self, x, y):
        self.insMsgWnd = Window(x, y, P_CHIP_SIZE*25,P_CHIP_SIZE*5,0)
        px.play(3, SNDEFX["miss"], resume=True)
    def draw(self, P_adrCursor):
        self.insMsgWnd.draw()
        self.insMsgWnd.drawText(self.insMsgWnd.P_x +16 ,self.insMsgWnd.P_y + 16, [ITEMS[9][0]+"は　ここでは　つかえない"], JP_FONT)
        self.flgDispFin = True


#****#****#****#****#**** ->cmdFunc #****#****#****#****#****
class cmdSave(cmd):
    def __init__(self):
        super().__init__(self)
        self.insMsgWnd = Window(16,88,px.width - (P_BLOCK_SIZE*2),24,1)
        self.GameData = {}

    def exec(self):
        if not self.flgFin:
            self.GameData["name"]		= OBJ_CHAR_LIST[0].name
            self.GameData["B_addr_X"]	= OBJ_CHAR_LIST[0].B_addr[X]
            self.GameData["B_addr_Y"]	= OBJ_CHAR_LIST[0].B_addr[Y]
            self.GameData["lvl"]		= OBJ_CHAR_LIST[0].lvl
            self.GameData["MHP"]		= OBJ_CHAR_LIST[0].st.MHP
            self.GameData["MMP"]		= OBJ_CHAR_LIST[0].st.MMP
            self.GameData["HP"]			= OBJ_CHAR_LIST[0].st.HP
            self.GameData["MP"]			= OBJ_CHAR_LIST[0].st.MP
            self.GameData["ATK"]		= OBJ_CHAR_LIST[0].st.ATK
            self.GameData["DEF"]		= OBJ_CHAR_LIST[0].st.DEF
            self.GameData["SPD"]		= OBJ_CHAR_LIST[0].st.SPD
            self.GameData["MGR"]		= OBJ_CHAR_LIST[0].st.MGR
            self.GameData["EXP"]		= OBJ_CHAR_LIST[0].st.xp
            self.GameData["GP"]			= OBJ_CHAR_LIST[0].st.gp
            self.GameData["ITEMS"]		= OBJ_CHAR_LIST[0].Item
            self.GameData["EQUIP"]		= OBJ_CHAR_LIST[0].eq
            self.GameData["MAGIC"]		= OBJ_CHAR_LIST[0].magic
            self.GameData["flgCoil"]	= EVENT_STAT.get(0)
            self.GameData["flgBattery"]	= EVENT_STAT.get(1)
            self.GameData["flgSolar"]	= EVENT_STAT.get(2)
            self.GameData["flgAurora"]	= EVENT_STAT.get(3)
            self.GameData["flgBrave"]	= EVENT_STAT.get(4)
            self.GameData["_1stGuard"]	= EVENT_STAT.get(5)
            self.GameData["_2ndGuard"]	= EVENT_STAT.get(6)
            self.GameData["_3rdGuard"]	= EVENT_STAT.get(7)
            self.GameData["Boss1kill"]	= EVENT_STAT.get(8)
            self.GameData["Boss2kill"]	= EVENT_STAT.get(9)
#最終ボス戦の情報はセーブしない
            self.GameData["flgDoor1"]	= EVENT_STAT.get(12)
            self.GameData["flgDoor2"]	= EVENT_STAT.get(13)
            self.GameData["flgDoor3"]	= EVENT_STAT.get(14)
            
            jdump = json.dumps(self.GameData, ensure_ascii=False)
            jenc  = jdump.encode("utf-8")
            jsonObj = bytes(b ^ ENCRYPT_KEY[i % len(ENCRYPT_KEY)] for i, b in enumerate(jenc))
            path = px.user_data_dir("moq","OldJRPGlikeEZ")
            with open(path + "savedata.bin", "wb") as f:
                f.write(DATAHEADER + jsonObj)

            self.flgFin=True
    
    def draw(self):
        if self.flgFin:
            self.insMsgWnd.draw()
            self.insMsgWnd.drawText(self.insMsgWnd.P_x + 8 ,self.insMsgWnd.P_y + 8, ["データを　ほぞんしました"], JP_FONT)
            self.flgDispFin = True


#****#****#****#****#**** ->cmdFunc #****#****#****#****#****
class cmdLoad(cmd):
    def __init__(self):
        super().__init__(self)
        self.insMsgWnd = Window(16,88,px.width - (P_BLOCK_SIZE*2),24,1)
        self.GameData  = {}
        self.flgNoPath = False

    def exec(self):
        path = px.user_data_dir("moq","OldJRPGlikeEZ")
        if os.path.isfile(path + "savedata.bin") == False:
            self.flgNoPath = True
            return False

        if not self.flgFin:
            reloadGameStatus() 

            with open(path + "savedata.bin", "rb") as f:
                jsonObj=f.read()

            if not jsonObj.startswith(DATAHEADER):
                raise ValueError("Invalid save data")
            encrypted = jsonObj[4:]
            jenc = bytes(b ^ ENCRYPT_KEY[i % len(ENCRYPT_KEY)] for i, b in enumerate(encrypted))

            jdump = jenc.decode("utf-8")
            self.GameData = json.loads(jdump)

            OBJ_CHAR_LIST[0].name			= self.GameData["name"]
            OBJ_CHAR_LIST[0].B_addr[X]      = self.GameData["B_addr_X"]
            OBJ_CHAR_LIST[0].B_addr[Y]      = self.GameData["B_addr_Y"]
            OBJ_CHAR_LIST[0].lvl            = self.GameData["lvl"]
            OBJ_CHAR_LIST[0].st.MHP         = self.GameData["MHP"]
            OBJ_CHAR_LIST[0].st.MMP         = self.GameData["MMP"]
            OBJ_CHAR_LIST[0].st.HP          = self.GameData["HP"]
            OBJ_CHAR_LIST[0].st.MP          = self.GameData["MP"]
            OBJ_CHAR_LIST[0].st.ATK         = self.GameData["ATK"]
            OBJ_CHAR_LIST[0].st.DEF         = self.GameData["DEF"]
            OBJ_CHAR_LIST[0].st.SPD         = self.GameData["SPD"]		
            OBJ_CHAR_LIST[0].st.MGR         = self.GameData["MGR"]
            OBJ_CHAR_LIST[0].st.xp          = self.GameData["EXP"]
            OBJ_CHAR_LIST[0].st.gp          = self.GameData["GP"]
            OBJ_CHAR_LIST[0].Item           = self.GameData["ITEMS"]
            OBJ_CHAR_LIST[0].eq             = self.GameData["EQUIP"]
            OBJ_CHAR_LIST[0].magic          = self.GameData["MAGIC"]
            EVENT_STAT.set( 0, self.GameData["flgCoil"] )   
            EVENT_STAT.set( 1, self.GameData["flgBattery"] )
            EVENT_STAT.set( 2, self.GameData["flgSolar"] )  
            EVENT_STAT.set( 3, self.GameData["flgAurora"] ) 
            EVENT_STAT.set( 4, self.GameData["flgBrave"] )  
            EVENT_STAT.set( 5, self.GameData["_1stGuard"] ) 
            EVENT_STAT.set( 6, self.GameData["_2ndGuard"] ) 
            EVENT_STAT.set( 7, self.GameData["_3rdGuard"] ) 
            EVENT_STAT.set( 8, self.GameData["Boss1kill"] ) 
            EVENT_STAT.set( 9, self.GameData["Boss2kill"] ) 
#ロード時の最終ボス戦情報は常にFalse         
            EVENT_STAT.set(10, False )             
            EVENT_STAT.set(11, False )             
            EVENT_STAT.set(12, self.GameData["flgDoor1"] )             
            EVENT_STAT.set(13, self.GameData["flgDoor2"] )             
            EVENT_STAT.set(14, self.GameData["flgDoor3"] )             

            self.flgFin=True
    
            return True


    def draw(self):
        if self.flgNoPath:
            self.insMsgWnd.draw()
            self.insMsgWnd.drawText(self.insMsgWnd.P_x + 8 ,self.insMsgWnd.P_y + 8, ["データが　そんざいしません"], JP_FONT)
            self.flgDispFin = True
            return
        if self.flgFin:
            self.insMsgWnd.draw()
            self.insMsgWnd.drawText(self.insMsgWnd.P_x + 8 ,self.insMsgWnd.P_y + 8, ["データを　よびだしました"], JP_FONT)
            self.flgDispFin = True


#****#****#****#****#**** ->cmdFunc #****#****#****#****#****
class cmdQuit(cmd):
    def __init__(self):
        pass
    def exec(self):
        px.quit()


#****#****#****#****#**** ->cmdFunc #****#****#****#****#****
class cmdInn(cmd):
    def __init__(self, x, y, insW = None):
        super().__init__(self)
        if isinstance(insW,Window):
            self.insMsgWnd=insW
        else:
            self.insMsgWnd = Window(x, y, P_CHIP_SIZE*13,P_CHIP_SIZE*5,0)
        self.img = px.Image(px.width, px.height)
        self.img.load(0,0, "assets/Inn.jpg")
        self.cnt = 0
        self.flgPoor = False

    def exec(self):
        fee = int(( ((OBJ_CHAR_LIST[0].lvl ** 2) * 3) - (OBJ_CHAR_LIST[0].lvl * 2) ) / 10 + 1)
        if OBJ_CHAR_LIST[0].st.gp < fee:
            self.msg = ["おかねが　たりないよ！","とっとと　でていきな！"]
            self.flgFin = True
            self.flgPoor = True

        if not self.flgFin:
            OBJ_CHAR_LIST[0].st.HP = OBJ_CHAR_LIST[0].st.MHP
            OBJ_CHAR_LIST[0].st.MP = OBJ_CHAR_LIST[0].st.MMP
            OBJ_CHAR_LIST[0].st.gp -= fee
            self.msg = ["ゆっくりやすんで","ぜんかいだ"]
            self.flgFin = True

        if self.keycheck() != None:
            return True
        return None

    def draw(self):
        px.cls(0)
        if self.flgFin:
            if self.flgPoor == False:
                self.cnt += 48
                px.blt(0,0, self.img, 0,0, px.width, self.cnt, colkey=0)

            self.insMsgWnd.draw()
            self.insMsgWnd.drawText(self.insMsgWnd.P_x +8 ,self.insMsgWnd.P_y + 8, self.msg, JP_FONT)
            if self.cnt == px.height:
                self.flgDispFin = True


#****#****#****#****#**** ->cmdFunc #****#****#****#****#****
class cmdBuy(cmd):
    def __init__(self, x, y, insW, iteminfo):
        super().__init__(self)
        self.insMsgWnd=insW

        self.ItemName = str(iteminfo[0])
        self.ItemPrice= int(iteminfo[len(iteminfo)-1])
        self.flgBuy   = False

    def exec(self):
        if IS_DEBUG == False:
            if OBJ_CHAR_LIST[0].st.gp < self.ItemPrice:
                self.msg = ["なんだい　かねがたりてないよ！","さっさとかえんな！！"]
                self.flgFin = True

        if not self.flgFin:
            for i in range(len(WEAPONS)-1):
                if self.ItemName == WEAPONS[i][0]:
                    StsVal = WEAPONS[i][1] - WEAPONS[OBJ_CHAR_LIST[0].eq[0]][1]
                    OBJ_CHAR_LIST[0].eq[0] = i
                    OBJ_CHAR_LIST[0].st.ATK += StsVal
                    self.flgBuy = True
            for i in range(len(ARMORS)-1):
                if self.ItemName == ARMORS[i][0]:
                    StsVal = ARMORS[i][1] - ARMORS[OBJ_CHAR_LIST[0].eq[1]][1]
                    OBJ_CHAR_LIST[0].eq[1] = i
                    OBJ_CHAR_LIST[0].st.DEF += StsVal
                    self.flgBuy = True
            for i in range(len(SHIELDS)-1):
                if self.ItemName == SHIELDS[i][0]:
                    StsVal = SHIELDS[i][1] - SHIELDS[OBJ_CHAR_LIST[0].eq[2]][1]
                    OBJ_CHAR_LIST[0].eq[2] = i
                    OBJ_CHAR_LIST[0].st.DEF += StsVal
                    self.flgBuy = True
            for i in range(len(ITEMS)-5):
                if self.ItemName == ITEMS[i][0]:
                    for j in range(len(OBJ_CHAR_LIST[0].Item)-1):
                        if OBJ_CHAR_LIST[0].Item[j][0] == i and OBJ_CHAR_LIST[0].Item[j][1] >= 9:
                            self.msg = ["それいじょう　もてないよ"]
                            self.flgFin = True
                            break
                    if self.flgFin == False:
                        getItem(i)
                        self.flgBuy = True

            if self.flgBuy:
                if IS_DEBUG == False:
                    OBJ_CHAR_LIST[0].st.gp -= self.ItemPrice
                self.msg = ["おかいあげ　ありがとう　ございました"]
                self.flgFin = True

        if self.keycheck() != None:
            return True
        
        return None

    def draw(self):
        if self.flgFin:
            self.insMsgWnd.draw()
            self.insMsgWnd.drawText(self.insMsgWnd.P_x +8 ,self.insMsgWnd.P_y + 16, self.msg, JP_FONT)
            self.flgDispFin = True


#****#****#****#****#**** ->cmdFunc #****#****#****#****#****
class cmdAttack(cmd):
    def __init__(self, x, y, iOfs, iDfs, iWnd):
        super().__init__(self)
        self.insMsgWnd = iWnd
        self.Of = iOfs
        self.Df = iDfs
        self.msg = []

    def update(self):
        if not self.flgFin:
            if (self.Of.st.SPD * px.rndi(0,255)) >= (self.Df.st.SPD * px.rndi(0, 62+self.Df.st.SPD )):
                if (self.Of.st.ATK - self.Df.st.DEF/2) >= (self.Of.st.ATK/2 + 1):
                    self.drawData = max(2, int((px.rndi(0,255)*(self.Of.st.ATK - self.Df.st.DEF//2+1)//256 + self.Of.st.ATK - self.Df.st.DEF//2)/4))
                elif (self.Of.st.ATK - self.Df.st.DEF/2) < 0 or (self.Of.st.ATK - self.Df.st.DEF/2) < (self.Of.st.ATK/2 + 1):
                    self.drawData = max(1, int(px.rndi(0,255)*(self.Of.st.ATK - self.Df.st.DEF//2+1)//256 + 0.2))

                self.drawData = -(-self.drawData//1)

                self.Df.st.HP -= self.drawData
                self.msg = [self.Of.name +"　の　こうげき！", "", "　" + str(self.drawData).translate(h2z)+"ポイントの　ダメージ！"]
                px.play(3,SNDEFX["attack2"], resume=True)
            else:
                self.msg = [self.Of.name +"　の　こうげき！", " ","　・・・は　はずれてしまった！！"]
                px.play(3,SNDEFX["miss"], resume=True)

            self.flgFin = True
        return self.keycheck()
    
    def draw(self, P_adrCursor):
        if self.flgFin:
            self.insMsgWnd.draw()
            self.insMsgWnd.drawText(self.insMsgWnd.P_x + P_CHIP_SIZE*2 , self.insMsgWnd.P_y + P_CHIP_SIZE*2 , self.msg, JP_FONT)
            self.flgDispFin = True


#****#****#****#****#**** ->cmdFunc #****#****#****#****#****
class cmdRunaway(cmd):
    def __init__(self, x, y, iOfs, iDfs, iWnd):
        super().__init__(self)
        self.insMsgWnd = iWnd
        self.I = iOfs
        self.E = iDfs
        self.Phase = 2
        self.adjBlock = 0
        if self.E.st.SPD >= 100:
            self.adjBlock = 0
        elif self.E.st.SPD >= 46:
            self.adjBlock = 64
        elif self.E.st.SPD > 36:
            self.adjBlock = 32
        elif self.E.st.SPD > 27:
            self.adjBlock = 16
        elif self.E.st.SPD > 18:
            self.adjBlock = 8

    def update(self):
        if not self.flgFin:
            if (self.I.st.SPD * px.rndi(0,200)) >= (self.E.st.SPD * px.rndi(self.adjBlock, 62+self.E.st.SPD )):
                self.drawData = [self.I.name+"は　にげのびた！"]
                px.play(3,SNDEFX["run"], resume=True)
                self.Phase = 4
            else:
                self.drawData = [self.I.name+"は　にげそこねた！！"]
                px.play(3, SNDEFX["miss"], resume=True)
                self.Phase = 2
            self.flgFin = True
        return self.keycheck()

    def draw(self, P_adrCursor):
        if self.flgFin:
            self.insMsgWnd.draw()
            self.insMsgWnd.drawText(self.insMsgWnd.P_x + P_CHIP_SIZE*2 , self.insMsgWnd.P_y + P_CHIP_SIZE*2 , self.drawData, JP_FONT)
            self.flgDispFin = True


#****#****#****#****#**** Battle #****#****#****#****#****
class Battle:
    def __init__(self, insYusha:Character, MobID:int, flgBoss:bool=False, flgLastBattle:bool=False):
        self.ME         = self
        self.HERO       = insYusha # = OBJ_CHAR_LIST[0]
        self.flgBoss    = flgBoss
        self.flgLast    = flgLastBattle
        self.MobID      = MobID
        if self.flgBoss:
            self.MOB    = Boss(MobID)
        else:
            self.MOB    = Monster(MobID)

        self.Phase      = 0 # 0:開始 1:戦闘メニュー選択中 2:戦闘処理中　3:勝利 4:逃走 8:終了 9:死亡

        self.WndAddr    = [P_CHIP_SIZE, P_CHIP_SIZE * 18] #152]
        self.wndSize    = [px.width - (P_CHIP_SIZE*2), px.height - self.WndAddr[Y] - P_CHIP_SIZE]
        self.insWndMesg = Window(*self.WndAddr, *self.wndSize, 1)
        self.insMnuCmnd = MenuBattle(*self.WndAddr, [1,4],[["たたかう"],["まほう"],["アイテム"],["にげる"]], 4, self.ME)

        self.insWndStat = Window(P_CHIP_SIZE,P_CHIP_SIZE, P_CHIP_SIZE*11,P_CHIP_SIZE*6, 2)

        self.insSubMnu  = None

        self.turnSide   = True # 真:自分のターン 偽:相手のターン
        self.flgCmd     = False
        self.flgSubMnu  = False
        self.flgMsgWnd  = False
        self.flgWin     = False


    def update(self):
        match self.Phase:
            case 0:
                if IS_DEBUG:
                    self.Phase = 3
                    return True
                if self.flgLast:
                    reloadBGM(99)
                elif self.flgBoss:
                    reloadBGM(90)
                else:
                    reloadBGM(9)

                if self.insWndMesg.update() == False:
                    self.Phase = 1
            case 1:
                if self.flgMsgWnd:
                    self.flgMsgWnd = self.insWndMesg.update()
                    return True

                if self.insMnuCmnd.flgSubMnu:
                    self.insMnuCmnd.flgSubMnu = self.insMnuCmnd.insSubMnu.update()
                    if self.insMnuCmnd.flgSubMnu == False:
                        return True

                    itemname = str(self.insMnuCmnd.insSubMnu.selMnu).split("　")
                    if itemname[0] == ITEMS[0][0]: #["くすりのくさ",0],
                        self.insMnuCmnd.insSubMnu.insMsgWnd = None
                        del self.insMnuCmnd.insSubMnu
                        self.insMnuCmnd.flgSubMnu = False
                        self.insCmd = cmdHPherb(*self.WndAddr, self.insWndMesg)
                        self.flgCmd = True
                        self.Phase  = 2
                    elif itemname[0] == ITEMS[1][0]: #["まほうのくさ",1],
                        self.insMnuCmnd.insSubMnu.insMsgWnd = None
                        del self.insMnuCmnd.insSubMnu
                        self.insMnuCmnd.flgSubMnu = False
                        self.insCmd = cmdMPherb(*self.WndAddr, self.insWndMesg)
                        self.flgCmd = True
                        self.insWndStat.update()
                        self.Phase  = 2
                    elif itemname[0] == MAGICS[0][0]: # "ヒール"
                        self.insMnuCmnd.insSubMnu.insMsgWnd = None
                        del self.insMnuCmnd.insSubMnu
                        self.insMnuCmnd.flgSubMnu = False
                        self.insCmd = cmdHeal(*self.WndAddr, self.HERO, 1, self.insWndMesg)
                        self.flgCmd = True
                        self.insWndStat.update()
                        self.Phase  = 2
                    elif itemname[0] == MAGICS[1][0]: # "マジックアロー"
                        self.insMnuCmnd.insSubMnu.insMsgWnd = None
                        del self.insMnuCmnd.insSubMnu
                        self.insMnuCmnd.flgSubMnu = False
                        self.insCmd = cmdMagicArrow(*self.WndAddr, self.insMnuCmnd.mnuType, self.HERO, self.MOB, self.insWndMesg)
                        self.flgCmd = True
                        self.insWndStat.update()
                        self.Phase  = 2
                    elif itemname[0] == MAGICS[3][0]: # "リターン"
                        self.insMnuCmnd.insSubMnu.insMsgWnd = None
                        del self.insMnuCmnd.insSubMnu
                        self.insMnuCmnd.flgSubMnu = False
                        self.insCmd = cmdReturn(*self.WndAddr, self.insMnuCmnd.mnuType, self.insWndMesg)
                        self.flgCmd = True
                        self.Phase  = 2
                    elif itemname[0] == MAGICS[2][0]: # "サンクチュアリ"
                        self.insMnuCmnd.insSubMnu.insMsgWnd = None
                        del self.insMnuCmnd.insSubMnu
                        self.insMnuCmnd.flgSubMnu = False
                        self.insCmd = cmdSanctuary(*self.WndAddr, self.insMnuCmnd.mnuType, self.insWndMesg)
                        self.flgCmd = True
                        self.Phase  = 2
                    elif itemname[0] == MAGICS[4][0]: # "グレートヒール"
                        self.insMnuCmnd.insSubMnu.insMsgWnd = None
                        del self.insMnuCmnd.insSubMnu
                        self.insMnuCmnd.flgSubMnu = False
                        self.insCmd = cmdGreatHeal(*self.WndAddr, self.HERO, 1, self.insWndMesg)
                        self.flgCmd = True
                        self.insWndStat.update()
                        self.Phase  = 2
                    elif itemname[0] == MAGICS[5][0]: # "エクスプロード"
                        self.insMnuCmnd.insSubMnu.insMsgWnd = None
                        del self.insMnuCmnd.insSubMnu
                        self.insMnuCmnd.flgSubMnu = False
                        self.insCmd = cmdExprode(*self.WndAddr, self.insMnuCmnd.mnuType, self.HERO, self.MOB, self.insWndMesg)
                        self.flgCmd = True
                        self.insWndStat.update()
                        self.Phase  = 2                                
                    return True

                selMnu = self.insMnuCmnd.update()
                match selMnu:
                    case "たたかう":
                        self.insCmd = cmdAttack(*self.WndAddr, self.HERO, self.MOB, self.insWndMesg)
                        self.flgCmd = True
                        self.Phase  = 2
                    case "まほう":
                        menuitem = []
                        for i in range(len(OBJ_CHAR_LIST[0].magic)):
                            menuitem.append([ str(MAGICS[OBJ_CHAR_LIST[0].magic[i]][0]).ljust(10,"　")+ str(MAGICS[OBJ_CHAR_LIST[0].magic[i]][1]).translate(h2z) ])

                        if len(menuitem) == 0:
                            self.Msg = ["まほうは　つかえない"]
                            self.flgMsgWnd = True
                            self.insWndMesg.tTimer = 0
                        else:
                            self.insMnuCmnd.insSubMnu = MenuBattle(self.insMnuCmnd.P_adrCursor[X], self.insMnuCmnd.P_adrCursor[Y]-P_CHIP_SIZE*3, [1,len(menuitem)], menuitem, 13, self)
                            self.insMnuCmnd.insSubMnu.insMsgWnd = self.insWndMesg
                            self.insMnuCmnd.flgSubMnu = True
                    case "アイテム":
                        menuitem = []
                        for i in range(2):
                            if OBJ_CHAR_LIST[0].Item[i][1] > 0:
                                menuitem.append([ str(ITEMS[OBJ_CHAR_LIST[0].Item[i][0]][0]).ljust(10,"　")+ str(OBJ_CHAR_LIST[0].Item[i][1]).translate(h2z) ])

                        if len(menuitem) == 0:
                            self.Msg = ["なにも　もっていない"]
                            self.flgMsgWnd = True
                            self.insWndMesg.tTimer = 0
                        else:
                            self.insMnuCmnd.insSubMnu = MenuBattle(*self.insMnuCmnd.P_adrCursor, [1,len(menuitem)], menuitem, 13)
                            self.insMnuCmnd.insSubMnu.insMsgWnd = self.insWndMesg
                            self.insMnuCmnd.flgSubMnu = True
                    case "にげる":
                        if self.flgBoss:
                            self.Msg = ["　このたたかいから　ひくわけには　いかない！！"]
                            self.flgMsgWnd = True
                            self.insWndMesg.tTimer = 0
                        else:
                            self.Phase  = 2
                            self.insCmd = cmdRunaway(*self.WndAddr, self.HERO, self.MOB, self.insWndMesg)
                            self.flgCmd = True

                return True
            case 2:
                selMnu = ""
                if self.flgCmd:
                    if self.turnSide:
                        flgTmp = self.insCmd.update()
                        if flgTmp != None:
                            if isinstance(self.insCmd, cmdRunaway):
                                self.Phase = self.insCmd.Phase
                            if self.Phase != 2:
                                return True
                            if self.insCmd.flgDispFin:
                                if self.MOB.st.HP <= 0:
                                    self.Phase = 3
                                    return True
                                act = 0
                                if self.MOB.mg >= 0:
                                    act = px.rndi(0,1)
                                match act:
                                    case 0:
                                        self.insCmd = cmdAttack(*self.WndAddr, self.MOB, self.HERO, self.insWndMesg)
                                    case 1:
                                        match self.MOB.mg:
                                            case 0:
                                                self.insCmd = cmdHeal(*self.WndAddr, self.MOB, 1, self.insWndMesg)
                                            case 1:
                                                self.insCmd = cmdMagicArrow(*self.WndAddr, self.insMnuCmnd.mnuType, self.MOB, self.HERO, self.insWndMesg)
                                            case 4:
                                                self.insCmd = cmdGreatHeal(*self.WndAddr, self.MOB, 1, self.insWndMesg)
                                            case 5:
                                                self.insCmd = cmdExprode(*self.WndAddr, self.insMnuCmnd.mnuType, self.MOB, self.HERO, self.insWndMesg)

                                self.flgCmd = True
                                self.turnSide = False



                        return True
                    else:
                        flgTmp = self.insCmd.update()
                        if flgTmp != None:
                            if self.insCmd.flgDispFin:
                                # if self.HERO.st.HP == 0:
                                if self.HERO.st.HP <= 0:
                                    self.Phase = 9
                                    return True
                                del self.insCmd
                                self.flgCmd = False
                                self.turnSide = True
                                self.Phase = 1
                        return True

            case 8:
                if self.flgWin:
                    chkLevelUp()
                self.insWndMesg.tTimer=0
                return self.insWndMesg.update()
            case 9:
                return self.insWndMesg.update()
        
        return True

    def draw(self):
        match self.Phase:
            case 0:
                self.insWndMesg.draw()
                tmptxt = "%sが　あらわれた"%self.MOB.name
                self.insWndMesg.drawText(self.insWndMesg.P_x + self.insWndMesg.P_width//2 - len(tmptxt)*P_CHIP_SIZE//2, self.insWndMesg.P_y + self.insWndMesg.P_height//2 - P_CHIP_SIZE, [tmptxt])
                self.insWndMesg.tTimer = 0
            case 1:
                self.insMnuCmnd.draw()
                self.insWndStat.draw()
                if self.flgSubMnu:
                    self.insSubMnu.draw()
                if self.flgMsgWnd:
                    self.insWndMesg.draw()
                    self.insWndMesg.drawText(self.insWndMesg.P_x+P_CHIP_SIZE, self.insWndMesg.P_y+P_CHIP_SIZE, self.Msg)
            case 2:
                self.insWndStat.draw()
                self.insCmd.draw([self.insWndMesg.P_x+P_CHIP_SIZE, self.insWndMesg.P_y+P_CHIP_SIZE])
                self.insWndMesg.tTimer = 0
            case 3:
                if self.flgBoss and self.MobID==3:
                    reloadBGM("Ending")
                else:
                    reloadBGM(8)
                self.insWndStat.draw()
                self.insWndMesg.draw()
                self.insWndMesg.drawText(self.insWndMesg.P_x+P_CHIP_SIZE*2, self.insWndMesg.P_y+P_CHIP_SIZE*2, 
                                         ["%s　を　ぶっころした"%self.MOB.name,
                                          "",
                                          "　%s　のけいけんち　と、"%str(self.MOB.st.xp).translate(h2z),
                                          "　%s　のおかねを　てにいれた"%str(self.MOB.st.gp).translate(h2z)])
                self.HERO.st.xp = min(self.HERO.st.xp + self.MOB.st.xp, 65535)
                self.HERO.st.gp = min(self.HERO.st.gp + self.MOB.st.gp, 65535)
                self.insWndMesg.tTimer = 0
                self.Phase = 8
                self.flgWin = True
                if self.flgBoss:
                    match self.MobID:
                        case 0:
                            EVENT_STAT.set(8,True)
                        case 1:
                            EVENT_STAT.set(9,True)
                            getItem(7)
                            EVENT_STAT.set(2,True)
                            self.insWndMesg.drawText(self.insWndMesg.P_x+P_CHIP_SIZE, self.insWndMesg.P_y+P_CHIP_SIZE + 7*P_CHIP_SIZE, 
                                         ["なんと　たいようのかぜを　てにいれた！"])
                        case 2:
                            self.insWndMesg.drawText(self.insWndMesg.P_x+P_CHIP_SIZE, self.insWndMesg.P_y+P_CHIP_SIZE + 7*P_CHIP_SIZE, 
                                         ["まもののおうは　しずかに　よこたわっている"])
                            EVENT_STAT.set(10,True)
                        case 3:
                            self.insWndMesg.drawText(self.insWndMesg.P_x+P_CHIP_SIZE, self.insWndMesg.P_y+P_CHIP_SIZE + 7*P_CHIP_SIZE, 
                                         ["まもののおうは　ついに　いきたえた！","あなたは　しめいを　はたしたのだ！！"])
                            EVENT_STAT.set(11,True)
                            
            case 4:
                self.insWndStat.draw()
                self.insCmd.draw([self.insWndMesg.P_x+P_CHIP_SIZE, self.insWndMesg.P_y+P_CHIP_SIZE])
                self.insWndMesg.tTimer = 0
                self.Phase = 8
            case 8:
                pass
            case 9:
                self.insWndStat.draw()
                self.insWndMesg.draw()
                self.insWndMesg.drawText(self.insWndMesg.P_x+P_CHIP_SIZE, self.insWndMesg.P_y+P_CHIP_SIZE, ["%s　が　おっちんだ"%self.HERO.name])
                self.insWndMesg.tTimer = 0
        # ステータス表示
        self.insWndStat.draw()
        self.insWndStat.drawText(self.insWndStat.P_x+P_CHIP_SIZE,self.insWndStat.P_y+P_CHIP_SIZE,[self.HERO.name,"ＨＰ：%s"%str(self.HERO.st.HP).translate(h2z),"ＭＰ：%s"%str(self.HERO.st.MP).translate(h2z)])
        #モンスター表示
        px.text(px.width//2 - (len(self.MOB.name)*P_CHIP_SIZE//2) + P_CHIP_SIZE, px.height//2 - self.MOB.imgBlk*P_CHIP_SIZE*2 + P_CHIP_SIZE , self.MOB.name, 7, JP_FONT)        
        px.blt( px.width//2 - self.MOB.imgBlk*P_CHIP_SIZE//2, px.height//2 - self.MOB.imgBlk*P_CHIP_SIZE + 8, IMGIDX_MOB, 
                self.MOB.imgBlk*P_CHIP_SIZE*self.MOB.colVer, self.MOB.imgAddr*P_CHIP_SIZE, 
                self.MOB.imgBlk*P_CHIP_SIZE,self.MOB.imgBlk*P_CHIP_SIZE, colkey=0, scale=2)


#****#****#****#****#**** BattleMenu #****#****#****#****#****
class MenuBattle(Menu):
    def __init__(self, x, y, ishape, items, iLen, Parent:Battle =None):
        super().__init__(x, y, ishape, items, iLen, 1)
        self.Parent = Parent
        if isinstance(Parent, Battle):
            self.insMsgWnd = Parent.insWndMesg


    def chkCmdRtn(self):
        flgTmp = self.insCmd.update()
        if flgTmp:
            self.flgCmd = False
            self.insSubMnu = False
            return False
        elif flgTmp == False:
            self.flgCmd = False
        return True


    def menuBattle(self, P_x, P_y):
        if self.selMnu != "":
            return self.selMnu
        return True


#****#****#****#****#**** Monster #****#****#****#****#****        
class Monster:
    def __init__(self, MobID:int):
        self.name   = MONSTERS[MobID][0]
        self.st     = Status(MONSTERS[MobID][1],MONSTERS[MobID][2],MONSTERS[MobID][3],MONSTERS[MobID][4],MONSTERS[MobID][5],MONSTERS[MobID][6],MONSTERS[MobID][7],MONSTERS[MobID][8])
        self.mg     = MONSTERS[MobID][9]
        self.imgBlk = MONSTERS[MobID][10]
        self.colVer = MONSTERS[MobID][11]
        self.imgTyp = MONSTERS[MobID][12]
        self.imgAddr= 0
        for i in range(MobID):
            if MONSTERS[i][12] == self.imgTyp:
                break
            elif MONSTERS[i][11] == 0:
                self.imgAddr += MONSTERS[i][10]

class Boss(Monster):
    def __init__(self, MobID:int):
        self.name   = BOSS[MobID][0]
        self.st     = Status(BOSS[MobID][1],BOSS[MobID][2],BOSS[MobID][3],BOSS[MobID][4],BOSS[MobID][5],BOSS[MobID][6],BOSS[MobID][7],BOSS[MobID][8])
        self.mg     = BOSS[MobID][9]
        self.imgBlk = BOSS[MobID][10]
        self.colVer = BOSS[MobID][11]
        self.imgTyp = BOSS[MobID][12]
        self.imgAddr= 20
        for i in range(MobID):
            if BOSS[i][12] == self.imgTyp:
                break
            elif BOSS[i][11] == 0:
                self.imgAddr += BOSS[i][10]
                


#******************************************************************************#
# メインロジック
#******************************************************************************#
class App():
    def __init__(self):
        px.init(B_DISP_SIZE*P_BLOCK_SIZE, B_DISP_SIZE*P_BLOCK_SIZE, title="Old JRPG like EasyVer.", quit_key=9999)
        
        px.load(ASSET_FILE,excl_tilemaps=True)
        px.tilemaps[0]  = px.Tilemap.from_tmx("assets/CRPG.tmx",0)

        self.img = px.Image(px.width, px.height) #タイトル画像
        self.img.load(0,0, "assets/Title.bmp")

        global JP_FONT
        JP_FONT         = px.Font("assets/misaki_gothic_2nd.bdf")

        global OBJ_CHAR_LIST

        self.World      = Map()
        self.flgWindow  = False
        self.flgWindow2 = False
        self.insWindow  = ""
        self.flgMenu    = True
        self.insMenu    = MenuTitle(self)
        self.txtMsg     = ""
        self.insBattle  = ""
        self.flgCongrat = False
        self.cnt        = 0

        reloadGameStatus()

        self.now_scene  = SCENE_STATUS["Title"]
        self.back_scene = self.now_scene

        reloadBGM(self.now_scene)
#デバッグ用
        if IS_DEBUG:
            px.mouse(True)

        px.run(self.update, self.draw)



    def talk(self, charid:int, ):
        match charid:
            case 1:
                if EVENT_STAT.get(10) == False:
                    px.flip()
                    self.flgWindow  = True
                    self.insBattle  = Battle(OBJ_CHAR_LIST[0], 2, True )
                    self.back_scene = self.now_scene
                    self.now_scene  = SCENE_STATUS["Battle"]
                    return ["ついにここまでやってきたか　"+OBJ_CHAR_LIST[0].name+"よ","","なにゆえ　わがしはいを　こばむのだ？","にんげんは　おろかなそんざいだ","たやすく　よくにまみれ　たしゃをがいする",
                            "","それでも　やつらを　まもるというなら","たたかうほか　あるまいな・・・　ゆくぞ！！"]
            case 2:
                if EVENT_STAT.get(5) == False:
                    EVENT_STAT.set(5,True)
                    OBJ_CHAR_LIST[0].st.gp += 120
                    return ["よくぞきた！"+OBJ_CHAR_LIST[0].name+"よ！","このせかいのしはいをたくらむ","まもののおうを　たおしてほしいのだ・・・",""
                            ,"ひがしもんの　つうこうきょかを　あたえる","",
                            "このかねで　たびのしたくを　ととのえ","まちのひがしから　ぼうけんにでるがよい"]
                            
                elif EVENT_STAT.get(8) == False:
                    return ["ほくせいの　やまのなかに　すみついた","つよきまものを　たおせたなら","みなみのもんの　つうこうをきょかしよう"]
                elif EVENT_STAT.get(6) == False:
                    EVENT_STAT.set(6,True)
                    return ["よくぞもどった　"+OBJ_CHAR_LIST[0].name+"よ！","","すでにほうこくは　うけておる","みなみのもんの　つうこうをきょかしよう"]
                else:
                    return ["よくぞきた！"+OBJ_CHAR_LIST[0].name+"よ！","ぼうけんは　じゅんちょうか？","",
                            "なんとうの　みずうみには　いってみたか？","もりをこえねば　ならぬゆえ","ゆうきが　ためされるがの"]
            case 3:
                if EVENT_STAT.get(0) == False:
                    return ["よくぞここへたどりついた！" + OBJ_CHAR_LIST[0].name+"よ！","すまぬが　ひとつねがいを　きいてくれぬか","",
                            "もりのほくせい　いりぐちあたりで　はしをわたって","すすんださき　うみぞいの　きのねもとに","ふるくから　ねむるとつたわる","ざいほうを　ひとめ　みてみたいのだ",
                            "","さすれば　みなみもんの　つうこうを　きょかしよう"]
                elif EVENT_STAT.get(7) == False:
                    EVENT_STAT.set(7,True)
                    return ["これが　つたえきく　ざいほうか！","・・・うつくしいが　ちんみょうな　ものだな","","まあよい　みなみもんは　じゆうにとおれ","",
                            "おお、そうじゃ！ついでといっては　なんだが","もりのうらもん　も　あけておいてやろう"]
                else:
                    return [OBJ_CHAR_LIST[0].name+"よ　そなたのゆくさきに　ひかりあれ"]

            case 4:
                if EVENT_STAT.get(2) == False:
                    return ["ニイさん　こんなとこまで　よくきたね","","とつぜんあらわれた　まものヤロウが","たいせつなものを　うばってっちまった","おかげで　さいきんは　りょうも　あがったりだよ",
                            "","クソッ　あのイモムシやろうめ！！","しかし　さばくのおくにゃ　とてもいけねえ…"]
                else:
                    return ["ニイさん　アンタの　おかげかい？","いきなり　かぜが　もどってきやがった！","","みかけによらず　やるじゃねーか！","アンタにゃ　デッカイかりが　できちまったね",
                            "","そうそう　ひがしのさばくにゃ　もういったかい？","おたからが　かくされてるって　はなしだよ"]
            case 5:
                if EVENT_STAT.get(2) == False:
                    return ["ようこそオアシスへ、たびのかた","ここは　かぜのとまった　オアシス・・・","","ふたたび　かぜがふくのを　まちわびています"]
                elif EVENT_STAT.get(4) == False:
                    return ["かぜをもたらす　えいゆうよ　かんげいします","おつかれでしょう　ゆっくりおやすみください","","えいゆうに　ふさわしいぶぐが","にしのぬまに　ねむっています",
                            "","てにするためには　あかしがひつようです","はるかほくとう　しれんのしまへ　むかうのです"]
                elif OBJ_CHAR_LIST[0].eq[1] != 5:
                    return ["あかしをてにした　えいゆうよ","ぶぐを　てに　いれられよ","","にしのぬまの　いちばんおくから","みなみのすなち そこから　まっすぐひがし","ぶぐは　ぬまのちゅうおうに"]
                else:
                    return ["まことのえいゆうよ　どうか　まもののおうを","","ゆかれよ　きたのかなた　ゆきのだいちへ","かのちをみはる　しんかんに","おしえを　こうのです"]
            case 6:
                if EVENT_STAT.get(4) == False:
                    return ["よくぞごぶじでまいられた","","しかし　さきへすすむには　まだはやい","","あかしを　てにいれられよ",""]
                elif OBJ_CHAR_LIST[0].eq[2] != 4:
                    return ["あらくれのすむ　やまのふもと","ながれにうかぶ　ちいさなしまに","いにしえのぶぐが　ねむるという","","きっと　あなたのたすけと　なるはず"]
                elif EVENT_STAT.get(1) == False:
                    return ["にしへゆき　まもののしろを　のぞむこじまに","ながいあいだ　まりょくをたくわえた","こだいのどうぐが　うまっています","","ほしのちからを　みちびくかぎと　なるでしょう"]
                elif EVENT_STAT.get(3) == False:
                    return ["ゆきのだいち　ほくとうのみさき","やまあいの　さいだんへ","みっつのたからを　ささげるのです","","まもののしまへ　わたるための","かがやくちからを　えられるでしょう"]
                elif OBJ_CHAR_LIST[0].eq[0] != 5:
                    return ["ゆきのだいちの　やまあいを ひがしに","","そのさきに　ひそやかにたつ　ふるきさいだん","ささげられしは　すべてのあくを　きりさくひかり"]
                else:
                    return ["よくぞごぶじでまいられた！","","まもののしろは　やみに　とざされていると　きく","ゆめゆめ　したくをおこたらぬよう"]

            case 7:
                self.insWindow  = Window(16,16,px.width - (P_BLOCK_SIZE*2),104,0)
                self.insMenu = MenuShop(36, 36, self.insWindow)
                self.flgMenu = True
                return ["いらっしゃい！ここは　なんでもや　だ！"]
            case 8:
                insCmd = cmdInn(28,36)
                self.insMenu = MenuYesNo(24, 128, ["やすんでいきますか？"], insCmd, self)
                self.flgMenu = True
                return ["ここはやどやです","いっぱくの　やどだいは　"+str(int(( ((OBJ_CHAR_LIST[0].lvl ** 2) * 3) - (OBJ_CHAR_LIST[0].lvl * 2) ) / 10 + 1)).translate(h2z)+"　です",
                        "","","　　しょじきん："+str(OBJ_CHAR_LIST[0].st.gp).translate(h2z) ]
            case 9:
                return ["にじいろに　かがやく　よぞらの　ベール","","オーロラを　まとうものだけが","まものたちの　しろへ　ゆけるのじゃ",
                        "","かみのごかごが　あらんことを"]
            case 10:
                if EVENT_STAT.get(4):
                    OBJ_CHAR_LIST[charid].B_addr = [132,157]
                    return [OBJ_CHAR_LIST[0].name+"か　ひさしいな","ひがしのやまの　はなしは　きいたか？","",
                            "ときおり　やまはだが　ひかってみえるそうだ","あそこで　ひかるような　いしは　とれないはずだが",
                            "きょうみがあれるなら　いってみてはどうだ"]
                elif EVENT_STAT.get(5):
                    if OBJ_CHAR_LIST[charid].B_addr == [132,158]:
                        OBJ_CHAR_LIST[charid].B_addr = [132,157]
                        return ["きょかを えたようだな　とおるがいい","","もりには　きけんなまものが　ひそんでいる","つよくなるまで　そうげんをあるくのだ","","まちがっても　ひがしのやまには　ちかづくなよ","それと　データのほぞんも　わすれないようにな"]
                    else:
                        return ["もりには　きけんなまものが　ひそんでいる","つよくなるまで　そうげんをあるくのだ","ひがしのやまには　ちかづくなよ","","では　きをつけて　いくのだぞ"]
                else:
                    return ["ここを　とおすわけには　いかん","きょかをえてから　でなおすがいい"]
            case 11:
                if EVENT_STAT.get(6):
                    if OBJ_CHAR_LIST[charid].B_addr == [118,170]:
                        OBJ_CHAR_LIST[charid].B_addr = [117,170]
                        return ["きょかを えたようだな","ここを　とおるがいい","このさきはとてもきけんだ","きをひきしめて　いくのだぞ","","にしのもりの　めいろをぬけ","もりのまちを　めざすのだ"]
                    else:
                        return ["このさきはとてもきけんだ","きをひきしめて　いくのだぞ","","にしのもりの　めいろをぬけ","もりのまちを　めざすのだ"]
                else:
                    return ["ここを　とおすわけには　いかん","きょかをえてから　でなおすがいい"]

            case 12:
                self.insWindow  = Window(16,16,px.width - (P_BLOCK_SIZE*2),104,0)
                self.insMenu = MenuShop(36, 36, self.insWindow)
                self.flgMenu = True
                return ["とおでするなら　まほうのくさを　もっておくべし"]
            case 13:
                insCmd = cmdInn(28,36)
                self.insMenu = MenuYesNo(24, 128, ["やすんでいきますか？"], insCmd, self)
                self.flgMenu = True
                return ["ここはやどやです","いっぱくの　やどだいは　"+str(int(( ((OBJ_CHAR_LIST[0].lvl ** 2) * 3) - (OBJ_CHAR_LIST[0].lvl * 2) ) / 10 + 1)).translate(h2z)+"　です",
                        "","","　　しょじきん："+str(OBJ_CHAR_LIST[0].st.gp).translate(h2z) ]
            case 14:
                return ["たいようからとどく かがやきのもとが","ほしをとりまく　ちからにぶつかり","オーロラが　うまれるのじゃ",
                        "","かみのごかごが　あらんことを"]
            case 15:
                if EVENT_STAT.get(7):
                    if OBJ_CHAR_LIST[charid].B_addr == [80,223]:
                        OBJ_CHAR_LIST[charid].B_addr = [81,223]
                        return ["きょかを えたようだな","ここを　とおるがいい","もりのめいろを　ぬけて","さばくを　みなみへすすむのだ"]
                    else:
                        return ["もりのめいろを　ぬけて","さばくを　みなみへすすむのだ"]
                else:
                    return ["ここを　とおすわけには　いかん","きょかをえてから　でなおすがいい"]
                
            case 16:
                self.insWindow  = Window(16,16,px.width - (P_BLOCK_SIZE*2),104,0)
                self.insMenu = MenuShop(36, 36, self.insWindow)
                self.flgMenu = True
                return ["くすりのくさは　つよくなるほど　こうかがあがるぞ"]
            case 17:
                insCmd = cmdInn(28,36)
                self.insMenu = MenuYesNo(24, 128, ["やすんでいきますか？"], insCmd, self)
                self.flgMenu = True
                return ["ここはやどやです","いっぱくの　やどだいは　"+str(int(( ((OBJ_CHAR_LIST[0].lvl ** 2) * 3) - (OBJ_CHAR_LIST[0].lvl * 2) ) / 10 + 1)).translate(h2z)+"　です",
                        "","","　　しょじきん："+str(OBJ_CHAR_LIST[0].st.gp).translate(h2z) ]
            case 18:
                return ["ほしのちからは　ひとには　あやつれぬが","つたえきく　カガクのワザで","まねごとならば　できようか","","でんせつのきんぞくで　つくられた　どうぐに","まりょくをとおすのじゃ",
                        "","かみのごかごが　あらんことを"]
            
            case 19:
                self.insWindow  = Window(16,16,px.width - (P_BLOCK_SIZE*2),104,0)
                self.insMenu = MenuShop(36, 36, self.insWindow)
                self.flgMenu = True
                return ["しゅごのよろいは　まものを　とおざけてくれるぜ"]
            case 20:
                insCmd = cmdInn(28,36)
                self.insMenu = MenuYesNo(24, 128, ["やすんでいきますか？"], insCmd, self)
                self.flgMenu = True
                return ["ここはやどやです","いっぱくの　やどだいは　"+str(int(( ((OBJ_CHAR_LIST[0].lvl ** 2) * 3) - (OBJ_CHAR_LIST[0].lvl * 2) ) / 10 + 1)).translate(h2z)+"　です",
                        "","","　　しょじきん："+str(OBJ_CHAR_LIST[0].st.gp).translate(h2z) ]
            case 21:
                return ["はるかきた　ゆきのだいちに　あるという","ふるきさいだんで　オーロラをよびおこすのだ",
                        "","かみのごかごが　あらんことを"]
            case 22:
                self.insWindow  = Window(16,16,px.width - (P_BLOCK_SIZE*2),104,0)
                self.insMenu = MenuShop(36, 36, self.insWindow, 1)
                self.flgMenu = True
                return ["きっと　こうかいは　させないぜ","","","","うみのそこから　ひきあげたって　いわくつきの","ここでしか　てにはいらない　いっぴんだ！"]
            case 23:
                insCmd = cmdInn(28,36)
                self.insMenu = MenuYesNo(24, 128, ["やすんでいきますか？"], insCmd, self)
                self.flgMenu = True
                return ["ここはやどやです","いっぱくの　やどだいは　"+str(int(( ((OBJ_CHAR_LIST[0].lvl ** 2) * 3) - (OBJ_CHAR_LIST[0].lvl * 2) ) / 10 + 1)).translate(h2z)+"　です",
                        "","","　　しょじきん："+str(OBJ_CHAR_LIST[0].st.gp).translate(h2z) ]
            case 24:
                return ["これよりさきは　まものうごめく　しれんのしま","つぎつぎに　おそいくる　まものをしりぞけねば",
                        "ゆうきのあかしを　てにすることは　かなわず",
                        "","かみのごかごが　あらんことを"]


    def CheckEvent(self, B_Addr, now_dir):
        B_targetAddr = [ B_Addr[X] + CHARA_DIR[now_dir][X], B_Addr[Y] + CHARA_DIR[now_dir][Y] ]
        #対象を調べる１：タイルマップからpgetしてイベント起動チップの存在をチェック（４チップのオブジェクトの場合は左上チップで判定）・・・要らなくなるかも
#デバッグ用
        if IS_DEBUG:
            print(px.tilemaps[0].pget((B_Addr[X]+CHARA_DIR[now_dir][X])*2, (B_Addr[Y]+CHARA_DIR[now_dir][Y])*2))

        #対象を調べる２：向き先アドレスにイベント対象が存在する場合（アドレス直書きで指定）
        match [ B_Addr[X]+CHARA_DIR[now_dir][X],B_Addr[Y]+CHARA_DIR[now_dir][Y] ]:
            case [121,226]:
                if EVENT_STAT.get(9) == False:
                    px.flip()
                    self.flgWindow  = True
                    self.insBattle  = Battle(OBJ_CHAR_LIST[0], 1, True )
                    self.back_scene = self.now_scene
                    self.now_scene  = SCENE_STATUS["Battle"]
                    return ["「ＧＶＲＲＯＯＯＯＯ！！！！」","","きょだいな　まものが　おそってきた！"]
            case [52,107]:
                if EVENT_STAT.get(8) == False:
                    px.flip()
                    self.flgWindow  = True
                    self.insBattle  = Battle(OBJ_CHAR_LIST[0], 0, True )
                    self.back_scene = self.now_scene
                    self.now_scene  = SCENE_STATUS["Battle"]
                    return ["「シャーーッッ！！！！」","","まものが　おそってきた！"]
            case [28,179]:
                if EVENT_STAT.get(0) == False:
                    getItem(5)
                    EVENT_STAT.set(0, True)
                    return ["なんと　オリハルコイルを　みつけた！"]
            case [72,126]:
                if OBJ_CHAR_LIST[0].eq[2] != 4:
                    if EVENT_STAT.get(4):
                        StsVal = SHIELDS[4][1] - SHIELDS[OBJ_CHAR_LIST[0].eq[2]][1]
                        OBJ_CHAR_LIST[0].eq[2] = 4
                        OBJ_CHAR_LIST[0].st.DEF += StsVal
                        return ["なんと　しんわのたてを　てにいれた！","","あるく　たびに　たいりょくが　かいふくする！"]
            case [228,65]:
                if OBJ_CHAR_LIST[0].eq[0] != 5:
                    if EVENT_STAT.get(4):
                        StsVal = WEAPONS[5][1] - WEAPONS[OBJ_CHAR_LIST[0].eq[0]][1]
                        OBJ_CHAR_LIST[0].eq[0] = 5
                        OBJ_CHAR_LIST[0].st.ATK += StsVal
                        return ["なんと　でんせつのけんを　てにいれた！"]
            case [39,38]:
                if EVENT_STAT.get(12) == False:
                    if OBJ_CHAR_LIST[0].Item[4][1] == 0:
                        return ["かぎを　もっていない"]
                    else:
                        OBJ_CHAR_LIST[0].Item[4][1] -= 1
                        EVENT_STAT.set(12, True)
                        return ["かぎをつかい　とびらをひらいた"]
            case [276,17]:
                if EVENT_STAT.get(13) == False:
                    if OBJ_CHAR_LIST[0].Item[4][1] == 0:
                        return ["かぎを　もっていない"]
                    else:
                        OBJ_CHAR_LIST[0].Item[4][1] -= 1
                        EVENT_STAT.set(13, True)
                        return ["かぎをつかい　とびらをひらいた"]
            case [223,66]:
                if EVENT_STAT.get(14) == False:
                    if OBJ_CHAR_LIST[0].Item[4][1] == 0:
                        return ["かぎを　もっていない"]
                    else:
                        OBJ_CHAR_LIST[0].Item[4][1] -= 1
                        EVENT_STAT.set(14, True)
                        return ["かぎをつかい　とびらをひらいた"]
            case [193,175]:
                if EVENT_STAT.get(4):
                    OBJ_CHAR_LIST[0].B_addr = [260,148]
                    px.cls(0)
                    return ["なにかが　きらきらと　ひかっている","そっとふれてみた","","・・・",
                            "そのてが　とつぜん　ひきよせられる！！","","めまいをおぼえ　とじためを　ふたたびひらいたとき",
                            "さきほどとは　まるでちがう　けしきがみえた・・・"]

        #話す：Characterのリストをループして座標に存在チェック
        for c in range(1,len(OBJ_CHAR_LIST)):
            if OBJ_CHAR_LIST[c].B_addr == B_targetAddr:
                return self.talk(c)

        #足元を調べる：現在のアドレスでイベント判定（イベント判定対象座標は事前定義）
        match B_Addr:
            case [276,21]:
                if EVENT_STAT.get(3) == False:
                    if EVENT_STAT.get(0) and EVENT_STAT.get(1) and EVENT_STAT.get(2):
                        tTimer = px.frame_count
                        while True:
                            px.flip()
                            px.dither(0.5)
                            px.rect(0,0, px.width,px.height, px.frame_count //2 % 16)
                            if tTimer + 120 < px.frame_count:
                                px.dither(1)
                                break
                        getItem(8)
                        EVENT_STAT.set(3, True)
                        return ["まりょくをとおすと　コイルがひかり","ほしのちからが　あたりをみたす","たいようふうと　ぶつかりあって","",
                                "かがやきのもとに　うまれたのは・・・","","なんと　オーロラベールを　てにいれた！"]
                    elif EVENT_STAT.get(0):
                        return ["みたこともない　きんぞくでできた　さいだんだ","とうめいのカバーのなかで　ケーブルがとぎれている","","ここに　コイルを　セットできそうだ"]
                    elif EVENT_STAT.get(1):
                        return ["みたこともない　きんぞくでできた　さいだんだ","とうめいカバーのそばが　しかくく　くぼんでいる　","","ここに　バッテリを　セットできそうだ"]
                    else:
                        return ["みたこともない　きんぞくでできた　さいだんは","すっかりこけむして　まるでねむっているようだ","",""]
            case [180,209]:
                if EVENT_STAT.get(4):
                    OBJ_CHAR_LIST[0].B_addr = [188,282]
                    return ["さいだんの　まえに　たつと","ゆうきのあかしが　かがやきだした","",
                            "それに　おうじるかのように","さいだんから　ひかりがあふれだす！",
                            "まばゆい　ひかりに　あたりは　しろくそまり","",
                            "ひかりが　きえると　けしきが　いっぺんしている！"]
                else:
                    return ["ゆうきのさいだん　と　かかれている","","とても　しずかな　ばしょだ"]
            case [72,70]:
                if EVENT_STAT.get(1) == False:
                    getItem(6)
                    EVENT_STAT.set(1, True)
                    return ["なんと　まどうバッテリを　みつけた！"]
            case [268,135]:
                if EVENT_STAT.get(4) == False:
                    getItem(9)
                    EVENT_STAT.set(4, True)
                    return ["なんと　ゆうきのあかしを　みつけた！"]
            case [144,230]:
                if OBJ_CHAR_LIST[0].eq[1] != 5:
                    if EVENT_STAT.get(4):
                        StsVal = ARMORS[5][1] - ARMORS[OBJ_CHAR_LIST[0].eq[1]][1]
                        OBJ_CHAR_LIST[0].eq[1] = 5
                        OBJ_CHAR_LIST[0].st.DEF += StsVal
                        return ["なんと　むてきのよろいを　てにいれた！","","どくぬまなどの　ダメージを　けいげんする"]
            case [54,20]:
                if OBJ_CHAR_LIST[0].Item[0][1] < 5:
                    getItem(0)
                    return ["なんと　くすりのくさを　みつけた！"]
            case [19,32]:
                if OBJ_CHAR_LIST[0].Item[0][1] < 5:
                    getItem(0)
                    return ["なんと　くすりのくさを　みつけた！"]
            case [41,29]:
                if OBJ_CHAR_LIST[0].Item[0][1] < 5:
                    getItem(0)
                    return ["なんと　くすりのくさを　みつけた！"]
            case [30,20]:
                if OBJ_CHAR_LIST[0].Item[1][1] < 2:
                    getItem(1)
                    return ["なんと　まほうのくさを　みつけた！"]
            case [39,27]:
                if OBJ_CHAR_LIST[0].Item[1][1] < 4:
                    getItem(1)
                    return ["なんと　まほうのくさを　みつけた！"]
            case [38,19]:
                if OBJ_CHAR_LIST[0].Item[1][1] < 4:
                    getItem(1)
                    return ["なんと　まほうのくさを　みつけた！"]
            case _:
                #何もなかった場合
                return ["あしもとを　しらべてみた・・・","しかし","そこには　なにも　なかった"]

        return ["あしもとを　しらべてみた・・・","しかし","そこには　なにも　なかった"]
        
    def YouDied(self):
        if self.flgWindow:
            if self.insWindow.update() == False:
                insCmdLoad = cmdLoad()
                if insCmdLoad.exec():
                    insCmdLoad.draw()
                    self.music = reloadBGM(self.now_scene)
                    self.flgWindow = False
                else:
                    self.World      = Map()
                    self.flgWindow  = False
                    self.flgWindow2 = False
                    self.insWindow  = ""
                    self.flgMenu    = True
                    self.insMenu    = MenuTitle(self)
                    self.txtMsg     = ""
                    self.insBattle  = ""
                    self.flgCongrat = False
                    self.cnt        = 0

                    reloadGameStatus()

                    self.now_scene  = SCENE_STATUS["Title"]
                    self.back_scene = self.now_scene

                    reloadBGM(self.now_scene)


        else:
            self.flgWindow = True
            self.insWindow  = Window(16,88,px.width - (P_BLOCK_SIZE*2),40,1)
            self.txtMsg = Message(24, 95, ["あなたは　しにました","さいごのセーブちてんに　もどります"])


    def update(self):
        if OBJ_CHAR_LIST[0].flgYouDied:
            px.flip()
            self.YouDied()
            return

        match self.now_scene:
            case 3: # SCENE_STATUS["Title"]
                rc = self.insMenu.update()
                if rc:
                    px.cls(0)
                elif rc == False:
                    self.now_scene = 3

                return
            case 4: # SCENE_STATUS["NameEntry"]
                if self.flgMenu:
                    self.flgMenu = self.insMenu.update()
                else:
                    self.flgMenu    = True
                    self.insMenu    = MenuNameEntry(self)
                    # self.music = reloadBGM(self.now_scene)
                    reloadBGM(self.now_scene)

                if self.flgWindow:
                    self.flgWindow = self.insWindow.update()

                return
            case 1000:
                if self.cnt >= 505:
                    if px.btn(px.GAMEPAD1_BUTTON_A) or px.btn(px.GAMEPAD1_BUTTON_B):
                        px.quit()


        #ラストバトル
        if self.flgCongrat:
            if self.now_scene != SCENE_STATUS["Ending"] and self.now_scene != 1000 and self.flgWindow2 == False:
                self.flgWindow2  = True
                self.txtMsg     = Message(32, 32, ["かくして　ものがたりは　しゅうえんをむかえた","","","このさき　ほしのゆくすえが　どうなったか","","それは　だれにも　しりえない・・・"])
                self.insWindow  = Window(16,16,px.width - (P_BLOCK_SIZE*2),104,3)
            elif self.now_scene != SCENE_STATUS["Ending"] and self.now_scene != 1000 and self.flgWindow:
                if self.insWindow.update() == False:
                    self.flgWindow2 = False
                    self.now_scene  = SCENE_STATUS["Ending"]
            return


        if EVENT_STAT.get(11) and self.now_scene != SCENE_STATUS["Battle"]:
            if self.flgWindow:
                if self.insWindow.update() == False:
                    self.flgCongrat = True
            else:
                px.flip()
                self.flgWindow  = True
                self.txtMsg     = Message(24, 24, ["いまいましい　ニンゲンどもめ・・・","ほしのちからを　つかいはたす　つもりなのか？","キサマらは　いきとしいけるもの　すべてのてきだ！",
                                                "","おろかなニンゲンどもに　おおいなるわざわいを！！","","","　　　　　　　　　　　　　はぎょろもろーーっ！！"])
                self.insWindow  = Window(16,16,px.width - (P_BLOCK_SIZE*2),104,3)
                return

        elif EVENT_STAT.get(10) and self.now_scene != SCENE_STATUS["Battle"]:
            px.flip()
            self.flgWindow  = True
            self.txtMsg     = Message(24, 24, ["ぐぐぐ・・・まさか　ここまでやるとは","","もはや　これまでか・・・しかし！ただではしなん！",
                                               "わがいのちと　ひきかえに　きさまを！！","しでのたびの　みちづれに　してくれるわぁっ！！"])
            self.insWindow  = Window(16,16,px.width - (P_BLOCK_SIZE*2),104,0)
            self.insBattle  = Battle(OBJ_CHAR_LIST[0], 3, True, True)
            self.back_scene = self.now_scene
            self.now_scene  = SCENE_STATUS["Battle"]


        #ウインドウ表示中はウインドウ更新のみ
        if self.flgWindow and self.flgMenu:
            self.flgWindow = self.flgMenu = self.insMenu.update()
            return

        if self.flgWindow:
            self.flgWindow = self.insWindow.update()
            return
        else:
            self.insWindow = ""

        if self.flgMenu:
            self.flgMenu = self.insMenu.update()
            return
        else:
            self.insMenu = ""
            

        #戦闘画面
        if self.now_scene == SCENE_STATUS["Battle"] and not (self.flgWindow or self.flgMenu):
            if self.insBattle.update():
                return
            else:
                self.now_scene = self.back_scene
                if EVENT_STAT.get(11) == False:
                    self.music = reloadBGM(self.now_scene)
                if self.insBattle.Phase == 9:
                    OBJ_CHAR_LIST[0].flgYouDied = True
                else:
                    del self.insBattle
                return

        #移動画面
        if (self.now_scene == SCENE_STATUS["Field"]) or (self.now_scene == SCENE_STATUS["Dungeon"]):
            
            #メインキャラ（リスト0番固定、ウインドウフラグ有り）
            moved = OBJ_CHAR_LIST[0].update(self.flgWindow,OBJ_CHAR_LIST)
            if OBJ_CHAR_LIST[0].flgYouDied:
                return
            #一般キャラ
            for charID in range(1,len(OBJ_CHAR_LIST)):
                    OBJ_CHAR_LIST[charID].update(False,OBJ_CHAR_LIST)

            #マップ状況更新とエンカウントチェック
            if self.World.update(OBJ_CHAR_LIST[0].flgMove, OBJ_CHAR_LIST[0].now_dir, OBJ_CHAR_LIST[0].B_addr[X], OBJ_CHAR_LIST[0].B_addr[Y]) and moved:
                px.flip()

                self.insWindow  = Window(16,88,px.width - (P_BLOCK_SIZE*2),40,1)
                self.txtMsg     = Message(self.insWindow.P_x + 16, self.insWindow.P_y + 16, ["まものが　あらわれた！"])
                self.flgWindow  = True

                MobID = getLivingMobID(*OBJ_CHAR_LIST[0].B_addr)
                self.insBattle  = Battle(OBJ_CHAR_LIST[0], MobID)
                self.back_scene = self.now_scene
                self.now_scene  = SCENE_STATUS["Battle"]
                return
            else:
                pass

            if (OBJ_CHAR_LIST[0].sanctuaryCount == 350):
                self.World.rndEncount  = self.World.generateRandom(350)
            if OBJ_CHAR_LIST[0].flgSanctuary:
                self.insWindow  = Window(16,88,px.width - (P_BLOCK_SIZE*2),40,1)
                self.txtMsg     = Message(self.insWindow.P_x + 16, self.insWindow.P_y + 16, ["まもののけはいが　ちかづいた"])
                self.flgWindow  = True
                OBJ_CHAR_LIST[0].flgSanctuary = False
                return

            #キャラ移動中のキー操作無効
            if OBJ_CHAR_LIST[0].flgMove:
                pass
            #移動中及びウインドウ表示中でない場合はキー判定
            else:
                if px.btnp(px.KEY_Z,10,5) or px.btnp(px.GAMEPAD1_BUTTON_A, 10, 5) or px.btnp(px.KEY_RETURN, 10, 5):
                    px.flip()
                    px.play(3,SNDEFX["pi"], resume=True)
                    self.txtMsg = Message(24, 24, self.CheckEvent(OBJ_CHAR_LIST[0].B_addr, OBJ_CHAR_LIST[0].now_dir))
                    self.flgWindow  = True
                    if isinstance(self.insWindow, Window) == False:
                        self.insWindow  = Window(16,16,px.width - (P_BLOCK_SIZE*2),104,0)
                    return
                if px.btnp(px.KEY_X,10,5) or px.btnp(px.GAMEPAD1_BUTTON_B, 10, 5) or px.btnp(px.KEY_SPACE, 10, 5):
                    px.flip()
                    self.flgMenu  = True
                    self.insMenu  = Menu(16,16, [2,2],[["ステータス","まほう"],["アイテム","システム"]])
                    return


    def draw(self):
        px.cls(0)

        if self.flgWindow2 and self.now_scene != SCENE_STATUS["Ending"] and self.now_scene != 1000:
            self.insWindow.draw()
            self.insWindow.drawText(self.txtMsg.P_x, self.txtMsg.P_y, self.txtMsg.msg , JP_FONT)
        elif self.now_scene == SCENE_STATUS["Ending"] and self.now_scene != 1000:
            self.insWindow.draw()
            self.insWindow.drawText(self.txtMsg.P_x, self.txtMsg.P_y, self.txtMsg.msg , JP_FONT)
            if self.cnt >= 1.5:
                self.cnt = 0
                px.dither(1)
                self.now_scene = 1000
            else:
                self.cnt += 0.02
                px.dither(1-self.cnt)
            return            
            

        match self.now_scene:
            case 3: # SCENE_STATUS["Title"]
                px.blt(0,0, self.img, 0,0, px.width,px.height)
                px.text(180,230,"Easy Version.", px.frame_count//3%16)
                self.insMenu.draw()
                return
            case 4: # SCENE_STATUS["NameEntry"]
                if self.flgMenu:
                    self.insMenu.draw()
                else:
                    self.now_scene = SCENE_STATUS["Field"]
                    self.music = reloadBGM(self.now_scene)
                
                if self.flgWindow:
                    self.insWindow.draw()
                    self.insWindow.drawText(self.txtMsg.P_x, self.txtMsg.P_y, self.txtMsg.msg , JP_FONT)
                
                return
            case 1000:
                px.text(P_BLOCK_SIZE+2, px.height -self.cnt,                     
                        "Ｐｙｘｅｌ  （ＧａｍｅＥｎｇｉｎｅ）", 7, JP_FONT)
                px.text(P_BLOCK_SIZE+2, px.height -self.cnt + 8,                 
                        "                   ｂｙ   Ｔａｋａｓｈｉ  Ｋｉｔａｏ", 7, JP_FONT)
                px.text(P_BLOCK_SIZE+2, px.height -self.cnt + P_BLOCK_SIZE*3,    
                        "ＭｉｓａｋｉＦｏｎｔ  （Ｆｏｎｔ）", 7, JP_FONT)
                px.text(P_BLOCK_SIZE+2, px.height -self.cnt + 8 + P_BLOCK_SIZE*3,
                        "                   ｂｙ   Ｎｕｍ  Ｋａｄｏｍａ" ,7, JP_FONT)
                px.text(P_BLOCK_SIZE+2, px.height -self.cnt + P_BLOCK_SIZE*6,    
                        "８－ｂｉｔ ＢＧＭ ｇｅｎｅｒａｔｏｒ  （ＢＧＭｔｏｏｌ）", 7, JP_FONT)
                px.text(P_BLOCK_SIZE+2, px.height -self.cnt + 8 + P_BLOCK_SIZE*6,
                        "                   ｂｙ   ｆｒｅｎｃｈｂｒｅａｄ" ,7, JP_FONT)
                px.text(P_BLOCK_SIZE+2, px.height -self.cnt + P_BLOCK_SIZE*9,    
                        "Ｄｅｖｅｌｏｐｅｄ ｂｙ   ＭｏＱ", 7,JP_FONT)
                px.text(P_BLOCK_SIZE+2, px.height -self.cnt + P_BLOCK_SIZE*24,   "あそんでくださって　どうもありがとう　ございます！",7,JP_FONT)
                if self.cnt < 510:
                    self.cnt += 0.2
                else:
                    px.text(93, px.height -self.cnt + P_BLOCK_SIZE*26,
                            "－　Ｆｉｎ．－",7,JP_FONT)
                    
                    px.text(80, 230,
                            "(press key to quit)",7,JP_FONT)
                return

        if (self.now_scene == SCENE_STATUS["Battle"]) and not (self.flgWindow or self.flgMenu):
            self.insBattle.draw()
        else:   #　"Field","Town","Dungeon",etc...
            #マップ描画
            self.World.draw()

            #一般キャラ描画
            for i in range(1,len(OBJ_CHAR_LIST)):
                OBJ_CHAR_LIST[i].draw(self.World.B_drawStart, self.World.P_offset)
            #イベントキャラ描画
            if EVENT_STAT.get(7) == False:  #森裏門
                px.blt( ((91 -self.World.B_drawStart[X]-1)*P_BLOCK_SIZE) - self.World.P_offset[X],
                        ((209-self.World.B_drawStart[Y]-1)*P_BLOCK_SIZE) - self.World.P_offset[Y], IMGIDX_CHIP,
                          48,72, 16,16, colkey=0)
            if EVENT_STAT.get(8) == False:  #森ボス
                px.blt( ((52 -self.World.B_drawStart[X]-1)*P_BLOCK_SIZE) - self.World.P_offset[X],
                        ((107-self.World.B_drawStart[Y]-1)*P_BLOCK_SIZE) - self.World.P_offset[Y], IMGIDX_CHIP,
                          0,72, 16,16, colkey=0)
            if EVENT_STAT.get(9) == False:  #砂漠ボス
                px.blt( ((121-self.World.B_drawStart[X]-1)*P_BLOCK_SIZE) - self.World.P_offset[X],
                        ((226-self.World.B_drawStart[Y]-1)*P_BLOCK_SIZE) - self.World.P_offset[Y], IMGIDX_CHIP,
                          16,72, 16,16, colkey=0)
            if EVENT_STAT.get(12) == False:  #ドア１
                px.blt( ((39 -self.World.B_drawStart[X]-1)*P_BLOCK_SIZE) - self.World.P_offset[X],
                        ((38 -self.World.B_drawStart[Y]-1)*P_BLOCK_SIZE) - self.World.P_offset[Y], IMGIDX_CHIP,
                          32,72, 16,16, colkey=0)
            if EVENT_STAT.get(13) == False:  #ドア２
                px.blt( ((276-self.World.B_drawStart[X]-1)*P_BLOCK_SIZE) - self.World.P_offset[X],
                        ((17 -self.World.B_drawStart[Y]-1)*P_BLOCK_SIZE) - self.World.P_offset[Y], IMGIDX_CHIP,
                          32,72, 16,16, colkey=0)
            if EVENT_STAT.get(14) == False:  #ドア３
                px.blt( ((223-self.World.B_drawStart[X]-1)*P_BLOCK_SIZE) - self.World.P_offset[X],
                        ((66 -self.World.B_drawStart[Y]-1)*P_BLOCK_SIZE) - self.World.P_offset[Y], IMGIDX_CHIP,
                          32,72, 16,16, colkey=0)
            if EVENT_STAT.get(0) == False and px.frame_count%100 in (0,1,2,3):  #オリハルコイル　ヒント
                px.blt( ((28-self.World.B_drawStart[X]-1)*P_BLOCK_SIZE) - self.World.P_offset[X] + px.rndi(0,7),
                        ((179 -self.World.B_drawStart[Y]-1)*P_BLOCK_SIZE) - self.World.P_offset[Y] + px.rndi(-4,3), IMGIDX_CHIP, 40,40, 8,8, colkey=0)
            if EVENT_STAT.get(1) == False and px.frame_count%100 in (0,1,2):  #まどうバッテリ　ヒント
                px.blt( ((72-self.World.B_drawStart[X]-1)*P_BLOCK_SIZE) - self.World.P_offset[X] + px.rndi(0,7),
                        ((70 -self.World.B_drawStart[Y]-1)*P_BLOCK_SIZE) - self.World.P_offset[Y] + px.rndi(0,7), IMGIDX_CHIP, 40,40, 8,8, colkey=0)
            if EVENT_STAT.get(4) == False and px.frame_count%256 in (0,1):  #ゆうきのあかし　ヒント
                px.blt( ((268-self.World.B_drawStart[X]-1)*P_BLOCK_SIZE) - self.World.P_offset[X] + px.rndi(0,7),
                        ((135 -self.World.B_drawStart[Y]-1)*P_BLOCK_SIZE) - self.World.P_offset[Y] + px.rndi(0,7), IMGIDX_CHIP, 40,40, 8,8, colkey=0)
            if EVENT_STAT.get(4) and px.frame_count%32 in (0,1,2,3):  #ゆうきのさいだん　ヒント
                px.blt( ((180-self.World.B_drawStart[X]-1)*P_BLOCK_SIZE) - self.World.P_offset[X] + px.rndi(0,7),
                        ((209 -self.World.B_drawStart[Y]-1)*P_BLOCK_SIZE) - self.World.P_offset[Y] + px.rndi(0,7), IMGIDX_CHIP, 40,40, 8,8, colkey=0)
            if EVENT_STAT.get(4) and OBJ_CHAR_LIST[0].eq[2] != 4 and px.frame_count%100 in (0,1,2,3): #しんわのたてヒント
                px.blt( ((72-self.World.B_drawStart[X]-1)*P_BLOCK_SIZE) - self.World.P_offset[X] + px.rndi(0,7),
                        ((126 -self.World.B_drawStart[Y]-1)*P_BLOCK_SIZE) - self.World.P_offset[Y] + px.rndi(0,7), IMGIDX_CHIP, 40,40, 8,8, colkey=0)
            if EVENT_STAT.get(4) and OBJ_CHAR_LIST[0].eq[1] != 5 and px.frame_count%256 in (0,1): #むてきのよろいヒント
                px.blt( ((144-self.World.B_drawStart[X]-1)*P_BLOCK_SIZE) - self.World.P_offset[X] + px.rndi(0,7),
                        ((230 -self.World.B_drawStart[Y]-1)*P_BLOCK_SIZE) - self.World.P_offset[Y] + px.rndi(0,7), IMGIDX_CHIP, 40,40, 8,8, colkey=0)
            if OBJ_CHAR_LIST[0].Item[0][1] < 5 and px.frame_count%128 in (0,1,2):  #　ヒント
                px.blt( ((54-self.World.B_drawStart[X]-1)*P_BLOCK_SIZE) - self.World.P_offset[X] + px.rndi(0,7),
                        ((20 -self.World.B_drawStart[Y]-1)*P_BLOCK_SIZE) - self.World.P_offset[Y] + px.rndi(0,7), IMGIDX_CHIP, 40,40, 8,8, colkey=0)
            if OBJ_CHAR_LIST[0].Item[0][1] < 5 and px.frame_count%128 in (0,1,2):  #　ヒント
                px.blt( ((19-self.World.B_drawStart[X]-1)*P_BLOCK_SIZE) - self.World.P_offset[X] + px.rndi(0,7),
                        ((32 -self.World.B_drawStart[Y]-1)*P_BLOCK_SIZE) - self.World.P_offset[Y] + px.rndi(0,7), IMGIDX_CHIP, 40,40, 8,8, colkey=0)
            if OBJ_CHAR_LIST[0].Item[0][1] < 5 and px.frame_count%128 in (0,1,2):  #　ヒント
                px.blt( ((41-self.World.B_drawStart[X]-1)*P_BLOCK_SIZE) - self.World.P_offset[X] + px.rndi(0,7),
                        ((29 -self.World.B_drawStart[Y]-1)*P_BLOCK_SIZE) - self.World.P_offset[Y] + px.rndi(0,7), IMGIDX_CHIP, 40,40, 8,8, colkey=0)
            if OBJ_CHAR_LIST[0].Item[1][1] < 2 and px.frame_count%128 in (0,1,2):  #　ヒント
                px.blt( ((30-self.World.B_drawStart[X]-1)*P_BLOCK_SIZE) - self.World.P_offset[X] + px.rndi(0,7),
                        ((20 -self.World.B_drawStart[Y]-1)*P_BLOCK_SIZE) - self.World.P_offset[Y] + px.rndi(0,7), IMGIDX_CHIP, 40,40, 8,8, colkey=0)
            if OBJ_CHAR_LIST[0].Item[1][1] < 4 and px.frame_count%128 in (0,1,2):  #　ヒント
                px.blt( ((39-self.World.B_drawStart[X]-1)*P_BLOCK_SIZE) - self.World.P_offset[X] + px.rndi(0,7),
                        ((27 -self.World.B_drawStart[Y]-1)*P_BLOCK_SIZE) - self.World.P_offset[Y] + px.rndi(0,7), IMGIDX_CHIP, 40,40, 8,8, colkey=0)
            if OBJ_CHAR_LIST[0].Item[1][1] < 4 and px.frame_count%128 in (0,1,2):  #　ヒント
                px.blt( ((38-self.World.B_drawStart[X]-1)*P_BLOCK_SIZE) - self.World.P_offset[X] + px.rndi(0,7),
                        ((19 -self.World.B_drawStart[Y]-1)*P_BLOCK_SIZE) - self.World.P_offset[Y] + px.rndi(0,7), IMGIDX_CHIP, 40,40, 8,8, colkey=0)
            if EVENT_STAT.get(4) and px.frame_count%16 in (0,1,2,3):  #しれんのしま　ワープポイント　ヒント
                px.blt( ((193-self.World.B_drawStart[X]-1)*P_BLOCK_SIZE) - self.World.P_offset[X] + px.rndi(0,7),
                        ((175 -self.World.B_drawStart[Y]-1)*P_BLOCK_SIZE) - self.World.P_offset[Y] + px.rndi(0,7), IMGIDX_CHIP, 40,40, 8,8, colkey=0)


            #魔王城エリア
            if ((13 <= OBJ_CHAR_LIST[0].B_addr[X] <= 63) and (15 <= OBJ_CHAR_LIST[0].B_addr[Y] <= 65)) or ((64 <= OBJ_CHAR_LIST[0].B_addr[X] <= 79) and (20 <= OBJ_CHAR_LIST[0].B_addr[Y] <= 51)):
                if OBJ_CHAR_LIST[0].flgLantern == False:
                    px.rect(0, 0,
                            px.width, px.height/2-P_BLOCK_SIZE*1.5, 1)
                    px.rect(0, px.height/2+P_BLOCK_SIZE*1.5,
                            px.width, px.height/2-P_BLOCK_SIZE*1.5, 1)
                    px.rect(0, px.height/2-P_BLOCK_SIZE*1.5,
                            px.width/2-P_BLOCK_SIZE*1.5, 3*P_BLOCK_SIZE, 1)
                    px.rect(px.width/2+P_BLOCK_SIZE*1.5, px.height/2-P_BLOCK_SIZE*1.5,
                            px.width/2-P_BLOCK_SIZE*1.5, 3*P_BLOCK_SIZE, 1)
                elif OBJ_CHAR_LIST[0].LanternCount > 50 :
                    px.rect(0, 0,
                            px.width, px.height/2-P_BLOCK_SIZE*1.5 -P_BLOCK_SIZE*2, 1)
                    px.rect(0, px.height/2+P_BLOCK_SIZE*1.5+P_BLOCK_SIZE*2,
                            px.width, px.height/2-P_BLOCK_SIZE*1.5, 1)
                    px.rect(0, px.height/2-P_BLOCK_SIZE*1.5-P_BLOCK_SIZE*2,
                            px.width/2-P_BLOCK_SIZE*1.5-P_BLOCK_SIZE*2, 7*P_BLOCK_SIZE, 1)
                    px.rect(px.width/2+P_BLOCK_SIZE*1.5+P_BLOCK_SIZE*2, px.height/2-P_BLOCK_SIZE*1.5-P_BLOCK_SIZE*2,
                            px.width/2-P_BLOCK_SIZE*1.5-P_BLOCK_SIZE*2, 7*P_BLOCK_SIZE, 1)
                elif OBJ_CHAR_LIST[0].LanternCount > 0 :
                    px.rect(0, 0,
                            px.width, px.height/2-P_BLOCK_SIZE*1.5 -P_BLOCK_SIZE*1, 1)
                    px.rect(0, px.height/2+P_BLOCK_SIZE*1.5+P_BLOCK_SIZE*1,
                            px.width, px.height/2-P_BLOCK_SIZE*1.5, 1)
                    px.rect(0, px.height/2-P_BLOCK_SIZE*1.5-P_BLOCK_SIZE*1,
                            px.width/2-P_BLOCK_SIZE*1.5-P_BLOCK_SIZE*1, 7*P_BLOCK_SIZE, 1)
                    px.rect(px.width/2+P_BLOCK_SIZE*1.5+P_BLOCK_SIZE*1, px.height/2-P_BLOCK_SIZE*1.5-P_BLOCK_SIZE*1,
                            px.width/2-P_BLOCK_SIZE*1.5-P_BLOCK_SIZE*1, 7*P_BLOCK_SIZE, 1)

            #勇者描画
            OBJ_CHAR_LIST[0].draw()
            
            if self.flgWindow and self.flgMenu:
                self.insWindow.draw()
                self.insWindow.drawText(self.txtMsg.P_x, self.txtMsg.P_y, self.txtMsg.msg , JP_FONT)
                self.insMenu.draw()
            elif self.flgWindow:
                self.insWindow.draw()
                self.insWindow.drawText(self.txtMsg.P_x, self.txtMsg.P_y, self.txtMsg.msg , JP_FONT)
            elif self.flgMenu:
                self.insMenu.draw()

#デバッグ用
        if not IS_DEBUG:
            return
        
        if px.btnp(px.MOUSE_BUTTON_LEFT,8,4):
            px.rect(5,5,px.width-10,px.height-10,3)
            px.text(7,7,"pixel座標 X="+str(px.mouse_x)+" Y="+str(px.mouse_y),5,font=JP_FONT)
            px.text(7,19,"tile座標 X="+str(px.mouse_x//(P_BLOCK_SIZE/2))+" Y="+str(px.mouse_y//(P_BLOCK_SIZE/2)),5,font=JP_FONT)
            px.text(7,31,"tile ID ="+str(px.tilemap(0).pget(px.mouse_x//(P_BLOCK_SIZE/2),px.mouse_y//(P_BLOCK_SIZE/2))),5,font=JP_FONT)
            while True:
                px.flip()
                if px.btnp(px.MOUSE_BUTTON_LEFT,8,4):
                    break

#_/_/_/_/_/_/_/アプリケーション処理実行_/_/_/_/_/_/_/
App()