import pygame, sys
from pygame.locals import *
import mmap
from struct import unpack

clock = pygame.time.Clock()

class VGAConsole(object):
    def __init__(self, surface=None, pos=(0,0)):
        self.surface = surface
        self.blitpos = pos
        self.load_data()
        self.vgabuf = mmap.mmap(-1, 4000)
        if not pygame.font.get_init():
            pygame.font.init()
        self.screen = pygame.surface.Surface((640,400),0,8)
        self.font = pygame.font.Font('VGA.ttf', 16)
        self.cursor = self.font.render(chr(219),0,self.VGA_PALETTE[7])
        pygame.mouse.set_visible(False)
        self.pos = [0,0]
        self.foreground = 15
        self.background = 1
        self.shift = False
        self.cframe = 0
        self.cframes = []
        self.stack = []
        for c in ('|', '/', '-', '\\',):
            self.cframes.append(self.font.render(c,0,self.VGA_PALETTE[self.foreground],self.VGA_PALETTE[self.background]))
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
        self.draw_cursor()
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
        if c == 13:
            self.pos[1] = 0
            self.pos[0] +=1
        elif c == 8:
            if self.pos[1] > 0:
                self.pos[1] -=1
                self.setxy(self.pos[0], self.pos[1], 0)
        elif c == 9:
            self.pos[1] += 8
        elif c == 27:
            pygame.quit()
            sys.exit()
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
        row,col = self.mousepos()
        self.screen.blit(self.cursor, (col*8,row*16))
    def draw_cursor(self):
        self.screen.blit(self.cframes[self.cframe/3%4], (self.pos[1]*8,self.pos[0]*16))
        self.cframe+=1
    def handle_event(self, event):
        if event.type == MOUSEBUTTONUP:
            oldpos = self.pos
            self.clear_window(9, 9, 9, 33)
            self.pos = oldpos
        elif event.type == KEYDOWN:
            if event.key == K_LSHIFT or event.key == K_RSHIFT:
                self.shift = True
            if event.key > 0 and event.key < 256:
                c = event.key
                if self.shift:
                    if c > 96 and c < 123:
                        c-=32
                    elif c in self.US_SHIFTMAP.keys():
                        c = self.US_SHIFTMAP[c]
                self.type(c)
        elif event.type == KEYUP:
            if event.key == K_LSHIFT or event.key == K_RSHIFT:
                self.shift = False

class ExampleApp(VGAConsole):
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
        self.write('Welcome to VGAConsole!\rC:\>')

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
