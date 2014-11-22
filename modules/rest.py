#-------------------------------------------------------------------------------
# Name:        XtremIOSnap - Rest Module
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
import requests
from requests.auth import HTTPBasicAuth
import json
from modules.logger import Logger
requests.packages.urllib3.disable_warnings()

class Restful:

    def __init__(self,logfile,debugmode,global_XMS_IP,global_XMS_USER,global_XMS_PASS):

        global rest_logger
        global XMS_IP
        global XMS_USERID
        global XMS_PASS
        if debugmode == True:
            rest_logger = Logger(logfile,logging.DEBUG,logging.INFO)
        else:
            rest_logger = Logger(logfile,logging.INFO,logging.INFO)

        rest_logger.debug('Loading Restful Module')
        XMS_IP = global_XMS_IP
        XMS_USERID = global_XMS_USER
        XMS_PASS = global_XMS_PASS


    def _get(self,XMS_URL):
        rest_logger.debug('Starting _get module')

        try:
            rest_logger.debug('_get - https://'+XMS_IP+XMS_URL)
            resp = requests.get(
                'https://'+XMS_IP+XMS_URL,
                auth=HTTPBasicAuth(XMS_USERID,XMS_PASS),
                verify=False
                )
        except requests.exceptions.RequestException as e:
            rest_logger.error(e)
            sys.exit(1)

        if resp.status_code == 200:
            rest_logger.debug('_get - Get Request Status: <'+str(resp.status_code)+'>')
            rest_logger.debug('_get - '+resp.text)
        else:
            rest_logger.error('_get - Get Request Status: <'+str(resp.status_code)+'>')
            rest_logger.error(resp.text)
            sys.exit(1)

        return resp

    def _post(self,XMS_URL,PAYLOAD):
        rest_logger.debug('Starting _post module')

        j=json.loads(PAYLOAD)

        try:
            rest_logger.debug('_post - https://'+XMS_IP+XMS_URL)
            rest_logger.debug('_post - '+PAYLOAD)
            resp = requests.post(
                'https://'+XMS_IP+XMS_URL,
                auth=HTTPBasicAuth(XMS_USERID,XMS_PASS),
                verify=False,
                json=j
                )
        except requests.exceptions.RequestException as e:
            rest_logger.error(e)
            sys.exit(1)

        if resp.status_code == 201:
            rest_logger.debug('_post - Post Request Status: <'+str(resp.status_code)+'>')
            rest_logger.debug(resp.text)
        else:
            rest_logger.critical('_post - Post Request Status: <'+str(resp.status_code)+'>')
            rest_logger.critical(resp.text)
            sys.exit(1)

        return resp

    def _put(self,XMS_URL,PAYLOAD):
        rest_logger.debug('Starting _put module')

        j=json.loads(PAYLOAD)

        try:
            rest_logger.debug('_put - https://'+XMS_IP+XMS_URL)
            rest_logger.debug('_put - '+PAYLOAD)
            resp = requests.put(
                'https://'+XMS_IP+XMS_URL,
                auth=HTTPBasicAuth(XMS_USERID,XMS_PASS),
                verify=False,
                json=j
                )
        except requests.exceptions.RequestException as e:
            rest_logger.error(e)
            sys.exit(1)

        if resp.status_code == 200:
            rest_logger.debug('_put - Put Request Status: <'+str(resp.status_code)+'>')
            rest_logger.debug(resp.text)
        else:
            rest_logger.critical('_put - Put Request Status: <'+str(resp.status_code)+'>')
            rest_logger.critical(resp.text)
            sys.exit(1)

        return resp

    def _delete(self,XMS_URL):
        rest_logger.debug('Starting _delete module')

        try:
            rest_logger.debug('_delete - https://'+XMS_IP+XMS_URL)
            resp = requests.delete(
                'https://'+XMS_IP+XMS_URL,
                auth=HTTPBasicAuth(XMS_USERID,XMS_PASS),
                verify=False
                )
        except requests.exceptions.RequestException as e:
            rest_logger.error(e)
            sys.exit(1)

        if resp.status_code == 200:
            rest_logger.debug('_delete - Delete Request Status: <'+str(resp.status_code)+'>')
            rest_logger.debug(resp.text)
        else:
            rest_logger.critical('_delete - Delete Request Status: <'+str(resp.status_code)+'>')
            rest_logger.critical(resp.text)
            sys.exit(1)

        return resp

