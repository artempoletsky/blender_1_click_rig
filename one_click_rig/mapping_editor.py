import bpy
import re
from . import preferences

from . import bl_info

class MappingEntry(bpy.types.PropertyGroup):
    bone_from: bpy.props.StringProperty()
    bone_to: bpy.props.StringProperty()

mappings = {
    'head': r'(?i)(head)',
    'neck': r'(?i)(neck)',
    'pelvis': r'(?i)(pelvis|hip)',

    'thigh': r'(?i)(thigh|leg)',
    'shin': r'(?i)(shin|calf|leg)',
    'foot': r'(?i)(foot)',
    'toe': r'(?i)(toe|ball)',

    'thumb': r'(?i)(thumb)',
    'index': r'(?i)(index)',
    'middle': r'(?i)(mid)',
    'ring': r'(?i)(ring)',
    'pinky': r'(?i)(pinky)',

    'hand': '(?i)(hand)',
    'shoulder': '(?i)(shoulder|clavicle|collar)',
    'upperarm': '(?i)(upper_arm|upperarm|shldr)',
    'forearm': '(?i)(forearm|lowerarm)',

    'breast': '(?i)(breast|pectoral)',

    'spine': '(?i)(abdomen|chest|spine|pelvis|head|neck|hip)',
}

def get_bone_type(name):
    for type, exp in mappings.items():
        res = re.findall(exp, name)
        if res:
            return type
    return None

def get_bone_index(name):
    res = re.findall('(\d+)', name)
    if not res:
        return None
    return int(res[-1])

def get_bone_side(name):
    res = re.findall('(?i)([\._-]l|left)', name)
    if res:
        return 'l'
    res = re.findall('(?i)([\._-]r|right)', name)
    if res:
        return 'r'
    return None

def try_match_bone(name, names_to_search):

    index = get_bone_index(name)
    type = get_bone_type(name)
    side = get_bone_side(name)

    if not type:
        return None

    best_name = None
    for n in names_to_search:
        bone_type = get_bone_type(n)
        bone_side = get_bone_side(n)
        if bone_type == type and bone_side == side:
            bone_index = get_bone_index(n)
            if index != None and bone_index == index:
                return n

            if not best_name:
                best_name = n

    return best_name

class MappingEditorOperator(bpy.types.Operator):
    """Select two armatures. And set relations between bones."""
    bl_idname = "object.ocr_mapping_editor"
    bl_label = "Mapping editor"
    bl_options = {'REGISTER', 'UNDO'}

    example_prop: bpy.props.BoolProperty(name="Example prop", default=False)

    entries: bpy.props.CollectionProperty(type=MappingEntry)
    # names2: bpy.props.PointerProperty(type=Array)

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == 'VIEW_3D'
            and len(context.selected_objects) > 0
            and context.view_layer.objects.active
            and context.object.mode == 'OBJECT')

    def execute(self, context):
        self.prefs = preferences.get_prefs()

        self.report({'INFO'}, self.prefs.hello)
        return {'FINISHED'}

    def invoke(self, context, event):
        print(bl_info)
        selected = list(context.selected_objects)
        active = context.view_layer.objects.active
        selected.remove(active)

        # print(active.name, selected[0].name)
        bones1 = active.data.bones
        bones2 = selected[0].data.bones

        names1 = [bone.name for bone in bones1]
        names2 = [bone.name for bone in bones2]
        for name in names1:
            entry = self.entries.add()
            entry.bone_from = name
            entry.bone_to = try_match_bone(name, names2) or ''
            # self.names1.append(bone.name)


        # self.matches = [ for name in self.names1]
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width = 800)

    def draw(self, context):
        layout = self.layout

        # col.label(text="Custom Interface!")

        main_rows = layout.row()

        # print(get_bone_type(bones1[0].name))
        # print(get_bone_type(bones2[0].name))
        i = 0
        for e in self.entries:
            if i % 40 == 0:
                col = main_rows.column()
                main_rows.separator()

            row = col.row()
            subcol = row.column()
            # subcol.label(text = name1)
            subcol.prop(e, 'bone_from', text = '')
            subcol = row.column()
            subcol.prop(e, 'bone_to',  text = '')

            i += 1
