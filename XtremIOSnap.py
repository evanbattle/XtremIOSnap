#-------------------------------------------------------------------------------
# Name:        XtremIOSnap
# Purpose:     Create and delete snapshots on an XtremIO array using the RESTful
#              Services.
#
# Author:      Evan R. Battle
#              Sr. Systems Engineer, EMC
#              evan.battle@emc.com
#
# Version:     3.0
#
# Created:     11/20/2014
#
# Licence:     Open to distribute and modify.  This example code is unsupported
#              by both EMC and the author.  IF YOU HAVE PROBLEMS WITH THIS
#              SOFTWARE, THERE IS NO ONE PROVIDING TECHNICAL SUPPORT FOR
#              RESOLVING ISSUES. USE CODE AS IS!
#
#              THIS CODE IS NOT AFFILIATED WITH EMC CORPORATION.
#-------------------------------------------------------------------------------
import sys
import os
import signal
import logging
import datetime
from docopt import docopt
from modules.logger import Logger
from modules.encoder import Encode
from modules.options import Options
from modules.options import exit_gracefully
from modules.rest import Restful

var_cwd =  os.getcwd()

__doc__ = """
Usage:
    XtremIOSnap.py [-h]
    XtremIOSnap.py [(--encode --user=<XMS_USER> --pass=<XMS_PASS>)]
    XtremIOSnap.py [(--host=<XMS_IP> --user=<XMS_USER> --pass=<XMS_PASS>)] [--e]  [(--f --snap=<object_to_snap>)] [--n=<number_of_snaps>] [--schedule=<schedule>] [--targetfolder=<target_folder>] [--l=<log_path>]
    XtremIOSnap.py [(--host=<XMS_IP> --user=<XMS_USER> --pass=<XMS_PASS>)] [--e]  [(--v --snap=<object_to_snap>)] [--n=<number_of_snaps>] [--schedule=<schedule>] [--targetfolder=<target_folder>] [--l=<log_path>]

Collect Performance Statistics from an XtremIO array and push them to vCenter Operations

Options:
    -h --help    show this
    --encode    used to encode the username and password
    --host=<XMS_IP>
    --e    If specified, will use the encoded User and Password
    --user=<XMS_USERID>
    --pass=<XMS_PASSWORD>
    --f    specify to signify the object to snap is a folder
    --v    specify to signify the object to snap is a volume
    --snap=<object_to_snap>    object to snap
    --n=<number_of_snaps>    [default: 5]
    --schedule=<schedule>    [hourly | daily | weekly] [default: hourly]
    --targetfolder=<target_folder>  target folder
    --l=<log_path>    [default: """+var_cwd+"""\XtremIOSnap.log]

"""

def main():
    log = options['--l']
    main_logger = Logger(options['--l'],logging.DEBUG,logging.INFO)
    main_logger.info('Running XtremIO Snap Script')
    main_options = Options(log,options)

    XMS_IP = options['--host']
    XMS_USER = main_options.XMS_USER
    XMS_PASS = main_options.XMS_PASS
    snap_tgt_folder = main_options.snap_tgt_folder
    parent_folder_id = main_options.var_snap_tgt_folder
    num_snaps = options['--n']
    snap_src = options['--snap']
    SnapFolder = '_Snapshots'
    bool_create_folder = True ## will change to False if the /_Snapshots folder already exists

    rest = Restful(log,XMS_IP,XMS_USER,XMS_PASS)

    folder_list = rest._get('/api/json/types/volume-folders').json()['folders']

    for folder_list_rs in folder_list:

        if folder_list_rs['name'] == '/'+ snap_tgt_folder:
            bool_create_folder = False
            main_logger.info('The target snapshot folder, '+folder_list_rs['name']+' already exists.')

    if bool_create_folder is True:
        cf_payload = '{\
            "caption": \"'+SnapFolder+'\" , \
            "parent-folder-id": \"/'+main_options.var_snap_tgt_folder+'\" \
            }'
        cf_resp = rest._post('/api/json/types/volume-folders',cf_payload)
        if cf_resp.status_code == 201:
            main_logger.info('Created folder: '+main_options.snap_tgt_folder)

    if options['--f'] ==True:
        newsnapsuffix = '.folder.'+main_options.schedule+'.'
        folder_vol_list = rest._get('/api/json/types/volume-folders/?name=/'+snap_src).json()['content']['direct-list']
        arr_folder_vol_list_component = []

        for folder_vol_list_rs in folder_vol_list:

            if '/_Snapshots' in folder_vol_list_rs[1]:
                pass

            else:
                arr_folder_vol_list_component.append(folder_vol_list_rs[1])
                main_logger.info('Will retain '+num_snaps+' snapshots for volume: '+folder_vol_list_rs [1])
                vol_snap_list = rest._get('/api/json/types/volumes/?name='+folder_vol_list_rs [1]).json()['content']['dest-snap-list']##<--Initial list of snapshots
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
                        rename_payload = '{"vol-name": \"'+rename_to+'\"}'
                        rename_resp = rest._put('/api/json/types/volumes/?name='+arr_vol_snap_list_component[y],rename_payload)

                        if rename_resp.status_code == 200:
                            main_logger.info(arr_vol_snap_list_component[y]+' was renamed to '+rename_to)

        timestamp = datetime.datetime.now()
        timestamp = timestamp.isoformat()
        arr_timestamp = timestamp.split('.',2) ##<--stripping the microseconds from the timestamp for aesthetics

        fullsuffix = '_'+arr_timestamp[0]+newsnapsuffix+'0'
        fs_payload = '{\
            "source-folder-id": \"/'+snap_src+'\" , \
            "suffix": \"'+fullsuffix+'\" ,\
            "folder-id": \"/'+snap_tgt_folder+'\" \
            }'
        vol_snap = rest._post('/api/json/types/snapshots',fs_payload)
##        vol_snap = Post(log,XMS_IP,'/api/json/types/snapshots',XMS_USER,XMS_PASS,fs_payload)

        folder_vol_list = rest._get('/api/json/types/volume-folders/?name=/'+snap_src).json()['content']['direct-list']

##        folder_vol_list = Get(log,XMS_IP,'/api/json/types/volume-folders/?name=/'+snap_src,XMS_USER,XMS_PASS).json()['content']['direct-list']
        arr_folder_vol_list_component = []
        for folder_vol_list_rs in folder_vol_list:
            if '/_Snapshots' in folder_vol_list_rs[1]:
                pass
            else:
                vol_snap_list = rest._get('/api/json/types/volumes/?name='+folder_vol_list_rs [1]).json()['content']['dest-snap-list']##<--Refresh the snap list
##                vol_snap_list = Get(log,XMS_IP,'/api/json/types/volumes/?name='+folder_vol_list_rs [1],XMS_USER,XMS_PASS)##<--Refresh the snap list

                arr_vol_snap_list_component = []
                for vol_snap_list_rs in vol_snap_list:
                    if newsnapsuffix in vol_snap_list_rs[1]:
                        arr_vol_snap_list_component.append(vol_snap_list_rs[1])

                arr_vol_snap_list_component.sort(reverse=False)

                for x in xrange(len(arr_vol_snap_list_component)-(int(num_snaps))):
                    if newsnapsuffix in arr_vol_snap_list_component[x]:
                        main_logger.info(str(x)+': '+ arr_vol_snap_list_component[x])
                        get_snap_details = rest._get('/api/json/types/snapshots/?name='+arr_vol_snap_list_component[x])
##                        get_snap_details = Get(log,XMS_IP,'/api/json/types/snapshots/?name='+arr_vol_snap_list_component[x],XMS_USER,XMS_PASS)

                        arr_ancestor_vol_id = get_snap_details.json()['content']['ancestor-vol-id']
                        snap_parent_name = arr_ancestor_vol_id[1]
                        snap_creation_time = get_snap_details.json()['content']['creation-time']
                        snap_space_consumed = get_snap_details.json()['content']['logical-space-in-use']
                        arr_snap_lun_mapping = get_snap_details.json()['content']['lun-mapping-list']
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
                            delete_status = rest._delete('/api/json/types/volumes/?name='+arr_vol_snap_list_component[x])
##                            delete_status = Delete(log,XMS_IP,'/api/json/types/volumes/?name='+arr_vol_snap_list_component[x],XMS_USER,XMS_PASS)

    elif options['--v'] ==True:
        main_logger.info('Will retain '+num_snaps+' snapshots for volume: '+snap_src)
        newsnapsuffix = '.'+main_options.schedule+'.'
        vol_snap_list = rest._get('/api/json/types/volumes/?name='+snap_src).json()['content']['dest-snap-list']
##        vol_snap_list = Get(log,XMS_IP,'/api/json/types/volumes/?name='+snap_src,XMS_USER,XMS_PASS).json()['content']['dest-snap-list']
        arr_vol_snap_list_component = []
        for vol_snap_list_rs in vol_snap_list:
            if newsnapsuffix in vol_snap_list_rs[1]:
                if '.folder.' in vol_snap_list_rs[1]:
                    pass
                else:
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
                rename_payload = '{"vol-name": \"'+rename_to+'\"}'
                rename_resp = rest._put('/api/json/types/volumes/?name='+arr_vol_snap_list_component[y],rename_payload)

                if rename_resp.status_code == 200:
                            main_logger.info(arr_vol_snap_list_component[y]+' was renamed to '+rename_to)
##                rename_resp = Put(log,XMS_IP,'/api/json/types/volumes/?name='+arr_vol_snap_list_component[y],XMS_USER,XMS_PASS,rename_payload)
        timestamp = datetime.datetime.now()
        timestamp = timestamp.isoformat()
        arr_timestamp = timestamp.split('.',2) ##<--stripping the microseconds from the timestamp for aesthetics
        fullsuffix = '_'+arr_timestamp[0]+newsnapsuffix
        newsnap = snap_src+fullsuffix+'0'##<--sets the newly created snapshot to always be .0
        vol_snap_payload = '{\
            "ancestor-vol-id": \"'+snap_src+'\" , \
            "snap-vol-name": \"'+newsnap+'\" ,\
            "folder-id": \"/'+snap_tgt_folder+'\" \
            }'
        vol_snap_resp = rest._post('/api/json/types/snapshots',vol_snap_payload)
##        vol_snap_resp = Post(log,XMS_IP,'/api/json/types/snapshots',XMS_USER,XMS_PASS,vol_snap_payload)
        vol_snap_list = rest._get('/api/json/types/volumes/?name='+snap_src).json()['content']['dest-snap-list']
##        vol_snap_list = Get(log,XMS_IP,'/api/json/types/volumes/?name='+snap_src,XMS_USER,XMS_PASS).json()['content']['dest-snap-list']
        arr_vol_snap_list_component = []
        for vol_snap_list_rs in vol_snap_list:
            if newsnapsuffix in vol_snap_list_rs[1]:
                if '.folder.' in vol_snap_list_rs[1]:
                    pass
                else:
                    arr_vol_snap_list_component.append(vol_snap_list_rs[1])

        arr_vol_snap_list_component.sort(reverse=False)

        for x in xrange(len(arr_vol_snap_list_component)-(int(num_snaps))):
            if newsnapsuffix in arr_vol_snap_list_component[x]:
                main_logger.info(str(x)+': '+ arr_vol_snap_list_component[x])
                get_snap_details = rest._get('/api/json/types/snapshots/?name='+arr_vol_snap_list_component[x])

##                get_snap_details = Get(log,XMS_IP,'/api/json/types/snapshots/?name='+arr_vol_snap_list_component[x],XMS_USER,XMS_PASS)

                arr_ancestor_vol_id = get_snap_details.json()['content']['ancestor-vol-id']
                snap_parent_name = arr_ancestor_vol_id[1]
                snap_creation_time = get_snap_details.json()['content']['creation-time']
                snap_space_consumed = get_snap_details.json()['content']['logical-space-in-use']
                arr_snap_lun_mapping = get_snap_details.json()['content']['lun-mapping-list']

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
                    delete_status = rest._delete('/api/json/types/volumes/?name='+arr_vol_snap_list_component[x])

##                    delete_status = Delete(log,XMS_IP,'/api/json/types/volumes/?name='+arr_vol_snap_list_component[x],XMS_USER,XMS_PASS)

    else:
        print 'NO FOLDER OR VOLUME OPTION SPECIFIED'
        sys.exit(1)


    main_logger.info('Complete!')

    sys.exit(0)


if __name__ == '__main__':
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, exit_gracefully)
    options = docopt(__doc__, argv=None, help=True, version=None, options_first=False)
    main()


