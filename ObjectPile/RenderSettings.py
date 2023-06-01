def RenderSettings(FRAME_START, FRAME_END, FRAME_STEP):

	import bpy

	# RENDER SETTINGS:
	bpy.context.scene.cycles.samples = 300
	bpy.context.scene.cycles.preview_samples = 90
	bpy.context.scene.render.engine = 'CYCLES'
	bpy.context.scene.cycles.feature_set = 'EXPERIMENTAL'
	bpy.context.scene.cycles.device = 'GPU' # 'CPU' or 'GPU'
	bpy.context.scene.cycles.progressive = 'PATH'


	# CAMERA RESOLUTION AND RENDERING:
	bpy.context.scene.render.resolution_x = 640
	bpy.context.scene.render.resolution_y = 480
	bpy.context.scene.frame_start = FRAME_START
	bpy.context.scene.frame_end = FRAME_END
	bpy.context.scene.frame_step = FRAME_STEP
	bpy.ops.ptcache.bake_all(bake=True)



	# LENS SETTINGS:
	bpy.context.object.data.type = 'PERSP' # 'PERSP', 'ORTHO', 'PANO'
	bpy.context.object.data.lens = 50
	bpy.context.object.data.lens_unit = 'MILLIMETERS'
	bpy.context.object.data.sensor_fit = 'AUTO'
	bpy.context.object.data.sensor_width = 36 # in mm


	# STEREO CAMERA SETTINGS:
	STEREOSCOPY_FLAG = True # True or False
	if STEREOSCOPY_FLAG == True:
		bpy.context.scene.render.use_multiview = STEREOSCOPY_FLAG
		bpy.context.scene.render.views["left"].file_suffix = "_L"
		bpy.context.scene.render.views["right"].file_suffix = "_R"
		bpy.context.object.data.stereo.convergence_mode = 'OFFAXIS'
		bpy.context.object.data.stereo.convergence_distance = 1.84
		bpy.context.object.data.stereo.interocular_distance = 0.025

	# OUTPUT SETTINGS:
	bpy.context.scene.view_layers["View Layer"].use_pass_combined = True
	bpy.context.scene.view_layers["View Layer"].use_pass_z = True
	bpy.context.scene.view_layers["View Layer"].use_pass_vector = True
	bpy.context.scene.view_layers["View Layer"].use = True

	# GRAVITY SETTINGS:
	bpy.context.scene.use_gravity = True
	bpy.context.scene.gravity[2] = -9.81 # Along Z-Axis



def RenderSettingsForrest(FRAME_START, FRAME_END, FRAME_STEP, QUALITY_FLAG):

	import bpy


	# RENDER SETTINGS:
	if QUALITY_FLAG == 'HQ':
		bpy.context.scene.cycles.samples = 128
		bpy.context.scene.cycles.preview_samples = 32
	if QUALITY_FLAG == 'LQ': # ONLY FOR DEPTH MAP
		bpy.context.scene.cycles.samples = 1
		bpy.context.scene.cycles.preview_samples = 0

	bpy.context.scene.render.engine = 'CYCLES'
	bpy.context.scene.cycles.feature_set = 'EXPERIMENTAL'
	bpy.context.scene.cycles.device = 'GPU' # 'CPU' or 'GPU'
	bpy.context.scene.cycles.progressive = 'PATH'


	# CAMERA RESOLUTION AND RENDERING:
	bpy.context.scene.render.resolution_x = 640
	bpy.context.scene.render.resolution_y = 480
	bpy.context.scene.frame_start = FRAME_START
	bpy.context.scene.frame_end = FRAME_END
	bpy.context.scene.frame_step = FRAME_STEP
	bpy.ops.ptcache.bake_all(bake=True)




	# LENS SETTINGS:
	bpy.context.object.data.type = 'PERSP' # 'PERSP', 'ORTHO', 'PANO'
	bpy.context.object.data.lens = 50
	bpy.context.object.data.lens_unit = 'MILLIMETERS'
	bpy.context.object.data.sensor_fit = 'AUTO'
	bpy.context.object.data.sensor_width = 36 # in mm


	# STEREO CAMERA SETTINGS:
	STEREOSCOPY_FLAG = False # True or False
	if STEREOSCOPY_FLAG == True:
		bpy.context.scene.render.use_multiview = STEREOSCOPY_FLAG
		bpy.context.scene.render.views["left"].file_suffix = "_L"
		bpy.context.scene.render.views["right"].file_suffix = "_R"
		bpy.context.object.data.stereo.convergence_mode = 'OFFAXIS'
		bpy.context.object.data.stereo.convergence_distance = 1.84
		bpy.context.object.data.stereo.interocular_distance = 0.025

	# OUTPUT SETTINGS:
	bpy.context.scene.view_layers["View Layer"].use_pass_combined = True
	bpy.context.scene.view_layers["View Layer"].use_pass_z = True
	bpy.context.scene.view_layers["View Layer"].use_pass_vector = True
	bpy.context.scene.view_layers["View Layer"].use = True

	# GRAVITY SETTINGS:
	bpy.context.scene.use_gravity = True
	bpy.context.scene.gravity[2] = -9.81 # Along Z-Axis
