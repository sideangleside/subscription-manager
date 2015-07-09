
# To get gtk.gdk.threads_init
import gtk

# objects
from gobject import GObject
from gobject import MainLoop

# methods
from gobject import add_emission_hook, idle_add, source_remove, timeout_add
from gobject import markup_escape_text

# enums
from gobject import SIGNAL_RUN_LAST
from gobject import TYPE_BOOLEAN, TYPE_PYOBJECT, PARAM_READWRITE

# These are not exact replacements, but for our purposes they
# are used in the same places in the same way. A purely GObject
# app with no gui may want to distinquish.
threads_init = gtk.gdk.threads_init


class SignalFlags(object):
    RUN_LAST = SIGNAL_RUN_LAST


constants = [TYPE_BOOLEAN, TYPE_PYOBJECT, PARAM_READWRITE]
methods = [add_emission_hook, idle_add, markup_escape_text,
           source_remove, threads_init, timeout_add]
enums = [SignalFlags]
objects = [GObject, MainLoop]
__all__ = objects + methods + constants + enums