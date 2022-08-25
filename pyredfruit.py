#!/usr/bin/env python

import datetime
import sys
import gi

gi.require_version("Gtk", "3.0")
# pylint: disable=wrong-import-position
from gi.repository import GLib, Gtk


class Time:
    def __init__(self):
        # We need to use datetime.datetime, not datetime.time.
        # See:
        #     https://bugs.python.org/issue1118748
        #     https://bugs.python.org/issue1487389
        # for more information as to why. So we can't do this:
        #     self.remaining = datetime.time(0,25,0)
        #
        # NB This may not be a Bad Thing because we may decide to
        # implement time tracking in the future, which would require
        # dates.
        today = datetime.date.today()
        time = datetime.time(0, 25, 0)
        # Five seconds for testing ;)
        # time = datetime.time(0, 0, 5)
        self.remaining = datetime.datetime.combine(today, time)

    def decrement_second(self):
        a_second = datetime.timedelta(seconds=1)
        self.remaining = self.remaining - a_second

    def is_zero(self):
        return bool(self.remaining.time() == datetime.time(0,0,0))

    def __str__(self):
        return self.remaining.strftime("%M:%S")


class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title=sys.argv[0])

        self.time_left = Time()

        box = Gtk.Box(spacing=6)
        self.add(box)

        self.time_label = Gtk.Label()
        self.time_label.set_markup(
            f'<span size="500%" weight="bold">{self.time_left}</span>'
        )
        box.pack_start(self.time_label, True, True, 0)

        button = Gtk.Button.new_with_label("Start")
        button.connect("clicked", self.button_clicked)
        box.pack_start(button, True, True, 0)

    def button_clicked(self, button):
        button.set_label("Pause")
        self.start_timer()

    def time_up(self):
        dialog = Gtk.MessageDialog(
            buttons=Gtk.ButtonsType.OK,
            text="Time up, take a break"
        )
        dialog.run()
        dialog.destroy()

    def update_time(self):
        self.time_left.decrement_second()
        self.time_label.set_markup(
            f'<span size="500%" weight="bold">{self.time_left}</span>'
        )
        if self.time_left.is_zero():
            self.time_up()
            return False

        return True  # timeout_add_seconds will keep going

    def start_timer(self):
        GLib.timeout_add_seconds(1, self.update_time)


if __name__ == "__main__":
    win = MainWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()

    Gtk.main()
