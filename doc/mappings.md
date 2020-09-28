# Mappings and armature renaming

One Click Rig uses bone mapping system iternaly, and you can use it to rename bones. You can create and edit your own mappings for different skeletons.

## Rename armature by mapping

Usage: Select an armature. Choose the mapping and run operator. 

Bones in the mapping will be renamed according to the selected mapping.

Props:
1. Revese - rename backwards. E.g. if you choose uemannequin_rigify mapping, it will rename rigify names to UE names. 

If bone name not in the mapping, the operator will not rename it. 

## Add/Remove prefix

Used mostly internaly. 

But you can fix with it some Mixamo characters. Some of them have redundant prefixes in bones, for example `Boy:Head`. If you keep them, other operators won't work.

Props: 
1. Prefix - prefix to add/remove.

## Create a new mapping

To create a new mapping select two armatures. For example default rigify metarig, and armature from makehuman character. `From` armature must be active. 

usualy you need to create `From` *{armature_type}* `To` Rigify mappings.

Press the `New mapping` button.

The script will try to autofill table with names.

Check names and fill empty spaces. Usually autofill have bad results for spines and limbs and good for fingers. 
