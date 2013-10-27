'''
Theme Tweaker
Licensed under MIT
Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>
'''
import sublime
import sublime_plugin
from os import makedirs
from os.path import join, basename, exists, abspath, dirname, normpath
from plistlib import readPlistFromBytes, writePlistToBytes
import re
from ThemeTweaker.lib.rgba import RGBA
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


def packages_path(pth):
    return join(dirname(sublime.packages_path()), normpath(pth))


def get_setting(setting, override, default):
    value = override
    if value is None:
        value = sublime.load_settings(PLUGIN_SETTINGS).get(setting, default)
    return value


class ToggleThemeTweakerModeCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        global TWEAK_MODE
        TWEAK_MODE = not TWEAK_MODE
        sublime.status_message("TweakMode is %s" % ("enabled" if TWEAK_MODE else "disabled"))
        if not TWEAK_MODE:
            ThemeTweaker().clear_history()


class ThemeTweakerBrightnessCommand(sublime_plugin.ApplicationCommand):
    def run(self, direction="+", step=None, context=None):
        magnitude = -1.0 if direction == "-" else 1.0
        value = float(get_setting("brightness_step", step, .01)) * magnitude
        if value > -1.0 and value < 1.0:
            if context is not None and context in ["fg", "bg"]:
                ThemeTweaker().run("brightness(%f)@%s" % (value + 1.0, context))
            else:
                ThemeTweaker().run("brightness(%f)" % (value + 1.0))


class ThemeTweakerSaturationCommand(sublime_plugin.ApplicationCommand):
    def run(self, direction="+", step=None, context=None):
        magnitude = -1.0 if direction == "-" else 1.0
        value = float(get_setting("saturation_step", step, .1)) * magnitude
        if value > -1.0 and value < 1.0:
            if context is not None and context in ["fg", "bg"]:
                ThemeTweaker().run("saturation(%f)@%s" % (value + 1.0, context))
            else:
                ThemeTweaker().run("saturation(%f)" % (value + 1.0))


class ThemeTweakerHueCommand(sublime_plugin.ApplicationCommand):
    def run(self, direction="+", step=None, context=None):
        magnitude = -1 if direction == "-" else 1
        value = int(get_setting("hue_step", step, 10)) * magnitude
        if value >= -360 and value <= 360:
            if context is not None and context in ["fg", "bg"]:
                ThemeTweaker().run("hue(%d)@%s" % (value, context))
            else:
                ThemeTweaker().run("hue(%d)" % value)


class ThemeTweakerInvertCommand(sublime_plugin.ApplicationCommand):
    def run(self, context=None):
        if context is not None and context in ["fg", "bg"]:
            ThemeTweaker().run("invert@%s" % context)
        else:
            ThemeTweaker().run("invert")

class ThemeTweakerSepiaCommand(sublime_plugin.ApplicationCommand):
    def run(self, context=None):
        if context is not None and context in ["fg", "bg"]:
            ThemeTweaker().run("sepia@%s" % context)
        else:
            ThemeTweaker().run("sepia")


class ThemeTweakerColorizeCommand(sublime_plugin.ApplicationCommand):
    def run(self, hue=None, context=None):
        value = int(get_setting("colorize_hue", hue, 0))
        if context is not None and context in ["fg", "bg"]:
            ThemeTweaker().run("colorize(%d)@%s" % (value, context))
        else:
            ThemeTweaker().run("colorize(%d)" % value)


class ThemeTweakerGlowCommand(sublime_plugin.ApplicationCommand):
    def run(self, intensity):
        value = float(get_setting("glow_intensity", intensity, .2))
        ThemeTweaker().run("glow(%f)" % value)


class ThemeTweakerGrayscaleCommand(sublime_plugin.ApplicationCommand):
    def run(self, context=None):
        if context is not None and context in ["fg", "bg"]:
            ThemeTweaker().run("grayscale@%s" % context)
        else:
            ThemeTweaker().run("grayscale")


class ThemeTweakerCustomCommand(sublime_plugin.ApplicationCommand):
    def run(self, filters):
        ThemeTweaker().run(filters)


class ThemeTweakerClearCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        ThemeTweaker().clear()


class ThemeTweakerUndoCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        ThemeTweaker().undo()


class ThemeTweakerRedoCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        ThemeTweaker().redo()


class ThemeTweaker(object):
    def __init__(self, set_safe=False, init_theme=None):
        self.set_safe = set_safe
        self.init_theme = init_theme

    def _load_tweak_settings(self):
        self._ensure_temp()
        p_settings = {}
        tweaks = packages_path(join(normpath(TEMP_PATH), basename(TWEAK_SETTINGS)))
        if exists(tweaks):
            try:
                with open(tweaks, "r") as f:
                    # Allow C style comments and be forgiving of trailing commas
                    content = sanitize_json(f.read(), True)
                p_settings = json.loads(content)
            except:
                pass
        return p_settings

    def _save_tweak_settings(self):
        tweaks = packages_path(join(normpath(TEMP_PATH), basename(TWEAK_SETTINGS)))
        j = json.dumps(self.p_settings, sort_keys=True, indent=4, separators=(',', ': '))
        try:
            with open(tweaks, 'w') as f:
                f.write(j + "\n")
        except:
            pass

    def _set_theme_safely(self, name):
        pref_file = join(sublime.packages_path(), 'User', 'Preferences.sublime-settings')
        pref = {}
        if exists(pref_file):
            try:
                with open(pref_file, "r") as f:
                    # Allow C style comments and be forgiving of trailing commas
                    content = sanitize_json(f.read(), True)
                pref = json.loads(content)
            except:
                pass
        pref[SCHEME] = name
        j = json.dumps(pref, sort_keys=True, indent=4, separators=(',', ': '))
        try:
            with open(pref_file, 'w') as f:
                f.write(j + "\n")
        except:
            pass

    def _ensure_temp(self):
        temp = packages_path(TEMP_PATH)
        if not exists(temp):
            makedirs(temp)

    def _exists(self, pth):
        found = False
        if exists(packages_path(pth)):
            found = True
        else:
            try:
                sublime.load_settings(pth)
                found = True
            except:
                pass
        return found

    def _theme_valid(self, scheme_file):
        is_working = scheme_file.startswith(TEMP_PATH + '/')
        if is_working and self.scheme_map is not None and self.scheme_map["working"] == scheme_file and self._exists(self.scheme_map["original"]):
            self.scheme_file = packages_path(self.scheme_map["original"])
            self.scheme_clone = packages_path(self.scheme_map["working"])
            return True
        elif not is_working:
            self._ensure_temp()
            content = sublime.load_binary_resource(scheme_file)
            self.scheme_file = packages_path(scheme_file)
            self.scheme_clone = packages_path(join(normpath(TEMP_PATH), basename(scheme_file)))
            try:
                with open(self.scheme_clone, "wb") as f:
                    f.write(content)
                self.scheme_map = {"original": scheme_file, "working": "%s/%s" % (TEMP_PATH, basename(scheme_file)), "undo": "", "redo": ""}
                if self.set_safe:
                    self._set_theme_safely(self.scheme_map["working"])
                else:
                    self.settings.set(SCHEME, self.scheme_map["working"])
                self.p_settings["scheme_map"] = self.scheme_map
                self._save_tweak_settings()
                return True
            except Exception as e:
                print(e)
                sublime.error_message("Cannot clone theme")
                return
        return False

    def _setup(self, context=None):
        self.filters = []
        self.settings = sublime.load_settings(PREFERENCES)
        self.p_settings = self._load_tweak_settings()
        scheme_file = self.settings.get(SCHEME, None) if self.init_theme is None else self.init_theme
        self.scheme_map = self.p_settings.get("scheme_map", None)
        self.theme_valid = self._theme_valid(scheme_file)

    def clear(self):
        self._setup()

        if self.theme_valid:
            with open(self.scheme_clone, "wb") as f:
                f.write(sublime.load_binary_resource(self.scheme_map["original"]))
                self.scheme_map["redo"] = ""
                self.scheme_map["undo"] = ""
                self.p_settings["scheme_map"] = self.scheme_map
                self._save_tweak_settings()

    def clear_history(self):
        self._setup()

        if self.theme_valid:
            self.scheme_map["redo"] = ""
            self.scheme_map["undo"] = ""
            self.p_settings["scheme_map"] = self.scheme_map
            self._save_tweak_settings()

    def undo(self):
        self._setup()

        if self.theme_valid:
            plist = sublime.load_binary_resource(self.scheme_map["original"])
            undo = self.scheme_map["undo"].split(";")
            if len(undo) == 0:
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

    def redo(self):
        self._setup()

        if self.theme_valid:
            plist = sublime.load_binary_resource(self.scheme_map["original"])
            redo = self.scheme_map["redo"].split(";")
            if len(redo) == 0:
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

    def refresh(self):
        self._setup()

        if self.theme_valid:
            plist = sublime.load_binary_resource(self.scheme_map["original"])
            self.plist_file = ColorSchemeTweaker().tweak(
                readPlistFromBytes(plist),
                self.scheme_map["undo"]
            )

    def run(self, filters):
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
                undo = self.scheme_map["undo"].split(";") + ct._get_filters()
                self.scheme_map["redo"] = ""
                self.scheme_map["undo"] = ";".join(undo)
                self.p_settings["scheme_map"] = self.scheme_map
                self._save_tweak_settings()


class ThemeTweakerListener(sublime_plugin.EventListener):
    def on_query_context(self, view, key, operator, operand, match_all):
        return key == "theme_tweaker" and TWEAK_MODE


def plugin_loaded():
    # Just in case something went wrong,
    # and a theme got removed or isn't there on startup
    ThemeTweaker(set_safe=True).refresh()
