import bpy

bl_info = {
    "name": "Draw Seam",
    "category": "Object > Special > Draw Seam",
}


# Toggle displaying wire
# It's inside of the special menu in object mode
# previously it was q but I changed it
# The structure is not difficult at all
class DrawSeam(bpy.types.Operator):
    """Draw Seam"""                     # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "object.drawseam"       # unique identifier for buttons and menu items to reference.
    bl_label = "DrawSeam"              # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}   # enable undo for the operator.

    # You need this class method sentence for class methods
    @classmethod
    # what's cls?
    # anyway, with this, you can disable the menu
    def poll(cls, context):
        # Object has to mesh
        obj = bpy.context.active_object
        return bool(obj) & (obj.type == 'MESH') & (bpy.context.mode == 'OBJECT')

    def execute(self, context):  # execute() is called by blender when running the operator.
        obj = bpy.context.active_object

        bevel = [b for b in obj.modifiers if isinstance(b, bpy.types.BevelModifier)]
        if len(bevel) != 0:
            m = bevel[0]

            # Bevelを移動
            while obj.modifiers[0].name != m.name:
                bpy.ops.object.modifier_move_up(modifier=m.name)

            # Materialを追加
            mat = bpy.data.materials['Temp']
            bpy.ops.object.material_slot_add()
            obj.material_slots[obj.material_slots.__len__() - 1].material = mat

            # 調整
            m.segments = 2
            m.material = obj.material_slots.__len__() - 1
            m.limit_method = 'WEIGHT'
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier=m.name)

            # スケールをリセット
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

            # エディットモードへ
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')

            bpy.ops.mesh.select_all(action='DESELECT')

            bpy.context.object.active_material_index = obj.material_slots.__len__() - 1

            print(obj.material_slots.__len__() - 1)

            bpy.ops.object.material_slot_select()
            bpy.ops.mesh.hide(unselected=True)
            bpy.ops.mesh.mark_seam(clear=True)

            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
            bpy.ops.mesh.select_less()
            bpy.ops.mesh.mark_seam(clear=False)

            bpy.ops.mesh.reveal()
            bpy.ops.mesh.select_all(action='SELECT')

            bpy.ops.uv.unwrap(method='ANGLE_BASED', use_subsurf_data=True, margin=0.001)
            bpy.ops.object.mode_set(mode='OBJECT')

            bpy.ops.object.material_slot_remove()

        else:
            print("Doesn't have Bevel Modifier")

        return {'FINISHED'}  # this lets blender know the operator finished successfully.


# for menu to draw
# You can change this to Lambda
def menu_draw(self, context):
    self.layout.operator("object.drawseam")


# registering class and menu
def register():
    bpy.utils.register_class(DrawSeam)
    bpy.types.VIEW3D_MT_object_specials.append(menu_draw)


# Unregistering class and menu
def unregister():
    bpy.utils.unregister_class(DrawSeam)
    bpy.types.VIEW3D_MT_object_specials.remove(menu_draw)


# This allows you to run the script directly from blenders text editor
# to test the addon without having to install it.
if __name__ == "__main__":
    register()

# Debug ---------------------------------------------------------------------
debug = 1
if debug == 1:
    try:
        unregister()
    except:
        pass
    finally:
        register()
# ---------------------------------------------------------------------------
