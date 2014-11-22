#-------------------------------------------------------------------------------
# Name:        XtremIOSnap - Options Module
# Purpose:
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

import logging
import sys
from modules.logger import Logger
from modules.encoder import Encode

class Options:
    def __init__(self,logfile,options):

        global options_logger
        if options['--debug'] == True:
            options_logger = Logger(logfile,logging.DEBUG,logging.INFO)
        else:
            options_logger = Logger(logfile,logging.INFO,logging.INFO)

        options_logger.debug('Loading Options Module')
        encoder = Encode(options['--l'],options['--debug'])

        if options['--encode'] is True:
            options_logger.info('Encoding user id and password')
            encode_user = encoder._encodeuser(options['XMS_USER'])
            encode_pass = encoder._encodepass(options['XMS_PASS'])
            print ''
            print 'Encoded User ID = ' + encode_user
            print 'Encoded Password = ' + encode_pass
            print ''
            options_logger.info('Use the above, encoded, user id and password with the --e option')
            options_logger.info('to execute the tool without using the plain text usename and password')
            sys.exit(0)

        elif options['--e']:
            options_logger.debug('Using an encoded username and password')
            XMS_USER = encoder._decodeuser(options['XMS_USER'])
            XMS_PASS = encoder._decodepass(options['XMS_PASS'])

        else:
            options_logger.debug('Username and password are not encoded')
            XMS_USER = options['XMS_USER']
            XMS_PASS = options['XMS_PASS']

        self.XMS_USER = XMS_USER
        self.XMS_PASS = XMS_PASS

        if options['--schedule'] == 'hourly':
            options_logger.debug('Using the hourly schedule')
            self.schedule = 'hourly'

        elif options['--schedule'] == 'daily':
            options_logger.debug('Using the daily schedule')
            self.schedule = 'daily'

        elif options['--schedule'] == 'weekly':
            options_logger.debug('Using the weekly schedule')
            self.schedule = 'weekly'

        else:
            options_logger.critical('No schedule, or incorrect option Specified.  Exiting...')
            sys.exit(1)

        SnapFolder = '_Snapshots'

        self.var_snap_tgt_folder = options['--tf'] ## this should be an optional variable, if the customer wants to organize snapshots under a folder hierarchy

        if self.var_snap_tgt_folder == None:
            options_logger.debug('No snapshot target folder specified')
            self.var_snap_tgt_folder =''
            self.snap_tgt_folder = SnapFolder
            options_logger.debug('Using '+self.snap_tgt_folder+' as the snapshot target')
        else:
            self.snap_tgt_folder = self.var_snap_tgt_folder+'/'+SnapFolder
            options_logger.debug('Using '+self.snap_tgt_folder+' as the snapshot target')

##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##  exit_gracefully
##
##  gracefully exits if the script is interrupted
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def exit_gracefully(signum, frame):
    signal.signal(signal.SIGINT, original_sigint)

    try:
        if raw_input("\nDo you really want to quit? (y/n)> ").lower().startswith('y'):
            sys.exit(1)

    except KeyboardInterrupt:
        print("Ok, Exiting....")
        sys.exit(1)

    signal.signal(signal.SIGINT, exit_gracefully)



