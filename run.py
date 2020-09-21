import sys
import os
import bpy

blend_dir = os.path.dirname(bpy.data.filepath)
if blend_dir not in sys.path:
   sys.path.append(blend_dir)

import one_click_rig
#import single_file_addon
import importlib
importlib.reload(one_click_rig)
#imp.reload(single_file_addon)
one_click_rig.register()
#single_file_addon.register()
