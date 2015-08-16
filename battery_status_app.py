"""Simple battery status icon app."""
import re
import os
import gtk
import subprocess
import logging
import signal
import datetime

from optparse import OptionParser


ICONS_DIR = os.path.join(os.path.split(os.path.abspath(__file__))[0], "icons")


BATTERY_ICONS = {
    0: 'battery0.png',
    10: 'battery10.png',
    20: 'battery20.png',
    30: 'battery30.png',
    40: 'battery40.png',
    50: 'battery50.png',
    60: 'battery60.png',
    70: 'battery70.png',
    80: 'battery80.png',
    90: 'battery90.png',
    }


GLOBAL_ESTIMATE_DATA = None


def ResizePixbuf(pixbuf, width, height):
  """Resize pixbuf to keep ratio and fit the bounds."""
  px_width = pixbuf.get_width()
  px_height = pixbuf.get_height()

  if px_width > width:
    # scale to fit width
    ratio = width / float(px_width)
    px_width = width * ratio
    px_height = height * ratio


  if px_height > height:
    ratio = height / float(px_height)
    px_width = width * ratio
    px_height = height * ratio

  px_width = int(px_width)
  px_height = int(px_height)
  return pixbuf.scale_simple(px_width, px_height, gtk.gdk.INTERP_BILINEAR)


class BatteryStatusIcon(object):

  def __init__(self):
    self.icon = gtk.StatusIcon()
    self.pixbufs = {}
    for x, filename in BATTERY_ICONS.iteritems():
      self.pixbufs[x] = gtk.gdk.pixbuf_new_from_file(
          os.path.join(ICONS_DIR, filename))

  def _Set(self, pixbuf, tooltip):
    self.icon.set_from_pixbuf(pixbuf)
    if tooltip:
      self.icon.set_tooltip_text(tooltip)

  def _GetPixbuf(self, percentage):
    levels = sorted(self.pixbufs.keys())
    level = [x for x in levels if x <= percentage][-1]
    logging.info('Battery level found: %d for prcentage %s', level, percentage)
    pixbuf = self.pixbufs[level]
    return pixbuf

  def SetBatteryStatus(self, percentage, charging, remaining):
    if percentage is None:
      self._Set(self.pixbufs[0], "Error occred while running acpi.")
      return

    pixbuf = self._GetPixbuf(percentage)
    tooltip = "%d%%" % percentage
    if remaining:
      if charging:
        info = '%s until charged' % remaining
      else:
        info = '%s remaining' % remaining
      tooltip = "%s (%s)" % (tooltip, info)
    self._Set(pixbuf, tooltip=tooltip)


def GetBatteryInfo():
  """Returns current battery information."""
  logging.info('Battery check at %s', datetime.datetime.now())
  output = subprocess.check_output(('acpi', '-b'))
  print '%r' % output

  m = re.match(r'Battery \d+: (?P<status>\w+), (?P<percentage>\d+)%, '
      '(((?P<remaining>.{8}) (until charged|remaining))|'
      '(dis)?charging at zero rate - will never fully (dis)?charge.)\n', output)
  if not m:
    return None, None, None
  percentage = int(m.group('percentage'))
  chargning = m.group('status').upper() == 'CHARGING'
  remaining = m.group('remaining')
  print percentage, chargning, remaining
  return percentage, chargning, remaining


def GtkCallback(bts):
  """Helper method to be run by gtk as a callback."""
  percentage, charging, remaining = GetBatteryInfo()
  bts.SetBatteryStatus(percentage, charging, remaining)

  # Return True to run again.
  return True


def main():
  parser = OptionParser()
  parser.add_option('-t', '--timeout', dest='timeout', default=60,
                    help='Refresh rate in seconds', type=int)
  parser.add_option('-l', '--logfile', dest='logfile', default=None)
  options, _ = parser.parse_args()

  logging.basicConfig(filename=options.logfile)

  bts = BatteryStatusIcon()
  signal.signal(signal.SIGINT, gtk.main_quit)

  # Run now and every %options.timeout% seconds.
  GtkCallback(bts)
  def gtkCallback():
    return GtkCallback(bts)
  gtk.timeout_add(options.timeout * 1000, gtkCallback)
  gtk.main()


if __name__ == '__main__':
  main()
