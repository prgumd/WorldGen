import array
import os
os.environ["OPENCV_IO_ENABLE_OPENEXR"]="1"
import Imath
import OpenEXR
import numpy as np
import cv2
import matplotlib.pyplot as plt
import os
import argparse
import timeit

import torch

TAG_STRING = 'PIEH'
FLOW_THR = 1
count = 0

def Exr2Flow(exrfile):
	# file = cv2.imread(exrfile,  cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)
	
	# file = np.where(file<=0.0031308, 12.92*file, 1.055*np.power(file, 1/2.4) - 0.055)
	# # img = (file*255).astype(np.uint8)

	# print(file.shape)
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
 
	# return Img, Width, Height

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
	print("img : ", f.shape)
	f.close()

def main(exrfile):
	Img, Width, Height = Exr2Flow(exrfile)
	WriteFloFile(exrfile, Img, TAG_STRING, Width, Height)



if __name__ == '__main__':
	folder_dir = '/Users/riyakumari/Desktop/world-gen/render/flow/metric/'
	for image in os.listdir(folder_dir):
		if "exr" in image:
			main(folder_dir+image)
	
