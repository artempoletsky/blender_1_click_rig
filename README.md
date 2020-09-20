#  1 click rig
A collection of rig operators for Blender.

# Unreal operators

## Convert UE character to rigify

A combination of 3 operators:

1. Generate metarig from armature
2. Rigify generate rig
3. Bind rigify rig to armature

Usage: select unreal armature and run operator

## Generate metarig from armature

Creates rigify metarig.
Usage: select unreal armature and run operator

## Bind rigify rig to armature

Copies unreal armature to rigify rig and makes constraints.
Usage: 
1. select unreal armature
2. select rigify rig. Rig **MUST** be an active element. 
3. run operator. 

Original unreal armature will be copied on 24 layer of rigify rig. 
