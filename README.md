VGA Text mode console for Pygame
--------------------------------

My source code is highly undocumented at the current moment,
I do plan on adding doc strings throughout in a future revision.

At the current moment, the class runs as a stand-alone application,
but from looking at how the main() function works, you should be
able to easily tailor it to your own game/program.

This isn't yet a full VGA text mode emulator, and there are still
some major features missing.  One of the most notable features is
ANSI escape sequences.  At the moment, all the color and cursor
movement comands are done via the Python API.  However, in the
future, I do plan on implementing the ANSI escape sequences in so
that ANSI Art and other such programs that depend on ANSI will
function.

At the moment, there is no input or output buffering done on the
text.  The current write() statement accesses the VGA memory
buffer directly to do it's manipulation.  In a future release,
proper buffering will be added, this will enable a fully
functional command-line to be built with both stdin and stdout.

The current text cursor is fully animated, but can be changed
back to a solid brick or something else if it is too distracting
for your specific application or game.

A demo of mouse support is also available in this preview demo,
you can freely move the cursor around the screen and it will
respond to a click.  The mouse API is in there, but not used
in the demo application.  You can grab the text location of
the mouse using the getPos() API.

Another example API in this demo, is the basics of a windowing
system done in ASCII.  There is both an API to draw a window,
and then clear it afterwards.  There is currently no API to
save the contents behind the window.  However, you can use
the standard Pygame API on Surfaces to easily copy the image
data.  In the future, I will include such an API natively,
which will either copy the RAW memory buffer or copy the
image data onto a new Surface.

All current APIs in this preview demo are subject to change,
I will be spliting much of it into separate classes in the
future.  Classes which will be extendable by your own
application or game.  I hope to contain all the VGA specific
emulation in it's own class, text input, and mouse in their
own classes, etc...

In the next version, rather than rendering to a display
Surface directly, I will be rendering the VGA console to
it's own Surface, which can then be blitted onto your own
display and/or Surface.  This will make the VGA Console
easier to add into your own projects.

I may make it possible to choose different sizes for the
console row and column size in the future.  Although this
will break VGA compatibility, it may be useful for specific
applications and games to have a smaller size console.

VGA Graphics modes may be considered, but Pygame by itself
can already do a great job at that.

There are 2 included and required binary files in this
package.  One being a TrueType font which is copied pixel
for pixel from a VGA compatible BIOS.  It is highly
recommended to use this font for the most authentic VGA
text mode experience.  The other binary file is located
with the standard VGA 16 color palette and a US Shiftmap.

A Shiftmap is used to determine which character the user
wanted if they also had the shift key held down while
pressing another key.  SDL captures the RAW keyboard
deivce driver, and in order to make sure the correct
character is given when shift is held is to use a shiftmap.

The VGA.bin is easily editable using a standard hexeditor,
and is made into an external file to ease distribution
in multiple languages where different keyboards will be
involved.  Having it load as a small binary file ensures
a smaller memory footprint, as other shiftmaps and palettes
won't be loaded.  A tool to create these files will be
released in the next release.
