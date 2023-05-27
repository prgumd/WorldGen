import cv2
import numpy as np
import os
import argparse
import os


# Event Params:
EVENT_THRESHOLD = 10e-1
EVENT_ADDED_NOISE = 3e-3
EVENT_ADDED_NOISE_BLACK = 2e-1

# Event Params:
EVENT_THRESHOLD = 20e-2
EVENT_ADDED_NOISE = 3e-3
EVENT_ADDED_NOISE_BLACK = 2e-1

"""
Create Events from 2 Frames:

Inputs:
I1: Previous Image
I2: Current Image

Outputs:
ev_img: Event Image
noise_img: Event Image with Salt and Pepper Noise
"""
def create_event_img(I1, I2):
	I1 = cv2.imread(I1, cv2.IMREAD_ANYCOLOR)
	I2 = cv2.imread(I2, cv2.IMREAD_ANYCOLOR)

	I1 = cv2.cvtColor(I1, cv2.COLOR_BGR2GRAY)
	I2 = cv2.cvtColor(I2, cv2.COLOR_BGR2GRAY)

	# diff = np.log(cv2.cvtColor(I2, cv2.COLOR_BGR2GRAY) - cv2.cvtColor(I1, cv2.COLOR_BGR2GRAY))
	diff = np.log(I2) - np.log(I1)
	diff[abs(diff) < EVENT_THRESHOLD] = 0
	diff[diff < 0] = -1
	diff[diff > 0] = 1
	print(diff.shape)
	# Saves RGB version of events (np.shape(diff))
	ev_img = np.zeros((diff.shape[0], diff.shape[1],3))
	ev_img[diff == -1, 0] = 127
	ev_img[diff == 1, 2] = 255
	print(np.shape(ev_img))
	noise_img = add_noise(ev_img)
	return noise_img

"""
Add Noise to the Event Image:

Inputs:
Img: Input Event Image

Outputs:
noise_img: Event Image with Salt and Pepper Noise
"""

def add_noise(img):
	red = np.array([0, 0, 255], dtype='uint8')
	blue = np.array([255, 0, 0], dtype='uint8')
	black = np.array([0, 0, 0], dtype='uint8')

	noise_img = img.copy()
	noise_red = np.random.random(img.shape[:2])
	noise_blue = np.random.random(img.shape[:2])
	noise_black = np.random.random(img.shape[:2])
	noise_img[noise_blue > 1 - EVENT_ADDED_NOISE_BLACK] = black
	noise_img[noise_red > 1 - EVENT_ADDED_NOISE] = red
	noise_img[noise_blue > 1 - EVENT_ADDED_NOISE] = blue
	

	return noise_img

def main():
	# video_path = '/Users/riyakumari/Desktop/eventVid/WorldGen.mp4'
	# output_dir = '/Users/riyakumari/Desktop/eventVid/outputs/'

	# Dataset.generateEventsFromVid(video_path, output_dir)
	parser = argparse.ArgumentParser()
	
	parser.add_argument("--folderDir", type=str, help="path to images directory")
	parser.add_argument("--outputDir", type=str, help="path to output directory")
	args = vars(parser.parse_args())
	folder_dir = args["folderDir"]
	output_dir = args["outputDir"]
	if not os.path.isdir(output_dir):
		os.mkdir(output_dir)
		
	f1 = None
	f2 = None
	step = 0
	for filename in os.listdir(folder_dir):
		current_frame = os.path.join(folder_dir, filename)
		step+=1
		# checking if it is a file
		if os.path.isfile(current_frame):
			if f1 == None and f2 == None: 
				f1 = current_frame
				continue
			else:
				f2 = current_frame
			ev_img = create_event_img(f1, f2)
			filename = os.path.join(output_dir,"events{0}.png".format(step))
			cv2.imwrite(filename, ev_img)
			f1 = f2






if __name__ == "__main__":
	main()