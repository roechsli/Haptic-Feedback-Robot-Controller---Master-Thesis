import Image
import os
dir = "../oechslin_may/Figs/"

print("Created files:")
for files in os.listdir(dir):
    print(files)
    if ".eps" not in files:
        #print(files[:-4] + ".eps")
        im = Image.open(dir + files)
        im.save(dir + files[:-4] + ".eps")