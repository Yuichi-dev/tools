#! /usr/bin/python3
import os, sys, getopt, imagehash, time, PIL
from PIL import Image
import numpy as np

def print_progress_bar (iteration, total, prefix = 'Progress:', suffix = 'Complete', decimals = 1, length = 50, fill = '█', print_end = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        print_end   - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = print_end)
    if iteration == total: # Print a new line on completion
        print()

        
def find_duplicates(dir_name, print_list, hash_size, rem_ext):
    file_paths = [os.path.join(dir_name, file_name) for file_name in os.listdir(dir_name)]
    hashes = {} # {“Hash”: “Image”,…}
    duplicates = {} # File names of duplicates
    start_time = time.perf_counter()
    number_of_files = len(file_paths)
    
    print_progress_bar(0, number_of_files) # Create the progress bar
    
    for index, file_path in enumerate(file_paths):
        if os.path.isfile(file_path) and ".psd" not in file_path: # Skip .psd files since it takes forever to hash them.
            try:
                with Image.open(file_path) as img:
                    temp_hash = imagehash.average_hash(img, hash_size)
                    file_name = os.path.basename(file_path)
                    if temp_hash in hashes:
                        with Image.open(os.path.join(dir_name, hashes[temp_hash])) as img2: # Open the last duplicate and compare with current. Keep the highest res.
                            if temp_hash not in duplicates:
                                duplicates[temp_hash] = []
                            if img2.size[0] < img.size[0]:
                                duplicates[temp_hash].append(hashes[temp_hash])
                                hashes[temp_hash] = file_name
                            else:
                                duplicates[temp_hash].append(file_name)
                    else:
                        hashes[temp_hash] = file_name
            except KeyboardInterrupt: # Exit if interrupted with Ctrl+C
                print()
                sys.exit()
            except PIL.UnidentifiedImageError: # Skip all the files that PIL cant read.
                pass
        print_progress_bar(index + 1, number_of_files) # Update the progress bar
    end_time = time.perf_counter()
    print(f"Time taken: {end_time-start_time:0.4f} seconds. Total number of files checked: {number_of_files}.")
    number_of_dup = len([i for v in duplicates.values() for i in v])
    print(f"{number_of_dup} duplicate images found. Hash size was: {hash_size}")
    
    return duplicates, hashes
    
def print_duplicates(duplicates, hashes):
    for (k,v), (k2, v2) in zip(duplicates.items(), hashes.items()):
        print(f"\n{hashes[k]}\n---------------")
        for i in duplicates[k]:
            print(i)
                
def remove_duplicates(files, answer, dir_name):
    number_of_files = len([i for v in duplicates.values() for i in v])
    not_deleted = []
    print_progress_bar(0, number_of_files) # New progress bar for file deletion
    counter = 0
    for values in files.values():
        for file_name in values:
            try:
                os.remove(os.path.join(dir_name, file_name))
            except:
                not_deleted.append(os.path.join(dir_name, file_name))
            counter += 1
            print_progress_bar(counter, number_of_files) # Update the progress bar

    if len(not_deleted) != 0:
        print("Could not delete the following files:")
        for i in not_deleted:
            print(i)

def get_args(argv):
    help_text = ''.join(("Usage: rmi-dup.py -d <directory>\n",
                         "       rmi-dup.py -d <directory> -r .txt\n",  
                         "       rmi-dup.py -d <directory> -s 64\n",
                         "Removes all duplicate images from the specified directory\n",
                         "Duplicates can be in different resolution and/or format\n\n",
                         "-d, --directory    Specify directory from which to remove duplicate images\n",
                         "-h, --help         Display this help and exit\n",
                         "-l, --list         Use with -d to list duplicates in the specified folder\n",
                         "-s, --size         Size of the hashable image. Default = 8\n",
                         "-r, --remove       Remove files with given extension that share name with duplicates"))
    
    # Default args
    print_list = False
    run = False # This is so that the script runs after checking all parameters.
    hash_size = 8
    rem_ext = '' # Remove everything that shares the same name as the duplicates with chosen extension.
    
    try:
        opts, args = getopt.getopt(argv, "hld:s:r:", ["help","list","directory"])
    except:
        print("rmi-dup: invalid operand\nTry 'rmi-dup.py --help' for more information.")
        return
    if len(sys.argv) <= 1:
        print("rmi-dup: missing operand\nTry 'rmi-dup.py --help' for more information.")

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(help_text)
            sys.exit()
        elif opt in ("-d", "--directory"):
            dir_name = arg
            if os.path.exists(dir_name):
                run = True
            else:
                print(f"-d, --directory | {dir_name} does not exist")
                sys.exit()
        elif opt in ("-l", "--list"):
            print_list = True
        elif opt in ("-s", "--size"):
            try:
                hash_size = int(arg)    
            except:
                print(f"-s, --s | {arg} is not a valid number")
                sys.exit()
        elif opt in ("-r", "--remove"):
            rem_ext = arg
                
    if run == True:
        return dir_name, print_list, hash_size, rem_ext
    
if __name__ == "__main__":
    dir_name, print_list, hash_size, rem_ext = get_args(sys.argv[1:])
    duplicates, hashes = find_duplicates(dir_name, print_list, hash_size, rem_ext)
    if duplicates != {}:
        if print_list == True: # Check if -l, --list argument was given
            print_duplicates(duplicates, hashes)
        else:
            if rem_ext == '': # Check if -r, --remove argument was given
                answer = input("Do you want to delete all duplicate images?\nWrite 'delete' to confirm.\n")
            else:
                answer = input(f"Do you want to delete all duplicate images? This will also delete {rem_ext} files with same name as the duplicates\nWrite 'delete' to confirm.\n")
            if answer == "delete":
                print("Removing duplicates")
                remove_duplicates(duplicates, answer, dir_name)
                if rem_ext != '': # Check if -r, --remove argument was given
                    files_ext = {k:[os.path.splitext(v[i])[0]+rem_ext for i in range(len(v))] for (k, v) in duplicates.items()} # replaces extension with rem_ext
                    print(f"Removing {rem_ext} files")
                    remove_duplicates(files_ext, answer, dir_name)