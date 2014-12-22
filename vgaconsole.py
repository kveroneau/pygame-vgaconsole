import pygame, sys
from pygame.locals import *
import mmap
from struct import unpack

clock = pygame.time.Clock()

class Cursor(object):
    frames = None
    animated = False
    rate = 3
    def __init__(self, console, fg, bg):
        self.console = console
        self.cframe, self.cframes = 0, []
        for c in self.frames:
            self.cframes.append(console.font.render(c,0,fg,bg))
        if len(self.cframes) > 1:
            self.animated = True
    def draw(self, row=None, col=None):
        if row is None:
            pos = (self.console.pos[1]*8,self.console.pos[0]*16)
        else:
            pos = (col*8, row*16)
        if self.animated:
            frame = self.cframe/self.rate%len(self.cframes)
            self.cframe+=1
        else:
            frame = 0
        self.console.screen.blit(self.cframes[frame], pos)
        self.cframe+=1

class AnimatedCursor(Cursor):
    frames = ('|', '/', '-', '\\',)

class TraditionalCursor(Cursor):
    frames = ('_', ' ',)
    rate = 10

class BlockCursor(Cursor):
    frames = (chr(219),)

class BlinkCursor(Cursor):
    frames = (chr(219), ' ',)
    rate = 10

class TextBuffer(object):
    def __init__(self, console):
        self.console = console
        self.ibuffer = ''
        self.obuffer = ''
        self.input_active = False
        self.pos = [0,0]
    def write(self, data):
        self.obuffer+=data
        if not self.input_active:
            self.console.write(self.obuffer)
            self.obuffer = ''
    def read(self, size=None):
        if size is None:
            data = self.ibuffer
            self.ibuffer = ''
        else:
            if size>len(self.ibuffer):
                return self.read()
            data = self.ibuffer[:size]
            self.ibuffer = self.ibuffer[size:]
        return data
    def input(self, c):
        if c == 8:
            if len(self.ibuffer) > 0 and self.pos[1]+len(self.ibuffer) > 0:
                self.console.setxy(self.pos[0], self.pos[1]+len(self.ibuffer), 0)
                self.ibuffer = self.ibuffer[:-1]
        elif c == 27:
            pygame.quit()
            sys.exit()
        else:
            self.ibuffer += chr(c)
    def setpos(self, row=None, col=None):
        if row is None:
            self.pos = self.console.pos
        else:
            self.pos = [row,col]
    def draw(self):
        self.console.setpos(*self.pos)
        self.console.write(self.ibuffer)

class VGAConsole(object):
    cursor_klass = None
    mcursor_klass = None
    def __init__(self, surface=None, pos=(0,0)):
        self.surface = surface
        self.blitpos = pos
        self.load_data()
        self.vgabuf = mmap.mmap(-1, 4000)
        if not pygame.font.get_init():
            pygame.font.init()
        self.screen = pygame.surface.Surface((640,400),0,8)
        self.font = pygame.font.Font('VGA.ttf', 16)
        pygame.mouse.set_visible(False)
        self.pos = [0,0]
        self.foreground = 15
        self.background = 1
        self.shift = False
        self.stack = []
        self.ibuffer = ''
        self.render_cursor()
        self.render_mcursor()
        self.stdio = TextBuffer(self)
    def render_cursor(self):
        if self.cursor_klass:
            self.cursor = self.cursor_klass(self, self.VGA_PALETTE[self.foreground], self.VGA_PALETTE[self.background])
    def render_mcursor(self):
        if self.mcursor_klass:
            self.mcursor = self.mcursor_klass(self, self.VGA_PALETTE[self.foreground], self.VGA_PALETTE[self.background])
    def get_surface(self):
        return self.screen
    def set_color(self, fg=None, bg=None):
        if fg:
            self.foreground = fg
        if bg:
            self.background = bg
    def load_data(self):
        self.VGA_PALETTE, self.US_SHIFTMAP = [], {}
        with open('VGA.bin','rb') as f:
            for i in range(0,16):
                self.VGA_PALETTE.append(unpack('BBB',f.read(3)))
            for i in range(0,ord(f.read(1))):
                k,v = unpack('BB',f.read(2))
                self.US_SHIFTMAP[k] = v        
    def draw(self):
        self.screen.fill(self.VGA_PALETTE[self.background])
        self.stdio.draw()
        self.vgabuf.seek(0)
        for y in range(0,25):
            for x in range(0,80):
                attr = ord(self.vgabuf.read_byte())
                fg,bg = self.foreground,self.background
                if attr > 0:
                    fg,bg = attr&0xf, (attr&0xf0)>>4
                c = self.vgabuf.read_byte()
                if ord(c) > 0:
                    self.screen.blit(self.font.render(c,0,self.VGA_PALETTE[fg],self.VGA_PALETTE[bg]), (x*8,y*16))
        self.draw_mouse()
        if self.cursor_klass:
            self.cursor.draw()
        if self.surface:
            self.surface.blit(self.screen, self.blitpos)
    def setxy(self, row, col, c, fg=None, bg=None):
        if fg is None:
            fg = self.foreground
        if bg is None:
            bg = self.background
        self.vgabuf.seek((80*row+col)*2)
        self.vgabuf.write(chr(fg|bg<<4)+chr(c))
    def type(self, c):
        if c == 10:
            self.pos[1] = 0
            self.pos[0] +=1
        elif c == 9:
            self.pos[1] += 8
        else:
            self.setxy(self.pos[0], self.pos[1], c)
            self.pos[1] +=1
        if self.pos[1] > 80:
            self.pos[1] = 0
            self.pos[0] += 1
    def write(self, text):
        for c in text:
            self.type(ord(c))
    def push(self, t):
        self.stack.append(t)
    def pop(self):
        return self.stack.pop()
    def draw_window(self, row, col, height, width, title=None, fg=None, bg=None):
        self.push((self.foreground,self.background))
        if fg is not None:
            self.foreground = fg
        if bg is not None:
            self.background = bg
        self.setpos(row, col)
        brd = chr(205)*(width-1)
        self.write(chr(213)+brd+chr(184))
        for y in range(row+1, row+height):
            self.setxy(y, col, 179)
            self.setxy(y, col+width, 179)
        self.setpos(row+height, col)
        self.write(chr(212)+brd+chr(190))
        if title:
            self.setpos(row, col+((width/2)-len(title)/2))
            self.write(title)
        self.foreground,self.background = self.pop()
    def clear_window(self, row, col, height, width, bg=None):
        if bg is None:
            bg = self.background
        for y in range(row, row+height+1):
            self.setpos(y, col)
            self.write(chr(0)*(width+1))
    def setpos(self, row, col):
        self.pos = [row, col]
    def clear_screen(self):
        self.vgabuf.seek(0)
        self.vgabuf.write(chr(0)*4000)
        self.setpos(0, 0)
    def mousepos(self):
        x,y = pygame.mouse.get_pos()
        return (y/16, x/8)
    def draw_mouse(self):
        if self.mcursor_klass:
            self.mcursor.draw(*self.mousepos())
    def handle_event(self, event):
        if event.type == MOUSEBUTTONUP:
            oldpos = self.pos
            self.clear_window(9, 9, 9, 33)
            self.pos = oldpos
        elif event.type == KEYDOWN:
            if event.key == K_LSHIFT or event.key == K_RSHIFT:
                self.shift = True
            if event.key == 13:
                print "Capture this text in your own code: %s" % self.stdio.read()
                self.pos[0] +=1
                self.pos[1] = 0
                self.stdio.setpos(*self.pos)
            elif event.key > 0 and event.key < 256:
                c = event.key
                if self.shift:
                    if c > 96 and c < 123:
                        c-=32
                    elif c in self.US_SHIFTMAP.keys():
                        c = self.US_SHIFTMAP[c]
                self.stdio.input(c)
        elif event.type == KEYUP:
            if event.key == K_LSHIFT or event.key == K_RSHIFT:
                self.shift = False

class ExampleApp(VGAConsole):
    cursor_klass = AnimatedCursor
    mcursor_klass = BlockCursor
    def draw_ascii(self):
        row, col = 10,10
        for c in range(0,255):
            self.setxy(row,col,c)
            col +=1
            if col > 41:
                col = 10
                row+=1
    def init(self):
        self.draw_ascii()
        self.draw_window(9,9,9,33, ' ASCII ', 1, 15)
        self.setpos(0, 0)
        self.write('Welcome to VGAConsole!\nC:\>')
        self.stdio.setpos()

def main():
    pygame.display.init()
    screen = pygame.display.set_mode((640,400),0,8)
    pygame.display.set_caption('VGA Console test')
    vga = ExampleApp(screen)
    vga.init()
    vga.draw()
    pygame.display.update()
    while True:
        clock.tick(30)
        events = pygame.event.get()
        for e in events:
            if e.type == QUIT:
                pygame.quit()
                sys.exit()
            else:
                vga.handle_event(e)
        vga.draw()
        pygame.display.update()

if __name__ == '__main__':
    main()
