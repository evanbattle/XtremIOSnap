#-------------------------------------------------------------------------------
# Name:        XtremIOSnap - Logger Module
# Purpose:
#
# Author:      Evan R. Battle
#              Sr. Systems Engineer, EMC
#              evan.battle@emc.com
#
# Version:     3.1
#
# Created:     11/22/2014
#
# Licence:     Open to distribute and modify.  This example code is unsupported
#              by both EMC and the author.  IF YOU HAVE PROBLEMS WITH THIS
#              SOFTWARE, THERE IS NO ONE PROVIDING TECHNICAL SUPPORT FOR
#              RESOLVING ISSUES. USE CODE AS IS!
#
#              THIS CODE IS NOT AFFILIATED WITH EMC CORPORATION.
#-------------------------------------------------------------------------------

##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##  def_FuncLogger
##
##  this is the default logging function I use in all my python code
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
import inspect
import logging
import colorer

def Logger(logfile,file_level,console_level=None):

    function_name = inspect.stack()[1][3]
    logger = logging.getLogger(function_name)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        logger.handlers = []

    if console_level != None:
        ch = colorer.ColorizingStreamHandler()
        ch.setLevel(console_level)
        ch_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        ch.setFormatter(ch_format)
        logger.addHandler(ch)
    try:
        fh = logging.FileHandler(logfile.format(function_name))
    except IOError as e:
        print 'Logging IOError: ['+str(e.errno)+'] - '+e.strerror
        print 'Use the -l LogPath option'
        sys.exit(1)

    fh.setLevel(file_level)
    fh_format = logging.Formatter('%(asctime)s - %(lineno)d - %(levelname)8s - %(message)s')
    fh.setFormatter(fh_format)
    logger.addHandler(fh)

    return logger
