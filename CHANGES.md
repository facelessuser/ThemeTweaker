# ThemeTweaker 1.7.0

Nov 8, 2017

- **NEW**: Add documentation, quick start guide, and settings command to the quick panel.
- **NEW**: Use Sublime's dual column settings command.
- **FIX**: Race conditions with Sublime's resource access.
- **FIX**: Add fallback scheme reading if resource isn't indexed.
- **FIX**: Parse `selectionForeground` properly in legacy schemes.

# ThemeTweaker 1.6.0

Nov 4, 2017

- **NEW**: Add support `.sublime-color-scheme` hashed syntax highlighting.
- **FIX**: `.sublime-color-scheme` merge logic.

# ThemeTweaker 1.5.2

Oct 30, 2017

- **FIX**: Parse color scheme with unexpected extension correctly.

# ThemeTweaker 1.5.1

Oct 27, 2017

- **FIX**: Support for irregular `.sublime-color-scheme` values.

# ThemeTweaker 1.5.0

Oct 21, 2017

- **NEW**: New `.sublime-color-scheme` format support.
- **NEW**: Tweaked files are now prefixed with `tweak_`.
- **FIX**: Decreasing saturation and contrast factor to improve adjustment results.

# ThemeTweaker 1.4.1

Oct 8, 2017

- **FIX**: Fix dependencies.

# ThemeTweaker 1.4.0

Oct 3, 2017

- **NEW**: Add contrast command.
- **FIX**: Clean up and fix range checking and truncation of colors and scaling factors.

# ThemeTweaker 1.3.1

Oct 1, 2017

- **FIX**: Plist output would fail when processing global setting that was not a color.

# ThemeTweaker 1.3.0

> Released May 27, 2017

- **NEW**: Restrict phantoms to 3124+

# ThemeTweaker 1.2.0

> Released Nov 30, 2016

- **NEW**: New quickstart command in menu.
- **NEW**: Links in menu to navigate to official documentation and issue tracker.
- **FIX**: Skip processing popupCss and phantomCss.
