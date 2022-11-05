import os
import sys

absolutepath = os.path.abspath(__file__)
print(absolutepath)

fileDirectory = os.path.dirname(absolutepath)
print(fileDirectory)
#Path of parent directory
parentDirectory = os.path.dirname(fileDirectory)
print(parentDirectory)
#Navigate to Strings directory
newPath = os.path.join(parentDirectory, 'Strings')
print(newPath)
