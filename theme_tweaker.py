"""
Theme Tweaker.

Licensed under MIT
Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>
"""
import sublime
import sublime_plugin
from os import makedirs
from os.path import join, basename, exists, dirname, normpath
from plistlib import readPlistFromBytes, writePlistToBytes
from ThemeTweaker.lib.file_strip.json import sanitize_json
from ThemeTweaker.lib.color_scheme_tweaker import ColorSchemeTweaker
import json

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
        if value > -1.0 and value < 1.0:
            if context is not None and context in ["fg", "bg"]:
                ThemeTweaker(theme).run("brightness(%f)@%s" % (value + 1.0, context))
            else:
                ThemeTweaker(theme).run("brightness(%f)" % (value + 1.0))


class ThemeTweakerSaturationCommand(sublime_plugin.ApplicationCommand):
    """Tweak Saturation."""

    def run(self, direction="+", step=None, context=None, theme=None):
        """Run command."""

        magnitude = -1.0 if direction == "-" else 1.0
        value = float(get_setting("saturation_step", step, .1)) * magnitude
        if value > -1.0 and value < 1.0:
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
        if you modified it too soon.  So manually reading ws the safest.
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
            try:
                results = sublime.find_resources(basename(pth))
                if sublime.platform() == "windows":
                    for r in results:
                        if r.lower() == pth.lower():
                            found = True
                            break
                else:
                    found = pth in results
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
            content = sublime.load_binary_resource(scheme_file)
            self.scheme_file = packages_path(scheme_file)
            self.scheme_clone = packages_path(join(normpath(TEMP_PATH), basename(scheme_file)))
            try:
                with open(self.scheme_clone, "wb") as f:
                    f.write(content)
                self.scheme_map = {
                    "original": scheme_file,
                    "working": "%s/%s" % (TEMP_PATH, basename(scheme_file)),
                    "undo": "",
                    "redo": ""
                }
                if self.set_safe:
                    self._set_theme_safely(self.scheme_map["working"])
                else:
                    self.settings.set(SCHEME, self.scheme_map["working"])
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

        self.filters = []
        self.settings = sublime.load_settings(PREFERENCES)
        self.p_settings = self._load_tweak_settings()
        scheme_file = self.settings.get(SCHEME, None) if self.init_theme is None else self.init_theme
        self.scheme_map = self.p_settings.get("scheme_map", None)
        self.theme_valid = self._theme_valid(scheme_file, noedit=noedit)

    def clear(self):
        """Clear tweaks."""

        self._setup(noedit=True)

        if self.theme_valid:
            with open(self.scheme_clone, "wb") as f:
                f.write(sublime.load_binary_resource(self.scheme_map["original"]))
                self.scheme_map["redo"] = ""
                self.scheme_map["undo"] = ""
                self.p_settings["scheme_map"] = self.scheme_map
                self._save_tweak_settings()
        else:
            log("Theme has not been tweaked!", status=True)

    def clear_history(self):
        """Clear the history."""

        self._setup(noedit=True)

        if self.theme_valid:
            self.scheme_map["redo"] = ""
            self.scheme_map["undo"] = ""
            self.p_settings["scheme_map"] = self.scheme_map
            self._save_tweak_settings()
        else:
            log("Theme has not been tweaked!", status=True)

    def undo(self):
        """Revert last change."""

        self._setup(noedit=True)

        if self.theme_valid:
            plist = sublime.load_binary_resource(self.scheme_map["original"])
            undo = self.scheme_map["undo"].split(";")
            if len(undo) == 0 or (len(undo) == 1 and undo[0] == ""):
                log("Nothing to undo!", status=True)
                return
            redo = self.scheme_map["redo"].split(";")
            redo.append(undo.pop())
            self.scheme_map["redo"] = ";".join(redo)
            self.scheme_map["undo"] = ";".join(undo)
            self.plist_file = ColorSchemeTweaker().tweak(
                readPlistFromBytes(plist),
                self.scheme_map["undo"]
            )
            with open(self.scheme_clone, "wb") as f:
                f.write(writePlistToBytes(self.plist_file))
                self.p_settings["scheme_map"] = self.scheme_map
                self._save_tweak_settings()
        else:
            log("Theme has not been tweaked!", status=True)

    def redo(self):
        """Redo last reverted change."""

        self._setup(noedit=True)

        if self.theme_valid:
            plist = sublime.load_binary_resource(self.scheme_map["original"])
            redo = self.scheme_map["redo"].split(";")
            if len(redo) == 0 or (len(redo) == 1 and redo[0] == ""):
                log("Nothing to redo!", status=True)
                return
            undo = self.scheme_map["undo"].split(";")
            undo.append(redo.pop())
            self.scheme_map["redo"] = ";".join(redo)
            self.scheme_map["undo"] = ";".join(undo)
            self.plist_file = ColorSchemeTweaker().tweak(
                readPlistFromBytes(plist),
                self.scheme_map["undo"]
            )
            with open(self.scheme_clone, "wb") as f:
                f.write(writePlistToBytes(self.plist_file))
                self.p_settings["scheme_map"] = self.scheme_map
                self._save_tweak_settings()
        else:
            log("Theme has not been tweaked!", status=True)

    def refresh(self, noedit=False):
        """Refresh."""

        self._setup(noedit=noedit)

    def run(self, filters):
        """Run command."""

        self._setup()

        if self.theme_valid:
            plist = sublime.load_binary_resource(self.scheme_map["working"])
            ct = ColorSchemeTweaker()
            self.plist_file = ct.tweak(
                readPlistFromBytes(plist),
                filters
            )

            with open(self.scheme_clone, "wb") as f:
                f.write(writePlistToBytes(self.plist_file))
                undo = self.scheme_map["undo"].split(";") + ct.get_filters()
                self.scheme_map["redo"] = ""
                self.scheme_map["undo"] = ";".join(undo)
                self.p_settings["scheme_map"] = self.scheme_map
                self._save_tweak_settings()


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
