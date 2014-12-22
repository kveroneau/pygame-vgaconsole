import vgaconsole, pygame, sys

class SmileApp(vgaconsole.VGAConsole):
    def init(self):
        self.foreground = 0
        self.background = 2
        self.state = 'intro'
        self.draw_window(10,10,10,40,"Welcome to Smile!", 1, 15, True)
        self.write('In this demo you can move around with  the arrow keys, press ESC or close the window to quit.\n')
        self.write('\nPress ENTER to begin...')
        self.viewport()
        self.loc = [10,10]
    def draw_player(self):
        self.setxy(self.loc[0], self.loc[1], 2)
    def move_player(self, row, col):
        if self.getxy(row,col)[0] == 0:
            self.setxy(self.loc[0], self.loc[1], 0)
            self.loc = [row,col]
            self.draw_player()
    def handle_event(self, e):
        handler = getattr(self, 'handle_%s' % self.state, None)
        if handler:
            handler(e)
    def handle_intro(self, e):
        if e.type == vgaconsole.KEYDOWN:
            if e.key == 13:
                self.clear_window(10,10,10,40)
                self.bload('smile.map')
                self.draw_player()
                self.state = 'game'
    def handle_game(self, e):
        row, col = self.loc
        if e.type == vgaconsole.KEYDOWN:
            if e.key == vgaconsole.K_UP:
                row -=1
            elif e.key == vgaconsole.K_DOWN:
                row +=1
            elif e.key == vgaconsole.K_LEFT:
                col -=1
            elif e.key == vgaconsole.K_RIGHT:
                col +=1
            elif e.key == 27:
                pygame.quit()
                sys.exit()
        if row != self.loc[0] or col != self.loc[1]:
            self.move_player(row, col)

def main():
    pygame.display.init()
    screen = pygame.display.set_mode((640,400),0,8)
    pygame.display.set_caption('VGA Console ASCII Smile demo')
    vga = SmileApp(screen)
    vga.init()
    vga.draw()
    pygame.display.update()
    pygame.event.set_blocked(vgaconsole.MOUSEMOTION)
    while True:
        vgaconsole.clock.tick(30)
        events = pygame.event.get()
        for e in events:
            if e.type == vgaconsole.QUIT:
                pygame.quit()
                sys.exit()
            else:
                vga.handle_event(e)
        vga.draw()
        pygame.display.update()

if __name__ == '__main__':
    main()
