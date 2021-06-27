import disp
from disp import pygame as pg

import time
import numpy as np
import random

from field import Field
from field import fps_controller
from field import get_fps

from field import SCREEN_X_SIZE
from field import SCREEN_Y_SIZE
from field import MAX_FRAME_RATE
from field import SHIP_HIT_RANGE
from field import DIRECTION_DOWN
from field import DIRECTION_UP

"""
    #設定値
"""
MAX_HIT_POINT = 1000
MAX_ITEM_GAGE = 100




class Gun:

    def __init__(self):
        self.__rays_before_shoted_time_s = 0

        import gun_modules
        #このシップで使うガンモジュールのクラスを渡す
        self.eq_gun_module = [gun_modules.Straight , gun_modules.Splash]

        self.standing_module_id = 0

    def set_gun_module(self,gun_module):
        self.eq_gun_module[1] = gun_module

    def get_gun_module(self):
        return self.eq_gun_module[self.standing_module_id]

    def change_gun_module(self,ids=None):
        #1 <--> 0
        if ids == None:
            self.standing_module_id = 1 - self.standing_module_id
        else:
            self.standing_module_id = ids

    def can_shot(self):
        span_s = time.time() - self.__rays_before_shoted_time_s #前回発射からの経過時間

        if span_s >= self.eq_gun_module[self.standing_module_id].rays_interval_secs:
            self.__rays_before_shoted_time_s = time.time()
            return True

        #span_sはマイナスであってはいけない
        if span_s < 0:
            self.__rays_before_shoted_time_s = time.time()

        return False

    def set_shooted_ray(self,x,y,direction=0):

        from random import random
        rnd = 1.0 - random()*2

        ray = self.eq_gun_module[self.standing_module_id]( x,y ,direction,rnd )
        return ray



#シップの画像
clr_ship = ["g","b","r","y"]
pic_ship_up = [disp.picload("./data/pic/ship_"+clr_ship[i]+"_up.png",-1,size_x=48,size_y=48)for i in range(4)]
pic_ship_down = [disp.picload("./data/pic/ship_"+clr_ship[i]+"_down.png",-1,size_x=48,size_y=48)for i in range(4)]
class Battleship():
    """
        obj = Batteleship(obj_Field,DIRECTION_of_ship)
        １つのバトルシップに対して１つ
        フィールドオブジェクトを受け取る必要がある

        機体の向き direction_of_ship : DIRECTION_UP or DIRECTION_DOWN
    """

    def __init__(self,obj_field,direction_of_ship = DIRECTION_UP):

        self.state = {
                    "ID"   :None,
                    "NAME" :"ship-",
                    "HP"   : MAX_HIT_POINT,
                    "POS_X":500,
                    "POS_Y":500,
                    "SPEED_PER_SECS":300,
                    "DIRECTION":0,
                    "ITEM_GAGE":0,
                    }

        self.field = obj_field
        self.field.register_ship(self)

        self.state["NAME"] += str(self.state["ID"])

        self.state["DIRECTION"] = direction_of_ship

        if direction_of_ship == DIRECTION_UP:
            self.pic_ship = pic_ship_up[self.state["ID"]]
        else:
            self.pic_ship = pic_ship_down[self.state["ID"]]

        self.key_asign = {
                        "UP":-1,
                        "DOWN":-1,
                        "RIGHT":-1,
                        "LEFT":-1,
                        "MAIN_SHOT":-1,
                        "SUB_SHOT":-1,
                         }

        self.__move_list = []
        self.__move_exec_timer = 0

        self.gun = Gun()

    def init_key_asign(self):
        self.key_asign = {
                        "UP":pg.K_UP,
                        "DOWN":pg.K_DOWN,
                        "RIGHT":pg.K_RIGHT,
                        "LEFT":pg.K_LEFT,
                        "MAIN_SHOT":pg.K_z,
                        "SUB_SHOT":pg.K_x,
                         }

    def set_key_asign(self, UP,DOWN,RIGHT,LEFT , MAIN_SHOT,SUB_SHOT):
        """
            set_key_asign(self, UP,DOWN,RIGHT,LEFT , MAIN_SHOT,SUB_SHOT)
        """

        self.key_asign = {
                        "UP":UP,
                        "DOWN":DOWN,
                        "RIGHT":RIGHT,
                        "LEFT":LEFT,
                        "MAIN_SHOT":MAIN_SHOT,
                        "SUB_SHOT":SUB_SHOT,
                         }

    def set_pos(self,x,y):
        self.state["POS_X"] = x
        self.state["POS_Y"] = y

    def set_move_list(self,cmd=None):
        """
        キー入力を受け付けて、それをMoveListに登録する
        """
        if self.is_dead():return

        key = disp.pygame.key.get_pressed()

        if cmd == None:
            if key[self.key_asign["UP"]]    : self.__move_list.append("UP")
            if key[self.key_asign["DOWN"]]  : self.__move_list.append("DOWN")
            if key[self.key_asign["RIGHT"]] : self.__move_list.append("RIGHT")
            if key[self.key_asign["LEFT"]]  : self.__move_list.append("LEFT")
        else:
            if cmd=="UP"      : self.__move_list.append("UP")
            if cmd=="DOWN"    : self.__move_list.append("DOWN")
            if cmd=="RIGHT"   : self.__move_list.append("RIGHT")
            if cmd=="LEFT"   : self.__move_list.append("LEFT")


        if key[self.key_asign["SUB_SHOT"]] or cmd=="SUB_SHOT":
            self.gun.change_gun_module(1)
            if self.gun.can_shot():
                self.__move_list += ["SHOT" for i in range(self.gun.get_gun_module().rays_included_num)]

        elif key[self.key_asign["MAIN_SHOT"]] or cmd=="MAIN_SHOT":
            self.gun.change_gun_module(0)
            if self.gun.can_shot():
                self.__move_list += ["SHOT" for i in range(self.gun.get_gun_module().rays_included_num)]

    def move_list_executor(self,delay_s=0.01):
        """
        delay_s秒ごとにMoveListの内容を実行する
        """
        span_s = time.time() - self.__move_exec_timer
        if span_s < 0 :self.__move_exec_timer = time.time()

        if delay_s <= span_s:
            for cmd in self.__move_list:
                self.move_at_key(cmd)

            self.state["ITEM_GAGE"] += 15*delay_s#毎秒２０点アイテム出現ゲージが貯まる
            self.state["ITEM_GAGE"] -= self.__move_list.count("SHOT")*200*delay_s#弾を打つとアイテム出現ゲージが減少
            if self.state["ITEM_GAGE"] < 0 : self.state["ITEM_GAGE"] = 0

            if self.state["ITEM_GAGE"] > MAX_ITEM_GAGE:#アイテム出現ゲージが最大
                self.state["ITEM_GAGE"] = 0
                self.field.set_random_items(self)


            self.__move_list.clear()
            self.__move_exec_timer = time.time()



        #場外を引き戻す
        if self.state["POS_X"] < 0:
            self.state["POS_X"] = 0

        if self.state["POS_X"] > SCREEN_X_SIZE:
            self.state["POS_X"] = SCREEN_X_SIZE

        if self.state["POS_Y"] < 0:
            self.state["POS_Y"] = 0

        if self.state["POS_Y"] > SCREEN_X_SIZE:
            self.state["POS_Y"] = SCREEN_X_SIZE

    def move_at_key(self,key):
        import gun_modules
        spd_crrect = 1 / get_fps()

        if key == "UP":
            self.state["POS_Y"] -= self.state["SPEED_PER_SECS"] * spd_crrect

        elif key == "DOWN":
            self.state["POS_Y"] += self.state["SPEED_PER_SECS"] * spd_crrect

        elif key == "RIGHT":
            self.state["POS_X"] += self.state["SPEED_PER_SECS"] * spd_crrect

        elif key == "LEFT":
            self.state["POS_X"] -= self.state["SPEED_PER_SECS"] * spd_crrect

        elif key == "SHOT":
            if self.state["DIRECTION"] == DIRECTION_UP:
                data = self.gun.set_shooted_ray( self.state["POS_X"] , self.state["POS_Y"]-24 , self.state["DIRECTION"] )
            else:
                data = self.gun.set_shooted_ray( self.state["POS_X"] , self.state["POS_Y"]+24 , self.state["DIRECTION"] )

            self.field.set_to_ray_map( self.state["ID"] , data )

    def to_damage(self,power):
        self.state["HP"] -= power
        if self.state["HP"] < 0 :
            self.state["HP"] = 0

    def to_helth(self,helth):
        self.state["HP"] += helth
        if self.state["HP"] > MAX_HIT_POINT :
            self.state["HP"] = MAX_HIT_POINT

    def is_dead(self):
        if self.state["HP"] <= 0:
            self.state["HP"] = 0
            self.state["ITEM_GAGE"] = 0
            return True
        return False

    def draw(self):

        pos_x = self.state["POS_X"]
        pos_y = self.state["POS_Y"]

        if self.is_dead():
            # disp.pos(pos_x,pos_y)
            # disp.font(30)
            # disp.color(0,255,0)
            # disp.prints("x")
            return


        if self.state["DIRECTION"] == 0:#is UP?
            pos_x -= 24
            pos_y -= 24

        else:
            pos_x -= 24
            pos_y -= 24

        disp.pos(pos_x,pos_y)
        disp.color(0,255,0)
        disp.font(size=100)

        disp.picout(self.pic_ship)

        #当たり判定の円
        disp.color(127,127,127)
        disp.ellipse(self.state["POS_X"]-SHIP_HIT_RANGE/2 , self.state["POS_Y"]-SHIP_HIT_RANGE/2 , SHIP_HIT_RANGE,SHIP_HIT_RANGE)

        #HPが０になったら赤くなる　通常時白
        disp.font(20)
        disp.color(255,255,255)
        if self.state["HP"] <= 0:
            disp.color(255,0,0)

        #ラベルの基準座標
        label_x = self.state["POS_X"]-30
        label_y = self.state["POS_Y"]+30
        if self.state["DIRECTION"] == DIRECTION_DOWN:
            label_y -= 100

        # #名前の表示
        # disp.pos(label_x,label_y)
        # disp.prints(self.state["NAME"])

        #HPバー
        ber =  70 * (self.state["HP"]/MAX_HIT_POINT)
        if ber > 0:
            disp.box(label_x,label_y, ber,10)

        #アイテムゲージ
        label_y += 12
        disp.color(127,0,255)
        if self.state["ITEM_GAGE"] >= MAX_ITEM_GAGE*0.95 : disp.color(255,0,127)
        ber =  70 * (self.state["ITEM_GAGE"]/MAX_ITEM_GAGE)
        if ber > 0:
            disp.box(label_x,label_y, ber,3)

    def play_anime(self,time_s):
        x = self.state["POS_X"]
        y = self.state["POS_Y"]

        max_size = 800
        min_size = 100

        max_time_s = 0.5

        disp.color(240,255,240)

        size = (max_size-min_size) * (time_s/max_time_s) + min_size
        if size <= max_size:
            disp.ellipse(x-size/2,y-size/2 ,size,size ,1)

        size *= 0.7
        if size <= max_size:
            disp.ellipse(x-size/2,y-size/2 ,size,size ,2)

        size *= 0.7
        if size <= max_size:
            disp.ellipse(x-size/2,y-size/2 ,size,size ,3)

        if size > max_size:
            return False

        return True
