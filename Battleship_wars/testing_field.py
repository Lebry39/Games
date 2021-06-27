
import disp
import time
import numpy as np
import random

import field
from field import Field
from field import SCREEN_X_SIZE
from field import SCREEN_Y_SIZE
from field import MAX_FRAME_RATE
from field import SHIP_HIT_RANGE
from field import fps_controller
from field import fps_draw
from field import get_fps

from battel_ship import Battleship
from battel_ship import MAX_HIT_POINT
from battel_ship import DIRECTION_UP
from battel_ship import DIRECTION_DOWN

import gun_modules as gn

"""
ガンモジュールを試せます
"""
gun_module = gn.Ray_Wall



def main():
    from disp import pygame as pg
    #disp.screen_resize(400,500)

    field = Field()
    field.auto_wall_setting(0)

    ship = Battleship(field,DIRECTION_UP)
    ship.init_key_asign()
    ship.set_pos(400,750)

    ship_a = Battleship(field,DIRECTION_DOWN)
    ship_a.set_pos(400,200)


    field.set_item(400,400,gun_module ,DIRECTION_UP)

    #********** メインループ ************
    while(not ship_a.is_dead()):
        disp.color(0,0,0)
        disp.box(0,0 ,SCREEN_X_SIZE,SCREEN_Y_SIZE)

        fps_controller()
        fps_draw()


        #***************描画　キー受け付け　処理***************
        field.moving_items()
        field.draw_items()
        field.using_items()

        field.reserve_cmd_to_move_lists()
        field.move_lists_executor(delay_s=0.01)
        field.draw_ships()

        field.moving_rays()
        field.draw_rays()

        field.draw_walls()
        field.refrect_by_wall()

        field.draw_status()
        field.auto_wall_setting(30)

        #*************************************************

        disp.color(60,60,60)
        disp.line(0,SCREEN_Y_SIZE//2, SCREEN_X_SIZE,SCREEN_Y_SIZE//2,1)

        #画面の描画及びキーチェック
        disp.draw(0)
        disp.check(True)


if __name__ == "__main__":
    while(True):
        main()
