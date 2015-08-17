#!/usr/bin/python

import os
import re
import gtk
import json
import argparse
import pynotify
import time


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICONS_DIR = os.path.join(BASE_DIR, "icons")
CONFIG_FILE = "config.json"


def formatTime(seconds):
  if seconds < 60:
    return '%ds' % seconds
  minutes = seconds / 60
  seconds = seconds - (minutes * 60)
  if seconds:
    return '%dm %ds' % (minutes, seconds)
  else:
    return '%dm' % minutes


def parseTime(timeStr):
  """Parses time string and returns equivalend number od seconds."""
  regex = r'((\d+)[ms ]?\s*)'
  if not re.match(regex, timeStr + ' '):
    return ValueError("%s does not match %r" % (timeStr, regex))
  time = 0
  for match in re.findall('(\d+)([ms]?)', timeStr):
    if match[1] == 'm':
      time += 60 * int(match[0])
    else:
      time += int(match[0])
  return time


class TeaSetting(object):
  ICON = 'tea.png'
  def __init__(self, name='Tea', time=3*60):
    self.name = name
    self.time = time
  def getNotificationTitle(self):
    return 'Your Tea is ready!'
  def getNotificationDescription(self):
    return '%s tea is ready to drink! \nEnjoy!' % self.name
  def getMenuLabel(self):
    return '%s (%s)' % (self.name, formatTime(self.time))


class WaterSetting(object):
  ICON = 'water.png'
  def __init__(self, name='Water', time=5*60):
    self.name = name
    self.time = time
  def getNotificationTitle(self):
    return 'Your water for %s is ready!' % self.name
  def getNotificationDescription(self):
    return ''
  def getMenuLabel(self):
    return 'Water: %s (%s)' % (self.name, formatTime(self.time))


class PendingSetting(object):
  ICON = 'hourglass.png'
  def __init__(self, creation_time, setting):
    self.creation_time = creation_time
    self.setting = setting
  def getMenuLabel(self):
    menu_label = self.setting.getMenuLabel()
    time_left = (self.creation_time + self.setting.time) - time.time()
    return '%s to %s' % (formatTime(time_left), menu_label)


def GetIconMenuItem(image_name, image_size=20, label='', onclick=None, onclick_args=()):
  item = gtk.ImageMenuItem()
  image_path = os.path.join(ICONS_DIR, image_name)
  pixbuf = gtk.gdk.pixbuf_new_from_file(image_path)
  pixbuf = pixbuf.scale_simple(image_size, image_size, gtk.gdk.INTERP_BILINEAR)
  image = gtk.Image()
  image.set_from_pixbuf(pixbuf)
  item.set_image(image)
  item.set_property('always-show-image', True)

  item.set_label(label)
  if onclick:
    item.connect('activate', onclick, *onclick_args)
  return item


def GetIconMenuItemFromSetting(setting, onclick=None, onclick_args=()):
  return GetIconMenuItem(
      setting.ICON,
      label = setting.getMenuLabel(),
      onclick = onclick,
      onclick_args = onclick_args)


class TeaStatusIcon(object):
  def __init__(self, tea_config, water_config):
    self.icon = gtk.StatusIcon()
    self.icon_path = os.path.join(ICONS_DIR, 'tea.png')
    self.icon.set_from_file(self.icon_path)
    self.icon.connect('popup-menu', self.popupMenu)
    self.tea_config = tea_config
    self.water_config = water_config
    self.pending_notifications = {}
    self.notification_id = 0

  def getNotificationId(self):
    self.notification_id += 1
    return self.notification_id

  def removePendingNotification(self, id):
    try:
      del self.pending_notifications[id]
    except:
      pass

  def addPendingNotification(self, setting):
    id = self.getNotificationId()
    self.pending_notifications[id] = PendingSetting(time.time(), setting)
    return id

  def popupMenu(self, icon, button, time):
    self.menu = gtk.Menu()

    if self.water_config:
      for wc in self.water_config:
        item = GetIconMenuItemFromSetting(
            wc,
            onclick = self.addNotification,
            onclick_args=(wc,))
        self.menu.append(item)
      self.menu.append(gtk.SeparatorMenuItem())


    for tc in self.tea_config:
      item = GetIconMenuItemFromSetting(
          tc,
          onclick=self.addNotification,
          onclick_args=(tc,))
      self.menu.append(item)

    if self.pending_notifications:
      self.menu.append(gtk.SeparatorMenuItem())
      for pc in self.pending_notifications.values():
        item = GetIconMenuItemFromSetting(pc)
        self.menu.append(item)

    self.menu.append(gtk.SeparatorMenuItem())
    exit_item = gtk.MenuItem('Exit')
    exit_item.connect('activate', gtk.main_quit)
    self.menu.append(exit_item)


    self.menu.show_all()
    self.menu.popup(None, None, None, button, time)

  def addNotification(self, widget, setting):
    id = self.addPendingNotification(setting)
    gtk.timeout_add(setting.time * 1000, self.showNotification, setting, id)

  def showNotification(self, setting, id):
    n = pynotify.Notification(setting.getNotificationTitle(),
                              setting.getNotificationDescription(), '')
    n.set_timeout(pynotify.EXPIRES_NEVER)
    n.show()
    self.removePendingNotification(id)


def LoadConfig(path):
  with open(path, 'r') as fh:
    content = fh.read()
  conf = json.loads(content)
  if not conf:
    conf = {
        "tea": {
          "name": "Tea",
          "time": "5m",
          },
        "water": {
          "name": "Water",
          "time": "5m",
          },
        }

  teas = []
  for tea_conf in conf.get("tea", []):
    name = tea_conf.get("name", "")
    time = tea_conf.get("time", "")
    time = parseTime(time)
    if not name or not time:
      raise ValueError("Broken tea config: missing or empty name or time field")
    teas.append(TeaSetting(name=name, time=time))

  waters = []
  for water_conf in conf.get("water", []):
    name = water_conf.get("name", "")
    time = water_conf.get("time", "")
    if not name or not time:
      raise ValueError("Broken water config: missing or empty name or time field")
    time = parseTime(time)
    waters.append(WaterSetting(name=name, time=time))

  return teas, waters


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("--config", "-c", dest="config",
      default=os.path.join(BASE_DIR, CONFIG_FILE))
  args = parser.parse_args()

  teas, waters = LoadConfig(args.config)

  pynotify.init('TeaReminder')
  ti = TeaStatusIcon(teas, waters)
  gtk.main()
