import pygame
import sys
from pygame.locals import *
import random
import time


class Paddle(object):
    def __init__(self, x:int, y:int, width, height, colour, paddlespeed):
        self.x:int = x
        self.y:int = y
        self.vy = 0
        self.width = width
        self.height = height
        self.colour = colour
        self.paddlespeed=paddlespeed

    def draw(self, screen):
        pygame.draw.rect(screen, self.colour, self.rect())

    def move(self, screen):
        if self.y >= 0 and self.vy < 0:
                self.y += self.vy
        elif self.y <= screen.get_size()[1]-self.height and self.vy > 0:
                self.y += self.vy
        

    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    def collide(self, obj:object):
        pass


class LeftPaddle(Paddle):
    def __init__(self, x, y, width, height, colour, paddlespeed):
        super().__init__(x, y, width, height, colour, paddlespeed)

    def collide(self, obj:object, screen):
        if obj.x < (self.x+self.width) and obj.collided==False and obj.ToBeDestructed == False:
            # Ball Rect = (px + pw - 1, abs(vy/vx)*(px+pw+r-bx)+by-r, 2*r , 2*r)
            projected_objx=(self.x+self.width-1)
            projected_objy=(abs(obj.vy/obj.vx)*(self.x+self.width-1-obj.x)+obj.y)

            if self.rect().colliderect(pygame.Rect(projected_objx, projected_objy, obj.w, obj.h)):
                obj.x = projected_objx
                obj.y = projected_objy
                #obj.collided=True
                return True
            else:
                return False
        else: 
            return False


class RightPaddle(Paddle):
    def __init__(self, x, y, width, height, colour, paddlespeed):
        super().__init__(x, y, width, height, colour, paddlespeed)

    def collide(self, obj:object, screen):
        if obj.x + obj.w > self.x and obj.collided==False and obj.ToBeDestructed == False:
            #Rect = ( (Px-2r+1), ( abs(vy/vx)*(bx-px+r+1)+by-r, 2r, 2r )
            projected_objx=(self.x-obj.w+1)
            projected_objy=(abs(obj.vy/obj.vx)*(obj.x-projected_objx)+obj.y)
            
            if self.rect().colliderect(pygame.Rect(projected_objx, projected_objy, obj.w, obj.h)):
                obj.x = projected_objx
                obj.y = projected_objy
                #obj.collided=True
                return True
            else:
                return False
        else:
            return False


class GameObject(object):
    def __init__(self, x:int, y:int, w:int, h:int, vx:float, vy:float, colour):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.vx = vx
        self.vy = vy
        self.colour = colour
        self.collided=False
        self.ToBeDestructed=False

    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)
    
    def move(self, screen):
        if self.y < 0:
            self.vy = abs(self.vy)
        elif  self.y+self.h > screen.get_size()[1]:
            self.vy = -1 * abs(self.vy)
        self.x += self.vx
        self.y += self.vy

    def draw(self, screen):
        pygame.draw.rect(screen, self.colour, self.rect())

    def destruction(self, game):
        return True

    def collided_action(self, paddle:Paddle, screen):
        self.collided=True
        

class Enlarge(GameObject):
    def __init__(self, x:int, y:int, w:int, h:int, vx:float, vy:float, colour):
        super().__init__(x, y, w, h, vx, vy, colour)
        self.type='enlarge'
        self.collided=False

    def collided_action(self, paddle:Paddle, screen):
        if not(self.collided):
            if paddle.height < int(screen.get_size()[1]/2)-20:
                paddle.height += 20
            else:
                paddle.height = 100
            self.collided=True
        self.ToBeDestructed=True

class SpeedUp(GameObject):
    def __init__(self, x:int, y:int, w:int, h:int, vx:float, vy:float, colour):
        super().__init__(x, y, w, h, vx, vy, colour)
        self.type='speedup'
        self.collided=False

    def collided_action(self, paddle:Paddle, screen):
        if not(self.collided):
            if paddle.paddlespeed < 30:
                paddle.paddlespeed += 10
            else:
                paddle.paddlespeed = 10
            self.collided=True
        self.ToBeDestructed=True

class Ball(GameObject):

    def __init__(self, x:int, y:int, w:int, h:int, vx:float, vy:float, colour):
        super().__init__(x, y, w, h, vx, vy, colour)
        self.radius = (w/2)
        self.type='ball'

    def draw(self, surface):
        pygame.draw.circle(surface, self.colour, (self.x+self.radius, self.y+self.radius), self.radius, 0)
    
    def destruction(self, game):
        if self.x < 0:
            game.score[1] += 1
        else:
            game.score[0] += 1
        self.x = int(game.screen.get_size()[0]/2)
        self.y = int(game.screen.get_size()[1]/2)
        self.vx =(-1)**int(random.random()*10)*3
        self.vy =(-1)**int(random.random()*10)*3
        numberofballexist = 0
        for obj in game.objlist:
            if obj.type == 'ball':
                numberofballexist += 1
        if numberofballexist >1:
            self.ToBeDestructed=True
            return True
        else:
            return False
        
    def collided_action(self, paddle:Paddle, screen):
        self.collided=False
        if (abs(self.vx)<screen.get_size()[0]/3):
            self.vx = self.vx * -1.2
            self.vy = self.vy * 1.2
        else:
            self.vx = self.vx * -1

        if paddle.vy<0 and (abs(self.vy)<screen.get_size()[1]/2):
            self.vy += 5
                    
        elif paddle.vy>0 and (abs(self.vy)<screen.get_size()[1]/2):
            self.vy -= 5
                    

class Game(object):

    white = (255,255,255)
    black = (0,0,0)
    blue = (0, 128, 128)
    purple = (255, 0, 255)
    red = (196,0,0)
    orange = (255, 165, 0)

    FPS = 60



    def __init__(self):
        pygame.init()
        paddlesize=(20, 100)
        paddle_initial_speed=10
        self.objlist = []
        self.score=[0, 0]

        self.screen = pygame.display.set_mode((600,500))

        self.objlist.append(Ball( int(self.screen.get_size()[0]/2),  int(self.screen.get_size()[1]/2), 20, 20,(-1)**int(random.random()*10)*3, (-1)**int(random.random()*10)*3, self.black))
        
        #self.ball = Ball( int(self.screen.get_size()[0]/2),  int(self.screen.get_size()[1]/2), 3, 3, 10, self.black)
        self.left_bat = LeftPaddle(0, int(self.screen.get_size()[1]/2-paddlesize[1]/2), paddlesize[0], paddlesize[1], self.red, paddle_initial_speed)
        self.right_bat = RightPaddle(self.screen.get_size()[0]-20, int(self.screen.get_size()[1]/2-paddlesize[1]/2), paddlesize[0], paddlesize[1], self.blue, paddle_initial_speed)
        self.fpsClock = pygame.time.Clock()

        self.font = pygame.font.SysFont(None, 40)
        self.font.set_bold(True)

    def keypressdetection(self):
        key = pygame.key.get_pressed()
        if key[pygame.K_w]:
            self.left_bat.vy = -1 * abs(self.left_bat.paddlespeed)
        if key[pygame.K_s]:
            self.left_bat.vy = abs(self.left_bat.paddlespeed)
        if not( key[pygame.K_w] or key[pygame.K_s]) or (key[pygame.K_s] and key[pygame.K_w]):
            self.left_bat.vy = 0
        if key[pygame.K_UP]:
            self.right_bat.vy = -1 * abs(self.right_bat.paddlespeed)
        if key[pygame.K_DOWN]:
            self.right_bat.vy = abs(self.right_bat.paddlespeed)
        if not( key[pygame.K_UP] or key[pygame.K_DOWN]) or (key[pygame.K_UP] and key[pygame.K_DOWN]):
            self.right_bat.vy = 0


    def generategameobject(self):
        if int(random.random()*10) > 5:
            self.objlist.append(Ball( int(self.screen.get_size()[0]/2),  int(self.screen.get_size()[1]/2), 20, 20, (-1)**int(random.random()*10)*3, (-1)**int(random.random()*10)*3, self.black))
        enlargeexisted=False
        speedupexisted=False
        for obj in self.objlist:
            if obj.type == 'enlarge':
                enlargeexisted=True
            elif obj.type == 'speedup':
                speedupexisted =True
        if not( enlargeexisted ) and int(random.random()*10) > 7 :
            self.objlist.append(Enlarge( int(self.screen.get_size()[0]/2),  int(self.screen.get_size()[1]/2), 10, 10, (-1)**int(random.random()*10)*3, (-1)**int(random.random()*10)*6, self.purple))
        if not( speedupexisted ) and int(random.random()*10) > 7 :
            self.objlist.append(SpeedUp( int(self.screen.get_size()[0]/2),  int(self.screen.get_size()[1]/2), 10, 10, (-1)**int(random.random()*10)*3, (-1)**int(random.random()*10)*6, self.orange))


    def play(self):

        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
            #Key detection
            self.keypressdetection()

            #Move all game objects
            self.left_bat.move(self.screen)
            self.right_bat.move(self.screen)
            for obj in self.objlist:
                obj.move(self.screen)

            #Collision detection
            generate=False
            for obj in self.objlist:
                if self.left_bat.collide(obj, self.screen)==True:
                    obj.collided_action( self.left_bat, self.screen)
                    generate=True
                elif self.right_bat.collide(obj, self.screen)==True:
                     obj.collided_action( self.right_bat, self.screen)
                     generate=True
            for obj in self.objlist:
                if obj.ToBeDestructed == True:
                    self.objlist.remove(obj)
                    del obj
                elif obj.x < 0 or obj.x + obj.w > self.screen.get_size()[0]:
                    #calculate score and destroy the object if not only 1 ball left
                    if obj.destruction( self )==True:
                        self.objlist.remove(obj)
                        del obj
            if self.score[0] >= 100 or self.score[1] >= 100:
                if self.score[0]>=100:
                    winner='Left player'
                else:
                    winner='Right player'
                game_final_message = self.font.render( winner+' won !!!', True, self.red)
                game_final_message_rect = game_final_message.get_rect()
                game_final_message_rect.center = (self.screen.get_size()[0]/2,self.screen.get_size()[1]/2)
                game_final_message2 = self.font.render( 'Press any key to restart.', True, self.blue)
                game_final_message2_rect = game_final_message2.get_rect()
                game_final_message2_rect.center = (self.screen.get_size()[0]/2,self.screen.get_size()[1]/2+40)
                
                self.screen.blit(game_final_message, game_final_message_rect)
                pygame.display.update()
                time.sleep(3)
                self.screen.blit(game_final_message2, game_final_message2_rect)
                pygame.display.update()
                pygame.event.clear()
                while pygame.event.wait().type != pygame.KEYDOWN:
                    pass

                #Reset paddles parameters, scores and object list
                self.left_bat.height=100
                self.right_bat.height=100
                self.left_bat.vy = 10
                self.right_bat.vy = 10
                self.objlist.clear()
                self.objlist.append(Ball( int(self.screen.get_size()[0]/2),  int(self.screen.get_size()[1]/2), 20, 20,(-1)**int(random.random()*10)*3, (-1)**int(random.random()*10)*3, self.black))
                self.score=[0, 0]

            if generate == True:
                self.generategameobject()               


            self.draw()            
            pygame.display.update()
            self.fpsClock.tick(self.FPS)
    

    def draw(self):
        self.screen.fill(Game.white)
        self.left_bat.draw(self.screen)
        self.right_bat.draw(self.screen)

        leftscore = self.font.render(str(self.score[0]), True, self.red)
        rightscore = self.font.render(str(self.score[1]), True, self.blue)
        leftscorerect = leftscore.get_rect()
        rightscorerect = rightscore.get_rect()
        leftscorerect.center = (40,40)
        rightscorerect.center = (self.screen.get_size()[0]-50, 40)
        self.screen.blit(leftscore, leftscorerect)
        self.screen.blit(rightscore, rightscorerect)
        

        for obj in self.objlist:
            obj.draw( self.screen)
        

        pygame.display.update()


if __name__ == "__main__":
    Game().play()


