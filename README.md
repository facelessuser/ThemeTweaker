# ThemeTweaker

Change your Sublime tmTheme files by applying different color filters on the fly.

ThemeTweaker came out as a side project while I was working on ExportHtml.  I was dealing with the working with replicating the tmTheme in an HTML output, but later wanted to be able to modify the tmTheme with filters such as: rotating the hue, adjusting the contrast, increasing/deceasing the brightness, etc.  Some of the filters are useless, but they were fun to throw together.  I have been using it for a while, but recently decided to throw it together in its own package.  It can be used as a stand alone plugin for tweaking your themes, or it can be leveraged by other plugins for modifying color scheme (tmTheme) files.

# Features

ThemeTweaker has a number of commands that allow you to do the following:
- Increase/Decrease brightness
- Increase/Decrease saturation
- Rotate the hues of the theme
- Colorize the theme (make all of the colors different shades of one color)
- Convert the theme to grayscale
- Apply a Sepia filter
- Invert the color scheme
- Cause foreground scopes to glow (keywords etc. except for the main foreground color; maybe that will change)
- With filters that make sense, allow limiting the filter to background or foreground scopes
- Create shortcuts to adjust the color scheme only when in `ThemeMode`
- Allow *undo* and *redo* of filters while in `ThemeMode`
- A command to revert all filters in one shot and return to original theme
- Does not modify the original theme directly, but creates a copy
- Live update when applying filters

# Usage

In order to use ThemeTweaker, you can set up command palette commands, keymaps, menu items etc.  ThemeTweaker comes with an example keymap file to show how commands are constructed.

The default steps, or hues, or intensities (depending on the command), are defined in the settings file.  These can be changed if desired.

## Basic commands
- **Brightness**: `ThemeTweakerBrightnessCommand` can take a step value of float type to determine the magnitude of brightness to apply.  It is in relation to the center `1.0`.  So a value of `0.01` would shift it `1.01`. It also takes a direction argument which is denoted with a `+` or `-` direction. You can limit the filter to the background or foreground using the `context` arguement and giving it a value of `bg` or `fg` respectively.
- **Saturation**: `ThemeTweakerSaturationCommand` can take a step value of float type to determine the magnitude of saturation to apply.  It is in relation to the center `1.0`.  So a value of `0.01` would shift it `1.01`. It also takes a direction argument which is denoted with a `+` or `-` direction.  You can limit the filter to the background or foreground using the `context` arguement and giving it a value of `bg` or `fg` respectively.
- **Hue**: `ThemeTweakerHueCommand` can take an integer which represents a degree between `0` and `360` to shift the hue.  It also takes a direction argument which is denoted with a `+` or `-` direction.  You can limit the filter to the background or foreground using the `context` arguement and giving it a value of `bg` or `fg` respectively.
- **Colorize**: `ThemeTweakerColorizeCommand` can take a hue integer that all colors will be converted to.  All colors will be a shade of that hue depending on what their luminance was before conversion. Hues are between `0` and `360`.  You can limit the filter to the background or foreground using the `context` arguement and giving it a value of `bg` or `fg` respectively.
- **Invert**: `ThemeTweakerInvertCommand` will invert all of the colors.  You can limit the filter to the background or foreground using the `context` arguement and giving it a value of `bg` or `fg` respectively.
- **Sepia**: `ThemeTweakerSepiaCommand` will apply a sepia filter to all colors.  You can limit the filter to the background or foreground using the `context` arguement and giving it a value of `bg` or `fg` respectively.
- **Grayscale**: `ThemeTweakerGrayscaleCommand` will apply a grayscale filter to all colors.  You can limit the filter to the background or foreground using the `context` arguement and giving it a value of `bg` or `fg` respectively.
- **Glow**: `ThemeTweakerGlowCommand` can take a floating point glow intensity to determine the strength of the glow.  Glow should be between `0.0` and `1.0`.

Commands are constructed like so:
```javascript
{
    "keys": ["up"],
    "command": "theme_tweaker_brightness",
    "args": {
        "direction": "+"
    }
},
```

To limit a command or shortcut to only when `ThemeMode` is enabled:
```javascript
{
    "keys": ["up"],
    "command": "theme_tweaker_brightness",
    "context": [
        {"key": "theme_tweaker"}
    ],
    "args": {
        "direction": "+"
    }
},
```

To override the default step, hue, or intensity (override argument name will vary depending on function):
```javascript
{
    "keys": ["up"],
    "command": "theme_tweaker_brightness",
    "context": [
        {"key": "theme_tweaker"}
    ],
    "args": {
        "direction": "+",
        "step": 0.05
    }
},
```

Apply filter to just the foreground (for all commands except `glow`):
```javascript
{
    "keys": ["up"],
    "command": "theme_tweaker_brightness",
    "context": [
        {"key": "theme_tweaker"}
    ],
    "args": {
        "direction": "+",
        "step": 0.05,
        "context": "fg"
    }
},
```

`TweakMode` can be enabled/disabled via the command palette command `Theme Tweaker: Toggle Tweak Mode`

## Special Commands
- **Undo**: `ThemeTweakerUndoCommand` reverts the last applied filter.
- **Redo**: `ThemeTweakerRedoCommand` re-applys the last applied filter that was reverted.
- **Clear**: `ThemeTweakerClearCommand` clears all applied filters.

## Custom Filter Command

`ThemeTweakerCustomCommand` is a command that allows you to manually chain different filters together.  It takes a string with special syntax to apply filters.  It will not calculte values in relation to center, or take separate direction arguments etc.  All operations are defined by a single string.

example:
```javascript
{
    "keys": ["up"],
    "command": "theme_tweaker_custom",
    "context": [
        {"key": "theme_tweaker"}
    ],
    "args": {
        "filters": "grayscale@fg;sepia;colorize(0);hue(-30);brightness(1.050000)@bg;saturation(0.900000);brightness(0.950000)"
    }
},
```

The available filters are:
- grayscale
- sepia
- invert
- brightness(float)
- saturation(float)
- hue(signed integer)
- colorize(integer)
- glow(positive float)

To apply a filter to just the foreground or background, simply add `@fg` or `@bg` to the filter in question.
