import vgaconsole, cmd, pygame, sys, shlex, subprocess

class CLI(cmd.Cmd):
    """
    This is an example command line system, this class should work on either a
    normal command line by using the standard cmdloop() method or by attaching
    it to a VGA Console text buffer object.
    """
    intro = "Welcome to VGAConsole!"
    def emptyline(self):
        pass
    def do_exit(self, args):
        """ This command will exit this test console. """
        pygame.quit()
        sys.exit()
        return True
    def get_cursor(self, kind, args):
        """ A helper function to confirm the class is a cursor object. """
        if args == '':
            self.stdout.write(' ** You need to specify a %s cursor class to use.\n' % kind)
            return
        klass = getattr(vgaconsole, args, None)
        if klass is None:
            self.stdout.write(' ** Could not find that class.\n')
            return
        if isinstance(klass,type) and issubclass(klass, vgaconsole.Cursor):
            return klass
        else:
            self.stdout.write(' ** Class is not a valid Cursor class.\n')
    def do_mouse(self, args):
        """ Changes the mouse cursor to a different class. """
        if args == 'None':
            self.console.mcursor_klass = None
            self.console.render_mcursor()
            return
        klass = self.get_cursor('mouse', args)
        if klass:
            self.console.mcursor_klass = klass
            self.console.render_mcursor()
    def do_cursor(self, args):
        """ Changes the text cursor to a different class. """
        if args == 'None':
            self.console.cursor_klass = None
            self.console.render_cursor()
            return
        klass = self.get_cursor('text', args)
        if klass:
            self.console.cursor_klass = klass
            self.console.render_cursor()
    def do_ls(self, args):
        """ List available classes. """
        cursors = []
        for klass in dir(vgaconsole):
            o = getattr(vgaconsole, klass)
            if isinstance(o,type) and issubclass(o, vgaconsole.Cursor):
                cursors.append(klass)
        self.columnize(cursors)
    def do_cls(self, args):
        """ Clears the console. """
        self.console.clear_screen()
    def do_color(self, args):
        """ Changes both the foreground and background colors. """
        s = shlex.split(args)
        try:
            fg, bg = int(s[0]), int(s[1])
        except:
            self.stdout.write(' ** Please ensure you only use integers.\n')
            return
        if fg > 15 or bg > 15:
            self.stdout.write(' ** Please use values between 0 and 15.\n')
            return
        self.console.set_color(fg,bg)
    def do_shell(self, args):
        """ Example subprocess. """
        s = shlex.split(args)
        p = subprocess.Popen(s, stdout=subprocess.PIPE)
        out = p.communicate()
        self.stdout.write(out[0])
    def do_bload(self, args):
        """ Perfoems a bload operation. """
        if args != '':
            self.console.bload(args)
    def do_bsave(self, args):
        """ Performs a bsave operation. """
        if args != '':
            self.console.bsave(args)

class ConsoleApp(vgaconsole.VGAConsole):
    cursor_klass = vgaconsole.AnimatedCursor
    mcursor_klass = vgaconsole.BlockCursor
    def init(self):
        self.cli = CLI(stdin=self.stdio, stdout=self.stdio)
        self.cli.console = self
        self.stdio.write(self.cli.intro+'\n'+self.cli.prompt)
        #self.stdio.setpos()
    def parse(self):
        self.stdio.write('\n')
        line = self.stdio.read()
        if not self.cli.onecmd(line):
            self.stdio.write(self.cli.prompt)
            #self.stdio.setpos()

def main():
    pygame.display.init()
    screen = pygame.display.set_mode((640,400),0,8)
    pygame.display.set_caption('VGA Console Command line')
    vga = ConsoleApp(screen)
    vga.init()
    vga.draw()
    pygame.display.update()
    while True:
        vgaconsole.clock.tick(30)
        events = pygame.event.get()
        for e in events:
            if e.type == vgaconsole.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == vgaconsole.KEYDOWN and e.key == 13:
                vga.parse()
            else:
                vga.handle_event(e)
        vga.draw()
        pygame.display.update()

if __name__ == '__main__':
    main()
