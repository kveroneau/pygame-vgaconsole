import vgaconsole, pygame, sys

def main():
    pygame.display.init()
    screen = pygame.display.set_mode((640,400),0,8)
    pygame.display.set_caption('VGA Console BLOAD demo')
    vga = vgaconsole.VGAConsole(screen)
    vga.bload('bsaved.bsv')
    vga.draw()
    pygame.display.update()
    pygame.event.set_blocked(vgaconsole.MOUSEMOTION)
    while True:
        vgaconsole.clock.tick(30)
        events = pygame.event.get()
        for e in events:
            if e.type in (vgaconsole.QUIT, vgaconsole.KEYDOWN,):
                pygame.quit()
                sys.exit()
        vga.draw()
        pygame.display.update()

if __name__ == '__main__':
    main()
