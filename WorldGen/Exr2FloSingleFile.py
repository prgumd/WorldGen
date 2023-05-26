import array
import OpenEXR
import Imath
import numpy as np
import cv2
import matplotlib.pyplot as plt
import os
import argparse
import timeit
import flow_vis
import flow_vis_torch
import torch

TAG_STRING = 'PIEH'
FLOW_THR = 1
count = 0

def Exr2Flow(exrfile):
	file = OpenEXR.InputFile(exrfile)

	# Compute the size
	dw = file.header()['dataWindow']
	ImgSize = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)
	[Width, Height] = ImgSize
	print(Width)


	# R and G channel stores the flow in (u,v) (Read Blender Notes)
	FLOAT = Imath.PixelType(Imath.PixelType.FLOAT)
	# start = timeit.default_timer()
	(R,G,B) = [array.array('f', file.channel(Chan, FLOAT)).tolist() for Chan in ("R", "G", "B")]
	# stop = timeit.default_timer()
	# print('Time: ', stop - start) 
	
	Img = np.zeros((Height, Width, 3), np.float64)
	Img[:,:,0] = np.array(R).reshape(Img.shape[0], -1)
	Img[:,:,1] = -np.array(G).reshape(Img.shape[0], -1)
 
	return Img, Width, Height

def WriteFloFile(exrfile, Img, TAG_STRING, Width, Height):
	# Write to a .flo file: 
	# Ref: https://github.com/Johswald/flow-code-python/blob/master/writeFlowFile.py
	f = open(exrfile[:-4]+'.flo','wb')
	f.write(TAG_STRING)
	np.array(Width).astype(np.int32).tofile(f)
	np.array(Height).astype(np.int32).tofile(f)
	nBands = 2
	tmp = np.zeros((Height, Width * nBands))
	tmp[:,np.arange(Width)*2] = Img[:,:,0]
	tmp[:,np.arange(Width)*2 + 1] = Img[:,:,1]
	tmp.astype(np.float32).tofile(f)
	f.close()

def main(exrfile):
	Img, Width, Height = Exr2Flow(exrfile)
	# WriteFloFile(exrfile, Img, TAG_STRING, Width, Height)
	if(1):
		# displayflow(Img, Width, Height, exrfile)
		visualize_optical_flow(Img, exrfile)	

# Generate an HSV image using color to represent the gradient direction in a optical flow field
def visualize_optical_flow(flowin, exrfile):
	flow=np.ma.array(flowin, mask=np.isnan(flowin))
	theta = np.mod(np.arctan2(flow[:, :, 0], flow[:, :, 1]) + 2*np.pi, 2*np.pi)

	flow_norms = np.linalg.norm(flow, axis=2)
	flow_norms_normalized = flow_norms / np.max(np.ma.array(flow_norms, mask=np.isnan(flow_norms)))

	flow_hsv = np.zeros((flow.shape[0], flow.shape[1], 3), dtype=np.uint8)
	flow_hsv[:, :, 0] = 179 * theta / (2*np.pi)
	flow_hsv[:, :, 1] = 255 * flow_norms_normalized
	flow_hsv[:, :, 2] = 255 # * (flow_norms_normalized > 0)
	bgr = cv2.cvtColor(flow_hsv,cv2.COLOR_HSV2BGR)

	fig = plt.figure()
	# fig.set_size_inches(32, 18)
	plt.axis('off')
	# plt.imshow(bgr)
	# plt.show()


	# fig.savefig('out.png', bbox_inches='tight', pad_inches=0)
	plt.imsave(exrfile[:-4]+'.png', bgr)
	# plt.show()
	# plt.savefig(exrfile[:-4]+'.png')
	# cv2.imwrite("flow_vis.png", bgr)


	return flow_hsv

def displayflow(Img, Width, Height, exrfile):
	hsv = np.zeros((Height, Width, 3), np.uint8)
	hsv[...,1] = 255
	# print(np.shape(Img))
	mag, ang = cv2.cartToPolar(Img[...,0], Img[...,1])
	# mag = (mag < FLOW_THR ) * mag
	print(np.amax(ang), np.amin(ang))
	print(np.amax(mag), np.amin(ang))
	hsv[...,0] = ang * 180 / np.pi / 2
	hsv[...,2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
	# hsv[...,1] = 
	bgr = cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR)
	# cv2.imshow("colored flow", bgr)
	# cv2.waitKey(0)
	# cv2.destroyAllWindows()
	# I = Img[...,0:2]
	# print(np.shape(I))
	# print(np.shape(np.transpose(I)))
	# print((torch.from_numpy(np.transpose(I))).unsqueeze(0).shape)
	# flow_rgb = flow_vis_torch.flow_to_color()

	# I2 = torch.from_numpy(np.transpose(I)).unsqueeze(0)
	# flow_rgb = flow_vis_torch.flow_to_color(I2)
	
	fig = plt.figure()
	fig.set_size_inches(32, 18)
	plt.axis('off')
	# plt.imshow(bgr) # viridis, plasma
	# plt.imshow(2*Img[...,1]+ 10*Img[...,0], cmap='plasma')
	# plt.imshow(Img[...,0], cmap='plasma') # viridis, plasma
	# plt.imshow(2*Img[...,1]+ 10*Img[...,0], cmap='plasma') # plasma
	# plt.Axes(fig, [0., 0., 1., 1.])

	fig.savefig('./output/'+exrfile, bbox_inches='tight', pad_inches=0)

	# plt.imshow(ang)
	# plt.colorbar()
	# plt.show()
	# plt.savefig(exrfile[:-4]+'.png')
	# cv2.imwrite("abc.png", Img[...,0])

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	
	parser.add_argument("--folderDir", type=str, help="path to flow directory")
	args = vars(parser.parse_args())

	folder_dir = args["folderDir"]
	
	# folder_dir = './'
	for image in os.listdir(folder_dir):
		if "exr" in image:
			main(folder_dir+image)
	
