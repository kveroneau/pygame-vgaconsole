import vgaconsole, pygame, sys

class WindowingUI(vgaconsole.VGAConsole):
    mcursor_klass = vgaconsole.AnimatedCursor
    def init(self):
        self.foreground = 15
        self.background = 0
        self.state = None
        self.app = None
        self.frame = 0
        self.screen.set_alpha(0)
        self.screen.set_colorkey(0)
    def window(self, title, text, app):
        self.set_color(15,1)
        self.clear_window(10,10,10,40,c=32)
        self.draw_window(10,10,10,40,title, 15, 1, True)
        self.write(text)
        self.stdio.setpos()
        self.set_color(15,0)
        self.app = app
    def fadein(self):
        self.state = 'fadein'
        self.frame = 0
    def fadeout(self):
        self.state = 'fadeout'
        self.frame = 0
    def draw(self):
        if self.state is not None:
            super(WindowingUI, self).draw()
            self.frame+=5
            if self.state == 'fadein':
                self.screen.set_alpha(self.frame)
                if self.frame > 250:
                    self.state = 'ui'
            elif self.state == 'fadeout':
                self.screen.set_alpha(255-self.frame)
                if self.frame > 250:
                    self.state = None
    def handle_event(self, e):
        if self.app is None:
            return
        handler = getattr(self, 'handle_%s' % self.app, None)
        if handler:
            handler(e)
    def handle_control(self, e):
        if e.type == vgaconsole.MOUSEBUTTONDOWN:
            row,col = self.mousepos()
            if row == 11 and col > 11 and col < 30:
                self.window(' BLOAD Image ', 'Filename: ', 'fileinput')
                self.set_cursor(vgaconsole.AnimatedCursor)
                self.set_mcursor(None)
                self.state, self.filename = 'bload', None
            elif row == 12 and col > 11 and col < 30:
                self.window(' BSAVE Image ', 'Filename: ', 'fileinput')
                self.set_cursor(vgaconsole.AnimatedCursor)
                self.set_mcursor(None)
                self.state, self.filename = 'bsave', None
    def handle_fileinput(self, e):
        if e.type == vgaconsole.KEYDOWN and e.key == 13:
            self.set_cursor(None)
            self.filename = self.stdio.read()
            self.app = None
            self.set_mcursor(vgaconsole.AnimatedCursor)
        else:
            super(WindowingUI, self).handle_event(e)
    def handle_bsave(self, e):
        if e.type == vgaconsole.KEYDOWN and e.key == 13:
            self.set_cursor(None)
            self.filename = self.stdio.read()
            self.app = None
            self.set_mcursor(vgaconsole.AnimatedCursor)
        else:
            super(WindowingUI, self).handle_event(e)

class DrawApp(vgaconsole.VGAConsole):
    mcursor_klass = vgaconsole.BlockCursor
    def init(self):
        self.foreground = 15
        self.background = 0
        self.paint = False
        self.state = 'intro'
        self.draw_window(10,10,10,40," Welcome to VGA Draw! ", 2, 0, True)
        self.write('In this demo you can draw with your    mouse!  Press F1 for additional help atany time.  Files can be loaded and     saved from BSAVE format.\n')
        self.write('\nClick your mouse to begin...')
        self.viewport()
    def mousedraw(self):
        row, col = self.mousepos()
        self.setxy(row,col,219)
    def handle_event(self, e):
        handler = getattr(self, 'handle_%s' % self.state, None)
        if handler:
            handler(e)
    def handle_intro(self, e):
        if e.type == vgaconsole.MOUSEBUTTONUP:
            self.clear_window(10,10,10,40)
            self.state = 'draw'
    def handle_draw(self, e):
        if e.type == vgaconsole.MOUSEBUTTONDOWN:
            if e.button == 1:
                self.mousedraw()
                self.paint = True
            elif e.button == 3:
                if self.ui.state == None:
                    self.set_mcursor(None)
                    self.ui.window(' Control Box ', 'BLOAD a file\nBSAVE a file\n', 'control')
                    self.ui.fadein()
                    self.state = 'ui'
            elif e.button == 4:
                self.foreground +=1
                if self.foreground > 15:
                    self.foreground = 0
            elif e.button == 5:
                self.foreground -=1
                if self.foreground < 0:
                    self.foreground = 15
        elif e.type == vgaconsole.MOUSEBUTTONUP:
            if e.button == 1:
                self.paint = False
        elif self.paint and e.type == vgaconsole.MOUSEMOTION:
            self.mousedraw()
        elif e.type == vgaconsole.KEYDOWN:
            if e.key == 27:
                pygame.quit()
                sys.exit()
            elif e.key == vgaconsole.K_F1:
                self.set_mcursor(None)
                self.ui.window(' Help ', 'Right-click to access the Control box.\nUse mouse wheel to switch colors.', 'help')
                self.ui.fadein()
                self.state = 'ui'
    def handle_ui(self, e):
        if self.ui.state == 'bload' and self.ui.filename is not None:
            self.set_mcursor(vgaconsole.BlockCursor)
            self.ui.fadeout()
            self.state = 'draw'
            self.bload(self.ui.filename)
        elif self.ui.state == 'bsave' and self.ui.filename is not None:
            self.set_mcursor(vgaconsole.BlockCursor)
            self.ui.fadeout()
            self.state = 'draw'
            self.bsave(self.ui.filename)
        if e.type == vgaconsole.KEYDOWN:
            if e.key == 27:
                self.set_mcursor(vgaconsole.BlockCursor)
                self.ui.fadeout()
                self.state = 'draw'
        elif e.type == vgaconsole.MOUSEBUTTONDOWN:
            if e.button == 3:
                if self.ui.state == 'ui':
                    self.set_mcursor(vgaconsole.BlockCursor)
                    self.ui.fadeout()
                    self.state = 'draw'
        self.ui.handle_event(e)

def main():
    pygame.display.init()
    screen = pygame.display.set_mode((640,400))
    pygame.display.set_caption('VGA Console VGA Draw demo')
    vga = DrawApp(screen)
    vga.ui = WindowingUI(screen)
    vga.init()
    vga.ui.init()
    vga.draw()
    pygame.display.update()
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
        vga.ui.draw()
        pygame.display.update()

if __name__ == '__main__':
    main()
