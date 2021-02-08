# tools
## rmi-dup.py
![Image of rmi-dup](https://i.imgur.com/bSXGyD4.png)  
rmi-dup.py is a command line tool that removes duplicates from specified folder.  
It uses average hashing to accomplish this.  

<pre>
Usage: rmi-dup.py -d < directory >
Removes all duplicate images from the specified directory  
Duplicates can be in different resolution and/or format  

-d, --directory   Specify directory from which to remove duplicate images  
-h, --help        Display this help and exit  
-l, --list        Use with -d to list duplicates in the specified folder  
-s, --size        Size of the hashable image. Default = 8.  
</pre>   
