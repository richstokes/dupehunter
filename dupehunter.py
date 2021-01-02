#!/usr/bin/env python3
import sys
import signal
import os
import hashlib
import argparse
import questionary
from pandas import *

file_sizes = []
size_dupes = []
file_hashes = []
dupe_files_array = []
pandas.set_option('display.max_rows', None)
pandas.set_option('display.max_colwidth', 100)

def signal_handler(sig, frame):
    """Handle CTRL+C"""
    print('Quitting..')
    sys.exit(1)
signal.signal(signal.SIGINT, signal_handler)

def get_file_sizes(path):
    """Walk path and get each files size"""
    for dirName, subdirs, fileList in os.walk(path):
        print('🕵🏼‍♂️  Scanning dir %s' % dirName)

        for filename in fileList:
            file_path = os.path.join(dirName, filename)
            print('🕵🏼‍♂️  Checking file size on: %s.. ' % (file_path), end='')
            try:
                file_size = os.path.getsize(file_path)
                print(file_size)
                file_sizes.append([file_path, file_size])
            except OSError:
                print("Unable to get file size")

def get_file_sizes_with_scanlist(path, scanlist):
    """Walk path and get each files size, if it's extension is in the scanlist"""
    for dirName, subdirs, fileList in os.walk(path):
        print('🕵🏼‍♂️  Scanning dir %s' % dirName)

        for filename in fileList:
            file_path = os.path.join(dirName, filename)
            # print(filename.rpartition('.')[-1])
            if filename.rpartition('.')[-1].lower() in scanlist:
                print('🕵🏼‍♂️  Checking file size on: %s.. ' % (file_path), end='')
                try:
                    file_size = os.path.getsize(file_path)
                    print(file_size)
                    file_sizes.append([file_path, file_size])
                except OSError:
                    print("Unable to get file size")
            # else:
            #     print('Skipping %s' % (filename))
            #     print(filename.rpartition('.')[-1])


def check_dupe_file_sizes():
    """Iterate through the list of file sizes and extract the duplicates"""
    print('🕵🏼‍♂️  Looking for duplicate file sizes in %d items..' % (len(file_sizes)))
    counts = {}

    for elem in file_sizes:
        # add 1 to counts for this string, creating new element at this key
        # with initial value of 0 if needed
        counts[elem[1]] = counts.get(elem[1], 0) + 1

    uniques_array = []
    dupes_array = []
    for elem in file_sizes:
        # check that there's only 1 instance of this element.
        if counts[elem[1]] == 1:
            uniques_array.append(elem)
        else:
            dupes_array.append(elem)

    # print('Unique file sizes (%s):' % (len(uniques_array)))
    # print(uniques_array)

    if dupes_array:
        print('👯 Found %s files with identifcal file sizes:' % (len(dupes_array)))
        print(DataFrame(data=dupes_array,columns=["Filename","Size"]))
        for file in dupes_array:
            get_file_hashes(file[0])

def get_file_hashes(file_path):
    """Get the MD5 sum for a given file"""
    print("🤖 Getting file hash for: %s.. " % (file_path), end='')
    try:
        file_hash = hashlib.md5(open(file_path,'rb').read()).hexdigest()
        print(file_hash)
        file_hashes.append([file_path, file_hash])
    except PermissionError:
        print("Could not open file, permissions error.")
    except:
        print("Unexpected error reading file")

def check_dupe_file_hashes():
    """Cheks for duplicate MD5 hashes"""
    print('🕵🏼‍♂️  Looking for duplicate file hashes in %d items..' % (len(file_hashes)))
    counts = {}

    for elem in file_hashes:
        # add 1 to counts for this string, creating new element at this key
        # with initial value of 0 if needed
        counts[elem[1]] = counts.get(elem[1], 0) + 1

    uniques_array = []
    for elem in file_hashes:
        if counts[elem[1]] == 1:
            uniques_array.append(elem)
        else:
            dupe_files_array.append(elem)

    # print('Unique file hashes (%s):' % (len(uniques_array)))
    # print(uniques_array)

    # if dupe_files_array:
    #     print('Duplicated file hashes(%s):' % (len(dupe_files_array)))
    #     print(dupe_files_array)

def print_results():
    """Display results"""
    if len(dupe_files_array) == 0:
        print("✅ No duplicate files found!")
    else:
        print("👯 Found the following duplicate files:")
        print(DataFrame(data=sorted(dupe_files_array, key=lambda x : x[1]),
            columns=["Filename","Hash"]))

def delete_list():
    """Provide a list of duplicate files to delete from"""
    if dupe_files_array:
        print('\n🗑  Looking up files to delete..')
        seen_hashes = []

        for f in dupe_files_array:
            files_to_delete = []
            files_to_delete.append("Skip!")

            if f[1] in seen_hashes:
                pass
            else:
                for row, i in enumerate(dupe_files_array):
                    try:
                        column = i.index(f[1])
                    except ValueError:
                        continue
                    # print(row, column, end='') # Debug - shows location in 2d array
                    # print(dupe_files_array[row][0]) # Get file name of row that matches the hash we are searching on
                    files_to_delete.append(dupe_files_array[row][0])
                    seen_hashes.append(f[1])
                # print('Files to delete options: %s' % (files_to_delete)) # Debug
                selected_file = questionary.select(
                    "Which file would you like to delete?",
                    choices=files_to_delete).ask()  # returns value of selection

                if selected_file == "Skip!":
                    print('Skipping..')
                else:
                    print('Deleting:', selected_file)
                    try:
                        os.remove(selected_file)
                    except OSError:
                        print('Unable to delete', selected_file)

def main():
    """Main"""
    # Process arguments
    parser = argparse.ArgumentParser(description='A tool for checking for duplicate files.')
    parser.add_argument('-p','--path', nargs='*', default=".",
        help='<Required> File system path to scan for duplicates on')
    parser.add_argument('-s','--scanlist', nargs='*', default="",
        help='<Optional> Text file containg list of file extensions to check')
    parser.add_argument('-d','--deletefiles', nargs='*', default="",
        help='<Optional> If enabled, will prompt you to delete one of the clones')
    args = parser.parse_args()
    scanlist = args.scanlist
    scanpath = args.path
    deletefiles = args.deletefiles

    print("🐶 Started dupehunter")

    if scanlist: # Read lines from scanlist file into array
        with open(scanlist[0]) as f:
            content = f.readlines()
        scanlist = [x.strip() for x in content]

    # Do the things
    if scanlist:
        print("🐶 Checking for duplicate files (with extensions %s) in %s" % (scanlist, scanpath[0]))
        get_file_sizes_with_scanlist(scanpath[0], scanlist)
    else:
        print("🐶 Checking for duplicate files in %s" % (scanpath[0]))
        get_file_sizes(scanpath[0])

    check_dupe_file_sizes()
    check_dupe_file_hashes()
    print_results()

    if deletefiles:
        delete_list()

if __name__ == "__main__":
    main()
