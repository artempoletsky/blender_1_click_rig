import json
import bpy
import os
import re

mappings_folder = os.path.dirname(os.path.realpath(__file__)) + '/mappings/'
anim_mappings_folder = os.path.dirname(os.path.realpath(__file__)) + '/animation_mappings/'

def get_anim_mappings(self, context):
    # print(os.listdir(mappings_folder))
    names = [re.sub('.json$', '', name) for name in os.listdir(anim_mappings_folder) if name.endswith('.json')]
    return [(name, name, name) for name in names]

def get_mappings(self, context):
    # print(os.listdir(mappings_folder))
    names = [re.sub('.json$', '', name) for name in os.listdir(mappings_folder) if name.endswith('.json')]
    return [(name, name, name) for name in names]

def get_mapping_file(mapping, anim = False):
    return (anim_mappings_folder if anim else mappings_folder) + mapping + '.json'

def has_mapping(mapping, anim = False):
    return os.path.exists(get_mapping_file(mapping, anim = anim))

def load_mapping(mapping, anim = False):
    file = get_mapping_file(mapping, anim = anim)
    m = {}
    with open(file) as json_file:
        data = json.load(json_file)
    return data

def save_mapping(mapping, data, anim = False):
    file = get_mapping_file(mapping, anim = anim)
    with open(file, 'w') as outfile:
        json.dump(data, outfile, indent=2, separators=(',', ': '))

def remove_mapping(mapping, anim = False):
    os.remove(get_mapping_file(mapping, anim = anim))

class BoneMapping(object):
    """Map bones names from different rigs"""

    def __init__(self, name, reverse):
        data = load_mapping(name)
        mapping = {}
        for key, value in data:
            if reverse:
                mapping[value] = key
            else:
                mapping[key] = value
        self.mapping = mapping

    def get_name(self, name, safe = True):
        if name in self.mapping:
            return self.mapping[name]
        if safe:
            return name
        else:
            return None

    def rename_armature(self, armature):
        bpy.ops.object.mode_set(mode = 'EDIT')
        for bone in armature.edit_bones:
            bone.name = self.get_name(bone.name)
