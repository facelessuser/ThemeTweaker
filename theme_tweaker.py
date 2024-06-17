"""
Theme Tweaker.

Licensed under MIT
Copyright (c) 2013 - 2016 Isaac Muse <isaacmuse@gmail.com>
"""
import sublime
import sublime_plugin
import codecs
from os import makedirs
from os.path import join, basename, exists, dirname, normpath, splitext
from plistlib import writePlistToBytes
from .lib.file_strip.json import sanitize_json
from .lib.color_scheme_tweaker import ColorSchemeTweaker, get_tmtheme
from .lib.color_scheme_matcher import ColorSchemeMatcher
import json
import threading
import time


NEW_SCHEMES = int(sublime.version()) >= 3150
AUTO = int(sublime.version()) >= 4095

PLUGIN_SETTINGS = "theme_tweaker.sublime-settings"
TWEAK_SETTINGS = "theme_tweaker.tweak-settings"
PREFERENCES = 'Preferences.sublime-settings'
TEMP_FOLDER = "ThemeTweaker"
TEMP_PATH = "Packages/User/%s" % TEMP_FOLDER
TWEAKED = TEMP_PATH + "/tweaked.tmTheme"
SCHEME = "color_scheme"
TWEAK_MODE = False
THEME_TWEAKER_READY = False


def log(msg, status=False):
    """Standard log message."""

    string = str(msg)
    print("ThemeTweaker: %s" % string)
    if status:
        sublime.status_message(string)


def debug_log(s):
    """Debug log message."""

    if sublime.load_settings(PLUGIN_SETTINGS).get("debug", False):
        log(s)


def packages_path(pth):
    """Get packages path."""

    return join(dirname(sublime.packages_path()), normpath(pth))


def get_setting(setting, override, default):
    """
    Get the provided setting.

    If override is provided, just return that.
    """

    value = override
    if value is None:
        value = sublime.load_settings(PLUGIN_SETTINGS).get(setting, default)
    return value


class Lock(object):
    """Lock object."""

    lock = threading.Lock()
    condition = threading.Condition(threading.Lock())

    @classmethod
    def wait_lock(cls, timeout=2, force=False):
        """Acquire lock by waiting for the current one to timeout."""

        acquired = False
        with cls.condition:
            start = time.time()
            current = start
            while current < (start + timeout):
                if cls.lock.acquire(False):
                    acquired = True
                    break
                else:
                    cls.condition.wait(timeout - current + start)
                    current = time.time()
        if force and not acquired:
            cls.release_lock()
            acquired = cls.lock.acquire(False)
        return acquired

    @classmethod
    def release_lock(cls):
        """Release the lock."""

        try:
            cls.lock.release()
            with cls.condition:
                cls.condition.notify()
        except threading.ThreadError:
            pass


class ToggleThemeTweakerModeCommand(sublime_plugin.ApplicationCommand):
    """Toggle the theme tweak mode on/off."""

    def run(self):
        """Run command."""

        global TWEAK_MODE
        TWEAK_MODE = not TWEAK_MODE
        sublime.status_message("TweakMode is %s" % ("enabled" if TWEAK_MODE else "disabled"))
        if not TWEAK_MODE:
            ThemeTweaker().clear_history()


class ThemeTweakerBrightnessCommand(sublime_plugin.ApplicationCommand):
    """Tweak brightness."""

    def run(self, direction="+", step=None, context=None, theme=None):
        """Run command."""

        magnitude = -1.0 if direction == "-" else 1.0
        value = float(get_setting("brightness_step", step, .01)) * magnitude
        if value >= -1.0 and value <= 1.0:
            if context is not None and context in ["fg", "bg"]:
                ThemeTweaker(theme).run("brightness(%f)@%s" % (value + 1.0, context))
            else:
                ThemeTweaker(theme).run("brightness(%f)" % (value + 1.0))


class ThemeTweakerContrastCommand(sublime_plugin.ApplicationCommand):
    """Tweak contrast."""

    def run(self, direction="+", step=None, context=None, theme=None):
        """Run command."""

        magnitude = -1.0 if direction == "-" else 1.0
        value = float(get_setting("contrast_step", step, .01)) * magnitude
        if value >= -1.0 and value <= 1.0:
            if context is not None and context in ["fg", "bg"]:
                ThemeTweaker(theme).run("contrast(%f)@%s" % (value + 1.0, context))
            else:
                ThemeTweaker(theme).run("contrast(%f)" % (value + 1.0))


class ThemeTweakerSaturationCommand(sublime_plugin.ApplicationCommand):
    """Tweak Saturation."""

    def run(self, direction="+", step=None, context=None, theme=None):
        """Run command."""

        magnitude = -1.0 if direction == "-" else 1.0
        value = float(get_setting("saturation_step", step, .1)) * magnitude
        if value >= -1.0 and value <= 1.0:
            if context is not None and context in ["fg", "bg"]:
                ThemeTweaker(theme).run("saturation(%f)@%s" % (value + 1.0, context))
            else:
                ThemeTweaker(theme).run("saturation(%f)" % (value + 1.0))


class ThemeTweakerHueCommand(sublime_plugin.ApplicationCommand):
    """Tweak hue."""

    def run(self, direction="+", step=None, context=None, theme=None):
        """Run command."""

        magnitude = -1 if direction == "-" else 1
        value = int(get_setting("hue_step", step, 10)) * magnitude
        if value >= -360 and value <= 360:
            if context is not None and context in ["fg", "bg"]:
                ThemeTweaker(theme).run("hue(%d)@%s" % (value, context))
            else:
                ThemeTweaker(theme).run("hue(%d)" % value)


class ThemeTweakerInvertCommand(sublime_plugin.ApplicationCommand):
    """Invert colors."""

    def run(self, context=None, theme=None):
        """Run command."""

        if context is not None and context in ["fg", "bg"]:
            ThemeTweaker(theme).run("invert@%s" % context)
        else:
            ThemeTweaker(theme).run("invert")


class ThemeTweakerSepiaCommand(sublime_plugin.ApplicationCommand):
    """Apply sepia filter."""

    def run(self, context=None, theme=None):
        """Run command."""

        if context is not None and context in ["fg", "bg"]:
            ThemeTweaker(theme).run("sepia@%s" % context)
        else:
            ThemeTweaker(theme).run("sepia")


class ThemeTweakerColorizeCommand(sublime_plugin.ApplicationCommand):
    """Colorize the theme with the given hue."""

    def run(self, hue=None, context=None, theme=None):
        """Run command."""

        value = int(get_setting("colorize_hue", hue, 0))
        if context is not None and context in ["fg", "bg"]:
            ThemeTweaker(theme).run("colorize(%d)@%s" % (value, context))
        else:
            ThemeTweaker(theme).run("colorize(%d)" % value)


class ThemeTweakerGlowCommand(sublime_plugin.ApplicationCommand):
    """Apply glow effect."""

    def run(self, intensity=None, theme=None):
        """Run command."""

        value = float(get_setting("glow_intensity", intensity, .2))
        if value >= 0 and value <= 1.0:
            ThemeTweaker(theme).run("glow(%f)" % value)


class ThemeTweakerGrayscaleCommand(sublime_plugin.ApplicationCommand):
    """Apply grayscale filter."""

    def run(self, context=None, theme=None):
        """Run command."""

        if context is not None and context in ["fg", "bg"]:
            ThemeTweaker(theme).run("grayscale@%s" % context)
        else:
            ThemeTweaker(theme).run("grayscale")


class ThemeTweakerCustomCommand(sublime_plugin.ApplicationCommand):
    """Custom tweak command which takes filter options."""

    def run(self, filters, theme=None):
        """Run command."""

        ThemeTweaker(theme).run(filters)


class ThemeTweakerClearCommand(sublime_plugin.ApplicationCommand):
    """Clear current tweaks."""

    def run(self):
        """Run command."""

        ThemeTweaker().clear()


class ThemeTweakerUndoCommand(sublime_plugin.ApplicationCommand):
    """Undo last tweak."""

    def run(self):
        """Run command."""

        ThemeTweaker().undo()


class ThemeTweakerRedoCommand(sublime_plugin.ApplicationCommand):
    """Redo last tweak."""

    def run(self):
        """Run command."""

        ThemeTweaker().redo()


class ThemeTweaker(object):
    """Main tweak logic."""

    def __init__(self, init_theme=None, set_safe=False):
        """Initialize."""

        self.set_safe = set_safe
        self.init_theme = init_theme
        self.set_tweaked_scheme = False

    def _load_tweak_settings(self):
        """Load the tweak settings."""

        self._ensure_temp()
        p_settings = {}
        tweaks = packages_path(join(normpath(TEMP_PATH), basename(TWEAK_SETTINGS)))
        if exists(tweaks):
            try:
                with open(tweaks, "r") as f:
                    # Allow C style comments and be forgiving of trailing commas
                    content = sanitize_json(f.read(), True)
                p_settings = json.loads(content)
            except Exception:
                pass
        return p_settings

    def _save_tweak_settings(self):
        """Save the tweak settings."""

        tweaks = packages_path(join(normpath(TEMP_PATH), basename(TWEAK_SETTINGS)))
        j = json.dumps(self.p_settings, sort_keys=True, indent=4, separators=(',', ': '))
        try:
            with open(tweaks, 'w') as f:
                f.write(j + "\n")
        except Exception:
            pass

    def _set_theme_safely(self, name):
        """
        Safe variant of setting theme.

        At one point, Sublime would be left with an empty Preference file
        if you modified it too soon.  So manually reading was the safest.
        The problem may or may not exist now.
        """

        pref_file = join(sublime.packages_path(), 'User', 'Preferences.sublime-settings')
        pref = {}
        if exists(pref_file):
            try:
                with open(pref_file, "r") as f:
                    # Allow C style comments and be forgiving of trailing commas
                    content = sanitize_json(f.read(), True)
                pref = json.loads(content)
            except Exception:
                pass
        if pref[SCHEME] != name:
            pref[SCHEME] = name
            j = json.dumps(pref, sort_keys=True, indent=4, separators=(',', ': '))
            try:
                with open(pref_file, 'w') as f:
                    f.write(j + "\n")
            except Exception:
                pass

    def _ensure_temp(self):
        """Ensure temp path exists."""

        temp = packages_path(TEMP_PATH)
        if not exists(temp):
            makedirs(temp)

    def _exists(self, pth):
        """Check if theme exists."""

        found = False
        if exists(packages_path(pth)):
            found = True
        else:
            base = basename(pth)
            try:
                results = sublime.find_resources(base)
                if sublime.platform() == "windows":
                    for r in results:
                        if r.lower() == pth.lower():
                            found = True
                            break
                else:
                    found = pth in results
                if not found and results and pth == base and basename(results[0]) == base:
                    found = True
            except Exception:
                pass
        return found

    def _theme_valid(self, scheme_file, noedit=False):
        """Check if theme is valid."""

        is_working = scheme_file.startswith(TEMP_PATH + '/')
        if (
            is_working and self.scheme_map is not None and
            self.scheme_map["working"] == scheme_file and
            self._exists(self.scheme_map["original"])
        ):
            if self._exists(self.scheme_map["working"]):
                self.scheme_file = packages_path(self.scheme_map["original"])
                self.scheme_clone = packages_path(self.scheme_map["working"])
            else:
                # Recover from missing temp
                log("Revert to original because temp is missing")
                if self.set_safe:
                    self._set_theme_safely(self.scheme_map["original"])
                else:
                    self.settings.set(SCHEME, self.scheme_map["original"])
                self.scheme_map["redo"] = ""
                self.scheme_map["undo"] = ""
                self.p_settings["scheme_map"] = self.scheme_map
                self._save_tweak_settings()
            return True
        elif not is_working and not noedit:
            self._ensure_temp()
            csm = ColorSchemeMatcher(scheme_file)
            content = get_tmtheme(csm.get_scheme_obj()) if not NEW_SCHEMES else csm.get_scheme_obj()
            self.scheme_file = packages_path(scheme_file)
            base, old_ext = splitext(basename(scheme_file))
            if NEW_SCHEMES:
                ext = '.hidden-color-scheme' if old_ext == '.hidden-color-scheme' else '.sublime-color-scheme'
            else:
                ext = '.tmTheme'
            self.scheme_clone = packages_path(join(normpath(TEMP_PATH), 'tweak-' + base + ext))
            try:
                if NEW_SCHEMES:
                    with codecs.open(self.scheme_clone, "w", encoding='utf-8') as f:
                        f.write(sublime.encode_value(content, pretty=True))
                else:
                    with open(self.scheme_clone, "wb") as f:
                        f.write(writePlistToBytes(content))
                self.scheme_map = {
                    "original": scheme_file,
                    "working": "%s/%s" % (TEMP_PATH, 'tweak-' + base + ext),
                    "undo": "",
                    "redo": ""
                }
                self.set_tweaked_scheme = {
                    "set_safe": self.set_safe,
                    "scheme": self.scheme_map["working"],
                }
                self.p_settings["scheme_map"] = self.scheme_map
                self._save_tweak_settings()
                return True
            except Exception as e:
                log(e)
                sublime.error_message("Cannot clone theme")
                return False
        return False

    def _setup(self, noedit=False):
        """Setup."""

        self.set_tweaked_scheme = False
        self.filters = []
        self.settings = sublime.load_settings(PREFERENCES)
        self.p_settings = self._load_tweak_settings()
        scheme_file = self.settings.get(SCHEME, None) if self.init_theme is None else self.init_theme
        if AUTO and scheme_file == "auto":
            info = sublime.ui_info()
            scheme_file = info['color_scheme']['resolved_value']
        self.scheme_map = self.p_settings.get("scheme_map", None)
        self.theme_valid = self._theme_valid(scheme_file, noedit=noedit)

    def _set_tweaked_scheme(self):
        """Set the tweaked scheme."""

        if self.set_tweaked_scheme["set_safe"]:
            self._set_theme_safely(self.set_tweaked_scheme["scheme"])
        else:
            if self.settings.get(SCHEME) != self.set_tweaked_scheme["scheme"]:
                self.settings.set(SCHEME, self.set_tweaked_scheme["scheme"])
        self.set_tweaked_scheme = False
        Lock.release_lock()

    def _lock(self):
        """
        Acquire lock.

        Attempt to acquire a lock.
        If it fails try again and break lock if it fails.
        """

        locked = Lock.wait_lock()
        if not locked:
            locked = Lock.wait_lock(force=True)
        return locked

    def clear(self):
        """Clear tweaks."""

        if not self._lock():
            log('Failed to acquire lock!')
            return

        self._setup(noedit=True)

        if self.theme_valid:
            csm = ColorSchemeMatcher(self.scheme_map["original"])
            content = self._get_tmtheme(csm.get_scheme_obj()) if not NEW_SCHEMES else csm.get_scheme_obj()
            if NEW_SCHEMES:
                with codecs.open(self.scheme_clone, "w", encoding='utf-8') as f:
                    f.write(sublime.encode_value(content, pretty=True))
                    self.scheme_map["redo"] = ""
                    self.scheme_map["undo"] = ""
                    self.p_settings["scheme_map"] = self.scheme_map
                    self._save_tweak_settings()
            else:
                with open(self.scheme_clone, "wb") as f:
                    f.write(writePlistToBytes(content))
                    self.scheme_map["redo"] = ""
                    self.scheme_map["undo"] = ""
                    self.p_settings["scheme_map"] = self.scheme_map
                    self._save_tweak_settings()
            if self.set_tweaked_scheme:
                sublime.set_timeout(self._set_tweaked_scheme, 300)
            else:
                Lock.release_lock()
        else:
            Lock.release_lock()
            log("Theme has not been tweaked!", status=True)

    def clear_history(self):
        """Clear the history."""

        if not self._lock():
            log('Failed to acquire lock!')
            return

        self._setup(noedit=True)

        if self.theme_valid:
            self.scheme_map["redo"] = ""
            self.scheme_map["undo"] = ""
            self.p_settings["scheme_map"] = self.scheme_map
            self._save_tweak_settings()
            if self.set_tweaked_scheme:
                sublime.set_timeout(self._set_tweaked_scheme, 300)
            else:
                Lock.release_lock()
        else:
            Lock.release_lock()
            log("Theme has not been tweaked!", status=True)

    def is_new_format(self, filename):
        """Check if scheme is of the new format."""

        return filename.lower().endswith(('.sublime-color-scheme', '.hidden-color-scheme'))

    def undo(self):
        """Revert last change."""

        if not self._lock():
            log('Failed to acquire lock!')
            return

        self._setup(noedit=True)

        if self.theme_valid:
            csm = ColorSchemeMatcher(self.scheme_map["original"])

            undo = self.scheme_map["undo"].split(";")
            if len(undo) == 0 or (len(undo) == 1 and undo[0] == ""):
                log("Nothing to undo!", status=True)
                return
            redo = self.scheme_map["redo"].split(";")
            redo.append(undo.pop())
            self.scheme_map["redo"] = ";".join(redo)
            self.scheme_map["undo"] = ";".join(undo)

            self.plist_file = ColorSchemeTweaker().tweak(csm.get_scheme_obj(), self.scheme_map["undo"], not NEW_SCHEMES)
            if NEW_SCHEMES:
                with codecs.open(self.scheme_clone, "w", encoding='utf-8') as f:
                    f.write(sublime.encode_value(self.plist_file, pretty=True))
                    self.p_settings["scheme_map"] = self.scheme_map
                    self._save_tweak_settings()
            else:
                with open(self.scheme_clone, "wb") as f:
                    f.write(writePlistToBytes(self.plist_file))
                    self.p_settings["scheme_map"] = self.scheme_map
                    self._save_tweak_settings()
            if self.set_tweaked_scheme:
                sublime.set_timeout(self._set_tweaked_scheme, 300)
            else:
                Lock.release_lock()
        else:
            Lock.release_lock()
            log("Theme has not been tweaked!", status=True)

    def redo(self):
        """Redo last reverted change."""

        if not self._lock():
            log('Failed to acquire lock!')
            return

        self._setup(noedit=True)

        if self.theme_valid:
            csm = ColorSchemeMatcher(self.scheme_map["original"])

            redo = self.scheme_map["redo"].split(";")
            if len(redo) == 0 or (len(redo) == 1 and redo[0] == ""):
                log("Nothing to redo!", status=True)
                return
            undo = self.scheme_map["undo"].split(";")
            undo.append(redo.pop())
            self.scheme_map["redo"] = ";".join(redo)
            self.scheme_map["undo"] = ";".join(undo)

            self.plist_file = ColorSchemeTweaker().tweak(csm.get_scheme_obj(), self.scheme_map["undo"], not NEW_SCHEMES)
            if NEW_SCHEMES:
                with codecs.open(self.scheme_clone, "w", encoding='utf-8') as f:
                    f.write(sublime.encode_value(self.plist_file, pretty=True))
                    self.p_settings["scheme_map"] = self.scheme_map
                    self._save_tweak_settings()
            else:
                with open(self.scheme_clone, "wb") as f:
                    f.write(writePlistToBytes(self.plist_file))
                    self.p_settings["scheme_map"] = self.scheme_map
                    self._save_tweak_settings()
            if self.set_tweaked_scheme:
                sublime.set_timeout(self._set_tweaked_scheme, 300)
            else:
                Lock.release_lock()
        else:
            Lock.release_lock()
            log("Theme has not been tweaked!", status=True)

    def refresh(self, noedit=False):
        """Refresh."""

        if not self._lock():
            log('Failed to acquire lock!')
            return

        self._setup(noedit=noedit)

        if self.theme_valid and self.set_tweaked_scheme:
            sublime.set_timeout(self._set_tweaked_scheme, 300)
        else:
            Lock.release_lock()

    def run(self, filters):
        """Run command."""

        if not self._lock():
            log('Failed to acquire lock!')
            return

        self._setup()

        if self.theme_valid:
            csm = ColorSchemeMatcher(self.scheme_map["working"])
            content = csm.get_scheme_obj()
            ct = ColorSchemeTweaker()
            self.plist_file = ct.tweak(content, filters, not NEW_SCHEMES)

            if NEW_SCHEMES:
                with codecs.open(self.scheme_clone, "w", encoding='utf-8') as f:
                    f.write(sublime.encode_value(self.plist_file, pretty=True))
                    undo = self.scheme_map["undo"].split(";") + ct.get_filters()
                    self.scheme_map["redo"] = ""
                    self.scheme_map["undo"] = ";".join(undo)
                    self.p_settings["scheme_map"] = self.scheme_map
                    self._save_tweak_settings()
            else:
                with open(self.scheme_clone, "wb") as f:
                    f.write(writePlistToBytes(self.plist_file))
                    undo = self.scheme_map["undo"].split(";") + ct.get_filters()
                    self.scheme_map["redo"] = ""
                    self.scheme_map["undo"] = ";".join(undo)
                    self.p_settings["scheme_map"] = self.scheme_map
                    self._save_tweak_settings()
            if self.set_tweaked_scheme:
                sublime.set_timeout(self._set_tweaked_scheme, 300)
            else:
                Lock.release_lock()
        else:
            Lock.release_lock()


class ThemeTweakerIsReadyCommand(sublime_plugin.ApplicationCommand):
    """Command that can be called to test whether ThemeTweaker is ready."""

    @classmethod
    def is_tweakable(cls):
        """Check if tweakable (redundant; should remove)."""

        return THEME_TWEAKER_READY

    @classmethod
    def is_ready(cls):
        """Check if tweaker is ready."""

        return THEME_TWEAKER_READY

    def run(self):
        """Run command."""

        tweakable = ThemeTweakerIsReadyCommand.is_ready()
        if tweakable:
            log("Ready to tweak!")


class ThemeTweakerListener(sublime_plugin.EventListener):
    """Listen for tweak shortcut."""

    def on_query_context(self, view, key, operator, operand, match_all):
        """Check context of command."""

        return key == "theme_tweaker" and TWEAK_MODE


def plugin_loaded():
    """Setup plugin."""

    global THEME_TWEAKER_READY
    THEME_TWEAKER_READY = False

    # Just in case something went wrong,
    # and a theme got removed or isn't there on startup
    ThemeTweaker().refresh(noedit=True)
    THEME_TWEAKER_READY = True
    sublime.run_command("theme_tweaker_is_ready")
