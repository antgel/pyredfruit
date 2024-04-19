#!/usr/bin/env python

from playsound import playsound

import datetime
import sys
import gi

gi.require_version("Gtk", "3.0")
# pylint: disable=wrong-import-position
from gi.repository import GLib, Gtk


class Timer:
    def __init__(self, _type, minutes, seconds):
        self.type = _type
        self.set_remaining(minutes, seconds)

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

    def set_remaining(self, minutes, seconds):
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

    def __str__(self):
        return self.remaining.strftime("%M:%S")


class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title=sys.argv[0])

        self.state = "stopped"
        self.timer = Timer("pomodoro", 25, 0)

        box = Gtk.Box(spacing=6)
        self.add(box)

        self.time_label = Gtk.Label()
        self.time_label.set_markup(
            f'<span size="500%" weight="bold">{self.timer}</span>'
        )
        box.pack_start(self.time_label, True, True, 0)

        self.status = Gtk.Label()
        self.update_ui_state()
        box.pack_start(self.status, True, True, 0)

        state_button = Gtk.Button.new_with_label("Start")
        state_button.connect("clicked", self.clicked_state)
        box.pack_start(state_button, True, True, 0)

        reset_button = Gtk.Button.new_with_label("Reset")
        reset_button.connect("clicked", self.clicked_reset)
        box.pack_start(reset_button, True, True, 0)

    # There is probably (hopefully) a better way to do this rather than
    # calling this function every second when the timer ticks. Ideally
    # UI components would listen for state changes. But as I don't have
    # time to read all the docs, especially
    # https://python-gtk-3-tutorial.readthedocs.io/en/latest/application.html
    # which mentions Gio.SimpleAction amongst other things, and there
    # are only two labels that changes state at the moment, do it like this.
    # Or is it
    # https://python-gtk-3-tutorial.readthedocs.io/en/latest/objects.html
    def update_ui_state(self):
        self.status.set_label(f"{self.state} {self.timer.type}")
        self.time_label.set_markup(
            f'<span size="500%" weight="bold">{self.timer}</span>'
        )

    def clicked_reset(self, reset_button):
        self.reset_pomodoro()

    def clicked_state(self, state_button):
        match self.state:
            case "stopped":
                state_button.set_label("Pause")
                self.start_pomodoro()
            case "running":
                state_button.set_label("Restart")
                self.state = "paused"
            case "paused":
                state_button.set_label("Pause")
                self.state = "running"

    def time_up(self):
        playsound("bell.wav")
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
        self.reset_pomodoro()
        self.start_tick()
        self.state = "running"

    def reset_pomodoro(self):
        self.timer = Timer("pomodoro", 25, 0)

    def start_tick(self):
        GLib.timeout_add_seconds(1, self.update_state)

    def update_state(self):
        if self.state == "running":
            self.timer.decrement_second()

        if self.timer.has_expired():
            self.time_up()
            return False

        self.update_ui_state()
        return True  # timeout_add_seconds will keep going


if __name__ == "__main__":
    win = MainWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()

    Gtk.main()
