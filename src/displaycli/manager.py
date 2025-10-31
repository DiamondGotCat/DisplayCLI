import sys
import Quartz
from Cocoa import NSScreen
from math import gcd

class DisplayManager:

    def get_online_displays(self):
        err, display_ids, count = Quartz.CGGetOnlineDisplayList(0, None, None)
        if err != Quartz.kCGErrorSuccess:
            raise RuntimeError("Failed to get online display list")
        return [self._get_display_info(display_id) for display_id in display_ids]

    def get_main_display_id(self):
        return Quartz.CGMainDisplayID()

    def _get_display_info(self, display_id):
        is_main = Quartz.CGDisplayIsMain(display_id)
        name = "Unknown Display"
        for screen in NSScreen.screens():
            screen_info = screen.deviceDescription()
            if screen_info.get("NSScreenNumber") == display_id:
                if hasattr(screen, 'localizedName'):
                    name = screen.localizedName()
                else:
                    name = screen_info.get("NSDeviceDescriptionNameKey", "Unknown Display")
                break
        current_mode = self.get_current_mode(display_id)
        return {"id": display_id, "name": name, "is_main": is_main, "current_mode": current_mode}

    def get_display_modes(self, display_id):
        modes_ref = Quartz.CGDisplayCopyAllDisplayModes(display_id, None)
        if not modes_ref: return []
        modes = []
        for mode in modes_ref:
            if not mode: continue
            logical_width = Quartz.CGDisplayModeGetWidth(mode)
            logical_height = Quartz.CGDisplayModeGetHeight(mode)
            pixel_width = Quartz.CGDisplayModeGetPixelWidth(mode)
            pixel_height = Quartz.CGDisplayModeGetPixelHeight(mode)
            refresh_rate = Quartz.CGDisplayModeGetRefreshRate(mode)
            is_hidpi = pixel_width > logical_width or pixel_height > logical_height
            scale = int(pixel_width / logical_width) if is_hidpi and logical_width > 0 else 1
            modes.append({
                "width": logical_width, "height": logical_height,
                "pixel_width": pixel_width, "pixel_height": pixel_height,
                "refresh_rate": round(refresh_rate, 2),
                "hidpi": is_hidpi, "scale": scale, "mode_ref": mode
            })
        unique_modes = []
        seen = set()
        for mode in sorted(modes, key=lambda x: (x['width'], x['height'], x['refresh_rate']), reverse=True):
            key = (mode['width'], mode['height'], mode['refresh_rate'])
            if key not in seen:
                unique_modes.append(mode)
                seen.add(key)
        return unique_modes

    def get_current_mode(self, display_id):
        current_mode_ref = Quartz.CGDisplayCopyDisplayMode(display_id)
        if not current_mode_ref: return None
        logical_width = Quartz.CGDisplayModeGetWidth(current_mode_ref)
        logical_height = Quartz.CGDisplayModeGetHeight(current_mode_ref)
        pixel_width = Quartz.CGDisplayModeGetPixelWidth(current_mode_ref)
        pixel_height = Quartz.CGDisplayModeGetPixelHeight(current_mode_ref)
        refresh_rate = Quartz.CGDisplayModeGetRefreshRate(current_mode_ref)
        is_hidpi = pixel_width > logical_width or pixel_height > logical_height
        scale = int(pixel_width / logical_width) if is_hidpi and logical_width > 0 else 1
        return {
            "width": logical_width, "height": logical_height,
            "pixel_width": pixel_width, "pixel_height": pixel_height,
            "refresh_rate": round(refresh_rate, 2),
            "hidpi": is_hidpi, "scale": scale
        }

    def find_mode(self, display_id, width, height, refresh_rate=0):
        all_modes = self.get_display_modes(display_id)
        best_match = None
        for mode in all_modes:
            if mode['width'] == width and mode['height'] == height:
                if refresh_rate > 0:
                    if abs(mode['refresh_rate'] - refresh_rate) < 0.1:
                        return mode['mode_ref']
                elif best_match is None:
                    best_match = mode['mode_ref']
        return best_match

    def set_display_mode(self, display_id, mode_ref):
        config_ref = None
        result = Quartz.CGBeginDisplayConfiguration(None)

        if isinstance(result, tuple) and len(result) == 2:
            if isinstance(result[0], int):
                err, config_ref = result
            else:
                config_ref, err = result
        elif 'CGDisplayConfigRef' in str(type(result)):
            config_ref = result
            err = Quartz.kCGErrorSuccess
        else:
            err = int(result)
            config_ref = None

        if err != Quartz.kCGErrorSuccess:
            raise RuntimeError(f"Failed to begin display configuration. Error code: {err}")
        
        if config_ref is None:
            raise RuntimeError("Failed to begin display configuration: received null config reference.")

        err = Quartz.CGConfigureDisplayWithDisplayMode(config_ref, display_id, mode_ref, None)
        if err != Quartz.kCGErrorSuccess:
            Quartz.CGCancelDisplayConfiguration(config_ref)
            raise RuntimeError(f"Failed to configure display mode. Error code: {err}")

        err = Quartz.CGCompleteDisplayConfiguration(config_ref, Quartz.kCGConfigurePermanently)
        if err != Quartz.kCGErrorSuccess:
            Quartz.CGCancelDisplayConfiguration(config_ref)
            raise RuntimeError(f"Failed to complete display configuration. Error code: {err}")

    @staticmethod
    def get_aspect_ratio(width, height):
        if height == 0: return 0, 0
        common_divisor = gcd(width, height)
        return width // common_divisor, height // common_divisor
