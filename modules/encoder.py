#-------------------------------------------------------------------------------
# Name:        XtremIOSnap - Encoder module
# Purpose:     Encodes and Decodes the user ID and password so they don't have
#              to be stored in a batch file or task scheduler in plain text.
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
import base64
from modules.logger import Logger

class Encode:

    def __init__(self,logfile):

        global encode_logger
        encode_logger = Logger(logfile,logging.DEBUG,logging.INFO)
        encode_logger.debug('Loading Encode Module')

    def _encodeuser(self,user):

        encode_logger.debug('_encodeuser - Encoding User ID')
        encoded_user = base64.b64encode(user)
        return encoded_user

    def _encodepass(self,password):

        encode_logger.debug('_encodepass - Encoding Password')
        encoded_pass = base64.b64encode(password)
        return encoded_pass

    def _decodeuser(self,user):

        encode_logger.debug('_decodeuser - Decoding User')
        decoded_user = base64.b64decode(user)
        return decoded_user

    def _decodepass(self,password):

        encode_logger.debug('_decodepass - Decoding Password')
        decoded_pass = base64.b64decode(password)
        return decoded_pass
