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

import gun_modules

if __name__ == "__main__":
    from disp import pygame as pg
    #disp.screen_resize(400,500)

    field = Field()
    field.auto_wall_setting(0)

    ship = Battleship(field,DIRECTION_UP)
    ship.init_key_asign()
    ship.set_pos(400,750)


    ship_E = []
    is_rights = [True,False,True]
    is_main_shot = [True,False,True]

    for i in range(2):
        ship_E.append(Battleship(field,DIRECTION_DOWN))
        ship_E[i].set_pos(200*(i+1),100+(i+1)*50)
   
    #********** メインループ ************
    while(True):
        disp.color(0,0,0)
        disp.box(0,0 ,SCREEN_X_SIZE,SCREEN_Y_SIZE)

        fps_controller(60)
        fps_draw()

        for i in range(1):#len(ship_E)
            ship_e = ship_E[i]

            if ship.state["POS_X"]-150 > ship_e.state["POS_X"]:
                is_rights[i] = True
                if random.randint(0,2) == 0: is_main_shot[i] = not is_main_shot[i]

            if ship.state["POS_X"]+150 < ship_e.state["POS_X"]:
                is_rights[i] = False
                if random.randint(0,2) == 0: is_main_shot[i] = not is_main_shot[i]

            if is_rights[i]:
                ship_e.set_move_list(cmd="RIGHT")
            else:
                ship_e.set_move_list(cmd="LEFT")


            if is_main_shot[i]:
                ship_e.set_move_list(cmd="MAIN_SHOT")
            else:
                ship_e.set_move_list(cmd="SUB_SHOT")


        #***************描画　キー受け付け　処理***************
        field.moving_items()
        field.draw_items()
        field.using_items()

        field.reserve_cmd_to_move_lists()
        field.move_lists_executor(delay_s=(1/60))
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

        #画面病が及びキーチェック
        disp.draw(0)
        if(disp.check()):
            break
