import pygame

class UI:
    def __init__(self,surface):
        # setup
        self.display_surface = surface
        # health
        self.health_bar_topleft = (54,39)
        self.bar_max_width = 152
        self.bar_height = 4
        self.health_bar = pygame.image.load('./graphics/ui/health_bar.png').convert_alpha()
        # coins
        self.coin = pygame.image.load('./graphics/ui/coin.png').convert_alpha()
        self.coin_rect = self.coin.get_rect(topleft = (50,60))
        coin_amount_font = './graphics/ui/ARCADEPI.TTF'
        self.font = pygame.font.Font(coin_amount_font,(20))

    def show_health(self,current_health,full):
        self.display_surface.blit(self.health_bar,(20,10))
        current_health_ratio = current_health / full
        current_bar_width = self.bar_max_width * current_health_ratio
        health_bar_rect = pygame.Rect(self.health_bar_topleft,(current_bar_width,self.bar_height))
        pygame.draw.rect(self.display_surface,'#dc4949',health_bar_rect)
    
    def show_coins(self,amount):
        self.display_surface.blit(self.coin,self.coin_rect)
        coin_amount_surf = self.font.render(str(amount),False,'#33323d')
        coin_amount_rect = coin_amount_surf.get_rect(midleft = (self.coin_rect.right +10,self.coin_rect.centery))
        self.display_surface.blit(coin_amount_surf,coin_amount_rect)
    def update(self):
        pass