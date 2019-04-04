import pygame
import random
import time as pytime
from pygame import *
import math
import os
from ustu import *
import win32api

# Initialize

os.environ['SDL_VIDEO_CENTERED'] = '1'

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.init()
pygame.init()
pygame.font.init()

display_x = 1280
display_y = 720

gameDisplay = pygame.display.set_mode((display_x, display_y))

surface = pygame.Surface(gameDisplay.get_size())

# Colors

black = (0, 0, 0, 225)
white = (255, 255, 255, 255)

# Time

clock = pygame.time.Clock()

t = pygame.time.get_ticks()

last_t = t

# Misc

mousePOS = pygame.mouse.get_pos

running = True

gameSpeed = float(getattr(win32api.EnumDisplaySettings(win32api.EnumDisplayDevices().DeviceName, -1), 'DisplayFrequency'))

deltaTimeOffset = 75

# Class Stuff

class Player():
    playerList = []
    playerMortemList = []

    def __init__(self):
        self.keys = {}
        self.x = display_x / 2
        self.y = display_y / 2 - 250
        self.velocity_x = 0
        self.velocity_y = 0
        self.speed = 2
        self.dampening = 0.75
        self.sprite = pygame.image.load("Game Files/Sprites/Default.png").convert_alpha()
        self.sprite = pygame.transform.scale(self.sprite, (40, 40))
        self.width, self.height = self.sprite.get_rect().size
        self.mask = pygame.mask.from_surface(self.sprite)
        self.last_x = self.x
        self.last_y = self.y
        self.last_xDiff = self.last_x - self.x
        self.last_yDiff = self.last_y - self.y
        self.P2T_offset = 0
        self.P2T_magnitude = 0
        self.P2T_angle = 0
        self.P2T_trianAngle = 0
        self.ROToffset_x = 0
        self.ROToffset_y = 0
        self.hit = False
        self.playerList.append(self)

        # Quadrant

        self.quadrant = pygame.image.load("Game Files/Image Masking/Player_Quadrant.png").convert_alpha()
        self.quadrant = pygame.transform.scale(self.quadrant, ((int(self.width / 3)), int(self.height / 3)))
        self.qwidth, self.qheight = self.quadrant.get_rect().size
        self.quadrant_mask = pygame.mask.from_surface(self.quadrant)

        self.n = (self.x + self.width / 3, self.y)
        self.ne = (self.x + self.width / 1.5, self.y)
        self.e = (self.x + self.width / 1.5, self.y + self.height / 3)
        self.se = (self.x + self.width / 1.5, self.y + self.height / 1.5)
        self.s = (self.x + self.width / 3, self.y + self.height / 1.5)
        self.sw = (self.x, self.y + self.height / 1.5)
        self.w = (self.x, self.y + self.height / 3)
        self.nw = (self.x, self.y)

        self.offset_n = (int(Map.x - self.n[0]), int(Map.y - self.n[1]))
        self.offset_ne = (int(Map.x - self.ne[0]), int(Map.y - self.ne[1]))
        self.offset_e = (int(Map.x - self.e[0]), int(Map.y - self.e[1]))
        self.offset_se = (int(Map.x - self.se[0]), int(Map.y - self.se[1]))
        self.offset_s = (int(Map.x - self.s[0]), int(Map.y - self.s[1]))
        self.offset_sw = (int(Map.x - self.sw[0]), int(Map.y - self.sw[1]))
        self.offset_w = (int(Map.x - self.w[0]), int(Map.y - self.w[1]))
        self.offset_nw = (int(Map.x - self.nw[0]), int(Map.y - self.nw[1]))

        self.result_n = self.quadrant_mask.overlap(Map.mask, self.offset_n)
        self.result_ne = self.quadrant_mask.overlap(Map.mask, self.offset_ne)
        self.result_e = self.quadrant_mask.overlap(Map.mask, self.offset_e)
        self.result_se = self.quadrant_mask.overlap(Map.mask, self.offset_se)
        self.result_s = self.quadrant_mask.overlap(Map.mask, self.offset_s)
        self.result_sw = self.quadrant_mask.overlap(Map.mask, self.offset_sw)
        self.result_w = self.quadrant_mask.overlap(Map.mask, self.offset_w)
        self.result_nw = self.quadrant_mask.overlap(Map.mask, self.offset_nw)

        self.resultCount = 0

        self.overlap_height = 0
        self.overlap_width = 0

    def TargetUpdate(self, target):
        "Updates the target."
        self.P2T_offset = (target[0] - self.x - self.width / 2, target[1] - self.y - self.height / 2)
        self.P2T_magnitude = Mag(self.P2T_offset)
        try:
            self.P2T_angle = math.degrees(math.acos(self.P2T_offset[0] / self.P2T_magnitude))
            if self.P2T_offset[1] > 0:
                self.P2T_angle = 360 - self.P2T_angle

            if player1.P2T_offset[0] > 0 and player1.P2T_offset[1] <= 0:
                self.P2T_trianAngle = (player1.P2T_angle % 90)
            if player1.P2T_offset[0] <= 0 and player1.P2T_offset[1] < 0:
                self.P2T_trianAngle = 90 - (player1.P2T_angle % 90)
            if player1.P2T_offset[0] < 0 and player1.P2T_offset[1] >= 0:
                self.P2T_trianAngle = (player1.P2T_angle % 90)
            if player1.P2T_offset[0] >= 0 and player1.P2T_offset[1] > 0:
                self.P2T_trianAngle = 90 - (player1.P2T_angle % 90)
                
        except ZeroDivisionError:
            pass

    def Update(self):
        "Updates the player."
        self.n = (self.last_x + self.width / 3, self.last_y)
        self.ne = (self.last_x + self.width / 1.5, self.last_y)
        self.e = (self.last_x + self.width / 1.5, self.last_y + self.height / 3)
        self.se = (self.last_x + self.width / 1.5, self.last_y + self.height / 1.5)
        self.s = (self.last_x + self.width / 3, self.last_y + self.height / 1.5)
        self.sw = (self.last_x, self.last_y + self.height / 1.5)
        self.w = (self.last_x, self.last_y + self.height / 3)
        self.nw = (self.last_x, self.last_y)

        # Quadrant To Map Offset

        self.offset_n = (int(Map.x - self.n[0]), int(Map.y - self.n[1]))
        self.offset_ne = (int(Map.x - self.ne[0]), int(Map.y - self.ne[1]))
        self.offset_e = (int(Map.x - self.e[0]), int(Map.y - self.e[1]))
        self.offset_se = (int(Map.x - self.se[0]), int(Map.y - self.se[1]))
        self.offset_s = (int(Map.x - self.s[0]), int(Map.y - self.s[1]))
        self.offset_sw = (int(Map.x - self.sw[0]), int(Map.y - self.sw[1]))
        self.offset_w = (int(Map.x - self.w[0]), int(Map.y - self.w[1]))
        self.offset_nw = (int(Map.x - self.nw[0]), int(Map.y - self.nw[1]))

        # Collision Define

        self.result_n = self.quadrant_mask.overlap(Map.mask, self.offset_n)
        self.result_ne = self.quadrant_mask.overlap(Map.mask, self.offset_ne)
        self.result_e = self.quadrant_mask.overlap(Map.mask, self.offset_e)
        self.result_se = self.quadrant_mask.overlap(Map.mask, self.offset_se)
        self.result_s = self.quadrant_mask.overlap(Map.mask, self.offset_s)
        self.result_sw = self.quadrant_mask.overlap(Map.mask, self.offset_sw)
        self.result_w = self.quadrant_mask.overlap(Map.mask, self.offset_w)
        self.result_nw = self.quadrant_mask.overlap(Map.mask, self.offset_nw)

    def Respawn(self):
        "Respawns a player if they are dead, (planing to be revamped)."
        if len(Player.playerMortemList) != 0:
            if Contains(Player.playerMortemList, self)["result"]:
                Player.playerList.append(self)

                index = Contains(Player.playerMortemList, self)["index"]

                self.hit = False
                self.keys = {}
                self.x = display_x / 2
                self.y = display_y / 2 - 250
                self.velocity_x = 0
                self.velocity_y = 0

                del Player.playerMortemList[index]

    @staticmethod
    def TrueRespawn():
        "Respawns the player even if they're still alive, (planing to be revamped)."
        for player in Player.playerMortemList:
            Player.playerList.append(player)
        for i, player in enumerate(Player.playerMortemList):
            del Player.playerMortemList[i]
        for player in Player.playerList:
            player.hit = False
            player.keys = {}
            player.x = display_x / 2
            player.y = display_y / 2 - 250
            player.velocity_x = 0
            player.velocity_y = 0

    def Destroy(self):
        "Destroys the player, (planing to be revamped)."
        if len(Player.playerList) != 0:
            if Contains(Player.playerList, self)["result"]:
                index = Contains(Player.playerList, self)["index"]

                Player.playerMortemList.append(Player.playerList[index])

                del Player.playerList[index]

    def Move(self):
        "Moves the player."
        self.last_x = self.x
        self.last_y = self.y

        self.x += self.velocity_x
        self.y += self.velocity_y

        self.last_xDiff = self.last_x - self.x
        self.last_yDiff = self.last_y - self.y

        # Dampening/Deadzone

        self.velocity_x *= self.dampening
        self.velocity_y *= self.dampening
        deadzone = self.dampening * self.speed
        if self.velocity_x < deadzone and self.velocity_x > -deadzone:
            self.velocity_x = 0
        if self.velocity_y < deadzone and self.velocity_y > -deadzone:
            self.velocity_y = 0
    
    def Draw(self):
        "Draws The Player."
        # Player

        self.ROToffset_x, self.ROToffset_y = Player.Rotate(self.sprite, self.P2T_angle)["offset"]

        gameDisplay.blit(Player.Rotate(self.sprite, self.P2T_angle)["sprite"], (self.x - math.ceil(self.ROToffset_x / 2), math.ceil(self.y - self.ROToffset_y / 2)))

        # Player Quadrant

        #gameDisplay.blit(self.quadrant, (self.n))
        #gameDisplay.blit(self.quadrant, (self.ne))
        #gameDisplay.blit(self.quadrant, (self.e))
        #gameDisplay.blit(self.quadrant, (self.se))
        #gameDisplay.blit(self.quadrant, (self.s))
        #gameDisplay.blit(self.quadrant, (self.sw))
        #gameDisplay.blit(self.quadrant, (self.w))
        #gameDisplay.blit(self.quadrant, (self.nw))

    def CollisionCheck(self):
        "Checks if the player is colliding with anything."
        # Reset Variables

        self.resultCount = 0

        # Screen Border
        
        self.x = Constrain(self.x, 0, display_x - self.width)
        self.y = Constrain(self.y, 0, display_y - self.height)

        # Update the player

        self.Update()

        # Collision Count

        if self.result_n:
            self.resultCount += 1
            #gameDisplay.blit(self.quadrant, (self.n))
        if self.result_ne:
            self.resultCount += 1
            #gameDisplay.blit(self.quadrant, (self.ne))
        if self.result_e:
            self.resultCount += 1
            #gameDisplay.blit(self.quadrant, (self.e))
        if self.result_se:
            self.resultCount += 1
            #gameDisplay.blit(self.quadrant, (self.se))
        if self.result_s:
            self.resultCount += 1
            #gameDisplay.blit(self.quadrant, (self.s))
        if self.result_sw:
            self.resultCount += 1
            #gameDisplay.blit(self.quadrant, (self.sw))
        if self.result_w:
            self.resultCount += 1
            #gameDisplay.blit(self.quadrant, (self.w))
        if self.result_nw:
            self.resultCount += 1
            #gameDisplay.blit(self.quadrant, (self.nw))

        # Collision Check/Result

        if self.result_n and self.result_nw and self.result_ne:
            self.overlap_height = (self.quadrant_mask.overlap_area(Map.mask, self.offset_n) / self.qwidth) - 1

            self.y += self.overlap_height - self.velocity_y

            self.velocity_y = 0

        if self.result_s and self.result_sw and self.result_se:
            self.overlap_height = (self.quadrant_mask.overlap_area(Map.mask, self.offset_s) / self.qwidth) - 1

            self.y -= self.overlap_height + self.velocity_y

            self.velocity_y = 0

        if self.result_e and self.result_ne and self.result_se:
            self.overlap_width = (self.quadrant_mask.overlap_area(Map.mask, self.offset_e) / self.qheight) - 1

            self.x -= self.overlap_width + self.velocity_x

            self.velocity_x = 0

        if self.result_w and self.result_nw and self.result_sw:
            self.overlap_width = (self.quadrant_mask.overlap_area(Map.mask, self.offset_w) / self.qheight) - 1

            self.x += self.overlap_width - self.velocity_x

            self.velocity_x = 0

        # Sloped Collision x

        if self.result_nw and self.velocity_y < 0 and not self.result_sw:
            self.overlap_width = (self.quadrant_mask.overlap_area(Map.mask, self.offset_nw) / self.qheight) - 1
            self.x += self.velocity_y + self.velocity_x + (self.overlap_width + 10)
        if self.result_ne and self.velocity_y < 0 and not self.result_se:
            self.overlap_width = (self.quadrant_mask.overlap_area(Map.mask, self.offset_ne) / self.qheight) - 1
            self.x -= self.velocity_y + self.velocity_x + (self.overlap_width + 10)
        if self.result_sw and self.velocity_y > 0 and not self.result_nw:
            self.overlap_width = (self.quadrant_mask.overlap_area(Map.mask, self.offset_sw) / self.qheight) - 1
            self.x += self.velocity_y + self.velocity_x + (self.overlap_width + 10)
        if self.result_se and self.velocity_y > 0 and not self.result_ne:
            self.overlap_width = (self.quadrant_mask.overlap_area(Map.mask, self.offset_se) / self.qheight) - 1
            self.x -= self.velocity_y + self.velocity_x + (self.overlap_width + 10)

        # Sloped Collision y

        if self.result_nw and self.velocity_x < 0 and not self.result_ne:
            self.overlap_height = (self.quadrant_mask.overlap_area(Map.mask, self.offset_s) / self.qwidth) - 1
            self.y -= self.velocity_x - self.velocity_y - (self.overlap_height + 10)
        if self.result_ne and self.velocity_x > 0 and not self.result_nw:
            self.overlap_height = (self.quadrant_mask.overlap_area(Map.mask, self.offset_s) / self.qwidth) - 1
            self.y += self.velocity_x + self.velocity_y + (self.overlap_height + 10)
        if self.result_sw and self.velocity_x < 0 and not self.result_se:
            self.overlap_height = (self.quadrant_mask.overlap_area(Map.mask, self.offset_s) / self.qwidth) - 1
            self.y += self.velocity_x + self.velocity_y - (self.overlap_height + 10)
        if self.result_se and self.velocity_x > 0 and not self.result_sw:
            self.overlap_height = (self.quadrant_mask.overlap_area(Map.mask, self.offset_s) / self.qwidth) - 1
            self.y -= self.velocity_x + self.velocity_y + (self.overlap_height + 10)

        # Destroy the player if it is entierly inside a wall to prevent out-off-bounds

        if self.resultCount == 8:
            self.hit = True
            self.Destroy()

    @staticmethod
    def Rotate(sprite, angle):
        "Rotates a given sprite to a given angle."
        orig_rect = sprite.get_rect()
        beforeWidth =  orig_rect.size[0]
        beforeHeight = orig_rect.size[1]
        rot_image = pygame.transform.rotate(sprite, angle)
        afterwidth =  rot_image.get_rect().size[0]
        afterheight = rot_image.get_rect().size[1]
        deltaWidth = afterwidth - beforeWidth
        deltaHeight = afterheight - beforeHeight
        rot_rect = orig_rect.copy()
        rot_rect = rot_rect.inflate(deltaWidth, deltaHeight)
        rot_rect.center = rot_image.get_rect().center
        return {"sprite":rot_image, "offset":(deltaWidth, deltaHeight)}

class Map():
    "Map()"
    x = 0
    y = 0
    level = "Turbine1"
    sprite = pygame.image.load(f"Game Files/Levels/{level}/mask.png").convert_alpha()
    sprite = pygame.transform.scale(sprite, (display_x, display_y))
    width, height = sprite.get_rect().size
    rect = sprite.get_rect()
    mask = pygame.mask.from_surface(sprite)
    BGx = 0
    BGy = 0
    BGsprite = pygame.image.load(f"Game Files/Levels/{level}/level.png").convert_alpha()
    BGsprite = pygame.transform.scale(BGsprite, (display_x, display_y))

    @classmethod
    def DrawMap(cls):
        gameDisplay.blit(cls.sprite, (cls.x, cls.y))

    @classmethod
    def DrawLevel(cls):
        gameDisplay.blit(cls.BGsprite, (cls.BGx, cls.BGy))

    @classmethod
    def LevelChange(cls, level):
        cls.sprite = pygame.image.load(f"Game Files/Levels/{level}/mask.png").convert_alpha()
        cls.sprite = pygame.transform.scale(cls.sprite, (display_x, display_y))
        cls.mask = pygame.mask.from_surface(cls.sprite)
        cls.BGsprite = pygame.image.load(f"Game Files/Levels/{level}/level.png").convert_alpha()
        cls.BGsprite = pygame.transform.scale(cls.BGsprite, (display_x, display_y))

class Combat():
    "Combat()"
    entityList = []

    class Bullet():
        "Bullet()"
        def __init__(self):
            self.x = 0
            self.y = 0
            self.last_x = 0
            self.last_y = 0
            self.xDiff = 0
            self.yDiff = 0
            self.xDiff1 = 0
            self.yDiff1 = 0
            self.diffMag1 = 0
            self.diffMag2 = 0
            self.B2P_angle = 0
            self.sprite = pygame.image.load("Game Files/Sprites/Bullet.png").convert_alpha()
            self.sprite = pygame.transform.scale(self.sprite, (15, 15))
            self.mask = pygame.mask.from_surface(self.sprite)
            self.offset = 0
            self.result = False
            self.width, self.height = self.sprite.get_rect().size
            self.velocity = [0, 0]
            self.speed = 1
            self.creator = None
            self.hit = False

    def DestroyEntity(self):
        "Destroys a specified entity."
        Combat.entityList.remove(self)

    @staticmethod
    def UpdateEntity(entity):
        "Updates a specified entity."
        if len(Combat.entityList) != 0:
            if type(entity) == Combat.Bullet:
                bullet = entity

                try:
                    bullet.last_x = bullet.x
                    bullet.last_y = bullet.y

                    bullet.x += (bullet.velocity[0] * bullet.speed)
                    bullet.y += (bullet.velocity[1] * bullet.speed)

                    bullet.xDiff = bullet.x - bullet.last_x
                    bullet.yDiff = bullet.y - bullet.last_y

                except ZeroDivisionError:
                    pass

    @staticmethod
    def CollisionCheckEntity(entity, player):
        "Checks if an entity is colliding with anything."
        if len(Combat.entityList) != 0:
            bullet = entity
            try:
                bullet.diffMag = bullet.yDiff / math.sin(math.radians(bullet.B2P_angle))

            except ZeroDivisionError:
                bullet.diffMag = 1

            for i in range(math.floor(abs(bullet.diffMag))):
                bullet.xDiff1 = math.cos(math.radians(bullet.B2P_angle)) * i
                bullet.yDiff1 = math.sin(math.radians(bullet.B2P_angle)) * i

                if bullet.xDiff > 0:
                    bullet.xDiff1 = -bullet.xDiff1
                if bullet.yDiff > 0:
                    bullet.yDiff1 = -bullet.yDiff1

                bullet.offset = (int(player.x - (bullet.x - bullet.xDiff1)), int(player.y - (bullet.y - bullet.yDiff1)))

                bullet.result = bullet.mask.overlap(player.mask, bullet.offset)

                if player != bullet.creator:
                    if bullet.result:
                        player.hit = True

                        bullet.hit = True

                        break

                bullet.offset = (int(Map.x - (bullet.x - bullet.xDiff1)), int(Map.y - (bullet.y - bullet.yDiff1)))

                bullet.result = bullet.mask.overlap(Map.mask, bullet.offset)

                if bullet.result:
                    bullet.hit = True
                    break

                if bullet.x - bullet.xDiff1 > display_x:
                    bullet.hit = True
                    break

                elif bullet.x - bullet.xDiff1 < 0:
                    bullet.hit = True
                    break

                elif bullet.y - bullet.yDiff1 > display_y:
                    bullet.hit = True
                    break

                elif bullet.y - bullet.yDiff1 < 0:
                    bullet.hit = True
                    break

            if player.hit:
                player.Destroy()

            if bullet.hit:
                Combat.DestroyEntity(bullet)

        else: 
            bullet = entity

            bullet.offset = (int(player.x - bullet.x), int(player.y - bullet.y))

            bullet.result = bullet.mask.overlap(player.mask, bullet.offset)

            if player != bullet.creator:

                if bullet.result:
                    player.hit = True

                    bullet.hit = True

            bullet.offset = (int(Map.x - bullet.x), int(Map.y - bullet.y))

            bullet.result = bullet.mask.overlap(Map.mask, bullet.offset)

            if bullet.result:
                bullet.hit = True

            if bullet.x > display_x:
                bullet.hit = True

            elif bullet.x < 0:
                bullet.hit = True

            elif bullet.y > display_y:
                bullet.hit = True

            elif bullet.y < 0:
                bullet.hit = True
            
            if player.hit:
                player.Destroy()

            if bullet.hit:
                Combat.DestroyEntity(bullet)

    @staticmethod
    def DrawEntity(entity):
        "Draws an entity."
        if type(entity) == Combat.Bullet:
            bullet = entity
            gameDisplay.blit(bullet.sprite, (bullet.x, bullet.y))

# Object Assignment

player1 = Player()

player2 = Player()

player2.x = 100

player2.y = 100

# Main Loop

while running:

    t = pygame.time.get_ticks()

    deltaTime = (t - last_t) / 1000.0

    # Event Handeling For Each Player

    for event in pygame.event.get():

        if event.type == QUIT:
            pygame.quit()
            running = False

        if not running:
            break

        if event.type == pygame.MOUSEMOTION:
            mousePOS = pygame.mouse.get_pos()

        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                running = False

            if event.key == K_1:
                for player in Player.playerList:
                    player.TrueRespawn()
                for player in Player.playerMortemList:
                    player.TrueRespawn()

                Map.LevelChange("Turbine1")

            if event.key == K_2:
                for player in Player.playerList:
                    player.TrueRespawn()
                for player in Player.playerMortemList:
                    player.TrueRespawn()

                Map.LevelChange("Turbine2")

            if event.key == K_r:
                try:
                    player1.Respawn()
                    player2.Respawn()
                except NameError:
                    pass

            if event.key == K_x:
                player1.Destroy()
                player2.Destroy()
                Combat.entityList = []

        for player in Player.playerList:
            try:
                if player == player1:
                    # Controls

                    if event.type == KEYDOWN:

                        if event.key == K_w:
                            player.keys[K_w] = True

                        if event.key == K_a:
                            player.keys[K_a] = True

                        if event.key == K_s:
                            player.keys[K_s] = True

                        if event.key == K_d:
                            player.keys[K_d] = True

                        if event.key == K_SPACE:
                            pass

                        if event.key == K_LEFT:
                            pass

                        if event.key == K_RIGHT:
                            pass

                        if event.key == K_UP:
                            pass

                        if event.key == K_DOWN:
                            pass

                    if event.type == KEYUP:

                        if event.key == K_w:
                            player.keys[K_w] = False

                        if event.key == K_a:
                            player.keys[K_a] = False

                        if event.key == K_s:
                            player.keys[K_s] = False

                        if event.key == K_d:
                            player.keys[K_d] = False

                        if event.key == K_SPACE:
                            pass

                        if event.key == K_LEFT:
                            pass

                        if event.key == K_RIGHT:
                            pass

                        if event.key == K_UP:
                            pass

                        if event.key == K_DOWN:
                            pass

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        newBullet = Combat.Bullet()
                        newBullet.velocity = [math.sin(math.radians(player1.P2T_angle + 90)), math.cos(math.radians(player1.P2T_angle + 90))]
                        newBullet.x = (player.x +  (player1.width / 2) - newBullet.width / 2) - newBullet.velocity[0]
                        newBullet.y = (player.y + (player1.height / 2) - newBullet.height / 2) - newBullet.velocity[1]
                        newBullet.speed = 90
                        newBullet.creator = player1
                        newBullet.B2P_angle = player1.P2T_trianAngle
                        Combat.entityList.append(newBullet)

                    if event.type == pygame.MOUSEBUTTONUP:
                        pass

                    if event.type == pygame.MOUSEMOTION:
                        pass

            except NameError:
                pass

            try:
                if player == player2:
                    # Controls

                    if event.type == KEYDOWN:

                        if event.key == K_KP8:
                            player.keys[K_KP8] = True

                        if event.key == K_KP4:
                            player.keys[K_KP4] = True

                        if event.key == K_KP5:
                            player.keys[K_KP5] = True

                        if event.key == K_KP6:
                            player.keys[K_KP6] = True

                        if event.key == K_SPACE:
                            pass

                        if event.key == K_LEFT:
                            pass

                        if event.key == K_RIGHT:
                            pass

                        if event.key == K_UP:
                            pass

                        if event.key == K_DOWN:
                            pass

                    if event.type == KEYUP:

                        if event.key == K_KP8:
                            player.keys[K_KP8] = False

                        if event.key == K_KP4:
                            player.keys[K_KP4] = False

                        if event.key == K_KP5:
                            player.keys[K_KP5] = False

                        if event.key == K_KP6:
                            player.keys[K_KP6] = False

                        if event.key == K_SPACE:
                            pass

                        if event.key == K_LEFT:
                            pass

                        if event.key == K_RIGHT:
                            pass

                        if event.key == K_UP:
                            pass

                        if event.key == K_DOWN:
                            pass

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pass

                    if event.type == pygame.MOUSEBUTTONUP:
                        pass

                    if event.type == pygame.MOUSEMOTION:
                        pass

            except NameError:
                pass

    # Control Action For Each Player

    for player in Player.playerList:
        try:
            if player == player1:
                if player.keys.get(K_w, False) and not player.result_n:
                    player.velocity_y -= player.speed

                if player.keys.get(K_a, False) and not player.result_w:
                    player.velocity_x -= player.speed

                if player.keys.get(K_s, False) and not player.result_s:
                    player.velocity_y += player.speed

                if player.keys.get(K_d, False) and not player.result_e:
                    player.velocity_x += player.speed
        except NameError:
            pass

        try:
            if player == player2:
                if player.keys.get(K_KP8, False) and not player.result_n:
                    player.velocity_y -= player.speed

                if player.keys.get(K_KP4, False) and not player.result_w:
                    player.velocity_x -= player.speed

                if player.keys.get(K_KP5, False) and not player.result_s:
                    player.velocity_y += player.speed

                if player.keys.get(K_KP6, False) and not player.result_e:
                    player.velocity_x += player.speed

        except NameError:
            pass

    # Exit Without An Error Message

    if not running:
        break

    # Do The Actual Game

    Map.DrawLevel()

    for player in Player.playerList:
        Player.TargetUpdate(player, mousePOS)

        player.Draw()

        player.Move()

        player.CollisionCheck()

        for entity in Combat.entityList:
            Combat.UpdateEntity(entity)
            Combat.CollisionCheckEntity(entity, player)

    for entity in Combat.entityList:
        Combat.DrawEntity(entity)

    # This Always Goes Last

    pygame.display.flip()

    gameDisplay.fill(black)

    clock.tick(gameSpeed)

    last_t = t