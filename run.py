import sys
import os
import bpy

blend_dir = os.path.dirname(bpy.data.filepath)
if blend_dir not in sys.path:
   sys.path.append(blend_dir)

import rig_tools
#import single_file_addon
import imp
imp.reload(rig_tools)
#imp.reload(single_file_addon)
rig_tools.register()
#single_file_addon.register()
