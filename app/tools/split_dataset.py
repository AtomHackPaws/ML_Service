"""
Разделение датасета на подвыборки
"""
import random
import shutil
import os


path = "/mnt/linux-860/Dataset_HACK"
# path = "/mnt/linux-860/NEW_Data_HACK"

tr = 6100
vl = 841
ts = 1800

for i in ["TRAIN", "VALID", "TEST"]:
	os.makedirs(f"{path}/{i}/images/")
	os.makedirs(f"{path}/{i}/labels/")

images = os.listdir(f"{path}/images/")

random.shuffle(images)


def choose(count, folder):
	names = [images.pop().split(".")[-2] for _ in range(count)]
	for name in names:
		shutil.copyfile(f"{path}/images/{name}.jpg", f"{path}/{folder}/images/{name}.jpg")
		shutil.copyfile(f"{path}/labels/{name}.txt", f"{path}/{folder}/labels/{name}.txt")

choose(tr, "TRAIN")
choose(vl, "VALID")
choose(ts, "TEST")
