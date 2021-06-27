# -*- coding:utf-8 -*-
"""

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
■           Pygame によるウィンドウ表示を簡易化したモジュール                 ■
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊関数の説明＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊
screen_init(x,y,title)      #ウィンドウサイズ:x,y   左上に表示される文字列:title
screen_set(x,y,Fullscreen)  #ウィンドウサイズ:x,y   Fullscreen=1 有効
clear(r,g,b)                #引数省略可能 指定した色でスクリーンをクリア
draw(time_ms)          #描画を行う、絶対に呼び出されなければならない（引数は省略可能）

pos(x,y)                 #次回出力される時の座標を指定、左上が(0,0)
color(red,blue,green)    #次回出力される時の色を指定

font(size)                  #フォントサイズの指定
prints(text,theta)         #font関数で指定したサイズで文字列を出力 thetaで回転角度を指定[deg]

▼スタート座標:x,y Xサイズ:xx Yサイズ：yy 太さ:width（指定しないと塗りつぶされる）
line(x,y,xx,yy,width)       #線を出力　
box(x,y,xx,yy,width)        #四角形を出力
ellipse(x,y,xx,yy,width)    #楕円を出力

object = picload(name,colorkey)     #画像を読み込む　ファイル名:name 透明にする色(r,g,b):clrkey 無指定でもOK
picout(object)                      #画像の出力

●入力機器の状態を読み取る
key     #押されたキーの状態  K_<KEY>　のように格納される
curosr  #マウスカーソルの座標　(x,y)
click   #クリック状態　初期状態:0 左クリック：１　ホイールクリック:2　右クリック：３

＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊ミキサー(音声再生)の説明＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊
●ミュージックオブジェクト単体への操作
・作成（SE）     sound = pygame.mixer.sound.load("success.wav")  #wav形式のファイルのみ
・再生(SE)     sound.play(loops=-1,mixtime=0,fade_ms=0)        #loop=-1無限ループ mixtime=0最後まで再生 fade_ms=0フェードインなし

・作成(BGM)    pygame.mixer.music.load("levean_polkka.mp3")    #mp3でも何でもOK
・再生（BGM）    pygame.mixer.music.play(-1)#無限ループ


・停止         sound.stop()
・一時停止      sound.pause()
・再開         sound.unpause()
・フェードアウト   sound.fadeout(time_ms)

・音量取得      sound.get_volume()#0.0~1.0
・音量設定      sound.set_volume()#0.0~1.0
・再生時間取得   sound.get_length()#second

●ミュージックオブジェクト全体への操作
・全て停止      pygame.mixer.stop()
・全て一時停止   pygame.mixer.pause()
・全て再開      pygame.mixer.unpause()
・全てﾌｪｰﾄﾞｱｳﾄ   pygame.mixer.fadeout(time_ms)

●その他、設定など
・使用可能スピーカーを確保することで、音が途切れるのを防ぐ
pygame.miser.set_reserved(count)


"""
#
import pygame
from pygame.locals import *
import sys
import time
import numpy as np


SCR_RECT = Rect(0,0,800,480)

sc_size = [0,0]
sc_rate = [1.0,1.0]

clr = (0,0,0)#描画オブジェクトの色を指定(R,G,B)
ps = (0,0)#描画オブジェクトの中心（実際は左上）を指定(X,Y)

cursor = (0,0)#マウスカーソルの座標を保持(x,y)
click = 0#クリック状態を保持　ニュートラル:0 左クリック：１　ホイールクリック:2　右クリック：３
key = 0 #キーの状態を保持


scrn = 0#スクリーン情報を保持
fnt = 0#出力文字のフォント及びサイズを保持
def screen_init(x,y,title):
    pygame.init()

    infoObject = pygame.display.Info()
    w = infoObject.current_w
    h = infoObject.current_h
    print("disply size(",w,",",h,")")
    SCR_RECT = Rect(0,0,w,h)#初期の解像度を指定しておかないとフルスクリーンでやばい

    screen_set(x,y)
    pygame.display.set_caption(title)
def screen_set(x,y,full=0):
    global scrn,sc_size
    if(full==0):
        scrn = pygame.display.set_mode((x,y))
        pygame.mouse.set_visible(True)#Mouse hyouji suru
    else:
        scrn = pygame.display.set_mode((x,y),FULLSCREEN)
        pygame.mouse.set_visible(False)#Mouse hyouji sinai
    sc_size = [x,y]

def screen_resize(x,y):
    global scrn,sc_size,sc_rate
    sc_rate[0] = x/sc_size[0]
    sc_rate[1] = y/sc_size[1]
    screen_set(x,y)

def color(r,g,b):
    global clr
    clr = (r,g,b)
def pos(x,y):
    global ps,sc_rate
    ps = (int(x*sc_rate[0]),int(y*sc_rate[1]))
def clear(red=0,green=0,blue=0):
    scrn.fill((red,green,blue))

def font(size=16,name=None):
    global fnt,sc_rate
    fnt = pygame.font.Font(name,int(size*(sc_rate[0]+sc_rate[1])/2))

def prints(*texts,theta=0):
    global clr,fnt,scrn,ps
    text = "".join(map(str, texts))

    if(theta == 0):
        scrn.blit(fnt.render(text,True,clr),ps)
    else:
        txt = fnt.render(text,True,clr)
        txt = pygame.transform.rotate(txt,theta)
        rect = txt.get_rect()
        rect.center = ps
        scrn.blit(txt,rect)

def line(x,y,xx,yy,width=1):
    global clr,scrn
    pygame.draw.line(scrn,clr,(int(x*sc_rate[0]),int(y*sc_rate[1])),(int(xx*sc_rate[0]),int(yy*sc_rate[1])),width)

def box(x,y,xx,yy,width=0):#width >=0 のとき塗りつぶす
    global clr,scrn,sc_rate
    pygame.draw.rect(scrn,clr,Rect((int(x*sc_rate[0]),int(y*sc_rate[1])),(int(xx*sc_rate[0]),int(yy*sc_rate[1]))),width)

def ellipse(x,y,xx,yy,width=0):
    global clr,scrn,sc_rate
    pygame.draw.ellipse(scrn,clr,((int(x*sc_rate[0]),int(y*sc_rate[1])),(int(xx*sc_rate[0]),int(yy*sc_rate[1]))),width)

def picload(name,clrkey = None ,size_x=None,size_y=None):
    image = pygame.image.load(name).convert()
    if(clrkey != None):
        if clrkey == 0:
            image.convert_alpha()
        else:
            if(clrkey == -1):
                clrkey = image.get_at((1,1))
            image.set_colorkey(clrkey)

    if(size_x != None and size_y != None):
        image = pygame.transform.scale(image, (int(size_x*sc_rate[0]), int(size_y*sc_rate[1])))

    return image

def picout(image,sizex=None,sizey=None):
    global ps,scrn,sc_rate
    img = image
    if(sizex != None and sizey != None):
        img = pygame.transform.scale(image, (int(sizex*sc_rate[0]), int(sizey*sc_rate[1])))
    scrn.blit(img,ps)

def picout_from_opencvs_capboard(img,sizex,sizey):
    try:
        img = np.array(img)
        cvimg = img[:,:,::-1]
        shape = cvimg.shape[1::-1]
        cvimg =  pygame.image.frombuffer(cvimg.tostring(), shape, 'RGB')
        cvimg = pygame.transform.scale(cvimg, (sizex, sizey))
        picout(cvimg)
    except ValueError:
        pass

def draw(wait=10):#必ず記述する
    pygame.display.update()#画面へ描画
    pygame.time.wait(wait)

    #イベント
def check(exit_now = False):
    global cursor,click,key,sc_rate
    key = 0
    for event in pygame.event.get():#特殊条件から
        if(event.type == MOUSEBUTTONDOWN):#マウスの状態を取得
            click = event.button
        if(event.type == MOUSEBUTTONUP):
            click = 0
        if(event.type == MOUSEMOTION):
            cursor = pygame.mouse.get_pos()
            cursor = (int(cursor[0]/sc_rate[0]),int(cursor[1]/sc_rate[1]))

        if(event.type == KEYDOWN):
            key = event.key

            #Key == 27 Escape

        if(key==27):
            pygame.quit()
            sys.exit()

        if(event.type == QUIT):#閉じる
            if(exit_now):
                pygame.quit()
                sys.exit()
            else:
                return True

def music_init():
    pygame.mixer.quit()
    pygame.mixer.init(frequency=44100,size=16,channels=2,buffer=2048)
    pygame.mixer.stop()

bgm_volume = 0.5
def bgmload(name):
    global bgm_volume
    pygame.mixer.music.fadeout(300)
    pygame.mixer.music.load(name)
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.5)
def seload(name):
    snd = pygame.mixer.Sound(name)
    snd.set_volume(0.4)
    return snd
