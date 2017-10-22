# Getting Started

ThemeTweaker allows you to apply filters on a theme.  You can increase brightness, decrease saturation, rotate the hue, etc.

The plugin provides a number of commands that do various things.  These commands can be called by other plugins  
or can be bound to shortcuts so you can experiment with a theme:

- Increase/Decrease brightness.
- Increase/Decrease saturation.
- Rotate the hues of the theme.
- Colorize the theme (make all of the colors different shades of one color).
- Convert the theme to grayscale.
- Apply a Sepia filter.
- Invert the color scheme.
- Cause foreground scopes to glow (keywords etc. except for the main foreground color; maybe that will - change).

For quick setup, you can add these key maps to your `User/Default.sublime-keymap` file.  Notice that we set the context  
key to `theme_tweaker`; this will ensure that the keymaps are only valid when in *theme tweaker mode*.  Theme tweaker mode  
can be enabled from the command palette.

```js
    //////////////////////////////////
    // Theme Tweaker
    //////////////////////////////////
    {"keys": ["up"], "command": "theme_tweaker_brightness", "context": [{"key": "theme_tweaker"}], "args": {"direction": "+"}},
    {"keys": ["down"], "command": "theme_tweaker_brightness", "context": [{"key": "theme_tweaker"}], "args": {"direction": "-"}},
    {"keys": ["left"], "command": "theme_tweaker_contrast", "context": [{"key": "theme_tweaker"}], "args": {"direction": "-"}},
    {"keys": ["right"], "command": "theme_tweaker_contrast", "context": [{"key": "theme_tweaker"}], "args": {"direction": "+"}},
    {"keys": ["shift+up"], "command": "theme_tweaker_saturation", "context": [{"key": "theme_tweaker"}], "args": {"direction": "+"}},
    {"keys": ["shift+down"], "command": "theme_tweaker_saturation", "context": [{"key": "theme_tweaker"}], "args": {"direction": "-"}},
    {"keys": ["shift+left"], "command": "theme_tweaker_hue", "context": [{"key": "theme_tweaker"}], "args": {"direction": "-"}},
    {"keys": ["shift+right"], "command": "theme_tweaker_hue", "context": [{"key": "theme_tweaker"}], "args": {"direction": "+"}},
    {"keys": ["ctrl+1"], "command": "theme_tweaker_invert", "context": [{"key": "theme_tweaker"}]},
    {"keys": ["ctrl+2"], "command": "theme_tweaker_colorize", "context": [{"key": "theme_tweaker"}]},
    {"keys": ["ctrl+3"], "command": "theme_tweaker_sepia", "context": [{"key": "theme_tweaker"}]},
    {"keys": ["ctrl+4"], "command": "theme_tweaker_grayscale", "context": [{"key": "theme_tweaker"}]},
    {"keys": ["ctrl+5"], "command": "theme_tweaker_glow", "context": [{"key": "theme_tweaker"}]},
    {"keys": ["ctrl+z"], "command": "theme_tweaker_undo", "context": [{"key": "theme_tweaker"}]},
    {"keys": ["ctrl+shift+z"], "command": "theme_tweaker_redo", "context": [{"key": "theme_tweaker"}]},
    {"keys": ["escape"], "command": "theme_tweaker_clear", "context": [{"key": "theme_tweaker"}]}
```
[(view raw file to copy and paste shortcuts)](sub://Packages/ThemeTweaker/quickstart.md)

Each command increments by a default step value.  You can find the default step values in the [settings file]([settings](sub://Packages/ThemeTweaker/theme_tweaker.sublime-settings)).

For more information on configuring the commands, check out the [documentation](http://facelessuser.github.io/ThemeTweaker/usage/).

# I Need Help!

That's okay.  Bugs are sometimes introduced or discovered in existing code.  Sometimes the documentation isn't clear.  
Support can be found over on the [official repo](https://github.com/facelessuser/ThemeTweaker/issues).  Make sure to first search the documentation and previous issues  
before opening a new issue.  And when creating a new issue, make sure to fill in the provided issue template.  Please  
be courteous and kind in your interactions.
