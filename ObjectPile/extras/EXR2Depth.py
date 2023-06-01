import array
import OpenEXR
import Imath
import numpy as np
import cv2
import matplotlib.pyplot as plt
import os, glob
import argparse
import timeit

# TAG_STRING = 'PIEH'
DEPTH_THR_MAX = 1.5e1
DEPTH_THR_MIN = 0.5e1

def Exr2Flow(exrfile):
	file = OpenEXR.InputFile(exrfile)

	# Compute the size
	dw = file.header()['dataWindow']
	ImgSize = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)
	[Width, Height] = ImgSize


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


def main(exrdirectory, viewflow):
	os.chdir(exrdirectory)
	# print(exrdirectory)
	# exrfilelist = glob.glob([exrdirectory+'*.exr'])
	# print(exrfilelist)
	idx_count = 0
	for exrfile in glob.glob('*.exr'):
		print(exrfile)
		Img, Width, Height = Exr2Flow(exrfile)
		# WriteFloFile(exrfile, Img, TAG_STRING, Width, Height)
		# if(viewflow):
		displayflow(Img, Width, Height, exrfile)	

def displayflow(Img, Width, Height, exrfile):
	hsv = np.zeros((Height, Width, 3), np.uint8)
	hsv[...,1] = 255
	# print(np.shape(Img))
	
	mag, ang = (Img[...,0], Img[...,1])
	mag = (mag < DEPTH_THR_MAX ) * mag
	mag = (mag > DEPTH_THR_MIN ) * mag

	hsv[...,0] = ang * 180 / np.pi / 2
	
	# print(np.amax(ang), np.amin(ang))
	# print(np.amax(mag), np.amin(ang))
	
	hsv[...,2] = mag;
	
	# Uncomment if you want normalized depth in every image:
	hsv[...,2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX);

	#bgr = cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR)
	fig = plt.figure()
	print(mag.shape)
	cv2.imwrite('b/'+exrfile[:-4]+'.png', hsv[...,2])
	# Save Color Depth Map:
	plt.imshow(hsv[...,2], cmap='gray')
	# plt.colorbar()
	# plt.show()
	plt.savefig(exrfile[:-4]+'.png')

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--flowfiledirectory', type=str, default='/home/chahatdeep/git_cloned/blender-script/scripts/Test/', \
							help='Flow file')
	parser.add_argument('--viewflow', type=bool, default=True, \
							help='Flow file')
	exrdirectory = parser.parse_args().flowfiledirectory
	viewflow = parser.parse_args().viewflow
	main(exrdirectory, viewflow)


	
