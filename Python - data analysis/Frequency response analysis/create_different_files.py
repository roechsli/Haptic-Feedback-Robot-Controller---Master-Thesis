"""
This program takes one long  raw data text file and creates several different text files according to the
predefined frequency vector

Version: 1.01
Roman Oechslin
Master Thesis - University of Tokyo
Date: August 2018

"""

import shutil
import os
directory = "tmp_text_files/"
src_filename = "raw_data.txt"
freq_vec = ["1", "1.25", "1.6", "2", "2.5", "3", "4", "5", "6.3", "8", "10", "13",
            "16", "20", "25", "32", "40", "50", "63", "80", "100"]

if not os.path.exists(directory):
    os.makedirs(directory)
source = open(src_filename, "r")
num_lines = sum(1 for line in open(src_filename))
print("number of lines in file = " + str(num_lines))
iter_len = num_lines / len(freq_vec)
print("iter len = " + str(iter_len))
loop = 0
ignore_lines = 1500

for frequency in freq_vec:
    print(frequency)
    destination = open(directory + "f" + frequency + ".txt", "w")

    with open(src_filename) as fp:
        for i, line in enumerate(fp):
            if i >= loop * iter_len + ignore_lines:
                if i < (loop + 1) * iter_len - ignore_lines:
                    destination.write(line)
            elif i < loop * iter_len + ignore_lines:
                pass
            else:
                break

    destination.close()
    loop = loop + 1
source.close()
