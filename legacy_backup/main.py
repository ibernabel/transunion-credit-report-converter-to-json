import os

path1 = "./credit_reports/"
path2 = "./output_text/"
path3 = "./images/"

try:
    os.stat(path1)
    os.stat(path2)
    os.stat(path3)
except:
    os.mkdir(path1)
    os.mkdir(path2)
    os.mkdir(path3)
