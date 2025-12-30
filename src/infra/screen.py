import Quartz
from src.domain.coordinate import ScreenInfo
from typing import List

class MacScreenManager:
    @staticmethod
    def get_all_screens() -> List[ScreenInfo]:
        """
        Fetch all connected displays using Quartz (CoreGraphics).
        Returns a list of ScreenInfo objects with precise bounds and scale factors.
        """
        # Get list of active display IDs
        max_displays = 32
        error, displays, count = Quartz.CGGetActiveDisplayList(max_displays, None, None)
        
        if error != 0:
            raise RuntimeError(f"Failed to get display list: {error}")
            
        screen_infos = []
        
        for i in range(count):
            display_id = displays[i]
            
            # 1. Logical Bounds (Points)
            bounds = Quartz.CGDisplayBounds(display_id)
            x = int(bounds.origin.x)
            y = int(bounds.origin.y)
            width_pt = int(bounds.size.width)
            height_pt = int(bounds.size.height)
            
            # 2. Physical Dimensions (Pixels)
            # CGDisplayPixelsWide/High returns the *current mode* physical pixels
            width_px = Quartz.CGDisplayPixelsWide(display_id)
            height_px = Quartz.CGDisplayPixelsHigh(display_id)
            
            # 3. Calculate Scale Factor
            # Avoid division by zero
            if width_pt > 0:
                scale_x = width_px / width_pt
            else:
                scale_x = 1.0
                
            # For simplicity, we assume square pixels, so scale_x ~= scale_y
            
            info = ScreenInfo(
                x=x,
                y=y,
                width=width_pt,
                height=height_pt,
                scale_factor=round(scale_x, 2) # Round to nearest reasonable scale (1.0, 2.0, 1.5)
            )
            screen_infos.append(info)
            
        return screen_infos

if __name__ == "__main__":
    # verification script
    print("Detecting Screens via Quartz...")
    screens = MacScreenManager.get_all_screens()
    for idx, s in enumerate(screens):
        print(f"Screen {idx}: Pos({s.x},{s.y}) Size({s.width}x{s.height}) Scale({s.scale_factor})")
        print(f"   -> Logical Right/Bottom: ({s.logical_right}, {s.logical_bottom})")
