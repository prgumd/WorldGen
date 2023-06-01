#!/usr/bin/env python3

import argparse, shutil, os

parser = argparse.ArgumentParser()
parser.add_argument("--DataSetPath", help="Enter Base Data Set Path here.", \
						default="/home/chahatdeep/Downloads/ShapeNetCore.v2/")
parser.add_argument("--RemoveMaterialFlag", help="1 if you want to remove the \
				default materials, anything else to use default materials", \
				default=1, type=int)

# Removing material is a good option as loading materials takes about 2-20 times
# more time than loading the objects in the ShapeNetCorev2 Dataset, depending on
# object and number of assigned materials for that object in its .mtl file.


args = parser.parse_args()
print("Fetching Objects From: " + args.DataSetPath)

objList = open("OBJList.txt", "w")
for root, dirs, files in os.walk(args.DataSetPath):
	for file in files:
		if file.endswith(".obj"):
			 objList.writelines(os.path.join(root, file))
			 objList.writelines("\n")


# Remove material files from the dataset (by renaming to .tmp extension so 
# Blender doesn't load material files for the object)
if (args.RemoveMaterialFlag == 1):
	MTLFileList = open('OBJList.txt', 'r')
	Lines = MTLFileList.readlines()[:-1]

	for line in Lines:
		try:
			shutil.move(line.strip()[:-3] + 'mtl', line.strip()[:-3]+ 'tmp')
		except:
			print('Error in ' + line.strip()[:-3] + 'mtl')
			# "/home/chahatdeep/Downloads/ShapeNetCore.v2/"