import re

with open('ui/batch_mode.py', 'r') as f:
    text = f.read()

target = """            'tab_exclusion_stringer': getattr(self, 'safe_float')(getattr(self, 'tab_exclusion_stringer', tk.StringVar(value="10.0")), 10.0),
            'tab_exclusion_le_te': getattr(self, 'safe_float')(getattr(self, 'tab_exclusion_le_te', tk.StringVar(value="30.0")), 30.0),
        }"""

replacement = """            'tab_exclusion_stringer': getattr(self, 'safe_float')(getattr(self, 'tab_exclusion_stringer', tk.StringVar(value="10.0")), 10.0),
            'tab_exclusion_le_te': getattr(self, 'safe_float')(getattr(self, 'tab_exclusion_le_te', tk.StringVar(value="30.0")), 30.0),
            'cam_tool_dia': getattr(self, 'safe_float')(getattr(self, 'cam_tool_dia', tk.StringVar(value="2.0")), 2.0),
            'cam_mat_thick': getattr(self, 'safe_float')(getattr(self, 'cam_mat_thick', tk.StringVar(value="10.0")), 10.0),
            'cam_safe_z': getattr(self, 'safe_float')(getattr(self, 'cam_safe_z', tk.StringVar(value="5.0")), 5.0),
            'cam_feed_rate': getattr(self, 'safe_float')(getattr(self, 'cam_feed_rate', tk.StringVar(value="2000")), 2000.0),
            'cam_spindle_speed': getattr(self, 'safe_float')(getattr(self, 'cam_spindle_speed', tk.StringVar(value="12000")), 12000.0),
            'cam_extra_depth': getattr(self, 'safe_float')(getattr(self, 'cam_extra_depth', tk.StringVar(value="0.5")), 0.5),
            'cam_milling_dir': getattr(self, 'cam_milling_dir', tk.StringVar(value="Conventional (Outer CW)")).get(),
        }"""

if target in text:
    text = text.replace(target, replacement)
    with open('ui/batch_mode.py', 'w') as f:
        f.write(text)
    print("Successfully patched batch_mode.py")
else:
    print("Target string not found!")

