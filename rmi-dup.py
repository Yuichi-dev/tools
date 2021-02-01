#! /usr/bin/python3
import os, sys, getopt, imagehash, time
from PIL import Image

# Remove all duplicates. Works if the only difference is resolution and/or fileformat.
# Made by Jussi Lehtonen
def print_progress_bar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
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
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

def rm_dup(dir_name, print_list):
    file_names = os.listdir(dir_name)
    hashes = {} # {“Hash”: “Image”,…}
    duplicates = [] # File names of duplicates
    hash_size = 8 # Image will be resized to 8x8
    total_items = len(file_names) # Used for the progress bar
    start_time = time.perf_counter()
    
    print_progress_bar(0, total_items, prefix = 'Progress:', suffix = 'Complete', length = 50)
    for i, file_name in enumerate(file_names):
        file_path = os.path.join(dir_name, file_name)
        if os.path.isfile(file_path) and ".psd" not in file_path: # Skip .psd files since it takes forever to hash them.
            try:
                with Image.open(file_path) as img:
                    temp_hash = imagehash.average_hash(img, hash_size)
                    if temp_hash in hashes:
                        
                        # Open the previous duplicate and compare with current file.
                        # Keep the one with bigger resolution
                        img2 = Image.open(os.path.join(dir_name, hashes[temp_hash]))                      
                        if img2.size[0] < img.size[0]:
                            duplicates.append(hashes[temp_hash])
                            hashes[temp_hash] = file_name
                        else:
                            duplicates.append(file_name)
                    else:
                        hashes[temp_hash] = file_name
            except:
                pass
        print_progress_bar(i + 1, total_items, prefix = 'Progress:', suffix = 'Complete', length = 50) # Update the progress bar
    end_time = time.perf_counter()
    print(f"Time taken: {end_time-start_time:0.4f} seconds. Total number of files checked: {total_items}")
    print(f"{len(duplicates)} duplicate images found.")    
    if len(duplicates) != 0:
        if print_list == True:
            print("Duplicates found:")
            for i in duplicates:
                print(i)
        else:
            answer = input("Do you want to delete all duplicate images?\nWrite 'delete' to confirm.\n")
            if answer == "delete":
                not_deleted = []
                print_progress_bar(0, len(duplicates), prefix = 'Progress:', suffix = 'Complete', length = 50)
                for i, fn in enumerate(duplicates):
                    try:
                        os.remove(os.path.join(dir_name, fn))
                    except:
                        not_deleted.append(os.path.join(dir_name, fn))
                    print_progress_bar(i + 1, len(duplicates), prefix = 'Progress:', suffix = 'Complete', length = 50)

                if len(not_deleted) != 0:
                    print("Could not delete some files.\nMake sure the following files are not in use.")
                    for i in not_deleted:
                        print(i)

def main(argv):
    help_text = ''.join(("Usage: rmi-dup.py -d <directory>\n",
                         "Removes all duplicate images from the specified directory\n",
                         "Duplicates can be in different resolution and/or format\n\n",
                         "-d, --directory    Specify directory from which to remove duplicate images\n",
                         "-h, --help         Display this help and exit\n",
                         "-l, --list         Use with -d to list duplicates in the specified folder"))
    print_list = False
    
    try:
        opts, args = getopt.getopt(argv, "hld:", ["help","list","directory"])
    except:
        print("rmi-dup: invalid operand\nTry 'rmi-dup.py --help' for more information.")
        return
    if len(sys.argv) <= 1:
        print("rmi-dup: missing operand\nTry 'rmi-dup.py --help' for more information.")
    for opt, arg in opts:
        if opt in ("-l", "--list"):
            print_list = True
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(help_text)
            sys.exit()
        elif opt in ("-d", "--directory"):
            dir_name = arg
            if os.path.exists(dir_name):
                rm_dup(dir_name, print_list)
            else:
                print(f"{dir_name} does not exist")
if __name__ == "__main__":
    main(sys.argv[1:])