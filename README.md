XtremIOSnap
===========
   ------------------------------------------------------------------------
   XTREMIOSNAP
   
   This example code is unsupported by both EMC and the author.
   IF YOU HAVE PROBLEMS WITH THIS SOFTWARE, THERE IS NO ONE PROVIDING TECHNICAL SUPPORT FOR RESOLVING ISSUES. USE CODE AS IS!
    
   THIS GITHUB REPOSITORY IS NOT AFFILIATED WITH EMC CORPORATION.

   Version 3.0
    
   Create and maintain snapshots on an XtremIO array utilizing the REST API interface.  Designed and tested for v3.0.
   Visual C++ 2008 Redistributable package from MS (http://www.microsoft.com/en-us/download/details.aspx?id=29 ) is required for the compiled Windows executable.
   
   If you are running this in python, it was written against Python 2.7.8 and will require the requests (2.4.3 or newer) package and the docopt package to be installed using:
   
      pip install requests
      pip install requests --upgrade (if using an older version of requests)
      pip install docopt
    
   The script has been tested back to python 2.6 on both Linux (Ubuntu 14.04) and Mac OSX Mavericks.
   
   Usage:
      
      XtremIOSnap -h | --help
      XtremIOSnap (--encode) XMS_USER XMS_PASS [--l=<log_path>] [--debug]
      XtremIOSnap XMS_IP XMS_USER XMS_PASS [--e]  [(--f --snap=<object_to_snap>)] [--n=<number_of_snaps>] [--schedule=<schedule>] [--tf=<target_folder>] [--l=<log_path>] [--debug]
      XtremIOSnap XMS_IP XMS_USER XMS_PASS [--e]  [(--v --snap=<object_to_snap>)] [--n=<number_of_snaps>] [--schedule=<schedule>] [--tf=<target_folder>] [--l=<log_path>] [--debug]

   Create and maintain snapshots of both volumes and folders on an XtremIO array utilizing the REST API interface.  Designed and tested for XtremIO v3.0+.

Arguments:

      XMS_IP                  IP or Hostname of XMS (required)
      XMS_USER                Username for XMS
      XMS_PASS                Password for XMS

Options:

      -h --help               Show this help screen

      --encode                Use this option with the XMS_USER and XMS_PASS
                            arguments to generate an encoded Username and Password
                            so the user and password don't need to be saved in
                            clear text when using in a script or task scheduler.

    --e                     If specified, will use the encoded User and Password
                            generated by the --encode option.

    --f                     Specify to signify the object to snap is a folder.

    --v                     Specify to signify the object to snap is a volume.

    --snap=<object_to_snap> Object to snap, either a volume or folder

    --n=<number_of_snaps>   Number of snapshots to retain [default: 5]

    --schedule=<schedule>   [hourly | daily | weekly] Used in naming the snapsots
                            based on how they are scheduled [default: hourly]

    --tf=<target_folder>    When specified, a _Snapshot subfolder will be created
                            in this folder.  If not used, snapshots will be saved
                            in a _Snapshot folder at the root.

    --l=<log_path>          [default: """+var_cwd+"""/XtremIOSnap.log]

    --debug



   --schedule=hourly will append the suffix .hourly.0 allong with a timestamp to the newest snapshot.  The suffix will be shifted as new snaps are taken, up to the specified number of snapshots (hourly.0 will become hourly.1, hourly.1 will become hourly.2, etc.).  By default we will keep 5 hourly snapshots.

   --schedule=daily will append the suffix .daily.0 allong with a timestamp to the newest snapshot.  The suffix will be shifted as new snaps are taken, up to the specified number of snapshots (daily.0 will become daily.1, daily.1 will become daily.2, etc.). By default we will keep 5 daily snapshots.

   --schedule=weekly will append the suffix .weekly.0 allong with a timestamp to the newest snapshot.  The suffix will be shifted as new snaps are taken, up to the specified number of snapshots (weekly.0 will become weekly.1, weekly.1 will become weekly.2, etc.). By default we will keep 5 weekly snapshot.

   If the --n= option is not used, the script will maintain a maximum of 5 snapshots, deleting snaps on a FIFO basis, depending on the --schedule=hourly/daily/weekly option.

   The --f= switch is optional, if not specified, all snapshots will be placed into the /_Snapshots folder.  This is not really necessary for anything other than aesthetics.  You can select the "Show as Snapshot Hierarchy" to view snaps with their source LUN.

