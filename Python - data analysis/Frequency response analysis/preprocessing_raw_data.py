"""
This program reads out the raw data saved in hexadecimal format in the text files and converts it to
integer values and saves it as _csv.csv files.
Due to high errors in the initial few lines, the first 100 lines are cut out and also the last two lines are left out.

Version: 1.0
Roman Oechslin
Master Thesis - University of Tokyo

"""

import shutil
directory = "20180529_fra_logs/raw_data/"
#shutil.move( myfile + ".txt", myfile+"new" + ".txt")
import os

for filename in os.listdir(directory):
    print(filename)

    source= open(directory + filename, "r")
    destination= open("20180529_fra_logs/" + filename[:-4] + "_csv" + ".csv", "w")
    count = 0
    num_lines = sum(1 for line in open(directory + filename))
    print(num_lines)
    for line in source:
        count = count + 1
        if (count > 100 and count < num_lines - 2):
            buf = ""
            for character in line:
                if character == ";":
                    #print(buf)
                    destination.write(str(int(buf, 16)) + ";")#print(buf)
                    buf = ""
                elif character == "\n":
                    destination.write("\n")
                    buf = ""
                else:
                    buf = buf + character
    source.close()
    destination.close()
