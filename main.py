import pygame, sys
from settings import *
from level import Level
from overworld import Overworld
from ui import UI

class Game:
    def __init__(self):
        ##audio
        self.bg_overworld_audio= pygame.mixer.Sound('./audio/overworld_music.wav')
        self.bg_level_audio= pygame.mixer.Sound('./audio/level_music.wav')
        self.bg_level_audio.set_volume(0.1)

        # game attr
        self.max_level = 5
        self.max_health = 100
        self.current_health = 100
        self.coins = 0
        # overworld create
        self.overworld = Overworld(0,self.max_level,screen,self.create_level)
        self.status = 'overworld'
        self.bg_overworld_audio.set_volume(0.2)
        self.bg_overworld_audio.play(loops = -1)
        # interface player
        self.ui = UI(screen)

    def create_level(self, current_level):
        self.level = Level(current_level,screen,self.create_overworld, self.get_coins, self.change_health)
        self.status = 'level'
        self.bg_overworld_audio.stop()
        self.bg_level_audio.play(loops = -1)
        #print(current_level)
    def create_overworld(self, current_level, new_max_level):
        self.status = 'overworld'
        self.bg_level_audio.stop()
        self.bg_overworld_audio.play(loops = -1)
        if new_max_level > self.max_level:
            self.max_level = new_max_level
        self.overworld = Overworld(current_level,self.max_level,screen,self.create_level)
    def get_coins(self,amount):
        self.coins += amount
    def change_health(self, amount):
        self.current_health += amount
    def check_game_over(self):
        if self.current_health <= 0:
            self.current_health = self.max_health
            self.coins = 0
            self.max_level = 0
            self.overworld = Overworld(0,self.max_level,screen,self.create_level)
            self.status = 'overworld'
            self.bg_level_audio.stop()
            self.bg_overworld_audio.play(loops = -1)
    def run(self):
        if self.status == 'overworld':
            self.overworld.run()
        else:
            self.level.run()
            self.ui.show_health(
                self.current_health,
                self.max_health
                )
            self.ui.show_coins(self.coins)
            
            self.check_game_over()
## pygame setup
pygame.init()
screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption('Platformer game')
clock = pygame.time.Clock()
game = Game()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            
            sys.exit()

    screen.fill('grey')
    game.run()

    pygame.display.update()
    clock.tick(60) 