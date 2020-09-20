import bpy
from . import preferences
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
import json

class RenameBonesOperator(bpy.types.Operator, ImportHelper):
    """Rename bones"""
    bl_idname = "armature.rename_bones_by_mapping"
    bl_label = "Rename bones by mapping file"
    bl_options = {'REGISTER', 'UNDO'}

    # example_prop: bpy.props.BoolProperty(name="Example prop", default=False)

    # ImportHelper mixin class uses this
    filename_ext = ".json"

    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    reverse: BoolProperty(
        name="Reverse key-value pair",
        default=False,
    )
    #
    # type: EnumProperty(
    #     name="Example Enum",
    #     description="Choose between two items",
    #     items=(
    #         ('OPT_A', "First Option", "Description one"),
    #         ('OPT_B', "Second Option", "Description two"),
    #     ),
    #     default='OPT_A',
    # )

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == 'VIEW_3D'
            # and len(context.selected_objects) > 0
            and context.view_layer.objects.active
            and context.object.type == 'ARMATURE'
            and (context.object.mode == 'EDIT' or
            context.object.mode == 'POSE'))

    def execute(self, context):


        try:
            with open(self.filepath) as json_file:
                data = json.load(json_file)
            # print(data)
            # print(234234)
            # print(self.filepath)
            # f = open(self.filepath)
            # data = f.read()
            # f.close()
        except Exception as e:
            self.report({'ERROR'}, 'File `{}` not exists'.format(self.filepath))
            return {'FINISHED'}

        mapping = {}
        for obj in data:
            for key in obj:
                val = obj[key]
                if self.reverse:
                    temp = key
                    key = val
                    val = temp
                mapping[key] = val

        bones = context.object.data.bones
        # print(len(bones))
        for bone in bones:
            if bone.name in mapping:
                key = bone.name
                val = mapping[bone.name]
                bone.name = val
                print('Renaming {} to {}'.format(key, val))

        return {'FINISHED'}

    # def invoke(self, context, event):
    #     wm = context.window_manager
    #     return wm.invoke_props_dialog(self)
