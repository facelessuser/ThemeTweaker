# ThemeTweaker

## 1.9.3

-   **FIX**: Fix regression that broke theme handling.
-   **FIX**: Fix for recursive adjustments

## 1.9.2

-   **FIX**: Remove unnecessary dependencies.

## 1.9.1

-   **FIX**: Support for Package Control 4.0 (compatibility with latest `mdpopups`).

## 1.9.0

-   **NEW**: Add support for Sublime 4095 `auto` color scheme option.
-   **FIX**: Don't use old legacy RGB library, instead use `coloraide` library in `mdpopups`. Handles colors better.

## 1.8.2

-   **FIX**: Scheme variables should allow `-`.

## 1.8.1

-   **FIX**: Color matcher should update original scheme object with color translations, and should apply filter
    **after** initial parsing.

## 1.8.0

-   **NEW**: Add support for `.hidden-color-scheme`.

## 1.7.0

-   **NEW**: Add documentation, quick start guide, and settings command to the quick panel.
-   **NEW**: Use Sublime's dual column settings command.
-   **FIX**: Race conditions with Sublime's resource access.
-   **FIX**: Add fallback scheme reading if resource isn't indexed.
-   **FIX**: Parse `selectionForeground` properly in legacy schemes.

## 1.6.0

-   **NEW**: Add support `.sublime-color-scheme` hashed syntax highlighting.
-   **FIX**: `.sublime-color-scheme` merge logic.

## 1.5.2

-   **FIX**: Parse color scheme with unexpected extension correctly.

## 1.5.1

-   **FIX**: Support for irregular `.sublime-color-scheme` values.

## 1.5.0

-   **NEW**: New `.sublime-color-scheme` format support.
-   **NEW**: Tweaked files are now prefixed with `tweak_`.
-   **FIX**: Decreasing saturation and contrast factor to improve adjustment results.

## 1.4.1

-   **FIX**: Fix dependencies.

## 1.4.0

-   **NEW**: Add contrast command.
-   **FIX**: Clean up and fix range checking and truncation of colors and scaling factors.

## 1.3.1

-   **FIX**: Plist output would fail when processing global setting that was not a color.

## 1.3.0

-   **NEW**: Restrict phantoms to 3124+

## 1.2.0

-   **NEW**: New quickstart command in menu.
-   **NEW**: Links in menu to navigate to official documentation and issue tracker.
-   **FIX**: Skip processing popupCss and phantomCss.
