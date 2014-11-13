#-------------------------------------------------------------------------------
# Name:        XtremIOSnap
# Purpose:     Create and delete snapshots on an XtremIO array using the RESTful
#              Services.
#
# Author:      Evan R. Battle
#              Sr. Systems Engineer, EMC
#              evan.battle@emc.com
#
# Version:     2.5
#
# Created:     11/13/2014
#
# Licence:     Open to distribute and modify.  This example code is unsupported
#              by both EMC and the author.  IF YOU HAVE PROBLEMS WITH THIS
#              SOFTWARE, THERE IS NO ONE PROVIDING TECHNICAL SUPPORT FOR
#              RESOLVING ISSUES. USE CODE AS IS!
#
#              THIS CODE IS NOT AFFILIATED WITH EMC CORPORATION.
#-------------------------------------------------------------------------------

##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##  Load Modules
##
##  Requires the requests module, install via <pip install requests>
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
import sys
import os
import datetime
import signal
import logging
import inspect
import argparse
import requests ##<--This should be the only module that will need to be installed via pip
from requests.auth import HTTPBasicAuth
import json
import textwrap
import base64

var_cwd =  os.getcwd()

##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##  Parse CLI Arguments
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent('''\
        ------------------------------------------------------------------------
        XTREMIOSNAP
        \n
        Version 2.0
        \n
        Create and maintain snapshots on an XtremIO array utilizing the REST
        API interface.  Designed and tested for v3.0.
        \n
            The most common usage scenarios:

            -Take a snapshot on the XtremIO using an ecoded username and password:

                xtremiosnap.py -host [hostname or IP of XtremIO cluster] -ux \
[EncodedUname] -px [EncodedPassword] -vol [LUNName] -n \
[number of snaps to keep] -[hourly/daily/weekly] -f [Folder]

            -Generate the encoded username and password:

                xtremiosnap.py -e -up [PlainText Uname] -pp [PlainText Password]

            -Take a snapshot on the XtremIO using plain text username and password:

                xtremiosnap.py -host [hostname or IP of XtremIO cluster] -up \
[PlainTextUsername] -pp [PlainTextPassword] - vol [LUNName] -[hourly/daily/weekly]

        -hourly will append the suffix .hourly.0 allong with a timestamp to the \
newest snapshot.  The suffix will be shited as new snaps are taken, up to the \
specified number of snapshots (hourly.0 will become hourly.1, hourly.1 will become \
hourly.2, etc.).  By default we will keep 5 hourly snapshots.

        -daily will append the suffix .daily.0 allong with a timestamp to the \
newest snapshot.  The suffix will be shited as new snaps are taken, up to the \
specified number of snapshots (daily.0 will become daily.1, daily.1 will become \
daily.2, etc.). By default we will keep 5 daily snapshots.

        -weekly will append the suffix .weekly.0 allong with a timestamp to the \
newest snapshot.  The suffix will be shited as new snaps are taken, up to the \
specified number of snapshots (weekly.0 will become weekly.1, weekly.1 will become \
weekly.2, etc.). By default we will keep 1 weekly snapshot.

        If the -n option is not used, the script will maintain a maximum of 5 \
snapshots, deleting snaps on a FIFO basis, depending on the -hourly/daily/weekly \
option.

        The -f switch is optional, if not specified, all snapshots will be placed \
into the /_Snapshots folder.  This is not really necessary for anything other than \
aesthetics.  You can select the "Show as Snapshot Hierarchy" to view snaps with \
their source LUN.


        \n
        ------------------------------------------------------------------------
        '''),
        epilog='\n')
parser.add_argument(
    '-host','--host',
    dest='XMS_IP',
    help='Host name or IP address of the XMS.'
    )
parser.add_argument(
    '-e','--encode',
    action='store_true',
    default=False,
    dest='var_encode',
    help='This will encode the given username and password so they can be used \
        in batch processes without storing them in plain text'
    )
parser.add_argument(
    '-up','--userplain',
    dest='plain_XMS_USERID',
    help='Plain text Username'
    )
parser.add_argument(
    '-pp','--passplain',
    dest='plain_XMS_PASSWORD',
    help='Plain text Password'
    )
parser.add_argument(
    '-ux','--userencoded',
    dest='encoded_XMS_USERID',
    help='Encoded Username'
    )
parser.add_argument(
    '-px','--passencoded',
    dest='encoded_XMS_PASSWORD',
    help='Encoded Password'
    )
parser.add_argument(
    '-vol','--volume',
    dest='snap_src',
    help='The name of the LUN to be snapshotted'
    )
parser.add_argument(
    '-n','--numsnaps',
    dest='num_snaps_to_retain',
    help='Overrides the default number of snaps to retain of 5.'
    )
parser.add_argument(
    '-f','--folder',
    dest='var_snap_tgt_folder',
    help='Optional folder used to organize snapshots in a logical hierarchy, \
        using the "Show as Snapshot Hierarchy" option in the GUI may make more \
        sense than using this option.'
    )
parser.add_argument(
    '-hourly','--hourly',
    action='store_true',
    default=False,
    dest='var_hourly',
    help='This will create this as an hourly snapshot.  The snapshot will be \
        called volumename.hourly.0.  If this option is set, the default number \
        of snaps will be 5 unless the -n option is used.'
    )
parser.add_argument(
    '-daily','--daily',
    action='store_true',
    default=False,
    dest='var_daily',
    help='This will create this as a daily snapshot.  The snapshot will be \
        called volumename.daily.0.  If this option is set, the default number \
        of snaps will be 5 unless the -n option is used.'
    )
parser.add_argument(
    '-weekly','--weekly',
    action='store_true',
    default=False,
    dest='var_weekly',
    help='This will create this as a weekly snapshot.  The snapshot will be \
        called volumename.weekly.0.  If this option is set, the default number \
        of snaps will be 1 unless the -n option is used.'
    )
parser.add_argument(
    '-l','--log',
    dest='var_Logfile',
    default= var_cwd + '\\XtremIOSnap.log',
    help='Path to the log file.  by default it will be '+var_cwd+'\\XtremIOSnap.log'
    )

if len(sys.argv)==1:
    parser.print_help()
    sys.exit(1)

args=parser.parse_args()

##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##  MAIN FUNCTION
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def main():

    main_logger = def_FuncLogger(logging.DEBUG,logging.INFO)
    main_logger.info('Running XtremIO Snap Script')

    if args.var_encode is True: ##<--Neither the encoded or plain text username/password are stored anywhere
        main_logger.info('Encoding User ID:')
        main_logger.info('UserID hash is '+base64.b64encode(args.plain_XMS_USERID))
        main_logger.info('Password hash is '+base64.b64encode(args.plain_XMS_PASSWORD))
        main_logger.info('Use the hash vaues as the User ID and Password when using the -ux and -px switches.')
        sys.exit(0)

    if args.var_weekly == True:
        if args.num_snaps_to_retain == None:
            main_logger.info('Using the WEEKLY option')
            num_snaps_to_retain = 1
        else:
            num_snaps_to_retain = args.num_snaps_to_retain
        newsnapsuffix = '.weekly.'
    elif args.var_daily == True:
        if args.num_snaps_to_retain == None:
            main_logger.info('Using the DAILY option')
            num_snaps_to_retain = 5
        else:
            num_snaps_to_retain = args.num_snaps_to_retain
        newsnapsuffix = '.daily.'
    elif args.var_hourly == True:
        if args.num_snaps_to_retain == None:
            main_logger.info('Using the HOURLY option')
            num_snaps_to_retain = 5
        else:
            num_snaps_to_retain = args.num_snaps_to_retain
        newsnapsuffix = '.hourly.'
    else:
        main_logger.info('No hourly, daily, or weekly option specifed. Exiting.')
        sys.exit(1)
    main_logger.info('Using the '+newsnapsuffix+' option')

    XMS_IP = args.XMS_IP
    main_logger.info('Target XMS system is - '+XMS_IP)

    XMS_USERID, XMS_PASSWORD = def_CheckEncoding(
        args.plain_XMS_USERID,
        args.plain_XMS_PASSWORD,
        args.encoded_XMS_USERID,
        args.encoded_XMS_PASSWORD
        )

    if args.snap_src == None:
        main_logger.info('No volume specified.  Exiting.')
        main_logger.error('NO VOLUME SPECIFIED')
        sys.exit(1)
    else:
        snap_src = args.snap_src
        main_logger.info('Volume selected to snapshot = '+snap_src)

    SnapFolder = '_Snapshots'

    var_snap_tgt_folder = args.var_snap_tgt_folder ## this should be an optional variable, if the customer wants to organize snapshots under a folder hierarchy
    bool_create_folder = True ## will change to False if the /_Snapshots folder already exists

    if var_snap_tgt_folder == None:
        snap_tgt_folder = SnapFolder
    else:
        snap_tgt_folder = var_snap_tgt_folder+'/'+SnapFolder
    main_logger.info('Snapshot will be stored in the folder: '+snap_tgt_folder)

    folder_list = def_XMSGetRequest(
        XMS_IP,
        XMS_USERID,
        XMS_PASSWORD,
        'types/volume-folders',
        'folders'
        )

    for folder_list_rs in folder_list:
        if folder_list_rs['name'] == '/'+snap_tgt_folder:
            bool_create_folder = False
            main_logger.info('The target snapshot folder, '+folder_list_rs['name']+' already exists.')

    if bool_create_folder is True:
        folder_create = def_CreateXMSFolder(
            XMS_IP,
            XMS_USERID,
            XMS_PASSWORD,
            SnapFolder,
            var_snap_tgt_folder
            )

    main_logger.info('Using '+snap_tgt_folder+' for snapshots')

    main_logger.info('Will retain '+str(num_snaps_to_retain)+' snapshots for volume: '+snap_src)

    timestamp = datetime.datetime.now()
    timestamp = timestamp.isoformat()
    arr_timestamp = timestamp.split('.',2) ##<--stripping the microseconds from the timestamp for aesthetics

    newsnap = snap_src+'_'+arr_timestamp[0]+newsnapsuffix+'0'##<--sets the newly created snapshot to always be .0

    vol_snap_list = def_GetSnapList(XMS_IP,XMS_USERID,XMS_PASSWORD,snap_src)##<--Initial list of snapshots

    arr_vol_snap_list_component = []
    for vol_snap_list_rs in vol_snap_list:
        if newsnapsuffix in vol_snap_list_rs[1]:
            arr_vol_snap_list_component.append(vol_snap_list_rs[1])

    arr_vol_snap_list_component.sort(reverse=True)
    for y in range(len(arr_vol_snap_list_component)): ##<--shifting the suffix of each matchin snap by 1
        if newsnapsuffix in arr_vol_snap_list_component[y]:
            list_snapname = []
            try:
                list_snapname = arr_vol_snap_list_component[y].split('.',3)
            except:
                pass
            rename_to =list_snapname[0]+newsnapsuffix+str(y+1)
            renamestatus = def_RenameSnap(
                XMS_IP,
                XMS_USERID,
                XMS_PASSWORD,
                arr_vol_snap_list_component[y],
                rename_to
                )

    vol_snap = def_CreateXMSSnap(
        XMS_IP,
        XMS_USERID,
        XMS_PASSWORD,
        'types/snapshots',
        snap_src,
        newsnap,
        snap_tgt_folder
        )

    vol_snap_list = def_GetSnapList(XMS_IP,XMS_USERID,XMS_PASSWORD,snap_src)##<--Refresh the snap list

    arr_vol_snap_list_component = []
    for vol_snap_list_rs in vol_snap_list:
        if newsnapsuffix in vol_snap_list_rs[1]:
            arr_vol_snap_list_component.append(vol_snap_list_rs[1])

    arr_vol_snap_list_component.sort(reverse=False)

    for x in xrange(len(arr_vol_snap_list_component)-(int(num_snaps_to_retain))):
        if newsnapsuffix in arr_vol_snap_list_component[x]:
            main_logger.info(str(x)+': '+ arr_vol_snap_list_component[x])
            snap_parent_name, snap_creation_time, snap_space_consumed, arr_snap_lun_mapping = def_XMSGetSnapDetails(
                XMS_IP,
                XMS_USERID,
                XMS_PASSWORD,
                arr_vol_snap_list_component[x]
                )
            main_logger.info('Parent Volume of '+arr_vol_snap_list_component[x]+' = '+snap_parent_name)
            main_logger.info('Snap was created on '+snap_creation_time)
            main_logger.info('Snap is using '+ str((float(snap_space_consumed)/1024)/1024)+' GB')

            arr_lun_mapping_component = []

            if len(arr_snap_lun_mapping) > 0:##<--checking to see if an active LUN mapping exists
                for rs in arr_snap_lun_mapping:
                    arr_lun_mapping_component = [[y] for y in rs[0]]
                    arr_lun_mapping_component =str(arr_lun_mapping_component[1])
                    arr_lun_mapping_component = arr_lun_mapping_component.replace('[u\'','')
                    arr_lun_mapping_component = arr_lun_mapping_component.replace('\']','')
                    main_logger.info('Snapshot '+arr_vol_snap_list_component[x]+' is currently mapped to '+arr_lun_mapping_component+', it will not be deleted.')
            else:
                main_logger.info('No hosts mapped to '+arr_vol_snap_list_component[x]+', it will be deleted.')
                delete_status = def_DeleteSnap(
                    XMS_IP,
                    XMS_USERID,
                    XMS_PASSWORD,
                    arr_vol_snap_list_component[x]
                    )

    main_logger.info('Complete!')

    sys.exit(0)

##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##  def_RenameSnap
##
##  Takes the source snap (XMS_SRC_SNAP) and renames it to the variable given in
##  XMS_NEWSNAP.  Returns only the HTTP response code.
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def def_RenameSnap(
    XMS_IP,
    XMS_USERID,
    XMS_PASSWORD,
    XMS_SRC_SNAP,
    XMS_NEWSNAP
    ):

    renamesnap_logger = def_FuncLogger(logging.DEBUG,logging.INFO)
    renamesnap_logger.debug('Starting def_CreateXMSSnap module')

    payload = '{"vol-name": \"'+XMS_NEWSNAP+'\"}'

    j=json.loads(payload)

    renamesnap_logger.debug('JSON dumps: '+json.dumps(j))

    try:
        resp = requests.put(
            'https://'+XMS_IP+'/api/json/types/volumes/?name='+XMS_SRC_SNAP,
            auth=HTTPBasicAuth(XMS_USERID,XMS_PASSWORD),
            verify=False,
            json=j
            )
    except requests.exceptions.RequestException as e:
        renamesnap_logger.info(e)
        renamesnap_logger.error(e)
        sys.exit(1)

    renamesnap_logger.debug('Payload: '+json.dumps(payload))
    if resp.status_code == 200:
        renamesnap_logger.info('Response code received from XMS for RenameSnap: <'+str(resp.status_code)+'>')
        renamesnap_logger.info(XMS_SRC_SNAP+' was renamed to '+XMS_NEWSNAP)
        renamesnap_logger.debug(resp.text)
    else:
        renamesnap_logger.info('Response code received from XMS for RenameSnap: <'+str(resp.status_code)+'>')
        renamesnap_logger.info(resp.text)

    return resp

##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##  def_CheckEncoding
##
##  Takes the UserID and Password given as arguments, checks whether they are
##  encoded or not and returns the actual userID (XMS_USERID) and password
##  (XMS_PASSWORD).
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def def_CheckEncoding(
    plain_XMS_USERID,
    plain_XMS_PASSWORD,
    encoded_XMS_USERID,
    encoded_XMS_PASSWORD
    ):

    encoding_logger = def_FuncLogger(logging.DEBUG,logging.INFO)
    encoding_logger.debug('Starting def_CheckEncoding module')

    if plain_XMS_USERID == None:
        if encoded_XMS_USERID == None:
            encoding_logger.info('No username specified, exiting.')
            encoding_logger.error('No username specified, exiting.')
            sys.exit(1)
        else:
            encoding_logger.info('User ID is encoded.')
            try:
                XMS_USERID = base64.b64decode(encoded_XMS_USERID)
            except:
                encoding_logger.info('Invalid encoded User ID, exiting.')
                encoding_logger.error('Invalid encoded User ID, exiting.')
                sys.exit(1)
    else:
        encoding_logger.info('User ID is plain text.')
        XMS_USERID = plain_XMS_USERID

    if plain_XMS_PASSWORD == None:
        if encoded_XMS_PASSWORD == None:
            encoding_logger.info('No password specified, exiting')
            encoding_logger.error('No password specified, exiting')
            sys.exit(1)
        else:
            encoding_logger.info('Password is encoded.')
            try:
                XMS_PASSWORD = base64.b64decode(encoded_XMS_PASSWORD)
            except:
                encoding_logger.info('Invalid encoded Password, exiting.')
                encoding_logger.error('Invalid encoded Password, exiting.')
                sys.exit(1)
    else:
        encoding_logger.info('Password is plain text')
        XMS_PASSWORD = plain_XMS_PASSWORD
    return (
        XMS_USERID,
        XMS_PASSWORD
        )

##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##  def_XMSGetSnapDetails
##
##  Takes a snapshot name (XMS_SNAPNAME) and returns the parent LUN name, snap
##  creation time, logical space consumed, and a list of mapped LUNs (if any).
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def def_XMSGetSnapDetails(
    XMS_IP,
    XMS_USERID,
    XMS_PASSWORD,
    XMS_SNAPNAME
    ):

    getsnapdetails_logger = def_FuncLogger(logging.DEBUG,logging.INFO)
    getsnapdetails_logger.debug('Starting def_XMSGetSnapDetails module')

    try:
        resp = requests.get(
            'https://'+XMS_IP+'/api/json/types/snapshots/?name='+XMS_SNAPNAME,
            auth=HTTPBasicAuth(XMS_USERID,XMS_PASSWORD),
            verify=False
            )
    except requests.exceptions.RequestException as e:
        getsnapdetails_logger.info(e)
        getsnapdetails_logger.error(e)
        sys.exit(1)

    if resp.status_code == 200:
        getsnapdetails_logger.info('Response code received from XMS for GetSnapDetails: <'+str(resp.status_code)+'>')
        getsnapdetails_logger.debug(resp.text)
        getsnapdetails_logger.info('Snap details successfully retrieved.')
    else:
        getsnapdetails_logger.info('Response code received from XMS for GetSnapDetails: <'+str(resp.status_code)+'>')
        getsnapdetails_logger.info(resp.text)

    arr_ancestor_vol_id = []
    arr_ancestor_vol_id = resp.json()['content']['ancestor-vol-id']
    data_ancestor_vol_id_name = arr_ancestor_vol_id[1]
    data_creation_time = resp.json()['content']['creation-time']
    data_logical_space_consumed = resp.json()['content']['logical-space-in-use']
    arr_lun_mapping_list = []
    arr_lun_mapping_list = resp.json()['content']['lun-mapping-list']
    return (
        data_ancestor_vol_id_name,
        data_creation_time,
        data_logical_space_consumed,
        arr_lun_mapping_list
        )

##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##  def_CreateXMSSNAP
##
##  Takes a URL (XMS_URL) for types/volumes(this can be hardcoded, maybe i'll
##  change it in a future version), a source LUN name (XMS_SRC_VOL), a target
##  snapshot name (XMS_TGT_VOL), and a folder (XMS_FOLDER) and creates a snapshot
##  in the specified folder.  This only returns the HTTP response code.
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def def_CreateXMSSnap(
    XMS_IP,
    XMS_USERID,
    XMS_PASSWORD,
    XMS_URL,
    XMS_SRC_VOL,
    XMS_TGT_VOL,
    XMS_FOLDER
    ):

    createsnap_logger = def_FuncLogger(logging.DEBUG,logging.INFO)
    createsnap_logger.debug('Starting def_CreateXMSSnap module')

    payload = '{\
        "ancestor-vol-id": \"'+XMS_SRC_VOL+'\" , \
        "snap-vol-name": \"'+XMS_TGT_VOL+'\" ,\
        "folder-id": \"/'+XMS_FOLDER+'\" \
        }'

    j=json.loads(payload)

    createsnap_logger.debug('JSON dumps: '+json.dumps(j))

    try:
        resp = requests.post(
            'https://'+XMS_IP+'/api/json/'+XMS_URL,
            auth=HTTPBasicAuth(XMS_USERID,XMS_PASSWORD),
            verify=False,
            json=j
            )
    except requests.exceptions.RequestException as e:
        createsnap_logger.info(e)
        createsnap_logger.error(e)
        sys.exit(1)

    createsnap_logger.debug('Payload: '+json.dumps(payload))
    if resp.status_code == 201:
        createsnap_logger.info('Create Snap Status: <'+str(resp.status_code)+'>')
        createsnap_logger.debug(resp.text)
    else:
        createsnap_logger.info('Create Snap Status: <'+str(resp.status_code)+'>')
        createsnap_logger.info(resp.text)

    return resp

##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##  def_CreateXMSFolder
##
##  Creates a folder (XMS_FOLDER) under the parent folder (XMS_PARENTFOLDER).
##  Returns only the HTTP response code.
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def def_CreateXMSFolder(
    XMS_IP,
    XMS_USERID,
    XMS_PASSWORD,
    XMS_FOLDER,
    XMS_PARENTFOLDER
    ):

    createfolder_logger = def_FuncLogger(logging.DEBUG,logging.INFO)
    createfolder_logger.debug('Starting def_CreateXMSFolder module')

    payload = '{\
        "caption": \"'+XMS_FOLDER+'\" , \
        "parent-folder-id": \"/'+XMS_PARENTFOLDER+'\" \
        }'
    j=json.loads(payload)
    createfolder_logger.debug('JSON dumps: '+json.dumps(j))

    try:
        resp = requests.post(
            'https://'+XMS_IP+'/api/json/types/volume-folders',
            auth=HTTPBasicAuth(XMS_USERID,XMS_PASSWORD),
            verify=False,
            json=j
            )
    except requests.exceptions.RequestException as e:
        createfolder_logger.info(e)
        createfolder_logger.error(e)
        sys.exit(1)

    createfolder_logger.debug('Payload: '+payload)

    if resp.status_code == 201:
        createfolder_logger.info('Create Folder Status: <'+str(resp.status_code)+'>')
        createfolder_logger.debug(resp.text)
    else:
        createfolder_logger.info('Create Folder Status: <'+str(resp.status_code)+'>')
        createfolder_logger.info(resp.text)

    return resp

##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##  def_XMSGetRequest
##
##  This is a flexible function that takes a partial URL (types/volumes, etc)
##  and a JSON key and returns the value of that key.
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def def_XMSGetRequest(
    XMS_IP,
    XMS_USERID,
    XMS_PASSWORD,
    XMS_URL,
    JSON_KEY
    ):

    getrequest_logger = def_FuncLogger(logging.DEBUG,logging.INFO)
    getrequest_logger.debug('Starting XMSGetRequest Module')

    try:
        resp = requests.get(
            'https://'+XMS_IP+'/api/json/'+XMS_URL,
            auth=HTTPBasicAuth(XMS_USERID,XMS_PASSWORD),
            verify=False
            )
    except requests.exceptions.RequestException as e:
        getrequest_logger.info(e)
        getrequest_logger.error(e)
        sys.exit(1)

    if resp.status_code == 200:
        getrequest_logger.info('Get Request Status: <'+str(resp.status_code)+'>')
        getrequest_logger.debug(resp.text)
    else:
        getrequest_logger.info('Get Request Status: <'+str(resp.status_code)+'>')
        getrequest_logger.info(resp.text)
        sys.exit(1)

    data = resp.json()[JSON_KEY]
    return data

##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##  def_GetSnapList
##
##  Takes a LUN name (XMS_VOLUME) and returns an array containing the names of
##  all the snaps associated with that volume.
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def def_GetSnapList(
    XMS_IP,
    XMS_USERID,
    XMS_PASSWORD,
    XMS_VOLUME):

    getsnaplist_logger = def_FuncLogger(logging.DEBUG,logging.INFO)
    getsnaplist_logger.debug('Starting GetSnapList Module')

    getsnaplist_logger.info('Getting the list of snaps for '+XMS_VOLUME)

    try:
        resp = requests.get(
            'https://'+XMS_IP+'/api/json/types/volumes/?name='+XMS_VOLUME,
            auth=HTTPBasicAuth(XMS_USERID,XMS_PASSWORD),
            verify=False
            )
    except requests.exceptions.RequestException as e:
        getsnaplist_logger.info(e)
        getsnaplist_logger.error(e)
        sys.exit(1)

    if resp.status_code == 200:
        getsnaplist_logger.info('Get Snap List Status: <'+str(resp.status_code)+'>')
        getsnaplist_logger.debug(resp.text)
    else:
        getsnaplist_logger.info('Get Snap List Status: <'+str(resp.status_code)+'>')
        getsnaplist_logger.info(resp.text)
        sys.exit(1)

    arr_snap_list = []
    arr_snap_list = resp.json()['content']['dest-snap-list']
    return arr_snap_list

##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##  def_DeleteSnap
##
##  Takes a snapshot name (XMS_VOLUME) and deletes that snapshot.  In the case
##  a number of operations via the RESTful interface, snapshots are treated and
##  accessed just like the source volumes.  This returns only the HTTP response
##  code.
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def def_DeleteSnap(
    XMS_IP,
    XMS_USERID,
    XMS_PASSWORD,
    XMS_VOLUME):

    deletesnap_logger = def_FuncLogger(logging.DEBUG,logging.INFO)
    deletesnap_logger.debug('Starting SeleteSnap Module')

    deletesnap_logger.info('Deleting Snapshot: '+XMS_VOLUME)
    try:
        resp = requests.delete(
            'https://'+XMS_IP+'/api/json/types/volumes/?name='+XMS_VOLUME,
            auth=HTTPBasicAuth(XMS_USERID,XMS_PASSWORD),
            verify=False
            )
    except requests.exceptions.RequestException as e:
        deletesnap_logger.info(e)
        deletesnap_logger.error(e)
        sys.exit(1)

    if resp.status_code == 200:
        deletesnap_logger.info('Delete Snap Status: <'+str(resp.status_code)+'>')
        deletesnap_logger.debug(resp.text)
    else:
        deletesnap_logger.info('Delete Snap Status: <'+str(resp.status_code)+'>')
        deletesnap_logger.info(resp.text)
        sys.exit(1)

    return resp

##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##  def_FuncLogger
##
##  this is the default logging function I use in all my python code
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def def_FuncLogger(file_level,console_level=None):

    function_name = inspect.stack()[1][3]
    logger = logging.getLogger(function_name)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        logger.handlers = []

    if console_level != None:
        ch = logging.StreamHandler()
        ch.setLevel(console_level)
        ch_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        ch.setFormatter(ch_format)
        logger.addHandler(ch)
    try:
        fh = logging.FileHandler(args.var_Logfile.format(function_name))
    except IOError as e:
        print 'Logging IOError: ['+str(e.errno)+'] - '+e.strerror
        print 'Use the -l LogPath option'
        sys.exit(1)

    fh.setLevel(file_level)
    fh_format = logging.Formatter('%(asctime)s - %(lineno)d - %(levelname)8s - %(message)s')
    fh.setFormatter(fh_format)
    logger.addHandler(fh)

    return logger

##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##  def_exit_gracefully
##
##  gracefully exits if the script is interrupted
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def def_exit_gracefully(signum, frame):
    signal.signal(signal.SIGINT, original_sigint)

    try:
        if raw_input("\nDo you really want to quit? (y/n)> ").lower().startswith('y'):
            sys.exit(1)

    except KeyboardInterrupt:
        print("Ok, Exiting....")
        sys.exit(1)

    signal.signal(signal.SIGINT, def_exit_gracefully)

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

if __name__ == '__main__':
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, def_exit_gracefully)
    main()