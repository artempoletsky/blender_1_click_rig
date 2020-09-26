import bpy
import re
from . import preferences
import os

from . import map_bones

oops = bpy.ops.object

class MappingEntry(bpy.types.PropertyGroup):
    bone_from: bpy.props.StringProperty()
    bone_to: bpy.props.StringProperty()

mappings = {
    'palm': r'(?i)(carpal|palm)',
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
    res = re.findall('(^l[A-Z])', name)
    if res:
        return 'l'
    res = re.findall('(?i)([\._-]r|right)', name)
    if res:
        return 'r'
    res = re.findall('(^r[A-Z])', name)
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

class CreateMappingOperator(bpy.types.Operator):
    """Select two armatures. And set relations between bones."""
    bl_idname = "object.ocr_create_mapping"
    bl_label = "Create mapping"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == 'VIEW_3D'
            and len(context.selected_objects) == 2
            and context.view_layer.objects.active
            and context.object.mode == 'OBJECT')

    def execute(self, context):
        selected = list(context.selected_objects)
        active = context.view_layer.objects.active
        selected.remove(active)

        # print(active.name, selected[0].name)
        bones1 = active.data.bones
        bones2 = selected[0].data.bones

        names1 = [bone.name for bone in bones1]
        names2 = [bone.name for bone in bones2]
        ui = context.window_manager.one_click_rig_ui
        ui.edit_mapping = True
        ui.new_mapping_name = 'new_mapping_name'
        mapping_entries = ui.mapping_entries
        mapping_entries.clear()

        for name in names1:
            entry = mapping_entries.add()
            entry.bone_from = name
            entry.bone_to = try_match_bone(name, names2) or ''


        return {'FINISHED'}


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
    bl_idname = "object.ocr_save_mapping"
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
    bl_idname = "object.ocr_remove_mapping"
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


class RenameArmatureOperator(bpy.types.Operator):
    """Rename armature by mapping"""
    bl_idname = "armature.ocr_rename_armature"
    bl_label = "Rename armature"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == 'VIEW_3D'
            and context.view_layer.objects.active)

    def execute(self, context):
        ui = context.window_manager.one_click_rig_ui
        mapping = map_bones.BoneMapping(ui.active_mapping, ui.rename_reverse)
        mapping.rename_armature(context.object.data)
        return {'FINISHED'}

class AddPrefixOperator(bpy.types.Operator):
    """Add prefix"""
    bl_idname = "armature.ocr_add_prefix"
    bl_label = "Add prefix"
    bl_options = {'REGISTER', 'UNDO'}

    prefix: bpy.props.StringProperty(default = 'DEF-')

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == 'VIEW_3D'
            and context.view_layer.objects.active)

    def execute(self, context):
        oops.mode_set(mode = 'EDIT')
        for bone in context.object.data.edit_bones:
            bone.name = self.prefix + bone.name
        return {'FINISHED'}

class RemovePrefixOperator(bpy.types.Operator):
    """Remove prefix"""
    bl_idname = "armature.ocr_remove_prefix"
    bl_label = "Remove prefix"
    bl_options = {'REGISTER', 'UNDO'}

    prefix: bpy.props.StringProperty(default = 'DEF-')

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == 'VIEW_3D'
            and context.view_layer.objects.active)

    def execute(self, context):
        oops.mode_set(mode = 'EDIT')
        for bone in context.object.data.edit_bones:
            bone.name = re.sub('^'+self.prefix, '', bone.name)
        return {'FINISHED'}




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
    rename_reverse: bpy.props.BoolProperty(
        name = "Reverse",
        default = False
        )


class OCR_PT_BoneMappingsPanel(bpy.types.Panel):
    """
    Addon panel
    """
    bl_label = '1 click rig. Bone mappings'
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
        col.operator('object.ocr_save_mapping', text = 'Save mapping')
        return

    def draw(self, context):

        layout = self.layout
        col = layout.column()
        ui = context.window_manager.one_click_rig_ui

        col.prop(ui, 'active_mapping')
        col.prop(ui, "edit_mapping", toggle=True)
        col.operator("object.ocr_remove_mapping", text = 'Remove mapping')
        col.operator("object.ocr_create_mapping")

        if ui.edit_mapping:
            self.draw_mapping(col, ui)
        else:
            col.separator()
            row = col.row()
            row.operator("armature.ocr_rename_armature")
            row.prop(ui, 'rename_reverse')
            col.separator()
            row = col.row()
            row.operator("armature.ocr_add_prefix")
            row.operator("armature.ocr_remove_prefix")
            # props.name = ui.active_mapping
