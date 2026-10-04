# Workspace Attention

An Omarchy bar widget that highlights workspaces when a window requests attention, without automatically switching focus.

Urgent workspaces show an **amber label and a dot**. Hover for an attention hint; click to switch to the workspace. The indicator clears when Hyprland clears urgency, normally when you focus the requesting window. Switching to its workspace alone may not clear it if another window receives focus.

## Requirements

- Omarchy 4 / Quattro with the built-in Quickshell bar and plugin commands.
- Hyprland and Quickshell's `HyprlandWorkspace.urgent` property.
- Omarchy's bundled `qs.Ui` and `qs.Commons` QML modules and fonts.

Developed on Omarchy 4.0.4-1 and Hyprland 0.56.2. This is an Omarchy shell plugin, not a standalone Quickshell configuration or a Hyprland binary plugin.

## Install

```sh
omarchy plugin add https://github.com/curajorge/omarchy-workspace-attention.git --enable
```

This adds a replacement workspace widget. After confirming it appears, remove the original widget from the bar to avoid duplicate workspace indicators:

```sh
omarchy plugin disable omarchy.workspaces
omarchy bar move curajorge.workspace-attention --section left
```

If you already use a personal workspace clone, disable that clone instead. Back up `~/.config/omarchy/shell.json` first if you want to preserve its exact placement.

## Behavior and limitations

- Keeps Omarchy's workspace behavior: workspaces 1–5 remain visible; occupied workspaces up to 10 appear automatically.
- Supports horizontal and vertical bars.
- Adds a dot as well as color, so attention is not communicated by color alone.
- Uses native urgency notifications. No polling, background daemon, network requests, audio, or notification popups.
- Does not change focus settings. To prevent applications from taking focus, configure Hyprland's `misc.focus_on_activate = false` separately.
- Applications must actually request attention. A completed terminal command, unread message, or browser-tab change does not necessarily set window urgency.
- Workspaces above 10 and special workspaces are not displayed, matching the source widget's scope.

## Update or remove

```sh
omarchy plugin update curajorge.workspace-attention
```

Restore the original widget before removing this one:

```sh
omarchy plugin enable omarchy.workspaces
omarchy plugin remove curajorge.workspace-attention
```

## Development and validation

The repository root is the installable plugin. Edit a checkout in your user-owned plugin directory; never edit `/usr/share/omarchy/`. Omarchy hot-reloads plugin changes.

```sh
omarchy plugin validate .
qmllint -I "${OMARCHY_PATH:-/usr/share/omarchy}/shell" Workspaces.qml
```

QML linting requires the installed Omarchy/Quickshell imports. Depending on the distribution's QML tooling, its `qs` import alias may need to be made available to the linter.

Manual checks before releasing:

1. Confirm the widget loads and clicking a workspace works.
2. Have an unfocused application request attention; check for an amber label and dot without a focus change.
3. Focus that window and confirm the indicator clears.
4. Check multiple urgent windows, horizontal/vertical bars, and multiple monitors.
5. Disable, re-enable, and remove the plugin; confirm the original widget can be restored.

### Controlled attention test

From a terminal in your graphical session, run `python3 test-attention.py`.
A temporary blank test window opens. Switch to another workspace within 10 seconds.
The helper then sets the X11 urgency hint: the original workspace should turn amber
and show a dot while your current workspace keeps focus. Return and focus the test
window to clear the indicator. It closes automatically after another 60 seconds;
Ctrl+C in the launching terminal also stops it. Let the helper close its own window.

This optional manual helper needs Python 3, libX11, and XWayland (`DISPLAY`). It
tests an actual compositor urgency event, not a simulated widget color. Native
Wayland applications should also be checked separately. The helper's syntax has
been validated; its interactive pass/fail result must be observed on your desktop.

Manifest validation and runtime loading have been checked. End-to-end application urgency and the full multi-monitor matrix are not yet verified; this initial release is `0.1.0`.

Please include Omarchy, Hyprland, and Quickshell versions, bar orientation, and the application involved when reporting an issue. Avoid including private window titles or full desktop screenshots.

## Credits and license

Derived from Omarchy's built-in `shell/plugins/bar/widgets/Workspaces.qml`. The original workspace layout and switching logic come from Omarchy; this plugin adds attention styling. MIT licensed; see [LICENSE](LICENSE).

References: [Omarchy plugin development](https://plugins.omarchy.org/develop.html), [publishing guidelines](https://plugins.omarchy.org/publish.html), and [Omarchy source](https://github.com/omacom/omarchy).
