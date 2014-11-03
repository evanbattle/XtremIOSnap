XtremIOSnap
===========
   ------------------------------------------------------------------------
    XTREMIOSNAP
    This example code is unsupported by both EMC and the author.
    IF YOU HAVE PROBLEMS WITH THIS SOFTWARE, THERE IS NO ONE PROVIDING TECHNICAL SUPPORT FOR RESOLVING ISSUES. USE CODE AS IS!
    
    THIS GITHUB REPOSITORY IS NOT AFFILIATED WITH EMC CORPORATION.
   
   Version 1.0
  
   Create and maintain snapshots on an XtremIO array utilizing the REST API interface.  Designed and tested for v3.0.

   The most common usage scenarios:

   -Take a snapshot on the XtremIO using an ecoded username and password:

     xtremiosnap.py -host [hostname or IP of XtremIO cluster] -ux [EncodedUname] -px [EncodedPassword] -vol [LUNName] -n [number of snaps to keep] -f [Folder]

   -Generate the encoded username and password:

     xtremiosnap.py -e -up [PlainText Uname] -pp [PlainText Password]

   -Take a snapshot on the XtremIO using plain text username and password:

     xtremiosnap.py -host [hostname or IP of XtremIO cluster] -up [PlainTextUsername] -pp [PlainTextPassword] - vol [LUNName]

   If the -n option is not used, the script will maintain a maximum of 5 snapshots, deleting snaps on a FIFO basis. 
   The -f switch is optional, if not specified, all snapshots will be placed into the /_Snapshots folder.  
   This is not really necessary for anything other than aesthetics.  
   You can select the "Show as Snapshot Hierarchy" to view snaps with their source LUN.


