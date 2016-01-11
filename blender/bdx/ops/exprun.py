import os
import bpy
import subprocess
from .. import utils as ut


class BdxExpRun(bpy.types.Operator):
    """Export scenes to .bdx files, and run the BDX simulation"""
    bl_idname = "object.bdxexprun"
    bl_label = "Export and Run"

    def execute(self, context):
        j = os.path.join

        proot = ut.project_root()
        sroot = ut.src_root()
        asset_dir = j(proot, "android", "assets", "bdx")
        prof_scene_name = "__Profiler"

        # Check if profiler scene exists:
        bdx_scenes_dir = j(asset_dir, "scenes")
        no_profile_bdx = prof_scene_name + ".bdx" not in os.listdir(bdx_scenes_dir)
        show_framerate_profile = bpy.context.scene.game_settings.show_framerate_profile
        export_profile_scene = show_framerate_profile and no_profile_bdx
        
        if export_profile_scene:
        
            # Append profiler scene from default blend file:
            prof_blend_name = "profiler.blend"
            prof_scene_path = j(prof_blend_name, "Scene", prof_scene_name)
            prof_scene_dir = j(ut.gen_root(), prof_blend_name, "Scene", "")

            bpy.ops.wm.append(filepath=prof_scene_path, directory=prof_scene_dir, filename=prof_scene_name)

        # Save-out internal java files
        saved_out_files = ut.save_internal_java_files(sroot)

        # Clear inst dir (files generated by export_scene)
        inst = j(ut.src_root(), "inst")
        if os.path.isdir(inst):
            inst_files = ut.listdir(inst);
            for f in inst_files:
                os.remove(f)
        else:
            os.mkdir(inst)

        # Export scenes:
        for scene in bpy.data.scenes:
            file_name =  scene.name + ".bdx"
            file_path = j(asset_dir, "scenes", file_name)

            bpy.ops.export_scene.bdx(filepath=file_path, scene_name=scene.name, exprun=True)

        if export_profile_scene:
        
            # Remove temporal profiler scene:
            bpy.data.scenes.remove(bpy.data.scenes[prof_scene_name])

        # Modify relevant files:
        bdx_app = j(sroot, "BdxApp.java")

        # - BdxApp.java
        new_lines = []
        for scene in bpy.data.scenes:
            class_name = ut.str_to_valid_java_class_name(scene.name)
            if os.path.isfile(j(sroot, "inst", class_name + ".java")):
                inst = "new " + ut.package_name() + ".inst." + class_name + "()"
            else:
                inst = "null"

            new_lines.append('("{}", {});'.format(scene.name, inst))


        put = "\t\tScene.instantiators.put"

        ut.remove_lines_containing(bdx_app, put)

        ut.insert_lines_after(bdx_app, "Scene.instantiators =", [put + l for l in new_lines])

        scene = bpy.context.scene
        ut.replace_line_containing(bdx_app, "scenes.add", '\t\tBdx.scenes.add(new Scene("'+scene.name+'"));');

        ut.remove_lines_containing(bdx_app, "Bdx.firstScene = ")
        ut.insert_lines_after(bdx_app, "scenes.add", ['\t\tBdx.firstScene = "'+scene.name+'";'])

        # - DesktopLauncher.java
        rx = str(scene.render.resolution_x)
        ry = str(scene.render.resolution_y)

        dl = j(ut.src_root("desktop", "DesktopLauncher.java"), "DesktopLauncher.java")
        ut.set_file_var(dl, "title", '"'+ut.project_name()+'"')
        ut.set_file_var(dl, "width", rx)
        ut.set_file_var(dl, "height", ry)

        # - AndroidLauncher.java
        al = j(ut.src_root("android", "AndroidLauncher.java"), "AndroidLauncher.java")
        ut.set_file_var(al, "width", rx)
        ut.set_file_var(al, "height", ry)

        # Run engine:
        context.window.cursor_set("WAIT")

        gradlew = "gradlew"
        if os.name != "posix":
            gradlew += ".bat"
        
        print(" ")
        print("------------ BDX START --------------------------------------------------")
        print(" ")
        try:
            subprocess.check_call([os.path.join(proot, gradlew), "-p", proot, "desktop:run"])
        except subprocess.CalledProcessError:
            self.report({"ERROR"}, "BDX BUILD FAILED")
        print(" ")
        print("------------ BDX END ----------------------------------------------------")
        print(" ")

        # Delete previously saved-out internal files
        for fp in saved_out_files:
            os.remove(fp)

        context.window.cursor_set("DEFAULT")
        
        return {'FINISHED'}


def register():
    bpy.utils.register_class(BdxExpRun)


def unregister():
    bpy.utils.unregister_class(BdxExpRun)
