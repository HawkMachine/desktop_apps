"""Simple notification creator icon app."""
import os
import gtk
import pynotify
import signal
import datetime


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BELL_ICON_PATH = os.path.join(BASE_DIR, "bell.png")
HOURGLASS_ICON = os.path.join(BASE_DIR, "hourglass.png")


def formatTime(seconds):
  if seconds < 60:
    return '%ds' % seconds
  minutes = seconds / 60
  seconds = seconds - (minutes * 60)
  if seconds:
    return '%dm %ds' % (minutes, seconds)
  else:
    return '%dm' % minutes


def GetIconMenuItem(icon_path, image_size=20, label='', onclick=None, onclick_args=()):
  item = gtk.ImageMenuItem()
  pixbuf = gtk.gdk.pixbuf_new_from_file(icon_path)
  pixbuf = pixbuf.scale_simple(image_size, image_size, gtk.gdk.INTERP_BILINEAR)
  image = gtk.Image()
  image.set_from_pixbuf(pixbuf)
  item.set_image(image)
  item.set_property('always-show-image', True)

  item.set_label(label)
  if onclick:
    item.connect('activate', onclick, *onclick_args)
  return item


class DatetimeAndMessageDialog(object):

  def __init__(self, nc):
    self.nc = nc
    now = datetime.datetime.now()

    self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    self.window.connect("delete_event", self._DeleteEvent)
    self.window.set_size_request(640, 250)

    main_vbox = gtk.VBox()
    self.window.add(main_vbox)

    spin_frame = gtk.Frame("Create notification at ...")
    spin_frame.set_border_width(10)
    spin_buttons_box = gtk.HBox(False, 0)
    spin_frame.add(spin_buttons_box)
    main_vbox.pack_start(spin_frame)

    adj = gtk.Adjustment(now.hour, 0.0, 1000.0, 1.0, 5.0, 0.0)
    self.hours_spinner = gtk.SpinButton(adj, 0, 0)

    adj = gtk.Adjustment(now.minute, 0.0, 1000.0, 1.0, 5.0, 0.0)
    self.minutes_spinner = gtk.SpinButton(adj, 0, 0)

    adj = gtk.Adjustment(now.second, 0.0, 1000.0, 1.0, 5.0, 0.0)
    self.seconds_spinner = gtk.SpinButton(adj, 0, 0)

    spin_buttons_box.pack_start(self.hours_spinner)
    spin_buttons_box.pack_start(self.minutes_spinner)
    spin_buttons_box.pack_start(self.seconds_spinner)

    entry_frame = gtk.Frame("With message...")
    entry_frame.set_border_width(10)
    self.entry = gtk.Entry()
    entry_frame.add(self.entry)
    main_vbox.pack_start(entry_frame)

    ok_button = gtk.Button(stock=gtk.STOCK_OK)
    ok_button.connect('clicked', self._OkClicked)
    cancel_button = gtk.Button(stock=gtk.STOCK_CANCEL)
    cancel_button.connect('clicked', self._CancelClicked)
    buttons_box = gtk.HBox()
    buttons_box.pack_start(cancel_button)
    buttons_box.pack_start(ok_button)
    main_vbox.pack_start(buttons_box)

  def _OkClicked(self, *args, **kwargs):
    self.nc.CreateNotificationAt(self.getValue(), self.getMessage())
    self.window.hide_all()

  def _CancelClicked(self, *args, **kwargs):
    self.window.hide_all()

  def _DeleteEvent(self, *args, **kwargs):
    self.window.hide_all()
    return False

  def show(self):
    self.window.show_all()

  def getValue(self):
    now = datetime.datetime.now()
    d = datetime.datetime(
      year = now.year,
      month = now.month,
      day = now.day,
      hour = int(self.hours_spinner.get_value()),
      minute = int(self.minutes_spinner.get_value()),
      second = int(self.seconds_spinner.get_value()),
    )
    return d

  def getMessage(self):
    return self.entry.get_text()


class PeriodAndMessageDialog(object):

  def __init__(self, nc):
    self.nc = nc
    self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    self.window.connect("delete_event", self._DeleteEvent)
    self.window.set_size_request(640, 250)

    main_vbox = gtk.VBox()
    self.window.add(main_vbox)

    spin_frame = gtk.Frame("Create notification in ...")
    spin_frame.set_border_width(10)
    spin_buttons_box = gtk.VBox(False, 0)
    spin_frame.add(spin_buttons_box)
    main_vbox.pack_start(spin_frame)

    lbl = gtk.Label("Hours")
    lbl.set_size_request(50, 10)
    adj = gtk.Adjustment(0.0, 0.0, 1000.0, 1.0, 5.0, 0.0)
    self.hours_spinner = gtk.SpinButton(adj, 0, 0)
    self.hours_hbox = gtk.HBox()
    self.hours_hbox.pack_start(lbl)
    self.hours_hbox.pack_start(self.hours_spinner)

    lbl = gtk.Label("Minutes")
    lbl.set_size_request(50, 10)
    adj = gtk.Adjustment(0.0, 0.0, 1000.0, 1.0, 5.0, 0.0)
    self.minutes_spinner = gtk.SpinButton(adj, 0, 0)
    self.minutes_hbox = gtk.HBox()
    self.minutes_hbox.pack_start(lbl)
    self.minutes_hbox.pack_start(self.minutes_spinner)

    lbl = gtk.Label("Seconds")
    lbl.set_size_request(50, 10)
    adj = gtk.Adjustment(0.0, 0.0, 1000.0, 1.0, 5.0, 0.0)
    self.seconds_spinner = gtk.SpinButton(adj, 0, 0)
    self.seconds_hbox = gtk.HBox()
    self.seconds_hbox.pack_start(lbl)
    self.seconds_hbox.pack_start(self.seconds_spinner)

    self.hours_hbox.set_border_width(5)
    self.minutes_hbox.set_border_width(5)
    self.seconds_hbox.set_border_width(5)

    spin_buttons_box.pack_start(self.hours_hbox)
    spin_buttons_box.pack_start(self.minutes_hbox)
    spin_buttons_box.pack_start(self.seconds_hbox)

    entry_frame = gtk.Frame("With message...")
    entry_frame.set_border_width(10)
    self.entry = gtk.Entry()
    entry_frame.add(self.entry)
    main_vbox.pack_start(entry_frame)

    ok_button = gtk.Button(stock=gtk.STOCK_OK)
    ok_button.connect('clicked', self._OkClicked)
    cancel_button = gtk.Button(stock=gtk.STOCK_CANCEL)
    cancel_button.connect('clicked', self._CancelClicked)
    buttons_box = gtk.HBox()
    buttons_box.pack_start(cancel_button)
    buttons_box.pack_start(ok_button)
    main_vbox.pack_start(buttons_box)

  def _OkClicked(self, *args, **kwargs):
    at = datetime.datetime.now() + datetime.timedelta(seconds=self.getValue())
    self.nc.CreateNotificationAt(at, self.getMessage())
    self.window.hide_all()

  def _CancelClicked(self, *args, **kwargs):
    self.window.hide_all()

  def _DeleteEvent(self, *args, **kwargs):
    self.window.hide_all()
    return False

  def show(self):
    self.window.show_all()

  def getValue(self):
    v = self.hours_spinner.get_value() * 3600.0
    v += self.minutes_spinner.get_value() * 60.0
    v += self.seconds_spinner.get_value()
    return v

  def getMessage(self):
    return self.entry.get_text()


class NotificationCreator(object):

  def __init__(self):
    self.icon = gtk.StatusIcon()
    self.icon.set_from_file(BELL_ICON_PATH)
    self.icon.connect('popup-menu', self._PopupMenu)
    self.unacked_notifications = {}

    self.datetime_dialog = DatetimeAndMessageDialog(self)
    self.period_dialog = PeriodAndMessageDialog(self)

    self.next_id = 1
    self.pending_notifications = {}

  def _PopupMenu(self, icon, button, time):
    self.menu = gtk.Menu()

    for at, msg in sorted(self.pending_notifications.values()):
      delta = at - datetime.datetime.now()
      label = '%s to %s' % (formatTime(delta.total_seconds()), msg)
      self.menu.append(GetIconMenuItem(HOURGLASS_ICON, label=label))

    if self.pending_notifications:
      self.menu.append(gtk.SeparatorMenuItem())

    self.menu.append(
        GetIconMenuItem(
          BELL_ICON_PATH,
          label='Sleep ...',
          onclick=self._OnSleepClick))

    self.menu.append(
        GetIconMenuItem(
          BELL_ICON_PATH,
          label='Wait until ...',
          onclick=self._OnWaitUntilClick))

    # Exit menu item.
    exit_item = gtk.MenuItem('Exit')
    exit_item.connect('activate', gtk.main_quit)

    self.menu.append(gtk.SeparatorMenuItem())
    self.menu.append(exit_item)

    self.menu.show_all()
    self.menu.popup(None, None, None, button, time)

  def _GetNextId(self):
    next_id = self.next_id
    self.next_id += 1
    return next_id

  def CreateNotificationAt(self, at, msg):
    nid = self._GetNextId()
    delta = at - datetime.datetime.now()
    if delta.total_seconds() <= 0:
      self._ShowNotification('NOTIFICATION IN THE PAST!!!!', msg)
    else:
      self.pending_notifications[nid] = (at, msg)
      gtk.timeout_add(int(delta.total_seconds()) * 1000, self._ShowPendingNotification, nid)

  def _ShowNotification(self, title, msg):
    n = pynotify.Notification(title, msg, '')
    n.set_timeout(pynotify.EXPIRES_NEVER)
    n.show()

  def _ShowPendingNotification(self, nid):
    if nid not in self.pending_notifications:
      raise ValueError('Unrecognized notification id %s' % nid)
    at, msg = self.pending_notifications[nid]
    del self.pending_notifications[nid]

    self._ShowNotification('DANGER, DANGER!!! EXTERMINATE !!!', msg)

  def _OnWaitUntilClick(self, unused_arg):
    self.datetime_dialog.show()

  def _OnSleepClick(self, unused_arg):
    self.period_dialog.show()


def main():
  NotificationCreator()
  signal.signal(signal.SIGINT, gtk.main_quit)
  pynotify.init('NotificationCreator')
  gtk.main()


if __name__ == '__main__':
  main()
