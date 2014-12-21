import pygame, sys
from pygame.locals import *
import mmap
from struct import unpack

clock = pygame.time.Clock()

class VGAConsole(object):
    def __init__(self):
        self.loadData()
        self.vgabuf = mmap.mmap(-1, 4000)
        pygame.display.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((640,400),0,8)
        pygame.display.set_caption('VGA Console test')
        self.font = pygame.font.Font('VGA.ttf', 16)
        self.cursor = self.font.render(chr(219),0,self.VGA_PALETTE[7])
        pygame.mouse.set_visible(False)
        self.pos = [0,0]
        self.background = self.VGA_PALETTE[1]
        self.shift = False
        self.cframe = 0
        self.cframes = []
        for c in ('|', '/', '-', '\\',):
            self.cframes.append(self.font.render(c,0,self.VGA_PALETTE[15],self.background))
    def loadData(self):
        self.VGA_PALETTE, self.US_SHIFTMAP = [], {}
        with open('VGA.bin','rb') as f:
            for i in range(0,16):
                self.VGA_PALETTE.append(unpack('BBB',f.read(3)))
            for i in range(0,ord(f.read(1))):
                k,v = unpack('BB',f.read(2))
                self.US_SHIFTMAP[k] = v        
    def draw(self):
        self.screen.fill(self.background)
        self.vgabuf.seek(0)
        for y in range(0,25):
            for x in range(0,80):
                attr = ord(self.vgabuf.read_byte())
                fg,bg = 7,0
                if attr > 0:
                    fg,bg = attr&0xf, (attr&0xf0)>>4
                c = self.vgabuf.read_byte()
                if ord(c) > 0:
                    self.screen.blit(self.font.render(c,0,self.VGA_PALETTE[fg],self.VGA_PALETTE[bg]), (x*8,y*16))
        self.drawMouse()
        self.drawCursor()
        pygame.display.update()
    def setXY(self, row, col, c):
        self.vgabuf.seek((80*row+col)*2)
        self.vgabuf.write(chr(0x1f)+chr(c))
    def type(self, c):
        if c == 13:
            self.pos[1] = 0
            self.pos[0] +=1
        elif c == 8:
            if self.pos[1] > 0:
                self.pos[1] -=1
                self.setXY(self.pos[0], self.pos[1], 0)
        elif c == 9:
            self.pos[1] += 8
        elif c == 27:
            pygame.quit()
            sys.exit()
        else:
            self.setXY(self.pos[0], self.pos[1], c)
            self.pos[1] +=1
        if self.pos[1] > 80:
            self.pos[1] = 0
            self.pos[0] += 1
    def write(self, text):
        for c in text:
            self.type(ord(c))
    def draw_ascii(self):
        row, col = 10,10
        for c in range(0,255):
            self.setXY(row,col,c)
            col +=1
            if col > 41:
                col = 10
                row+=1
    def draw_window(self, row, col, height, width, title=None):
        self.setPos(row, col)
        brd = chr(205)*(width-1)
        self.write(chr(213)+brd+chr(184))
        for y in range(row+1, row+height):
            self.setXY(y, col, 179)
            self.setXY(y, col+width, 179)
        self.setPos(row+height, col)
        self.write(chr(212)+brd+chr(190))
        if title:
            self.setPos(row, col+((width/2)-len(title)/2))
            self.write(title)
    def clear_window(self, row, col, height, width):
        for y in range(row, row+height+1):
            self.setPos(y, col)
            self.write(chr(0)*(width+1))
    def setPos(self, row, col):
        self.pos = [row, col]
    def clearScreen(self):
        self.vgabuf.seek(0)
        self.vgabuf.write(chr(0)*4000)
        self.setPos(0, 0)
    def mousePos(self):
        x,y = pygame.mouse.get_pos()
        return (y/16, x/8)
    def drawMouse(self):
        row,col = self.mousePos()
        self.screen.blit(self.cursor, (col*8,row*16))
    def drawCursor(self):
        self.screen.blit(self.cframes[self.cframe/3%4], (self.pos[1]*8,self.pos[0]*16))
        self.cframe+=1
    def main(self):
        self.draw_ascii()
        self.draw_window(9,9,9,33, ' ASCII ')
        self.setPos(0, 0)
        self.write('Welcome to VGAConsole!\rC:\>')
        self.draw()
        #pygame.event.set_blocked(MOUSEMOTION)
        while 1:
            clock.tick(30)
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEBUTTONUP:
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
            self.draw()

VGAConsole().main()
