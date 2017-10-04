# ThemeTweaker

## Overview

Change your Sublime tmTheme files by applying different color filters on the fly.

ThemeTweaker came out as a side project while I was working on ExportHtml.  I was dealing with the replicating the tmTheme in an HTML output, but later wanted to be able to modify the tmTheme with filters such as: rotating the hue, adjusting the contrast, increasing/deceasing the brightness, etc.  Some of the filters are useless, but they were fun to throw together.  I have been using it for a while, but recently decided to throw it together in its own package.  It can be used as a stand alone plugin for tweaking your themes, or it can be leveraged by other plugins for modifying color scheme (tmTheme) files.

## Features

ThemeTweaker has a number of commands that allow you to do the following:

- Increase/decrease brightness.
- Increase/decrease saturation.
- Increase/decrease contrast.
- Rotate the hues of the theme.
- Colorize the theme (make all of the colors different shades of one color).
- Convert the theme to grayscale.
- Apply a Sepia filter.
- Invert the color scheme.
- Cause foreground scopes to glow (keywords etc. except for the main foreground color; maybe that will change).
- With filters that make sense, allow limiting the filter to background or foreground scopes.
- Create shortcuts to adjust the color scheme only when in `ThemeMode`.
- Allow *undo* and *redo* of filters while in `ThemeMode`.
- A command to revert all filters in one shot and return to original theme.
- Does not modify the original theme directly, but creates a copy.
- Live update when applying filters.

--8<-- "refs.md"
