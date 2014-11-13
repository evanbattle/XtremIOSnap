XtremIOSnap
===========
   ------------------------------------------------------------------------
   XTREMIOSNAP
   
   This example code is unsupported by both EMC and the author.
   IF YOU HAVE PROBLEMS WITH THIS SOFTWARE, THERE IS NO ONE PROVIDING TECHNICAL SUPPORT FOR RESOLVING ISSUES. USE CODE AS IS!
    
   THIS GITHUB REPOSITORY IS NOT AFFILIATED WITH EMC CORPORATION.

   Version 2.5
    
   Create and maintain snapshots on an XtremIO array utilizing the REST API interface.  Designed and tested for v3.0.
   Visual C++ 2008 Redistributable package from MS (http://www.microsoft.com/en-us/download/details.aspx?id=29 ) is required for the compiled Windows executable.
   
   If you are running this in python, it was written against Python 2.7.8 and will require the requests package to be installed using:
   
      pip install requests
    
   To run in Linux or MacOS, make sure to use the -l [Logfile] option.  The script have been tested back to python 2.6 on both Linux (Ubuntu 14.04) and Mac OSX Mavericks.
   
   The most common usage scenarios:

   -Take a snapshot on the XtremIO using an ecoded username and password:

      xtremiosnap.py -host [hostname or IP of XtremIO cluster] -ux [EncodedUname] -px [EncodedPassword] -vol [LUNName] -n [number of snaps to keep] -[hourly/daily/weekly] -f [Folder]
      
      xtremiosnap.py -host [hostname or IP of XtremIO cluster] -ux [EncodedUname] -px [EncodedPassword] -fol [FolderName] -n [number of snaps to keep] -[hourly/daily/weekly] -f [Folder]

   -Generate the encoded username and password:

      xtremiosnap.py -e -up [PlainText Uname] -pp [PlainText Password]

   -Take a snapshot on the XtremIO using plain text username and password:

      xtremiosnap.py -host [hostname or IP of XtremIO cluster] -up [PlainTextUsername] -pp [PlainTextPassword] - vol [LUNName] -[hourly/daily/weekly]

   -hourly will append the suffix .hourly.0 allong with a timestamp to the newest snapshot.  The suffix will be shited as new snaps are taken, up to the specified number of snapshots (hourly.0 will become hourly.1, hourly.1 will become hourly.2, etc.).  By default we will keep 5 hourly snapshots.

   -daily will append the suffix .daily.0 allong with a timestamp to the newest snapshot.  The suffix will be shited as new snaps are taken, up to the specified number of snapshots (daily.0 will become daily.1, daily.1 will become daily.2, etc.). By default we will keep 5 daily snapshots.

   -weekly will append the suffix .weekly.0 allong with a timestamp to the newest snapshot.  The suffix will be shited as new snaps are taken, up to the specified number of snapshots (weekly.0 will become weekly.1, weekly.1 will become weekly.2, etc.). By default we will keep 1 weekly snapshot.

   If the -n option is not used, the script will maintain a maximum of 5 snapshots, deleting snaps on a FIFO basis, depending on the -hourly/daily/weekly option.

   The -f switch is optional, if not specified, all snapshots will be placed into the /_Snapshots folder.  This is not really necessary for anything other than aesthetics.  You can select the "Show as Snapshot Hierarchy" to view snaps with their source LUN.

