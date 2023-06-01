#!/usr/bin/env python3

import argparse, shutil, os

parser = argparse.ArgumentParser()
parser.add_argument("--DataSetPath", help="Enter Base Data Set Path here.", \
						default="/home/chahatdeep/Downloads/MSCOCOunlabeled2017/unlabeled2017/")

# Removing material is a good option as loading materials takes about 2-20 times
# more time than loading the objects in the ShapeNetCorev2 Dataset, depending on
# object and number of assigned materials for that object in its .mtl file.


args = parser.parse_args()
print("Fetching Objects From: " + args.DataSetPath)

objList = open("TextureList.txt", "w")
for root, dirs, files in os.walk(args.DataSetPath):
	for file in files:
		if file.endswith(".jpg"):
			 objList.writelines(os.path.join(root, file))
			 objList.writelines("\n")
