import os
import math
import pygame
import fontfx
from constants import *

# Make an outlined box. The size is given without the 4 pixel border.
# This usually gets alphaed before stuff gets put in it.
def make_box(color = [111, 255, 148], size = [130, 40]):
  s = pygame.Surface([size[0] + 8, size[1] + 8], SRCALPHA, 32)
  s.fill(color + [100])
  r = s.get_rect()
  for c in [[255, 255, 255, 170], [212, 217, 255, 170],
            [255, 252, 255, 170], [88, 104, 255, 170]]:
    pygame.draw.rect(s, c, r, 1)
    r.width -= 2
    r.height -= 2
    r.top += 1
    r.left += 1
  return s

# Crossfading help text along the top of the screen.
class HelpText(pygame.sprite.Sprite):
  def __init__(self, strs, color, bgcolor, font, center):
    pygame.sprite.Sprite.__init__(self)
    self._idx = -1
    self._strings = [(s, font.render(s, True, color, bgcolor).convert())
                     for s in strs]
    self._center = center
    self._start = pygame.time.get_ticks()
    self._fade = -1
    self._bgcolor = bgcolor
    self._end = -1
    self.update(self._start)

  def update(self, time):
    time -= self._start
    # Time to switch to the next bit of text.
    if time > self._end:
      self._idx = (self._idx + 1) % len(self._strings)
      self.image = self._strings[self._idx][1]
      self.image.set_alpha(255)
      self._fade = time + 100 * len(self._strings[self._idx][0])
      self._end = self._fade + 750

    # There's a .75 second delay during which text crossfades.
    elif time > self._fade:
      p = (time - self._fade) / 750.0
      s1 = self._strings[self._idx][1]
      s1.set_colorkey(s1.get_at([0, 0]))
      s1.set_alpha(int(255 * (1 - p)))
      
      i = (self._idx + 1) % len(self._strings)
      s2 = self._strings[i][1]
      s2.set_colorkey(s2.get_at([0, 0]))
      s2.set_alpha(int(255 * p))

      h = max(s1.get_height(), s2.get_height())
      w = max(s1.get_width(), s2.get_width())
      self.image = pygame.Surface([w, h], 0, 32)
      self.image.fill(self._bgcolor)
      self.image.set_colorkey(self.image.get_at([0, 0]))
      r = s1.get_rect()
      r.center = self.image.get_rect().center
      self.image.blit(s1, r)
      r = s2.get_rect()
      r.center = self.image.get_rect().center
      self.image.blit(s2, r)

    self.image.set_colorkey(self.image.get_at([0, 0]))
    self.rect = self.image.get_rect()
    self.rect.center = self._center

# Flashy indicator for showing current menu position.
class ActiveIndicator(pygame.sprite.Sprite):
  def __init__(self, topleft):
    pygame.sprite.Sprite.__init__(self)
    self.image = pygame.image.load(os.path.join(image_path, "indicator.png"))
    self.image.convert()
    self.image.set_colorkey(self.image.get_at([0, 0]))
    self.rect = self.image.get_rect()
    self.rect.topleft = topleft

  def update(self, time):
    self.image.set_alpha(int(255 * (0.3 + (math.sin(time / 720.0)**2 / 3.0))))

# Box to indicate the current difficulty level.
class DifficultyBox(pygame.sprite.Sprite):
  def __init__(self, pid, numplayers):
    pygame.sprite.Sprite.__init__(self)
    self._topleft = [19 + (233 * pid), 414]

  def set(self, diff, color, feet, grade):
    f = pygame.font.Font(None, 24)
    self.image = make_box(color)

    t1 = fontfx.shadow(diff, f, 1, [255, 255, 255], [0, 0, 0])
    r1 = t1.get_rect()
    r1.center = [self.image.get_width()/2, 14]

    t2 = fontfx.shadow("x%d - %s" % (feet, grade), f, 1,
                       [255, 255, 255],[0, 0, 0])
    r2 = t2.get_rect()
    r2.center = [self.image.get_width()/2, 34]

    self.image.blit(t1, r1)
    self.image.blit(t2, r2)

    self.rect = self.image.get_rect()
    self.rect.topleft = self._topleft
    self.image.set_alpha(140)

SS_HELP = [
  "Up / Down changes song selection",
  "Left / Right changes difficulty setting",
  "Confirm / O / Up Right opens a folder or starts a song",
  "Cancel / X / Escape closes a folder or backs up",
  "Select / Tab takes you to a random song",
  "Start / Enter switches between screens",
  "F11 toggles fullscreen - S changes the sort mode.",
  "Enjoy pydance 0.9.0!",
  ]

ITEMS = [
  "A Song",
  "Another Song",
  "B99U",
  "Max 3.1415926535",
  "N.M.R sucks a lot",
  "I need more items",
  "BlarrrrrrrrrR!",
  "Cthulhu Fhtagn",
  "Almost done",
  "19 Smarch 2038",
  "This is not nearly",
  "enough songs yet.",
  "Lousy huge new song",
  "selection screen.",
  "I'll show you!",
  "This is the last one",
  "OR IS IT?!"
  ]
  

class ListBox(pygame.sprite.Sprite):
  def __init__(self, items, font, color, spacing, count, width, topleft):
    pygame.sprite.Sprite.__init__(self)
    self._items = items
    self._idx = self._oldidx = 0
    self._font = font
    self._h = spacing
    self._count = count
    self._w = width
    self._color = color
    self._topleft = topleft
    self._render()

  def set_index(self, idx):
    self._oldidx = self._idx
    self._idx = idx

  def update(self, time):
    if self._idx != self._oldidx:
      self._oldidx = self._idx
      self._render()

  def _render(self):
    self.image = pygame.Surface([self._w, self._h * self._count], SRCALPHA, 32)
    self.image.fill([0, 0, 0, 0])
    for i, y in zip(range(self._count),
                    range(self._h / 2, self._h * self._count, self._h)):
      idx = (self._idx + i) % len(self._items)
      t = fontfx.shadow(self._items[idx], self._font, 1, self._color,
                        [c / 8 for c in self._color])
      r = t.get_rect()
      r.centery = y
      r.left = 5
      self.image.blit(t, r)
    self.rect = self.image.get_rect()
    self.rect.topleft = self._topleft

class MainWindow(object):
  def __init__(self, screen, numplayers):
    self._screen = screen
    self._bg = pygame.image.load(os.path.join(image_path, "newss-bg.png"))
    self._sprites = pygame.sprite.RenderUpdates()
    diff1 = DifficultyBox(0, 2)
    diff1.set("MANIAC", [0, 255, 0], 7, "AA")
    diff2 = DifficultyBox(1, 2)
    diff2.set("TRICK", [255, 0, 0], 4, "C")
    self._list = ListBox(ITEMS, pygame.font.Font(None, 28), [255, 255, 255],
                         26, 16, 220, [410, 56])
    self._sprites.add([diff1, diff2, self._list])
    ActiveIndicator([405, 233]).add(self._sprites)
    self._sprites.add(HelpText(SS_HELP, [255, 255, 255], [0, 0, 0],
                               pygame.font.Font(None, 18), [206, 20]))
    self._screen.blit(self._bg, [0, 0])
    pygame.display.update()
    while True:
      self.update()
      pygame.time.delay(1)

  def update(self):
    self._sprites.update(pygame.time.get_ticks())
    pygame.display.update(self._sprites.draw(self._screen))
    self._sprites.clear(self._screen, self._bg)

def main():
  pygame.init()
  screen = pygame.display.set_mode([640, 480], 0, 16)
  MainWindow(screen, 1)

main()
