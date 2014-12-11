import os
import bpy
import shutil
from .. import utils as ut

j = os.path.join

class CreateBdxProject(bpy.types.Operator):
    """Create BDX project"""
    bl_idname = "scene.create_bdx_project"
    bl_label = "Create BDX project"

    def create_libgdx_project(self):
        sc = bpy.context.scene

        if (not sc.bdx_android_sdk.strip()):
            sc.bdx_android_sdk = j(os.getcwd(), "android-sdk")

        absp = bpy.path.abspath

        fmt = {"program": j(ut.gen_root(), "gdx-setup.jar"),
               "dir": j(absp(sc.bdx_base_path), sc.bdx_dir_name),
               "name": sc.bdx_proj_name,
               "package": sc.bdx_java_pack,
               "mainClass": "BdxApp",
               "sdkLocation": absp(sc.bdx_android_sdk)}

        cmd = 'java -jar "{program}" \
                --dir "{dir}" \
                --name "{name}" \
                --package {package} \
                --mainClass {mainClass} \
                --sdkLocation "{sdkLocation}"'

        error = os.system(cmd.format(**fmt))

        if error:
            raise Exception("Failed to create LibGDX project")

        ut.proot = fmt["dir"]

    def create_android_assets_bdx(self):
        """Creates the bdx directory structure in android/assets"""
        bdx = j(ut.project_root(), "android", "assets", "bdx")
        os.mkdir(bdx)
        os.mkdir(j(bdx, "scenes"))
        textures = j(bdx, "textures")
        os.mkdir(textures)
        os.mkdir(j(bdx, "audio"))
        os.mkdir(j(bdx, "fonts"))

        for png in ut.listdir_fullpath(ut.gen_root(), ".png"):
            shutil.copy(png, textures);

    def create_blender_assets(self):
        """
        Creates the blender directory in the root project,
        for .blends, and other assorted production resources.

        """
        blender = j(ut.project_root(), "blender")
        os.mkdir(blender)
        
        shutil.copy(j(ut.gen_root(), "game.blend"), blender)

    def replace_build_gradle(self):
        """Replaces the build.gradle file with a version that includes BDX dependencies"""
        bdx_build_gradle = j(ut.gen_root(), "build.gradle")
        gdx_build_gradle = j(ut.project_root(), "build.gradle")
        shutil.copy(bdx_build_gradle, gdx_build_gradle)

        sc = bpy.context.scene
        ut.set_file_var(gdx_build_gradle, "appName", "'{}'".format(sc.bdx_proj_name))

    def set_android_sdk_build_tools_version(self):
        # Get latest available version:
        def strv_to_intv(strv):
            h, t, o = strv.split('.')
            return int(h) * 100 + int(t) * 10 + int(o)
        sc = bpy.context.scene

        build_tools_dir = j(sc.bdx_android_sdk, "build-tools")

        if os.path.exists(build_tools_dir):
            version = sorted(os.listdir(build_tools_dir), key=strv_to_intv)[-1]
        else:
            version = "20.0.0"

        # Set corresponding line in android/build.gradle:
        android_build_gradle = j(ut.project_root(), "android", "build.gradle")
        new_line = '    buildToolsVersion "'+version+'"'
        ut.replace_line_containing(android_build_gradle, "buildToolsVersion", new_line)

    def replace_app_class(self):
        """Replaces the LibGDX app class with the BDX app class"""
        n = "BdxApp.java"
        bdx_app = j(ut.gen_root(), n)
        gdx_app = j(ut.src_root(), n)
        shutil.copy(bdx_app, gdx_app)

        ut.set_file_line(gdx_app, 1,
                         "package " + bpy.context.scene.bdx_java_pack + ';')

    def replace_desktop_launcher(self):
        n = "DesktopLauncher.java"
        bdx_dl = j(ut.gen_root(), n)
        gdx_dl = j(ut.src_root("desktop", n), n)
        shutil.copy(bdx_dl, gdx_dl);

        sc = bpy.context.scene

        ut.set_file_line(gdx_dl, 1,
                         "package " + sc.bdx_java_pack + '.desktop;')

        ut.set_file_line(gdx_dl, 5,
                         "import " + sc.bdx_java_pack + ".BdxApp;")

    def replace_android_launcher(self):
        n = "AndroidLauncher.java"
        bdx_al = j(ut.gen_root(), n)
        gdx_al = j(ut.src_root("android", n), n)
        shutil.copy(bdx_al, gdx_al)

        sc = bpy.context.scene

        ut.set_file_line(gdx_al, 1,
                         "package " + sc.bdx_java_pack + '.android;')

        ut.set_file_line(gdx_al, 8,
                         "import " + sc.bdx_java_pack + ".BdxApp;")

    def copy_bdx_libs(self):
        bdx_libs = j(ut.plugin_root(), "libs")
        libs = j(ut.project_root(), "core", "libs")
        shutil.copytree(bdx_libs, libs)

    def open_default_blend(self):
        proot = ut.project_root()
        fp = j(proot, "blender/game.blend")
        bpy.ops.wm.open_mainfile(filepath=fp)
        textures = j(proot, "android", "assets", "bdx", "textures")
        bpy.ops.file.find_missing_files(directory=textures)
        bpy.ops.wm.save_mainfile()

    def update_bdx_xml(self):
        proot = ut.project_root()
        bdx_xml = j(proot, "core/src/BdxApp.gwt.xml")
        ut.insert_lines_after(bdx_xml, "<module>", ["	<inherits name='com.Bdx' />"])

    def execute(self, context):
        context.window.cursor_set("WAIT")

        self.create_libgdx_project()
        self.create_android_assets_bdx()
        self.create_blender_assets()
        self.replace_build_gradle()
        self.set_android_sdk_build_tools_version()
        self.replace_app_class()
        self.replace_desktop_launcher()
        self.replace_android_launcher()
        self.copy_bdx_libs()
        self.update_bdx_xml()
        self.open_default_blend()

        #context.window.cursor_set("DEFAULT")

        return {'FINISHED'}


def register():
    bpy.utils.register_class(CreateBdxProject)


def unregister():
    bpy.utils.unregister_class(CreateBdxProject)