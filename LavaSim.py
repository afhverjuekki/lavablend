import os
import bpy
from bpy.props import StringProperty, CollectionProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper

import rasterio as rio

from mathutils import Vector

class LavaSim_Frame(bpy.types.PropertyGroup):
    index: bpy.props.IntProperty(default=0)
    object: bpy.props.PointerProperty(type=bpy.types.Object)

class LavaSimProperties(bpy.types.PropertyGroup):
    LavaSimFolder: bpy.props.StringProperty(
        name="LavaSim Folder",
        description="Path to the simulation folder",
        default=""
    )

    file_index_delimiter: bpy.props.StringProperty(
        name="File Index Delimiter",
        description="Delimiter for the file index",
        default="_"
    )

    create_mesh: bpy.props.BoolProperty(
        name="Create Mesh",
        description="Create a mesh from the volume",
        default=True
    )

    height_scale: bpy.props.FloatProperty(
        name="Height Scale",
        description="Scale the height of the mesh",
        default=1.0
    )

    lava_object: bpy.props.PointerProperty(type=bpy.types.Object)

    lava_index: bpy.props.IntProperty(default=0)

    lava_offset_x: bpy.props.FloatProperty(default=0.0)
    lava_offset_y: bpy.props.FloatProperty(default=0.0)

    frame_spacing: bpy.props.FloatProperty(default=1.0)
    

class LavaSim_File(bpy.types.PropertyGroup):
    index: bpy.props.IntProperty(default=0)
    name: bpy.props.StringProperty(default="")
    path: bpy.props.StringProperty(default="")


class LavaSim_Panel(bpy.types.Panel):
    bl_label = "LavaSim"
    bl_idname = "LAVA_SIM_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"HEADER_LAYOUT_EXPAND"}
    bl_category = "LavaSim"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator("lava_sim.pick_folder")
        if context.scene.lava_sim_properties.LavaSimFolder:
            col.separator(type="LINE")
            row = col.row()
            split = row.split(factor=0.8)
            split.label(text="File Index Delimiter")
            split.prop(context.scene.lava_sim_properties, "file_index_delimiter", text="")
            col.operator("lava_sim.import_files")
        if context.scene.lava_sim_files:
            col.separator(type="LINE")
            col.prop(context.scene.lava_sim_properties, "height_scale")
            col.prop(context.scene.lava_sim_properties, "lava_index")
            col.prop(context.scene.lava_sim_properties, "frame_spacing")
            row = col.row()
            row.prop(context.scene.lava_sim_properties, "lava_offset_x")
            row.prop(context.scene.lava_sim_properties, "lava_offset_y")
            col.prop(context.scene.lava_sim_properties, "create_mesh")
            if context.scene.lava_sim_properties.create_mesh:
                col.operator("lava_sim.render_mesh")
            else:
                col.operator("lava_sim.render_volume")


class LavaSim_PickFolder(bpy.types.Operator, ImportHelper):
    bl_label = "Pick Folder"
    bl_idname = "lava_sim.pick_folder"
    bl_options = {"REGISTER", "UNDO"}
    
    filename_ext = ""
    use_filter_folder = True
    directory: bpy.props.StringProperty(
        subtype='DIR_PATH'
    )
    
    def execute(self, context):
        context.scene.lava_sim_properties.LavaSimFolder = self.directory
        return {'FINISHED'}

class LavaSim_ImportFiles(bpy.types.Operator):
    bl_label = "Import Files"
    bl_idname = "lava_sim.import_files"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        dir = os.listdir(context.scene.lava_sim_properties.LavaSimFolder)
        files = []
        for file in dir:
            if file.endswith(".tif"):
                file_name = os.path.splitext(file)[0]
                file_index = file_name.split(context.scene.lava_sim_properties.file_index_delimiter)[-1]
                files.append({"index": file_index, "name": file_name, "path": os.path.join(context.scene.lava_sim_properties.LavaSimFolder, file)})
        
        files.sort(key=lambda x: int(x["index"]))
        for file in files:
            prop = context.scene.lava_sim_files.add()
            prop.index = int(file["index"])
            prop.name = file["name"]
            prop.path = file["path"]
        print("LavaSim Files imported");
        return {'FINISHED'}

class LavaSim_RenderVolume(bpy.types.Operator):
    bl_label = "Render Volume"
    bl_idname = "lava_sim.render_volume"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.ops.lava_sim.render()
        return {'FINISHED'}

class LavaSim_RenderMesh(bpy.types.Operator):
    bl_label = "Render Mesh"
    bl_idname = "lava_sim.render_mesh"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.types.Scene.lava_sim_frames = bpy.props.CollectionProperty(type=LavaSim_Frame)
        bpy.ops.lava_sim.render()
        return {'FINISHED'}

class LavaSim_Render(bpy.types.Operator):
    bl_label = "Render"
    bl_idname = "lava_sim.render"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        collection = bpy.data.collections.new(name="LavaSim Frames")
        bpy.context.collection.children.link(collection)
        for i in range(len(bpy.context.scene.lava_sim_files)):
            self.render_frame(context, i, collection)
            print(f"Rendered frame {i}")
        return {'FINISHED'}

    def render_frame(self, context, framepath, collection):
        frame = bpy.context.scene.lava_sim_frames.add()
        frame.index = len(bpy.context.scene.lava_sim_frames)

        file = context.scene.lava_sim_files[framepath]
        data = None
        width = 0   
        height = 0
        nodata = None
        transform = None
        crs = None
        
        # Get the DEM's transform and dimensions
        dem_transform = None
        dem_width = 0
        dem_height = 0
        dem_data = None
        dem_nodata = None
        with rio.open(context.scene.demm_properties.Filepath) as src:
            dem_transform = src.transform
            dem_width = src.width
            dem_height = src.height
            dem_data = src.read(1)
            dem_nodata = src.nodata
        
        with rio.open(file.path) as src:
            data = src.read(1)
            width = src.width
            height = src.height
            nodata = src.nodata
            transform = src.transform
            crs = src.crs
        
        if context.scene.lava_sim_properties.create_mesh:
            vertices, faces = self.create_mesh(data, width, height, nodata, transform, dem_transform, dem_width, dem_height, dem_data, dem_nodata)

            mesh = bpy.data.meshes.new(name="LavaSim Volume")
            mesh.from_pydata(vertices, [], faces)
            mesh.update()

            #if context.scene.lava_sim_properties.lava_object:
             #   bpy.data.objects.remove(context.scene.lava_sim_properties.lava_object, do_unlink=True)

            obj = bpy.data.objects.new(name="LavaSim Volume", object_data=mesh)
            collection.objects.link(obj)
            context.scene.lava_sim_properties.lava_object = obj

            """
            obj.animation_data_create()
            ac = bpy.data.actions.new(name="LavaSim Volume")
            obj.animation_data.action = ac
            fc = ac.fcurves.new(data_path="hide_viewport")
            fc.keyframe_points.add(4)

            fc.keyframe_points.foreach_set("co", [0, True, 1,False,framepath,True,framepath+1,False])"""
            
            obj.hide_viewport = True
            obj.hide_render = True
            obj.keyframe_insert(data_path="hide_viewport", frame=1)
            obj.keyframe_insert(data_path="hide_render", frame=1)

            obj.hide_viewport = True
            obj.hide_render = True
            obj.keyframe_insert(data_path="hide_viewport", frame=framepath*context.scene.lava_sim_properties.frame_spacing-1)
            obj.keyframe_insert(data_path="hide_render", frame=framepath*context.scene.lava_sim_properties.frame_spacing-1)

            obj.hide_viewport = False
            obj.hide_render = False
            obj.keyframe_insert(data_path="hide_viewport", frame=framepath*context.scene.lava_sim_properties.frame_spacing)
            obj.keyframe_insert(data_path="hide_render", frame=framepath*context.scene.lava_sim_properties.frame_spacing)

            
            obj.hide_viewport = True
            obj.hide_render = True
            obj.keyframe_insert(data_path="hide_viewport", frame=(framepath*context.scene.lava_sim_properties.frame_spacing)+context.scene.lava_sim_properties.frame_spacing)
            obj.keyframe_insert(data_path="hide_render", frame=(framepath*context.scene.lava_sim_properties.frame_spacing)+context.scene.lava_sim_properties.frame_spacing)
            #obj.select_set(True)
        else:
            vertices = self.create_vertices(data, width, height, nodata, transform, dem_transform, dem_width, dem_height, dem_data, dem_nodata)

            mesh = bpy.data.meshes.new(name="LavaSim Volume")
            mesh.from_pydata(vertices, [], [])
            mesh.update()

            obj = bpy.data.objects.new(name="LavaSim Volume", object_data=mesh)
            collection.objects.link(obj)
            context.scene.lava_sim_properties.lava_object = obj
        
        frame.object = obj
        #obj.hide_set(True)

        #self.set_view(context, width)
        return {'FINISHED'}
    
    def get_dem_height(self, x, y, dem_data, dem_transform, dem_width, dem_height, dem_nodata):
        #return dem_data[int(y), int(x)]+88.4382
        start = Vector((x, y, 1000))
        direction = Vector((x, y, 0)) - start
        direction.normalize()
        hit, loc, norm, idx, obj, mw = bpy.context.scene.ray_cast(bpy.context.view_layer.depsgraph, start, direction)
        if hit:
            return loc.z
        else:
            return None

    def create_vertices(self, data, width, height, nodata, transform=None, dem_transform=None, dem_width=0, dem_height=0, dem_data=None, dem_nodata=None):
        vertices = []

        for y in range(height):
            for x in range(width):
                if data[y, x] != nodata:
                    if transform and dem_transform:
                        # Convert pixel coordinates to geographic coordinates
                        lon, lat = transform * (x, y)
                        dem_x, dem_y = ~dem_transform * (lon, lat)
                        # Get DEM height at this location with offset
                        dem_height = self.get_dem_height(dem_x + bpy.context.scene.lava_sim_properties.lava_offset_x, 
                                                       dem_y + bpy.context.scene.lava_sim_properties.lava_offset_y, 
                                                       dem_data, dem_transform, dem_width, dem_height, dem_nodata)
                        # Add DEM height to lava thickness
                        total_height = dem_height + (data[y, x] * bpy.context.scene.lava_sim_properties.height_scale)
                        vertices.append((dem_x, dem_y, total_height))
                    else:
                        vertices.append((x + bpy.context.scene.lava_sim_properties.lava_offset_x, 
                                       y + bpy.context.scene.lava_sim_properties.lava_offset_y, 
                                       data[y, x] * bpy.context.scene.lava_sim_properties.height_scale))

        return vertices

    def create_mesh(self, data, width, height, nodata, transform=None, dem_transform=None, dem_width=0, dem_height=0, dem_data=None, dem_nodata=None):
        vertices = []
        faces = []
        vert_indices = {}

        for y in range(height):
            for x in range(width):
                if data[y, x] != nodata:
                    vert_idx = len(vertices)
                    if transform and dem_transform:
                        lon, lat = transform * (x, y)
                        dem_x, dem_y = ~dem_transform * (lon, lat)

                        # Get DEM height at this location
                        dem_height = self.get_dem_height(dem_x + bpy.context.scene.lava_sim_properties.lava_offset_x, dem_y + bpy.context.scene.lava_sim_properties.lava_offset_y, dem_data, dem_transform, dem_width, dem_height, dem_nodata)
                        # Add DEM height to lava thickness
                        total_height = dem_height + ((data[y, x] * bpy.context.scene.lava_sim_properties.height_scale))
                        vertices.append((dem_x, dem_y, total_height))
                    else:
                        vertices.append((x + bpy.context.scene.lava_sim_properties.lava_offset_x, y + bpy.context.scene.lava_sim_properties.lava_offset_y, data[y, x] * bpy.context.scene.lava_sim_properties.height_scale))
                    vert_indices[(x, y)] = vert_idx

        for y in range(height - 1):
            for x in range(width - 1):
                corners = [(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)]
                
                available = [corner for corner in corners if corner in vert_indices]

                if len(available) >= 3:
                    if len(available) == 4:
                        faces.append((
                            vert_indices[corners[0]],
                            vert_indices[corners[1]],
                            vert_indices[corners[2]]
                        ))
                        faces.append((
                            vert_indices[corners[2]],
                            vert_indices[corners[1]],
                            vert_indices[corners[3]]
                        ))
                    else:
                        faces.append((
                            vert_indices[available[0]],
                            vert_indices[available[1]],
                            vert_indices[available[2]]
                        ))

        return vertices, faces

    def set_view(self, context, width):
        print("Updating view...")
        context.space_data.clip_end = width*10
        context.scene.lava_sim_properties.lava_object.select_set(True)
        bpy.ops.view3d.view_selected()

classes = [
    LavaSimProperties,
    LavaSim_PickFolder,
    LavaSim_File,
    LavaSim_Panel,
    LavaSim_ImportFiles,
    LavaSim_RenderVolume,
    LavaSim_RenderMesh,
    LavaSim_Render,
    LavaSim_Frame
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.lava_sim_properties = bpy.props.PointerProperty(type=LavaSimProperties)
    bpy.types.Scene.lava_sim_files = bpy.props.CollectionProperty(type=LavaSim_File)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.lava_sim_properties
    del bpy.types.Scene.lava_sim_files
