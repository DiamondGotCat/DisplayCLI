import argparse
import sys
from nercone_modern.logging import ModernLogging
from .manager import DisplayManager

logger = ModernLogging("DisplayCLI", display_level="INFO")
manager = DisplayManager()

def list_displays(args):
    try:
        displays = manager.get_online_displays()
        print("Available Displays:")
        for disp in displays:
            main_marker = " (Main)" if disp['is_main'] else ""
            mode = disp['current_mode']
            res_str = f"{mode['width']}x{mode['height']}"
            hidpi_marker = f" @{mode['scale']}x (HiDPI)" if mode['hidpi'] else ""

            print(f"\n  ID: {disp['id']} | Name: {disp['name']}{main_marker}")
            print(f"    └─ Current: {res_str}{hidpi_marker} at {mode['refresh_rate']}Hz")

    except Exception as e:
        logger.log(f"Error listing displays: {e}", level_text="CRITICAL")
        sys.exit(1)

def list_modes(args):
    try:
        display_id = int(args.display_id)
        modes = manager.get_display_modes(display_id)
        
        if not modes:
            logger.log(f"No modes found for display ID {display_id}, or display ID is invalid.", level_text="WARN")
            return

        target_aspect_ratio = None
        if args.aspect_ratio:
            current_mode = manager.get_current_mode(display_id)
            if current_mode:
                target_aspect_ratio = manager.get_aspect_ratio(current_mode['width'], current_mode['height'])
                logger.log(f"Filtering for aspect ratio: {target_aspect_ratio[0]}:{target_aspect_ratio[1]}", level_text="INFO")

        print(f"Available modes for display ID {display_id}:")

        count = 0
        for mode in modes:
            if target_aspect_ratio:
                mode_ar = manager.get_aspect_ratio(mode['width'], mode['height'])
                if mode_ar != target_aspect_ratio:
                    continue

            hidpi_marker = f" @{mode['scale']}x (HiDPI)" if mode['hidpi'] else ""
            print(f"  - {mode['width']:>4} x {mode['height']:<4} @ {mode['refresh_rate']:>5.2f}Hz{hidpi_marker} (Pixels: {mode['pixel_width']}x{mode['pixel_height']})")
            count += 1
        
        if count == 0: logger.log("No matching modes found.", level_text="INFO")

    except ValueError:
        logger.log(f"Invalid display ID: {args.display_id}. Please provide a number.", level_text="ERROR")
        sys.exit(1)
    except Exception as e:
        logger.log(f"Error listing modes: {e}", level_text="CRITICAL")
        sys.exit(1)

def set_mode(args):
    try:
        display_id = int(args.display_id)
        width = int(args.width)
        height = int(args.height)
        refresh = float(args.refresh) if args.refresh else 0

        logger.log(f"Attempting to set display {display_id} to {width}x{height} @ {refresh if refresh > 0 else 'any'}Hz", level_text="INFO")
        mode_to_set = manager.find_mode(display_id, width, height, refresh)

        if not mode_to_set:
            logger.log(f"Could not find a matching mode.", level_text="ERROR")
            sys.exit(1)

        answer = logger.prompt("This will change your display resolution. Are you sure?", default="N", choices=["y", "N"], level_text="WARN")
        if answer.lower() != 'y':
            logger.log("Operation cancelled by user.", level_text="INFO")
            return

        manager.set_display_mode(display_id, mode_to_set)
        logger.log("Display mode changed successfully!", level_text="INFO")

    except ValueError:
        logger.log("Invalid arguments. Please ensure all IDs, dimensions are numbers.", level_text="ERROR")
        sys.exit(1)
    except RuntimeError as e:
        logger.log(f"Failed to set display mode: {e}", level_text="CRITICAL")
        logger.log("This operation may require administrator privileges. Try running with 'sudo'.", level_text="WARN")
        sys.exit(1)
    except Exception as e:
        logger.log(f"An unexpected error occurred: {e}", level_text="CRITICAL")
        sys.exit(1)
        
def show_current(args):
    try:
        display_id = int(args.display_id) if args.display_id else manager.get_main_display_id()
        if not args.display_id: logger.log(f"No ID provided, showing main display (ID: {display_id}).", level_text="DEBUG")

        info = manager._get_display_info(display_id)
        mode = info['current_mode']
        
        print(f"Current mode for display '{info['name']}' (ID: {info['id']}):")
        hidpi_marker = f" @{mode['scale']}x (HiDPI)" if mode['hidpi'] else ""
        print(f"  - Resolution:   {mode['width']}x{mode['height']}{hidpi_marker}")
        print(f"  - Pixel Size:   {mode['pixel_width']}x{mode['pixel_height']}")
        print(f"  - Refresh Rate: {mode['refresh_rate']}Hz")

    except ValueError:
        logger.log(f"Invalid display ID: {args.display_id}. Please provide a number.", level_text="ERROR")
        sys.exit(1)
    except Exception as e:
        logger.log(f"Error getting current mode: {e}", level_text="CRITICAL")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="A CLI tool to manage display resolutions on macOS.")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    p_list = subparsers.add_parser("displays", help="List all connected displays.")
    p_list.set_defaults(func=list_displays)

    p_modes = subparsers.add_parser("modes", help="List available modes for a specific display.")
    p_modes.add_argument("display_id", help="The ID of the display.")
    p_modes.add_argument("--aspect-ratio", action="store_true", help="Only show modes that match the current aspect ratio.")
    p_modes.set_defaults(func=list_modes)

    p_set = subparsers.add_parser("set", help="Set the resolution for a specific display.")
    p_set.add_argument("display_id", help="The ID of the display.")
    p_set.add_argument("width", help="The desired width.")
    p_set.add_argument("height", help="The desired height.")
    p_set.add_argument("--refresh", help="Optional: The desired refresh rate (Hz).")
    p_set.set_defaults(func=set_mode)
    
    p_current = subparsers.add_parser("current", help="Show the current resolution of a display.")
    p_current.add_argument("display_id", nargs="?", default=None, help="The ID of the display (defaults to the main display).")
    p_current.set_defaults(func=show_current)

    args = parser.parse_args()
    args.func(args)
