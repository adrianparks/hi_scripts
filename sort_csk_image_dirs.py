# sort_csk_image_dirs.py
#
# Version 1.0   AP  24Jan2018
# Version 1.1   AP  24Apr2018
# Version 1.2   AP  29May2018
# Version 1.3   AP  06Sep2018
#
# The tl;dr is that this script sorts downloaded CSK images into the correct
# directory structure for processing. 
#
# The longer version is this - each set of images comes in three directories:
# NNNNNN-XXXXX
# NNNNNN-YYYYY
# NNNNNN-ZZZZZ
#
# where NNNNNN is common across all three and XXXXX, YYYYY and ZZZZZ represent
# the images in the order Eyjafjallajokull, Tindfjoll and Hekla for ascending 
# data, or else Hekla, Tind and Eyja for descending data. Furthermore,
# XXXXX < YYYYY < ZZZZZ
#
# In each of these three directories can be found a .H5 image (among other
# data) which contains the date in the name. For example:
# CSKS2_SCS_B_HI_0B_HH_RD_SF_20170803194620_20170803194626.h5
# - for which the date is 2017-08-03.
#
# So for ascending data, XXXXX represents Eyja, YYYYY is Tind, ZZZZZ is Hekla
# and for descending data, ZZZZZ represents Eyja, YYYYY is Tind, XXXXX is Hekla
# These images should be arranged in the following directory structure:
#
# Eyja/YYYYMMDD_Eyja
# Tind/YYYYMMDD_Tind
# Hekla/YYYYMMDD_Hekla
#
# where (for descending data), the date (YYYYMMDD) for Eyja is drawn from the
# .H5 filename in NNNNNN-ZZZZZ, the date for Tind from NNNNNN-YYYYY and the 
# date for Hekla from NNNNNN-XXXXX
#
# For data covering areas other than Eyjafjallajokull, Tindfjoll and Hekla, the
# process is the same, but the directory structure is:
#
# nth/YYYYMMDD_nth
# mid/YYYYMMDD_mid
# sth/YYYYMMDD_sth
#
##############################################################################
#
# Running this script
#
# This script will rename the directories according to the process above,
# placing them in the subdirectories nth,mid and sth, or eyja,tind,hekla 
# (latter depends on which option you specify as a parameter to the script).
#
# These subdirectories must already exist, e.g.
# /home/data/CSK/SCS_B/4926_Katla_ASC/nth
# /home/data/CSK/SCS_B/4926_Katla_ASC/mid
# /home/data/CSK/SCS_B/4926_Katla_ASC/sth
#
# Download the data and unzip it under the root directory (where the root is for
# example /home/data/CSK/SCS_B/4926_Katla_ASC), and you should then have 
# something along the lines of
#
# /home/data/CSK/SCS_B/4926_Katla_ASC/140578-23790
# /home/data/CSK/SCS_B/4926_Katla_ASC/140578-23791
# /home/data/CSK/SCS_B/4926_Katla_ASC/140578-23796
#
# for each set of scenes (ascending in this case).
# 
# Now run this script and the directories will be moved to the correct
# subdirectory (nth,sth or mid) and renamed appropriately
#
# Make sure you give the asc or desc parameter to the script and are cd'ed
# to the directory you want to sort 
# (e.g. /home/data/CSK/SCS_B/5840_Hekla_Eyja_ASC)
#
# then run with "python sort_csk_image_dirs.py  [asc|desc] [eth|nms]"
# e.g. python sort_csk_image_dirs.py desc nms

import sys, re
import os,shutil
from datetime import datetime
from os.path import isfile
from collections import defaultdict

def main():

    if (len(sys.argv) != 3):
        print "Usage: " + sys.argv[0] + " [asc|desc] [eth|nms]"
        print "Use asc for ascending data, desc for descending"
        print "Use eth if subdirs are Eyja,Tind,Hekla"
        print "Use nms if subdirs are nth,mid,sth"
        exit(1)

    dataformat = sys.argv[1].lower()
    site_param = sys.argv[2].lower()

    if site_param == "eth":
            sites = ["Eyja","Tind","Hekla"]
    elif site_param == "nms":
            sites = ["nth","mid","sth"]
    else:
        print "Third argument must be [eth|nms]"
        exit(1)

    if dataformat == "desc":
        # descending data, so reverse the array from south to north
        sites.reverse()

    elif dataformat != "asc":
        print "Second argument must be [asc|desc]"
        exit(1)
    
    path = os.getcwd()

    if path[-1] != "/":
        path = path + "/"

    processed_file = path + "sorted.txt"

    # dictionary to hold image directories and their end timestamps
    images = defaultdict(list)

    # list of directories with data in them
    valid_dirs = []

    datadirs = os.listdir(path)
    datadirs.sort()
    for dir in datadirs:
        if (re.search('^\d{6}\-\d{5}',dir)):
            valid_dirs.append(dir)

    print "These all appear to be valid directories for processing:"
    if valid_dirs:
        print("\n".join(valid_dirs))
    else:
        print "None found\nTerminating script - no valid directories found."
        exit(1)
    print "We are going to sort this into subdirectories:"
    print("\n".join(sites))
    print "This is " + dataformat.upper() + "ENDING data"
    print "If this is all correct, enter 'y' to continue, otherwise enter 'n'"

    reply = str(raw_input("Continue?"+' (y/n): ')).lower().strip()
    if reply[0] != 'y':
        exit(0)
    else:

        for datadir in valid_dirs:
            subdir = path + datadir + "/"
            print "Checking directory " + datadir + " for image file..."
            datafiles = os.listdir(subdir)

            for datafile in datafiles:
                # typical data file will be
                #
                # CSKS2_SCS_B_HI_0B_HH_RD_SF_20170803194620_20170803194626.h5
                #
                # so we need to get out the two timestamps and carve into
                # their constituent parts (year, month, day, hour, min, sec)

                regex = r"""
                    ^(.*)         # CSKS2_SCS_B_HI_0B_HH_RD_SF_
                    (\d{4})     # 2017
                    (\d{2})     # 08
                    (\d{2})     # 03
                    (\d{2})     # 19
                    (\d{2})     # 46
                    (\d{2})     # 20
                    \_          # _
                    \d{4}       # 2017
                    \d{2}       # 08
                    \d{2}       # 03
                    \d{2}       # 19
                    \d{2}       # 46
                    \d{2}       # 26
                    \.h5$       # .h5
                    """

                if (re.search(regex,datafile,re.VERBOSE)):
                    print "Found image file " + datafile
                    match = re.search(regex,datafile,re.VERBOSE)

                    prefix = match.group(1)
                    syear = int(match.group(2))
                    smonth = int(match.group(3))
                    sday = int(match.group(4))
                    shour = int(match.group(5))
                    smin = int(match.group(6))
                    ssec = int(match.group(7))

                    timestamp = datetime(syear,smonth,sday,shour,smin,ssec)

                    # create a tuple containing the directory the image lives
                    # in and its datestamp, and add this tuple to the images
                    # dictionary (key is the prefix+date). When we are finished 
                    # each key will have as its value a list of three tuples -
                    # one for Eyja, Tind and Hekla respectively (although not
                    # sorted at this point
                    image_group = prefix + match.group(2) + match.group(3) + match.group(4)

                    tuple1 = (datadir,timestamp)
                    images[image_group].append(tuple1)

                    # Add this directory to the processed list
#                    with open(processed_file,"a+") as file:
#                        file.write(datadir + "\n")


    print " "

    for batch in images:

        if len(images[batch]) == 3:

            print "Checking batch with prefix " + batch

            # this sorts the list of three tuples by the value
            # i.e. date
            sorted_images = sorted(images[batch], key=lambda x: x[1])

            for count in range(0,3):
                print sorted_images[count][0] + " (datestamp " + \
                      str(sorted_images[count][1]) + ") is for " + sites[count]

                dir_download_date = sorted_images[count][1].strftime('%Y%m%d')
                old_datadir = path + sorted_images[count][0]
                new_datadir_short_name = dir_download_date + "_" + sites[count]
                new_datadir = path + sites[count] + "/" + new_datadir_short_name

#                new_symlink = path + sites[count] + "/" + new_datadir
#                print "Adding symlink from " + new_symlink + " to " + old_datadir
#                os.symlink(old_datadir,new_symlink)

                log = "Moved directory " + old_datadir + " to " + new_datadir
                print log

                with open(processed_file,"a+") as file:
                     file.write(log + "\n")

        	# uncomment the next line to do the deed, otherwise this is just a
        	# dry run that doesn't do anything.

                shutil.move(old_datadir, new_datadir)

        else:
            batch_length = len(images[batch])
            print "There should be three files with header " + batch
            print "but number of files found was in fact " + str(batch_length)
            print "Skipping these"

if __name__ == "__main__":
    main()

