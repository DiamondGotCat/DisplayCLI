
<img width="1920" alt="displaycli" src="https://github.com/user-attachments/assets/a292fa49-91bb-4e4c-aae9-50eb782e8abd" />

# DisplayCLI
A CLI tool to manage display resolutions on macOS.

## How it works
This uses Objective-C, Quartz, and Cocoa, which are available on macOS, to control the resolution state and settings.
This works in most cases, but there may be some cases where it doesn't work.
If it doesn't work, please create an issue or fix it and submit a pull request.
If you know the cause of the problem, please let me know.

## Requiments
- macOS (Recommend: macOS Catalina 10.15+)
- CPython 3.8+
- `uv` [PyPI↗︎](https://pypi.org/project/uv/) or `pip3` [PyPI↗︎](https://pypi.org/project/pip/) 
- `nercone-modern` [PyPI↗︎](https://pypi.org/project/nercone-modern/)
- `pyobjc` [PyPI↗︎](https://pypi.org/project/pyobjc/)

## Installation

### using uv (recommended)
```sh
uv tool install displaycli
```

### using pip3

**System Python:**
```sh
pip3 install displaycli --break-system-packages
```

**Venv Python:**
```sh
pip3 install displaycli
```

## Update

### using uv (recommended)
```sh
uv tool install displaycli --upgrade
```

### using pip3

**System Python:**
```sh
pip3 install displaycli --upgrade --break-system-packages
```

**Venv Python:**
```sh
pip3 install displaycli --upgrade
```

## Usage

### List Displays
```sh
displaycli displays
```

```text example_result.txt
nercone@demo ~/D/DisplayCLI> displaycli displays
DisplayTool INFO     | Available Displays:

  ID: 0 | Name: Unknown Display (Main)
    └─ Current: 1710x1112 @2x (HiDPI) at 60.0Hz
nercone@demo ~/D/DisplayCLI> 
```

### List Display's Native Supported Resolutions
```sh
displaycli modes <id of display>
```

```text example_result.txt
nercone@demo ~/D/DisplayCLI> displaycli modes 0 
DisplayTool INFO     | Available modes for display ID 0:
  - 2560 x 1664 @ 60.00Hz (Pixels: 2560x1664)
  - 2560 x 1600 @ 60.00Hz (Pixels: 2560x1600)
  - 2048 x 1332 @ 60.00Hz (Pixels: 2048x1332)
  - 2048 x 1280 @ 60.00Hz (Pixels: 2048x1280)
  - 1920 x 1200 @ 60.00Hz (Pixels: 1920x1200)
nercone@demo ~/D/DisplayCLI> 
```

### Check Display's Current Resolution
```sh
displaycli current <id of display>
```

```text example_result.txt
nercone@demo ~/D/DisplayCLI> displaycli current 0
DisplayTool INFO     | Current mode for display 'Unknown Display' (ID: 0):
  - Resolution:   1710x1112 @2x (HiDPI)
  - Pixel Size:   3420x2224
  - Refresh Rate: 60.0Hz
nercone@demo ~/D/DisplayCLI> 
```

### Change Display's Resolution (and Refresh Rate)
**Note:** This operation requires administrator privileges

```sh
sudo displaycli set <id of display> <width> <height> [--refresh <refresh rate>]
```

```text example_result.txt
nercone@demo ~/D/DisplayCLI> sudo displaycli set 0 2560 1664 --refresh 60
Password:
DisplayTool INFO     | Attempting to set display 0 to 2560x1664 @ 60.0Hz
            WARN     | This will change your display resolution. Are you sure? [y/N]y
            INFO     | Display mode changed successfully!
nercone@demo ~/D/DisplayCLI> 
```
