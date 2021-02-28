import pygame
import sys
import random
from os import path

pygame.init()
window = pygame.display.set_mode((400, 710))
pygame.display.set_caption('PyBird')
screen = pygame.Surface((400, 710))
icon = pygame.image.load('images/icon.png')
pygame.display.set_icon(icon)


# меню PyBird
class Menu:
    def __init__(self, pause=False):
        # в зависимости от пауза/главное меню
        if pause:
            self.menu_items = [(135, 400, 'CONTINUE', (255, 255, 255),
                               (0, 0, 0), 0),
                               (170, 450, 'QUIT', (255, 255, 255),
                               (0, 0, 0), 2)]
        else:
            self.menu_items = [(170, 400, 'PLAY', (255, 255, 255),
                               (0, 0, 0), 0),
                               (152, 450, 'RATING', (255, 255, 255),
                               (0, 0, 0), 1),
                               (170, 500, 'QUIT', (255, 255, 255),
                               (0, 0, 0), 2)]

    # рендер пунктов меню
    def render(self, screen, font, item_number):
        for i in self.menu_items:
            if item_number == i[5]:
                screen.blit(font.render(i[2], 1, (255, 255, 255)),
                                       (i[0] + 2, i[1] - 30))
                screen.blit(font.render(i[2], 1, i[4]), (i[0], i[1] - 30))
            else:
                screen.blit(font.render(i[2], 1, (0, 0, 0)),
                                       (i[0] + 2, i[1] - 30))
                screen.blit(font.render(i[2], 1, i[3]), (i[0], i[1] - 30))

    # меню
    def menu(self):
        running = True
        pygame.mouse.set_visible(True)
        pygame.key.set_repeat(0, 0)
        font_menu = pygame.font.Font('fonts/Thintel.ttf', 50)
        menu_image = pygame.image.load("images/menu.png").convert_alpha()
        item = 0
        while running:
            screen.fill((78, 192, 202))
            mouse_pos = pygame.mouse.get_pos()
            for i in self.menu_items:
                if mouse_pos[0] > i[0] and mouse_pos[0] < i[0] + 155 and\
                   mouse_pos[1] > i[1] and mouse_pos[1] < i[1] + 50:
                    item = i[5]
            self.render(screen, font_menu, item)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if item == 0:
                            return 'play'
                        if item == 1:
                            rating = Rating()
                            rating.rating()
                        if item == 2:
                            sys.exit()
                    if event.key == pygame.K_ESCAPE:
                        sys.exit()
                    if event.key == pygame.K_UP:
                        if item > 0:
                            item -= 1
                    if event.key == pygame.K_DOWN:
                        if item < len(self.menu_items) - 1:
                            item += 1
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if item == 0:
                        return 'play'
                    if item == 1:
                        rating = Rating()
                        rating.rating()
                    if item == 2:
                        sys.exit()
            window.blit(screen, (0, 0))
            window.blit(menu_image, (120, 120))
            pygame.display.update()


# класс PyBird
class PyBird:
    def __init__(self):
        self.screen = pygame.display.set_mode((400, 710))
        # звуки
        self.snd_dir = path.join(path.dirname(__file__), 'sounds')
        self.die_sound = pygame.mixer.Sound(path.join(self.snd_dir, 'die.wav'))
        self.point_sound = pygame.mixer.Sound(path.join(self.snd_dir,
                                                        'point.wav'))
        self.wing_sound = pygame.mixer.Sound(path.join(self.snd_dir,
                                                       'wing.wav'))
        # cпрайты
        self.background = pygame.image.load("images/background.png")
        self.birdStatuses = [pygame.image.load("images/"
                                               "soar.png").convert_alpha(),
                             pygame.image.load("images/"
                                               "fly.png").convert_alpha(),
                             pygame.image.load("images/"
                                               "dead.png").convert_alpha()]
        self.barrierTop = pygame.image.load("images/top.png").convert_alpha()
        self.barrierBottom = pygame.image.load("images/"
                                               "bottom.png").convert_alpha()
        self.ground = pygame.image.load("images/ground.png").convert_alpha()
        # герой игры
        self.bird = pygame.Rect(65, 50, 50, 50)
        self.score = 0  # счет
        self.dead = False
        self.status = 0  # переменная состояния птички
        #   0 - парит вниз
        #   1 - взлетает
        #   2 - умирает
        # характеристики
        self.gap = 130  # промежуток между препятствиями
        self.barrierX = 400  # положение препятсвий по оси x
        self.birdY = 350
        self.jump = 0  # скорость падения вниз
        self.jumpSpeed = 10  # скорость взлета
        self.gravity = 5
        self.offset = random.randint(-110, 110)
        # очки
        try:
            f = open('files/top10scores.txt')
            self.scores = [int(i.strip()) for i in f.readlines()]
        except:
            self.scores = []

    def updateWalls(self):
        self.barrierX -= 3  # скорость передвижения препятствий
        # по преодолению героем препятствия начисляется одно очко
        if self.barrierX < -85:
            # препятствие возвращается в прежнее положение
            self.barrierX = 400
            # увеличение на одно очко и звук при увеличении
            self.score += 1
            self.point_sound.play()
            self.offset = random.randint(-110, 110)

    def birdUpdate(self):
        if self.jump:
            # взлет при нажатии
            self.jumpSpeed -= 1
            self.birdY -= self.jumpSpeed
            self.jump -= 1
        else:
            # падение вниз при бездействии
            self.birdY += self.gravity
            self.gravity += 0.2
        self.bird[1] = self.birdY
        # препятствия выраженные в виде объектов-прямоуголников
        upRect = pygame.Rect(self.barrierX,
                             360 + self.gap - self.offset + 10,
                             self.barrierTop.get_width() - 10,
                             self.barrierTop.get_height())
        downRect = pygame.Rect(self.barrierX,
                               0 - self.gap - self.offset - 10,
                               self.barrierBottom.get_width() - 10,
                               self.barrierBottom.get_height())
        groundRect = pygame.Rect(0, 650, 400, 60)
        # при пересечении героя с препятствием self.dead = True
        if upRect.colliderect(self.bird):
            self.dead = True
        if downRect.colliderect(self.bird):
            self.dead = True
        if groundRect.colliderect(self.bird):
            self.dead = True
        # если нет пересечения
        if not 0 < self.bird[1] < 720:
            self.bird[1] = 50
            self.birdY = 50
            self.dead = False
            self.top_scores(self.score)
            self.score = 0
            self.barrierX = 400
            self.offset = random.randint(-110, 110)
            self.gravity = 5

    def top_scores(self, score):
        f = open('files/top10scores.txt', 'w')
        if score != 0:
            self.scores.append(score)
            self.scores.sort(reverse=True)
            for i in self.scores[:10]:
                f.write(str(i) + '\n')
        else:
            self.scores.sort(reverse=True)
            for i in self.scores[:10]:
                f.write(str(i) + '\n')

    def run(self):
        clock = pygame.time.Clock()
        pygame.font.init()
        font = pygame.font.Font('fonts/Thintel.ttf', 120)
        while True:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if (event.type == pygame.MOUSEBUTTONDOWN) and not self.dead:
                    self.jump = 17
                    self.gravity = 5
                    self.jumpSpeed = 10
                    self.wing_sound.play()
                if event.type == pygame.KEYDOWN and not self.dead:
                    if event.key == pygame.K_ESCAPE:
                        menu = Menu(True)
                        menu.menu()
                    if event.key == pygame.K_w or event.key == pygame.K_UP\
                       or pygame.K_SPACE:
                        self.jump = 17
                        self.gravity = 5
                        self.jumpSpeed = 10
                        self.wing_sound.play()
            self.screen.fill((255, 255, 255))
            # фон
            self.screen.blit(self.background, (0, 0))
            # препятствия
            self.screen.blit(self.barrierTop,
                             (self.barrierX, 360 + self.gap - self.offset))
            self.screen.blit(self.barrierBottom,
                             (self.barrierX, 0 - self.gap - self.offset))
            # "земля"
            self.screen.blit(self.ground, (0, 650))
            # очки
            self.screen.blit(font.render(str(self.score),
                                         -1,
                                         (0, 0, 0)),
                             (200, 50))
            self.screen.blit(font.render(str(self.score),
                                         -1,
                                         (255, 255, 255)),
                             (197, 50))
            if self.dead:
                self.status = 2
            elif self.jump:
                self.status = 1
            self.screen.blit(self.birdStatuses[self.status], (70, self.birdY))
            if not self.dead:
                self.status = 0
            # обновление
            self.updateWalls()
            self.birdUpdate()
            pygame.display.update()


# класс рейтинга очков
class Rating:
    def __init__(self):
        # back - выйти в главное меню
        self.items = [(50, 650, 'BACK', (255, 255, 255), (0, 0, 0), 0)]
        try:
            f = open('files/top10scores.txt')
            self.scores = [int(i.strip()) for i in f.readlines()]
            self.scores.sort(reverse=True)
        except:
            self.scores = []

    # рендер пункта back
    def render(self, screen, font, item_number):
        for i in self.items:
            if item_number == i[5]:
                screen.blit(font.render(i[2], 1, (255, 255, 255)),
                                       (i[0] + 2, i[1] - 30))
                screen.blit(font.render(i[2], 1, i[4]), (i[0], i[1] - 30))
            else:
                screen.blit(font.render(i[2], 1, (0, 0, 0)),
                                       (i[0] + 2, i[1] - 30))
                screen.blit(font.render(i[2], 1, i[3]), (i[0], i[1] - 30))

    # таблица рейтинга
    def rating(self):
        running = True
        pygame.mouse.set_visible(True)
        pygame.key.set_repeat(0, 0)
        font_item = pygame.font.Font('fonts/Thintel.ttf', 50)
        font = pygame.font.Font('fonts/Thintel.ttf', 30)
        menu_image = pygame.image.load("images/menu.png").convert_alpha()
        item = 0
        while running:
            screen.fill((78, 192, 202))
            mouse_pos = pygame.mouse.get_pos()
            for i in self.items:
                if mouse_pos[0] > i[0] and mouse_pos[0] < i[0] + 155 and\
                   mouse_pos[1] > i[1] and mouse_pos[1] < i[1] + 50:
                    item = i[5]
            self.render(screen, font_item, item)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return 'back'
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    return 'back'
            y = 50
            # прорисовка таблицы очков
            for count, value in enumerate(self.scores[:10], start=1):
                screen.blit(font.render(f'#{count}. {value}', -1,
                                        (255, 255, 255)), (52, y))
                screen.blit(font.render(f'#{count}. {value}', -1,
                                        (0, 0, 0)), (50, y))
                y += 50
            window.blit(screen, (0, 0))
            pygame.display.update()

menu = Menu()
menu.menu()
PyBird().run()
