#!/usr/bin/env python

import datetime
import sys
import gi

gi.require_version("Gtk", "3.0")
# pylint: disable=wrong-import-position
from gi.repository import GLib, Gtk


class Timer:
    def __init__(self, _type, minutes, seconds):
        self.type = _type
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
        time = datetime.time(0, minutes, seconds)
        self.remaining = datetime.datetime.combine(today, time)

    def decrement_second(self):
        a_second = datetime.timedelta(seconds=1)
        self.remaining = self.remaining - a_second

    def done_text(self):
        match self.type:
            case "break":
                return " Break over, time to focus"
            case "pomodoro":
                return "Timer up, take a break"

    def has_expired(self):
        return bool(self.remaining.time() == datetime.time(0, 0, 0))

    def __str__(self):
        return self.remaining.strftime("%M:%S")


class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title=sys.argv[0])

        self.timer = Timer("pomodoro", 25, 0)

        box = Gtk.Box(spacing=6)
        self.add(box)

        self.time_label = Gtk.Label()
        self.time_label.set_markup(
            f'<span size="500%" weight="bold">{self.timer}</span>'
        )
        box.pack_start(self.time_label, True, True, 0)

        button = Gtk.Button.new_with_label("Start")
        button.connect("clicked", self.clicked_start)
        box.pack_start(button, True, True, 0)

    def clicked_start(self, button):
        button.set_label("Pause")
        self.start_pomodoro()

    def time_up(self):
        dialog = Gtk.MessageDialog(
            buttons=Gtk.ButtonsType.OK, text=self.timer.done_text()
        )
        dialog.run()
        match self.timer.type:
            case "break":
                self.start_pomodoro()
            case "pomodoro":
                self.start_break()
        dialog.destroy()

    def start_break(self):
        self.timer = Timer("break", 5, 0)
        self.start_tick()

    def start_pomodoro(self):
        self.timer = Timer("pomodoro", 25, 0)
        self.start_tick()

    def start_tick(self):
        GLib.timeout_add_seconds(1, self.update_time)

    def update_time(self):
        self.timer.decrement_second()
        self.time_label.set_markup(
            f'<span size="500%" weight="bold">{self.timer}</span>'
        )
        if self.timer.has_expired():
            self.time_up()
            return False

        return True  # timeout_add_seconds will keep going


if __name__ == "__main__":
    win = MainWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()

    Gtk.main()
