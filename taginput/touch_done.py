# AllanC - when I was messing with rsync and merging my tags.txt with a local copy, 
#          the date modified times were damaged and the % done list was inacurate
#          I created this script to check for a 'title:' string in the files and touch them
#          This is a helper as documentation for karatag.py

import os

#def touch(fname, times = None):
#	with file(fname, 'a'):
#		os.utime(fname, times)

def touch(fname, times = None):
    fhandle = file(fname, 'a')
    try:
        os.utime(fname, times)
    finally:
        fhandle.close()

count = 0
for root, dirs, files in os.walk('./data'):
	for filename in files:
		filename = os.path.join(root,filename)

		touch_this_file = False
		fhandle = file(filename, 'r')
		try:
			for line in fhandle:
				if 'title:' in line:
					touch_this_file = True
					break
		finally:
			fhandle.close()

		if touch_this_file:			
			print(filename)
			touch(filename)
			count += 1


print(count)

