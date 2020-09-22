
import bpy, _thread, time
import rna_keymap_ui
from bpy.app.translations import contexts as i18n_contexts
from bpy.app.handlers import persistent


class RigToolsPreferencesAddKeymapOperator(bpy.types.Operator):
    """Add key map item"""
    bl_idname = "boilerpate_preferences.keyitem_add"
    bl_label = "Add Key Map Item"

    def execute(self, context):
        km = context.keymap

        kmi = km.keymap_items.new("object.empty_operator", 'A', 'PRESS')
        context.preferences.is_dirty = True
        return {'FINISHED'}



user_prefs = bpy.context.preferences.themes[0].view_3d

class RigToolsPreferencesDefaults():
    hello = "Hello world!"

defaults = RigToolsPreferencesDefaults()

class RigToolsPreferences(bpy.types.AddonPreferences):
    bl_idname = 'one_click_rig'

    tabs : bpy.props.EnumProperty(name="Tabs",
        items = [("GENERAL", "General", ""),
            ("KEYMAPS", "Keymaps", ""),
            ("COLORS", "Colors", ""),],
        default="GENERAL")

    hello : bpy.props.StringProperty(name = "Hello text", default = defaults.hello)

    is_installed : bpy.props.BoolProperty(name = "Is installed", default = False)
    version : bpy.props.StringProperty(name = "Version", default = '(0, 0, 0)')


    def draw(self, context):
        layout = self.layout

        # # TAB BAR
        # row = layout.row()
        # row.prop(self, "tabs", expand=True)
        #
        # box = layout.box()
        #
        # if self.tabs == "GENERAL":
        #     self.draw_general(box)
        #
        # elif self.tabs == "COLORS":
        #     self.draw_colors(box)
        #
        # elif self.tabs == "KEYMAPS":
        #     self.draw_keymaps(box)

    def draw_general(self, layout):
        row = layout.row()
        col = row.column()

        col.label(text="General settings:")
        col.prop(self, "hello")
        col.separator()

    def draw_colors(self, layout):
        layout.use_property_split = True
        flow = layout.grid_flow(row_major=False, columns=0, even_columns=True, even_rows=False, align=False)

        # flow.prop(self, "cutting_edge")

    def draw_keymaps(self, layout):
        row = layout.row()
        col = row.column()

        col.label(text="Keymap settings:")

        wm = bpy.context.window_manager
        kc = wm.keyconfigs.user
        km = kc.keymaps['Object Mode']
        col.context_pointer_set("keymap", km)
        for kmi in km.keymap_items:
            if is_addon_keymap(kmi):
                rna_keymap_ui.draw_kmi(["ADDON", "USER", "DEFAULT"], kc, km, kmi, col, 0)
        subcol = col.split(factor=0.2).column()
        # subcol.operator(RigToolsPreferencesAddKeymapOperator.bl_idname, text="Add New", text_ctxt=i18n_contexts.id_windowmanager, icon='ADD')

from bl_keymap_utils.io import keyconfig_init_from_data

def get_prefs():
    prefs = get_addon_prefs()
    if prefs:
        return prefs
    return RigToolsPreferencesDefaults()

def get_addon_prefs():
    addons_prefs = bpy.context.preferences.addons
    id = RigToolsPreferences.bl_idname
    return addons_prefs[id].preferences if id in addons_prefs else None

def is_addon_keymap(kmi):
    return kmi.idname in {'paint.toggle_weight_paint',}

# OVERRIDE DEFAULT KEYMAPS
@persistent
def on_load():
    # print('on_load')
    return
    # keyconfigs = bpy.context.window_manager.keyconfigs
    # kmis = keyconfigs.default.keymaps['Mesh'].keymap_items
    # i = 0
    # while not 'mesh.knife_tool' in kmis and i < 100:
    #     time.sleep(.1)
    #     i += 1
    # print(i)
    # kmis['mesh.knife_tool'].alt = True


def register_keymaps():

    keyconfigs = bpy.context.window_manager.keyconfigs
    # kc_defaultconf = keyconfigs.default
    kc_addonconf = keyconfigs.addon

    keyconfig_init_from_data(kc_addonconf, [
         (
            "Weight Paint",
            {"space_type": 'EMPTY', "region_type": 'WINDOW'},
            {"items": [
                ("paint.toggle_weight_paint", {"type": 'X', "value": 'PRESS'},
                 {"properties": [],
                  "active":True}),
            ]},
        ),
    ])

    # OVERRIDE DEFAULT KEYMAPS

    # kmis = keyconfigs.default.keymaps['Mesh'].keymap_items
    # if 'mesh.knife_tool' in kmis:
    #     kmis['mesh.knife_tool'].alt = True
    # else:
    #     _thread.start_new_thread(on_load,())

    prefs = get_addon_prefs()
    if prefs and prefs.is_installed:
        # print('addon is installed')
        return
    # print('addon is installing')

    if prefs:
        prefs.is_installed = True

    #

def unregister_keymaps():
    keyconfigs = bpy.context.window_manager.keyconfigs
    kc_addonconf = keyconfigs.addon

    km = kc_addonconf.keymaps['Weight Paint']
    #
    for kmi in km.keymap_items:
        if is_addon_keymap(kmi):
            km.keymap_items.remove(kmi)

    # OVERRIDE DEFAULT KEYMAPS

    # kc = keyconfigs.default
    # km = kc.keymaps['Mesh']
    # km.keymap_items['mesh.knife_tool'].alt = False
    return
