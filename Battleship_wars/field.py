import disp
import time
import numpy as np
import random


"""
    # 設定値
"""
SCREEN_X_SIZE = 800
SCREEN_Y_SIZE = 800
STATUS_BER_LENGTH = 150

MAX_FRAME_RATE = 200
SHIP_HIT_RANGE = 10

"""
    # 定数
"""
DIRECTION_UP = 0
DIRECTION_DOWN = 1

#ランダムで出現するガンモジュールのセット
def get_setted_items():
    import gun_modules as gn

    items = [ gn.Laser, gn.Meteo , gn.Circle,
              gn.Delay, gn.Mine  , gn.Sine , gn.Ray_Wall]

    SETTED_ITEMS = []

    nx = sum([1 for i in items if i.rank!="S"])
    ns = sum([1 for i in items if i.rank=="S"])
    per = 0.2

    no_s_num = (ns/per - ns)
    clone_num = max( 1 , no_s_num/nx )

    for itm in items:
        if itm.rank!="S":
            SETTED_ITEMS += [itm for i in range(clone_num)]
        else:
            SETTED_ITEMS.append(itm)

    return SETTED_ITEMS




#画面の初期設定
disp.screen_init( (SCREEN_X_SIZE+STATUS_BER_LENGTH) , SCREEN_Y_SIZE , "BATTEL SHIPS")
import gun_modules


calc_fps_counter = 0
calc_fps_before_times = 0
calc_fps_fps = MAX_FRAME_RATE
calc_fps_T = 0
def fps_controller(max_fps = None):
    global calc_fps_counter,calc_fps_before_times,calc_fps_fps,calc_fps_T

    if max_fps == None:
        wait_s = 1 / MAX_FRAME_RATE - (time.time()-calc_fps_T)
    else:
        wait_s = 1 / max_fps - (time.time()-calc_fps_T)

    if  wait_s >= 0:
        time.sleep(wait_s)

    calc_fps_counter += 1
    if calc_fps_counter >= 10 :
        calc_fps_fps = calc_fps_counter // (time.time()-calc_fps_before_times)

        calc_fps_counter = 0
        calc_fps_before_times = time.time()

    calc_fps_T = time.time()

def fps_draw():
    disp.font(20)
    disp.color(0,255,0)
    disp.pos(0,0)
    disp.prints("fps "+str(get_fps()))

def get_fps():
    if(calc_fps_fps < 1):
        return MAX_FRAME_RATE

    return calc_fps_fps



class Wall:
    def __init__(self, x,y, size_x,size_y ,  is_throuth_rays=False ,is_hidden=False ,durability=float("inf")):
        self.pos_x = x
        self.pos_y = y

        self.size_x = size_x
        self.size_y = size_y

        self.is_throuth_rays = is_throuth_rays
        self.is_hidden = is_hidden

        self.max_durability = durability
        self.durability = durability

    def is_del_ray(self,ray):
        if self.is_throuth_rays:
            return False

        if self.is_into_the_wall(ray.pos_x,ray.pos_y):
            import gun_modules as gn

            self.durability -= ray.rays_power
            if type(ray) == gn.Straight:
                self.durability -= ray.rays_power*4

            return True

        return False

    def is_broken(self):
        if self.durability <= 0 : return True
        return False

    def is_into_the_wall(self,x,y):
        end_x = self.pos_x + self.size_x
        end_y = self.pos_y + self.size_y

        if x >= self.pos_x and x <= end_x:
            if y >= self.pos_y and y <= end_y:
                return True
        return False

    def get_refrected_move(self,x,y):

        if not self.is_into_the_wall(x,y):
            return (0,0)

        end_x = self.pos_x + self.size_x
        end_y = self.pos_y + self.size_y

        to_x = self.pos_x - x
        to_y = self.pos_y - y

        if abs(to_x) > abs(end_x - x):
            to_x = end_x - x

        if abs(to_y) > abs(end_y - y):
            to_y = end_y - y

        if (to_x+x) <= 0 or (to_x+x) >= SCREEN_X_SIZE:#xへの移動は画面外にでる？
            return (0,to_y)

        else:
            if abs(to_x) < abs(to_y):
                return (to_x,0)
            else:
                return (0,to_y)


        return (0,0)

    def draw(self):
        if self.is_hidden:
            return

        disp.color(255,255,255)

        if self.is_throuth_rays or self.max_durability == float("inf"):
            disp.box(self.pos_x,self.pos_y,self.size_x,self.size_y, 1)

        else:
            hp_per = 0.93 + 0.07*(self.durability/self.max_durability)
            span = self.size_y - self.size_y * hp_per
            stage = self.size_y/(span+1)

            for i in range(int(stage)):
                y = self.pos_y+ i*(span+1)
                disp.box(self.pos_x,y, self.size_x ,1)


class Field:
    """
        フィールド全体で共有するデータの管理を行う
        バトルシップへフィールドオブジェクトを登録する
    """
    def __init__(self):


        """
            【 ray_map 】
            フィールド上にいるシップの弾を管理する
            ray_map[(int)id] -> [{ "X":x , "Y":y , "MODULE":ins , "DIRECTION":direction , "RND":rnd },...]
            各弾の座標            :x,y
            弾変移インスタンス       : obj.calc(delta_time_s)  return of (d_x , d_y)
            弾の進行方向          :direction => 0(UP) => 1(DOWN)
            乱数値               :rnd = (+1.00 ~ -1.00)

        """
        self.__rays_map = []

        #ray_hit_animation = [{"X":x , "Y":y , "MODULE":ins , "TIME_S":f}, ...]
        self.__animation = []

        self.__ray_before_times = time.time()
        self.__rays_display_window = { "X":SCREEN_X_SIZE,"Y":SCREEN_Y_SIZE }

        self.__next_ships_id = 0

        #state = [ship_obj,]
        self.__registered_ship_obj = []

        self.walls = [] #walls[obj_Wall,...]
        self.__auto_walls_before_times = time.time()
        self.residual_generate_walls = 0

        self.items = [] #items[obj_gun_module,...]
        self.__item_before_times = time.time()

    #シップ番号を割り当てる、重複があってはいけない
    def __asign_to_ship_id(self):
        nx_id = self.__next_ships_id
        self.__next_ships_id += 1

        self.__rays_map.append([])#新しいシップのために__rays_mapを作る
        return nx_id

    def register_ship(self,ship):
        if ship.state["ID"] != None:
            raise "REGISTER SHIP ERROR : This ship has already registered."

        ship.state["ID"] = self.__asign_to_ship_id()

        self.__registered_ship_obj.append(ship)
    def reserve_cmd_to_move_lists(self):
        for ship in self.__registered_ship_obj:
            ship.set_move_list()
    def move_lists_executor(self,delay_s):
        for ship in self.__registered_ship_obj:
            ship.move_list_executor(delay_s)
    def draw_ships(self):
        for ship in self.__registered_ship_obj:
            ship.draw()

    def set_to_ray_map(self,r_id,ray_info):
        self.__rays_map[ r_id ].append(ray_info)
    def moving_rays(self):

        def is_out_of_window(x,y):
            w_y = self.__rays_display_window["Y"] +100
            if y > w_y or y < 0-100:
                return True


            return False

        # TODO: 移動ライン上に機体が有るかを調べる必要がある。　これでは弾速が速い弾の当たり判定が大きくなってしまう。
        def damage_to_ship(ray , dx,dy):
            fm_x = min( ray.pos_x , ray.pos_x+dx)
            fm_y = min( ray.pos_y , ray.pos_y+dy)

            to_x = max( ray.pos_x, ray.pos_x+dx)
            to_y = max( ray.pos_y, ray.pos_y+dy)

            for ship in self.__registered_ship_obj:
                if ship.is_dead() : continue

                #発射方向と同じ向きの機体には当たらない
                if ship.state["DIRECTION"] == ray.direction:
                    continue

                x = ship.state["POS_X"]
                y = ship.state["POS_Y"]

                if ( fm_x < (x + SHIP_HIT_RANGE) and to_x > (x - SHIP_HIT_RANGE) ) and \
                 (fm_y < (y+SHIP_HIT_RANGE) and to_y > (y-SHIP_HIT_RANGE)):#移動範囲の中に入っていた

                    ship.to_damage(ray.rays_power)

                    if ship.is_dead():#今の弾で死んだ
                        dead = {"MODULE":ship ,"TIME_S":0 }
                        self.__animation.append(dead)

                    return True

            return False

        times_span_s = time.time() - self.__ray_before_times

        #弾の移動を適用
        for own_ship_id in range( len(self.__rays_map) ):

            i_r = 0
            while( i_r < len(self.__rays_map[own_ship_id]) ):
                ray = self.__rays_map[own_ship_id][i_r]

                #今回の動作量を受け取る d=(x,y)
                d = ray.calc( times_span_s )

                if damage_to_ship( ray ,d[0],d[1] ):#敵機体に命中した
                    del self.__rays_map[own_ship_id][i_r]

                    hit = {"MODULE":ray ,"TIME_S":0 }
                    self.__animation.append( hit )

                else:
                    #弾の移動を反映させる
                    ray.pos_x += d[0]
                    ray.pos_y += d[1]

                    if is_out_of_window( ray.pos_x,ray.pos_y ):
                        del self.__rays_map[own_ship_id][i_r]
                        #画面外へ出た弾を削除
                        #注意 : i+=1 をしていないのは、現在の要素を消したことで,現在のiが,(i+1)の場所を指すから

                    elif len(self.walls) != 0:
                        for i_w in range(len(self.walls)):
                            if self.walls[i_w].is_del_ray(ray):
                                del self.__rays_map[own_ship_id][i_r]
                                if self.walls[i_w].is_broken(): del self.walls[i_w]
                                hit = {"MODULE":ray ,"TIME_S":0 }
                                self.__animation.append( hit )
                                break
                        i_r += 1
                    else:
                        i_r += 1

        #アニメーションを適用
        i = 0
        while( i < len(self.__animation)):
            anime = self.__animation[i]

            anime["TIME_S"] += times_span_s

            if anime["MODULE"].play_anime(anime["TIME_S"]):
                i += 1
            else:
                del self.__animation[i]

        self.__ray_before_times = time.time()
    def draw_rays(self):

        for own_ship_id in range(len(self.__rays_map)):
            for ray in self.__rays_map[own_ship_id]:

                if ray.direction == DIRECTION_UP:#UP
                    disp.color(0,255,180)
                else:#DOWN
                    disp.color(255,220,0)

                ray.draw()

    def set_wall(self,pos_x,pos_y, size_x,size_y ,is_throuth_rays=False,is_hidden=False,durability=float("inf")):
        self.walls.append( Wall(pos_x,pos_y, size_x,size_y, is_throuth_rays , is_hidden, durability) )
    def auto_wall_setting(self,delay_s=0):
        span = time.time() - self.__auto_walls_before_times

        if span >= delay_s:
            durability = 5000

            self.walls.clear()

            wall_size_y = 50
            self.set_wall( 0, SCREEN_Y_SIZE/2-wall_size_y/2 , SCREEN_X_SIZE,wall_size_y , is_throuth_rays=True , is_hidden=True , durability=0)


            px = SCREEN_X_SIZE/8
            py = SCREEN_Y_SIZE/2-10
            sx = SCREEN_X_SIZE/12
            sy = 20

            for i in range(2):
                self.set_wall( px , py , sx,sy , is_throuth_rays=False , is_hidden=False , durability=durability)
                self.set_wall( px + sx*1+1 , py , sx,sy , is_throuth_rays=False , is_hidden=False , durability=durability)
                self.set_wall( px + sx*2+1 , py , sx,sy , is_throuth_rays=False , is_hidden=False , durability=durability)

                px = SCREEN_X_SIZE*5/8

            self.__auto_walls_before_times = time.time()
        else:
            self.residual_generate_walls = delay_s - span

    def refrect_by_wall(self):
        for ship in self.__registered_ship_obj:
            for w in self.walls:
                d = w.get_refrected_move(ship.state["POS_X"],ship.state["POS_Y"])
                ship.state["POS_X"] += d[0]
                ship.state["POS_Y"] += d[1]
    def draw_walls(self):
        for w in self.walls:
            w.draw()

    def set_random_items(self,obj_ship):
        from battel_ship import MAX_HIT_POINT
        from battel_ship import MAX_ITEM_GAGE

        from gun_modules import ITEM_GET_RANGE

        def rnd_x(no_x=-1000):
            while(True):
                x = 10 + random.random() * (SCREEN_X_SIZE-10)
                if (x+ITEM_GET_RANGE < obj_ship.state["POS_X"] or x-ITEM_GET_RANGE > obj_ship.state["POS_X"]) and \
                    (x+ITEM_GET_RANGE < no_x or x-ITEM_GET_RANGE > no_x):
                    return x

        y = SCREEN_Y_SIZE/2
        dy = ITEM_GET_RANGE
        if obj_ship.state["DIRECTION"] == DIRECTION_DOWN:
            dy = -dy


        setted_items = get_setted_items()
        g_x = rnd_x()
        self.set_item(g_x, y+dy, random.choice(setted_items) ,obj_ship.state["DIRECTION"])

        if obj_ship.state["HP"] <= MAX_HIT_POINT//2:#HPが半分の時回復アイテム出現
            h_x = rnd_x(g_x)
            self.set_helth_item(h_x,y+dy,obj_ship.state["DIRECTION"])


        #TODO:アイテム出現ゲージが最大になった時、モジュールが出現する。
        #出現座標は y=ship_y x=(0~SCREEN_X_SIZE) & x!=shipx±30
        #なお、HPが５０％以下のとき、モジュール＋回復アイテムが同時に出現する。
        #回復量は25~50%回復するようにする
    def set_item(self,pos_x,pos_y,module ,direction):
        self.items.append( gun_modules.item_gun_module(pos_x,pos_y ,module ,direction) )
    def set_helth_item(self,pos_x,pos_y,direction):
        self.items.append( gun_modules.item_health(pos_x,pos_y,direction) )
    def using_items(self):
        for ship in self.__registered_ship_obj:
            i = 0
            while(i < len(self.items)):
                if self.items[i].can_use( ship.state["POS_X"],ship.state["POS_Y"] ):
                    if type(self.items[i]) != gun_modules.item_health:
                        ship.gun.set_gun_module( self.items[i].get_module() )
                    else:
                        self.items[i].health(ship)

                    del self.items[i]

                else:
                    i += 1
    def draw_items(self):
        for item in self.items:
            item.draw()
    def moving_items(self):
        span = time.time() - self.__item_before_times

        i = 0
        while(i < len(self.items)):
            self.items[i].calc(span)
            if self.items[i].pos_y > SCREEN_Y_SIZE+100 or self.items[i].pos_y < -100:
                del self.items[i]
            else:
                i += 1


        self.__item_before_times = time.time()

    def draw_status(self):
        from battel_ship import MAX_HIT_POINT
        from battel_ship import MAX_ITEM_GAGE

        def draw(px,py,ship ):
            disp.color(80,80,80)
            disp.box(px+5,py+25 , 140,freme_size ,0)

            disp.color(255,255,255)
            disp.pos(px+36,py+40)
            disp.prints(ship.state["NAME"].center(16))

            disp.pos(px+10,py+36)
            disp.picout(ship.pic_ship,36,36)

            disp.color(0,0,0)
            disp.line(px+10,py+80 , px+140,py+80)

            hp_per = 100*ship.state["HP"]/MAX_HIT_POINT
            if hp_per >= 50   : disp.color(0,200,0)
            elif hp_per >= 25 : disp.color(200,200,0)
            else              : disp.color(200,20,0)
            disp.pos(px+75,py+110)
            disp.font(36)
            disp.prints("%03d" % hp_per,"%")

            disp.pos(px+100,py+150)
            disp.font(30)
            disp.color(200,0,200)
            item_gage = round( MAX_ITEM_GAGE - ship.state["ITEM_GAGE"] , 1)
            disp.prints(item_gage)

            sub_shot_obj = gun_modules.item_gun_module( px+30,py+110 ,ship.gun.eq_gun_module[1] ,ship.state["DIRECTION"])#装備中のモジュールをアイテムとして生成 動かないアイテム
            sub_shot_obj.draw()

            if ship.is_dead():
                disp.color(10,10,10)
                disp.line(px+145-3,py+25+2 ,px+5+3,py+freme_size+25-2 , 8)
                disp.line(px+5+3,py+25+2 ,px+145-3,py+freme_size+25-2 , 8)

        u_px = SCREEN_X_SIZE
        u_py = 0

        d_px = SCREEN_X_SIZE
        d_py = SCREEN_Y_SIZE//1.85

        disp.color(60,60,60)
        disp.box(u_px,u_py,STATUS_BER_LENGTH,SCREEN_Y_SIZE)

        #壁生成までのタイムリミット
        disp.color(40,40,40)
        disp.box(u_px,SCREEN_Y_SIZE//2 -15, 100,30 ,0)

        disp.pos(u_px+30,SCREEN_Y_SIZE//2-14)
        disp.color(100,100,100)
        disp.font(40)
        disp.prints("%02d" % int(self.residual_generate_walls))


        freme_size=150
        disp.font(27)
        for ship in self.__registered_ship_obj:
            if ship.state["DIRECTION"] == DIRECTION_UP : continue
            draw(u_px,u_py,ship)

            u_py += freme_size+30

        for ship in self.__registered_ship_obj:
            if ship.state["DIRECTION"] == DIRECTION_DOWN : continue
            draw(d_px,d_py,ship)

            d_py += freme_size+30
