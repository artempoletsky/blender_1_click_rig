import bpy
import re
from . import preferences
import os

from . import map_bones

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

# def load_active_mapping(ui)


class MappingRemoveEntryOperator(bpy.types.Operator):
    """Remove entry"""
    bl_idname = "object.ocr_mapping_remove_entry"
    bl_label = "Remove entry"
    # bl_options = {'REGISTER', 'UNDO'}

    index: bpy.props.IntProperty()

    def execute(self, context):
        ui = context.window_manager.one_click_rig_ui
        mapping_entries = ui.mapping_entries
        mapping_entries.remove(self.index)
        return {'FINISHED'}


class MappingAddEntryOperator(bpy.types.Operator):
    """Add entry"""
    bl_idname = "object.ocr_mapping_add_entry"
    bl_label = "Add entry"
    # bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ui = context.window_manager.one_click_rig_ui
        mapping_entries = ui.mapping_entries
        mapping_entries.add()
        return {'FINISHED'}

class SaveMappingOperator(bpy.types.Operator):
    """Save mapping"""
    bl_idname = "object.ocr_mapping_save"
    bl_label = "Owerwrite mapping?"
    # bl_options = {'REGISTER', 'UNDO'}

    # name: bpy.props.StringProperty()

    def execute(self, context):
        ui = context.window_manager.one_click_rig_ui
        mapping_entries = ui.mapping_entries
        data = [[e.bone_from, e.bone_to] for e in mapping_entries]
        map_bones.save_mapping(ui.new_mapping_name, data)
        ui.active_mapping = ui.new_mapping_name
        return {'FINISHED'}

    def invoke(self, context, event):
        ui = context.window_manager.one_click_rig_ui
        if map_bones.has_mapping(ui.new_mapping_name):
            return context.window_manager.invoke_confirm(self, event)
        else:
            return self.execute(context)

class RemoveMappingOperator(bpy.types.Operator):
    """Remove mapping"""
    bl_idname = "object.ocr_mapping_remove"
    bl_label = "Remove mapping?"
    # bl_options = {'REGISTER', 'UNDO'}

    # name: bpy.props.StringProperty()

    def execute(self, context):
        ui = context.window_manager.one_click_rig_ui
        map_bones.remove_mapping(ui.active_mapping)
        ui.reset_active_mapping()
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)



class OCRMappingPanelProps(bpy.types.PropertyGroup):


    def update_edit_mapping(self, value):
        if value:
            self.load_active_mapping()
            self.new_mapping_name = self.active_mapping

    def update_active_mapping(self, value):
        self.update_edit_mapping(self.edit_mapping)

    def load_active_mapping(self):
        data = map_bones.load_mapping(self.active_mapping)

        self.mapping_entries.clear()
        for key, value in data:
            entry = self.mapping_entries.add()
            entry.bone_from = key
            entry.bone_to = value

    def reset_active_mapping(self):
        self.active_mapping = map_bones.get_mappings(self, None)[0][0]

    active_mapping: bpy.props.EnumProperty(
        name = "Mapping",
        description = "Saved mappings",
        items = map_bones.get_mappings,
        update = update_active_mapping,
        default = None
        )

    edit_mapping: bpy.props.BoolProperty(
        name = "Edit mapping",
        default = False,
        update = update_edit_mapping
        )

    new_mapping_name: bpy.props.StringProperty()
    mapping_entries:bpy.props.CollectionProperty(type=MappingEntry)


class OCR_PT_BoneMappingsPanel(bpy.types.Panel):
    """
    Addon panel
    """
    bl_label = 'Bone mappings'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Rigify'

    def draw_mapping(self, col, ui):
        # main_rows = layout.row()

        # print(get_bone_type(bones1[0].name))
        # print(get_bone_type(bones2[0].name))
        i = 0
        for e in ui.mapping_entries:

            row = col.row()
            subcol = row.column()
            # subcol.label(text = name1)
            subcol.prop(e, 'bone_from', text = '')
            subcol = row.column()
            subcol.prop(e, 'bone_to',  text = '')
            subcol = row.column()
            prop = subcol.operator('object.ocr_mapping_remove_entry', icon = 'X', text = '')
            prop.index = i
            # row.separator()
            # subcol.separator()

            i += 1
        col.operator('object.ocr_mapping_add_entry')
        col.separator()
        col.label(text = 'New mapping name')
        col.prop(ui, 'new_mapping_name', text = '')
        col.separator()
        col.operator('object.ocr_mapping_save', text = 'Save mapping')
        return

    def draw(self, context):

        layout = self.layout
        col = layout.column()
        ui = context.window_manager.one_click_rig_ui

        col.prop(ui, 'active_mapping')
        col.prop(ui, "edit_mapping", toggle=True)
        col.operator("object.ocr_mapping_remove", text = 'Remove mapping')

        if ui.edit_mapping:
            self.draw_mapping(col, ui)
