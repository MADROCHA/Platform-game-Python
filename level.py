import pygame
from support import *
from settings import *
from tiles import AnimatedTile, Coin, Palm, Tile, StaticTile, Crate
from enemy import Enemy
from decorations import Clouds, Sky, Water
from player import Player
from particles import ParticleEffect
from game_data import levels

class Level:
    def __init__(self,current_level,surface,create_overworld,get_coins,change_health):
        ### setup
        ## audio
        self.get_coin_sound = pygame.mixer.Sound('./audio/effects/coin.wav')
        self.stomp_sound = pygame.mixer.Sound('./audio/effects/stomp.wav')
        ## general
        self.display_surface = surface
        self.world_shift = 0
        #self.current_x = None
        ## overworld connection
        self.current_level = current_level
        level_data = levels[self.current_level]
        self.new_max_level = level_data['unlock']
        self.create_overworld = create_overworld
        ## player
        player_layout = import_csv_layout(level_data['player'])
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()
        self.player_setup(player_layout, change_health)
        ##
        ##
        self.get_coins = get_coins
        ## dust
        self.player_on_ground = False
        self.dust_sprite = pygame.sprite.GroupSingle()
        ## explosion
        self.explosion_sprites = pygame.sprite.Group()
        ## terrain
        terrain_layout = import_csv_layout(level_data['terrain'])
        self.terrain_sprites = self.create_tile_group(terrain_layout,'terrain')
        ## grass
        grass_layout = import_csv_layout(level_data['grass'])
        self.grass_sprites = self.create_tile_group(grass_layout,'grass')
        ## crates
        crate_layout = import_csv_layout(level_data['crates'])
        self.crate_sprites = self.create_tile_group(crate_layout,'crates')
        ## coins
        coin_layout = import_csv_layout(level_data['coins'])
        self.coin_sprites = self.create_tile_group(coin_layout,'coins')
        ##
        fg_palm_layout = import_csv_layout(level_data['fg palms'])
        self.fg_palm_sprites = self.create_tile_group(fg_palm_layout,'fg palms')
        ##
        bg_palm_layout = import_csv_layout(level_data['bg palms'])
        self.bg_palm_sprites = self.create_tile_group(bg_palm_layout,'bg palms')
        ##
        enemy_layout = import_csv_layout(level_data['enemies'])
        self.enemy_sprites = self.create_tile_group(enemy_layout,'enemies')
        ##
        constraint_layout = import_csv_layout(level_data['constraints'])
        self.constraint_sprites = self.create_tile_group(constraint_layout,'constraints')
        ##
        self.sky = Sky(8)
        level_width = len(terrain_layout[0]) * tile_size
        self.water = Water(screen_height - 40,level_width)
        self.clouds = Clouds(400,level_width,15)
    
    def create_jump_particles(self,pos):
        if self.player.sprite.facing_right:
            pos -= pygame.math.Vector2(10,15)
        else:
            pos += pygame.math.Vector2(10,-15)
        jump_dust_particle = ParticleEffect(pos,'jump')
        self.dust_sprite.add(jump_dust_particle)

    def player_setup(self,layout, change_health):
        for row_index,row in enumerate(layout):
            for col_index,val in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size
                if val == '0':
                    #print('player start')
                    sprite = Player((x,y),self.display_surface,self.create_jump_particles,change_health)
                    self.player.add(sprite)
                if val == '1':
                    hat_surface = pygame.image.load('./graphics/character/hat.png').convert_alpha()
                    sprite = StaticTile(tile_size,x,y,hat_surface)
                    self.goal.add(sprite)
    
    def create_tile_group(self,layout,type):
        sprite_group = pygame.sprite.Group()
        for row_index,row in enumerate(layout):
            #print(row_index),print(row)   
            for col_index,val in enumerate(row):
                if val != '-1':
                    x = col_index * tile_size
                    y = row_index * tile_size

                    if type == 'terrain':
                        terrain_tile_list = import_cut_graphics('./graphics/terrain/terrain_tiles.png')
                        tile_surface = terrain_tile_list[int(val)]
                        sprite = StaticTile(tile_size,x,y,tile_surface)
                    if type == 'grass':
                        grass_tile_list = import_cut_graphics('./graphics/decoration/grass/grass.png')
                        tile_surface = grass_tile_list[int(val)]
                        sprite = StaticTile(tile_size,x,y,tile_surface)
                    if type == 'crates':
                        sprite = Crate(tile_size,x,y)
                    if type == 'coins':
                        if val == '0':
                            sprite = Coin(tile_size,x,y,'./graphics/coins/gold',5)
                        if val == '1':
                            sprite = Coin(tile_size,x,y,'./graphics/coins/silver',1)
                    if type == 'fg palms':
                        if val == '0':
                            sprite = Palm(tile_size,x,y,'./graphics/terrain/palm_small',38)
                        if val == '1':
                            sprite = Palm(tile_size,x,y,'./graphics/terrain/palm_large',64)
                    if type == 'bg palms':
                        sprite = Palm(tile_size,x,y,'./graphics/terrain/palm_bg',64)
                    if type == 'enemies':
                        sprite = Enemy(tile_size,x,y,)
                    if  type == 'constraints':
                        sprite = Tile(tile_size,x,y)
                        
                    sprite_group.add(sprite)
        return sprite_group
    
    def reverse_enemies_collides(self):
        for enemy in self.enemy_sprites.sprites():
            if pygame.sprite.spritecollide(enemy,self.constraint_sprites,False):
                enemy.reverse_speed()
    
    def horizontal_movement_collision(self):
        player = self.player.sprite
        player.collision_rect.x += player.direction.x * player.speed
        collidable_sprites = self.terrain_sprites.sprites() + self.crate_sprites.sprites() + self.fg_palm_sprites.sprites()
        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.collision_rect):
                if player.direction.x < 0: # move left
                    player.collision_rect.left = sprite.rect.right
                    player.on_left = True
                    #self.current_x = player.rect.left
                elif player.direction.x > 0: # move right
                    player.collision_rect.right = sprite.rect.left
                    player.on_right = True
                    #self.current_x = player.rect.right

        

    def vertical_movement_collision(self):
        player = self.player.sprite
        player.apply_gravity()
        collidable_sprites = self.terrain_sprites.sprites() + self.crate_sprites.sprites() + self.fg_palm_sprites.sprites()
        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.collision_rect):
                if player.direction.y > 0: ## move downwards
                    player.collision_rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True
                elif player.direction.y < 0: ## move upwards
                    player.collision_rect.top = sprite.rect.bottom
                    player.direction.y = 0
                    player.on_ceiling = True

        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False
        
    
    def scroll_x(self):
        player = self.player.sprite
        player_x = player.rect.centerx
        direction_x = player.direction.x

        if player_x < screen_width * 0.25 and direction_x < 0:
            self.world_shift = 8
            player.speed = 0
        
        elif player_x > screen_width - (screen_width * 0.25) and direction_x > 0:
            self.world_shift = -8
            player.speed = 0
        else:
            self.world_shift = 0
            player.speed = 8
    
    def get_player_on_ground(self):
        if self.player.sprite.on_ground:
            self.player_on_ground = True
        else:
            self.player_on_ground = False

    def create_landing_dust(self):
        if not self.player_on_ground and self.player.sprite.on_ground and not self.dust_sprite.sprites():
            if self.player.sprite.facing_right:
                offset = pygame.math.Vector2(10,20)
            else:
                offset = pygame.math.Vector2(-10,20)

            fall_dust_particle = ParticleEffect(self.player.sprite.rect.midbottom - offset,'land') 
            self.dust_sprite.add(fall_dust_particle)
    
    def check_death(self):
        if self.player.sprite.rect.top > screen_height:
            self.create_overworld(self.current_level,0)
    def check_win(self):
        if pygame.sprite.spritecollide(self.player.sprite,self.goal,False):
            self.create_overworld(self.current_level,self.new_max_level)
    def check_coin_collision(self):
        collided_coins = pygame.sprite.spritecollide(self.player.sprite,self.coin_sprites, True)
        if collided_coins:
            for coin in collided_coins:
                self.get_coin_sound.play()
                self.get_coins(coin.value)
    def check_enemy_collisions(self):
        enemy_collisions_list = pygame.sprite.spritecollide(self.player.sprite,self.enemy_sprites,False)
        if enemy_collisions_list:
            for enemy_collide in enemy_collisions_list:
                enemy_center = enemy_collide.rect.centery
                enemy_top = enemy_collide.rect.top
                player_bottom = self.player.sprite.rect.bottom
                if enemy_top < player_bottom < enemy_center and self.player.sprite.direction.y >= 0:
                    self.stomp_sound.play()
                    self.player.sprite.direction.y = -15
                    enemy_defeat_explosion_sprite = ParticleEffect(enemy_collide.rect.midtop,'explosion')
                    self.explosion_sprites.add(enemy_defeat_explosion_sprite)
                    enemy_collide.kill()
                    ## alternative landing -
                    #self.player.sprite.direction.y -= 15
                    ## 
                else:
                    self.player.sprite.get_hit_by_enemy()

    
    def run(self):
        ## RUN THE LEVEL / GAME
        self.sky.draw(self.display_surface)
        self.clouds.draw(self.display_surface,self.world_shift)

        self.bg_palm_sprites.update(self.world_shift)
        self.bg_palm_sprites.draw(self.display_surface)

        self.dust_sprite.update(self.world_shift)
        self.dust_sprite.draw(self.display_surface)

        self.terrain_sprites.update(self.world_shift)
        self.terrain_sprites.draw(self.display_surface)

        self.crate_sprites.update(self.world_shift)
        self.crate_sprites.draw(self.display_surface)

        self.enemy_sprites.update(self.world_shift)
        self.constraint_sprites.update(self.world_shift)
        self.reverse_enemies_collides()
        self.enemy_sprites.draw(self.display_surface)

        self.explosion_sprites.update(self.world_shift)
        self.explosion_sprites.draw(self.display_surface)


        self.grass_sprites.update(self.world_shift)
        self.grass_sprites.draw(self.display_surface)

        self.coin_sprites.update(self.world_shift)
        self.coin_sprites.draw(self.display_surface)

        self.fg_palm_sprites.update(self.world_shift)
        self.fg_palm_sprites.draw(self.display_surface)

        #self.dust_sprite.update(self.world_shift)
        #self.dust_sprite.draw(self.display_surface)

        self.player.update()
        self.horizontal_movement_collision()
        self.get_player_on_ground()
        self.vertical_movement_collision()
        self.create_landing_dust()

        self.scroll_x()
        self.player.draw(self.display_surface)
        self.goal.update(self.world_shift)
        self.goal.draw(self.display_surface)

        self.check_death()
        self.check_win()
        self.check_coin_collision()
        self.check_enemy_collisions()

        self.water.draw(self.display_surface, self.world_shift)
        