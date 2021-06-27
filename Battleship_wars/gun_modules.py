"""
    GunModuleを定義する場所
    定義方法については以下を参照


class Gun_Module_Name( <使用弾クラス> ):

    name = "Module Name"    #表示される名前
    rank = "RANK"           #モジュールのレア度 "S" "A" "B" "C"

    rays_included_num = num #一度に打ち出される弾の数[個]
    rays_min_span_s = secs  #打ち出される最小時間[秒]
    rays_power = int        #１発のダメージ量

    def __init__(self, x,y ,direction,rnd):
        self.init_ray(x,y ,direction,rnd)
        #以下自由

    def calc(self,delta_time_s ):

        # 下から上へ向かう弾の変化量を計算する。 delta_time_s は前の計算からの経過時間
        # ※ self.correction_to(dx,dy)の部分で方向の修正を行っている

        # self.pos_x : self.pos_x => 弾の座標
        # self.direction =>弾の発射向き DIRECTION_UP | DIRECTION_DOWN
        # self.rnd => +1.0 ~ -1.0

        return self.correction_to(dx,dy)

"""
import disp
import math

from field import SCREEN_X_SIZE
from field import SCREEN_Y_SIZE
from field import MAX_FRAME_RATE
from field import SHIP_HIT_RANGE
from field import DIRECTION_DOWN
from field import DIRECTION_UP

ITEM_SIZE = 36
ITEM_GET_RANGE = 50

pic_gun_module = {}
clr_gun_module = {}
for i in [ ["S",(200,0,200)] , ["A",(200,0,0)] , ["B",(0,200,200)] , ["C",(200,200,0)] ]:
    pic_gun_module[i[0]] = disp.picload( ("./data/pic/module_"+i[0]+".png") ,-1, ITEM_SIZE,ITEM_SIZE)
    clr_gun_module[i[0]] = i[1]

class item_gun_module():
    def __init__(self,x,y,module,direction):
        self.pos_x = x
        self.pos_y = y

        self.module = module
        self.direction = direction

    def calc( self,delta_time_s ):
        dx = delta_time_s * 75
        if self.direction != DIRECTION_DOWN:
            dx = -dx

        self.pos_y -= dx


    def draw(self):
        disp.pos(self.pos_x -ITEM_SIZE//2, self.pos_y -ITEM_SIZE//2)
        disp.picout( pic_gun_module[self.module.rank] )

        clr = clr_gun_module[self.module.rank]
        disp.color(clr[0],clr[1],clr[2])

        disp.font(ITEM_SIZE//2)
        disp.pos(self.pos_x -ITEM_SIZE//2, self.pos_y + 40)
        disp.prints(self.module.name)

        disp.font(30)
        disp.pos(self.pos_x +15 , self.pos_y + 10)
        disp.prints(self.module.rank)

    def can_use(self,x,y):
        if (x >= self.pos_x-ITEM_GET_RANGE//2) and (x <= self.pos_x+ITEM_GET_RANGE//2):
            if (y >= self.pos_y-ITEM_GET_RANGE//2) and (y <= self.pos_y+ITEM_GET_RANGE//2):
                return True
        return False

    def get_module(self):
        return self.module

pic_health = disp.picload("./data/pic/health.png",ITEM_SIZE,ITEM_SIZE)
class item_health():
    def __init__(self,x,y,direction):
        self.pos_x = x
        self.pos_y = y
        self.direction = direction

        self.health_num = 700

    def calc( self,delta_time_s ):
        dx = delta_time_s * 75
        if self.direction != DIRECTION_DOWN:
            dx = -dx

        self.pos_y -= dx

    def draw(self):
        disp.pos(self.pos_x -ITEM_SIZE//2, self.pos_y -ITEM_SIZE//2)
        disp.picout( pic_health )

        disp.font(ITEM_SIZE//2)
        disp.color(255,60,60)
        disp.pos(self.pos_x -ITEM_SIZE//2 -16, self.pos_y + 40)
        disp.prints("RECOVERY")

    def can_use(self,x,y):
        if (x >= self.pos_x-ITEM_GET_RANGE//2) and (x <= self.pos_x+ITEM_GET_RANGE//2):
            if (y >= self.pos_y-ITEM_GET_RANGE//2) and (y <= self.pos_y+ITEM_GET_RANGE//2):
                return True
        return False

    def health(self,obj_ship):
        obj_ship.to_helth(self.health_num)


#****************************** 弾の種類の定義 ******************************

#Template
class Ray():
    name = "-----"
    rank = "C"

    def init_ray(self, x,y ,direction,rnd):
        self.pos_x = x
        self.pos_y = y

        self.direction = direction
        self.rnd = rnd

    def draw(self):
        size_x = 6
        size_y = 10
        disp.ellipse(self.pos_x -size_x/2, self.pos_y -size_y/2 ,size_x,size_y )

    def play_anime(self,time_s):#着弾時のアニメーション
        x = self.pos_x
        y = self.pos_y

        max_size = 60
        min_size = 10

        max_time_s = 0.15

        if time_s > max_time_s:
            return False

        ITEM_SIZE = (max_size-min_size) * (time_s/max_time_s) + min_size

        disp.color(255,192,192)
        disp.ellipse(x-ITEM_SIZE/2,y-ITEM_SIZE/2 ,ITEM_SIZE,ITEM_SIZE ,1)

        ITEM_SIZE *= 0.8
        disp.color(255,220,220)
        disp.ellipse(x-ITEM_SIZE/2,y-ITEM_SIZE/2 ,ITEM_SIZE,ITEM_SIZE ,1)
        disp.ellipse(x-ITEM_SIZE/2,y-ITEM_SIZE/2 ,ITEM_SIZE,ITEM_SIZE-1 ,1)

        ITEM_SIZE *= 0.8
        disp.color(255,255,255)
        disp.ellipse(x-ITEM_SIZE/2,y-ITEM_SIZE/2 ,ITEM_SIZE,ITEM_SIZE ,1)
        disp.ellipse(x-ITEM_SIZE/2,y-ITEM_SIZE/2 ,ITEM_SIZE,ITEM_SIZE-1 ,1)
        disp.ellipse(x-ITEM_SIZE/2,y-ITEM_SIZE/2 ,ITEM_SIZE,ITEM_SIZE-2 ,1)

        return True

    def correction_to(self, dx,dy):
        if self.direction == DIRECTION_DOWN:
            return (dx , dy )

        else:
            return (dx , -dy)

#to Extends
class Ray_Default(Ray):
    def draw(self):

        size_x = 10
        size_y = 20
        disp.ellipse(self.pos_x-size_x/2,self.pos_y-size_y/2 ,size_x,size_y )

        disp.color(0,0,0)
        if self.direction == DIRECTION_UP:
            disp.box(self.pos_x-size_x/4,self.pos_y+3 ,size_x/2,size_y/2-3)
        else:
            disp.box(self.pos_x-size_x/4,self.pos_y-3 ,size_x/2,-size_y/2+3)

class Ray_L(Ray):
    def draw(self):

        size_x = 20
        size_y = 40
        disp.ellipse(self.pos_x-size_x/2,self.pos_y-size_y/2 ,size_x,size_y )
class Ray_M(Ray):
    def draw(self):

        size_x = 20
        size_y = 20
        disp.ellipse(self.pos_x-size_x/2,self.pos_y-size_y/2 ,size_x,size_y )


class Ray_Laser(Ray):
    def draw(self):
        size_x = 5
        size_y = 50
        disp.ellipse(self.pos_x-size_x/2,self.pos_y-size_y/2 ,size_x,size_y )


#****************************** 弾の飛び方の定義 *****************************
class Straight(Ray_Default):
    name = "BEAM"
    rank = "C"

    rays_included_num = 1
    rays_interval_secs = 0.075
    rays_power = 60

    def __init__(self, x,y ,direction,rnd):
        self.init_ray(x,y ,direction,rnd)

    def calc(self, delta_time_s):
        r = self.rnd * 6
        dx = 1 - 1 *(r)

        dx *= 0.05
        dy = delta_time_s*(500)

        return self.correction_to(dx,dy)
class Splash(Ray):
    name = "SPLASH"
    rank = "C"

    rays_included_num = 15
    rays_interval_secs = 0.5
    rays_power = 20

    def __init__(self,x,y ,direction,rnd):
        self.init_ray(x,y ,direction,rnd)

        self.rays_min_span_s = 0.01
        self.integ_y = 0

    def calc( self,delta_time_s ):
        r = self.rnd *2.2

        dx = (   1 *(r) ) + r *-(self.integ_y/300)**3
        dy = delta_time_s*(500)

        self.integ_y += dy

        return self.correction_to(dx,dy)


class Laser(Ray_Laser):
    name = "LASER"
    rank = "B"

    rays_included_num = 20
    rays_interval_secs = 0.5
    rays_power = 20

    def __init__(self,x,y ,direction,rnd):
        self.init_ray(x,y ,direction,rnd)

    def calc( self,delta_time_s ):
        r = self.rnd
        dx = 0
        dx *= 0.05
        dy = delta_time_s*(1000+300*r)

        return self.correction_to(dx,dy)
class Circle(Ray_L):
    name = "CIRCLE"
    rank = "B"

    rays_included_num = 30
    rays_interval_secs = 0.8
    rays_power = 100

    def __init__(self,x,y ,direction,rnd):
        self.init_ray(x,y ,direction,rnd)

    def calc( self,delta_time_s ):
        r = self.rnd
        dx = math.sin(r) * delta_time_s * 300
        dy = math.cos(r) * delta_time_s * 300

        return self.correction_to(dx,dy)
class Delay(Ray_Laser):
    name = "DELAY"
    rank = "B"

    rays_included_num = 20
    rays_interval_secs = 0.1
    rays_power = 10

    def __init__(self,x,y ,direction,rnd):
        self.init_ray(x,y ,direction,rnd)
        self.delay_timer = 0

    def calc( self,delta_time_s ):
        dx = 0
        dy = 0
        if self.delay_timer > 5 or self.delay_timer < 0.05 :
            r = self.rnd
            dx = 0
            dx *= 0.05
            dy = delta_time_s*(1500+300*r)


        self.delay_timer += delta_time_s

        return self.correction_to(dx,dy)

class Meteo(Ray_L):
    name = "METEO"
    rank = "A"

    rays_included_num = 5
    rays_interval_secs = 0.45
    rays_power = 400

    def __init__(self,x,y ,direction,rnd):
        self.init_ray(x,y ,direction,rnd)
        self.speed = 100


    def calc( self,delta_time_s ):
        r = self.rnd
        dx = r * 0.1
        dy = delta_time_s*self.speed

        self.speed += delta_time_s * 300

        return self.correction_to(dx,dy)
class Mine(Ray_M):
    name = "MINE"
    rank = "A"

    rays_included_num = 10
    rays_interval_secs = 1.5
    rays_power = 60

    def __init__(self,x,y ,direction,rnd):
        self.init_ray(x,y ,direction,rnd)
        self.delay_timer = 0

    def calc( self,delta_time_s ):
        dx = 0
        dy = 0
        if self.delay_timer < 1 :
            r = self.rnd
            dx = r*0.1
            dy = delta_time_s*400
        else:
            if self.delay_timer > 9:
                r = self.rnd
                dx = -r*1
                dy = -delta_time_s*300

        self.delay_timer += delta_time_s

        return self.correction_to(dx,dy)
class Sine(Ray_M):
    name = "SINE"
    rank = "A"

    rays_included_num = 10
    rays_interval_secs = 0.2
    rays_power = 10

    def __init__(self,x,y ,direction,rnd):
        self.init_ray(x,y ,direction,rnd)

    def calc( self,delta_time_s ):
        r = self.rnd
        if r > 0.1:
            dx = 4*math.sin(self.pos_y/30)
        elif r < -0.1:
            dx = 4*math.sin(self.pos_y/30+math.pi)
        else:
            dx = 0

        dy = delta_time_s*500

        return self.correction_to(dx,dy)

class Ray_Wall(Ray_M):
    name = "RAY WALL"
    rank = "S"

    rays_included_num = 80
    rays_interval_secs = 2
    rays_power = 240

    def __init__(self,x,y ,direction,rnd):
        self.init_ray(x,y ,direction,rnd)
        self.delay_timer = 0

    def calc( self,delta_time_s ):
        self.delay_timer += delta_time_s

        dx = 0
        dy = 0

        if self.delay_timer < 0.6:
            r = self.rnd
            dx = 0
            dx *= 0.05
            dy = delta_time_s*(600+500*r)

        elif self.delay_timer < 1:
            self.rnd = int(self.pos_y*10%2)

        elif self.delay_timer >= 1.5:
            r = self.rnd
            dy = 1
            if r == 0:
                dx = delta_time_s * 600
            else:
                dx = delta_time_s * -600
        return self.correction_to(dx,dy)
