from pygame.locals import *
import pad, pygame

(PASS, QUIT, UP, DOWN, LEFT, RIGHT, START, SELECT, MARK, UNMARK, PGUP,
 PGDN, FULLSCREEN, SORT, CLEAR) = range(15)

SCREENSHOT = SORT

non_player = [QUIT, PASS]

pad_defaults = {
  pad.QUIT: QUIT,
  pad.UP: UP,
  pad.DOWN: DOWN,
  pad.LEFT: LEFT,
  pad.RIGHT: RIGHT,
  pad.START: START,
  pad.UPRIGHT: PGUP,
  pad.DOWNRIGHT: PGDN,
  pad.UPLEFT: MARK,
  pad.DOWNLEFT: UNMARK,
  pad.SELECT: SELECT,
  }

key_defaults = {
  100 * K_f: FULLSCREEN,
  100 * K_BACKSPACE: SORT,
  100 * K_TAB: SELECT,
  }

# This class wraps pad and maps pad events to UI events.
class UI(object):
  def __init__(self, handler):
    self.handler = handler
    self.events = {}
    self.states = {}

    self.merge_events(-2, key_defaults)
    self.merge_events(0, pad_defaults)
    self.merge_events(1, pad_defaults)

    # So we don't crash adjusting nonsensical states
    for i in non_player: self.add_event(i, -1, i)

  def add_event(self, key, pid, event):
    self.events[key] = event
    self.states[(pid, event)] = False

  def merge_events(self, pid, events):
    for key, event in events.items():
      self.add_event(key, pid, event)

  def poll(self):
    pid, ev = self.handler.poll(True)

    nev = self.events.get(abs(ev), PASS)
    
    if ev < 0:
      self.states[(pid, nev)] = False
      nev = -nev
    else:
      self.states[(pid, nev)] = True

    return (pid, nev)

  def wait(self, delay = 20):
    ev = (-1, PASS)
    while ev[1] == PASS:
      ev = self.poll()
      pygame.time.wait(delay)
    return ev

  def empty(self):
    ev = (0, QUIT)
    while ev[1] != PASS: ev = self.poll()

  def set_repeat(*args): pass

ui = UI(pad.pad)