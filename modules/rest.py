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

    def __init__(self,logfile,global_XMS_IP,global_XMS_USER,global_XMS_PASS):

        global rest_logger
        global XMS_IP
        global XMS_USERID
        global XMS_PASS
        rest_logger = Logger(logfile,logging.DEBUG,logging.INFO)
        rest_logger.debug('Loading Encode Module')
        XMS_IP = global_XMS_IP
        XMS_USERID = global_XMS_USER
        XMS_PASS = global_XMS_PASS


    def _get(self,XMS_URL):
        rest_logger.debug('Starting rest_get module')

        try:
            rest_logger.debug('https://'+XMS_IP+XMS_URL)
            resp = requests.get(
                'https://'+XMS_IP+XMS_URL,
                auth=HTTPBasicAuth(XMS_USERID,XMS_PASS),
                verify=False
                )
        except requests.exceptions.RequestException as e:
            rest_logger.error(e)
            sys.exit(1)

        if resp.status_code == 200:
            rest_logger.debug('Get Request Status: <'+str(resp.status_code)+'>')
            rest_logger.debug(resp.text)
        else:
            rest_logger.info('Get Request Status: <'+str(resp.status_code)+'>')
            rest_logger.info(resp.text)
            sys.exit(1)

        return resp

    def _post(self,XMS_URL,PAYLOAD):
        rest_logger.debug('Starting rest_get module')

        j=json.loads(PAYLOAD)

        try:
            rest_logger.debug('https://'+XMS_IP+XMS_URL)
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
            rest_logger.debug('Post Request Status: <'+str(resp.status_code)+'>')
            rest_logger.debug(resp.text)
        else:
            rest_logger.info('Post Request Status: <'+str(resp.status_code)+'>')
            rest_logger.info(resp.text)
            sys.exit(1)

        return resp

    def _put(self,XMS_URL,PAYLOAD):
        rest_logger.debug('Starting rest_get module')

        j=json.loads(PAYLOAD)

        try:
            rest_logger.debug('https://'+XMS_IP+XMS_URL)
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
            rest_logger.debug('Put Request Status: <'+str(resp.status_code)+'>')
            rest_logger.debug(resp.text)
        else:
            rest_logger.info('Put Request Status: <'+str(resp.status_code)+'>')
            rest_logger.info(resp.text)
            sys.exit(1)

        return resp

    def _delete(self,XMS_URL):
        rest_logger.debug('Starting rest_get module')

        try:
            rest_logger.debug('https://'+XMS_IP+XMS_URL)
            resp = requests.delete(
                'https://'+XMS_IP+XMS_URL,
                auth=HTTPBasicAuth(XMS_USERID,XMS_PASS),
                verify=False
                )
        except requests.exceptions.RequestException as e:
            rest_logger.error(e)
            sys.exit(1)

        if resp.status_code == 200:
            rest_logger.debug('Delete Request Status: <'+str(resp.status_code)+'>')
            rest_logger.debug(resp.text)
        else:
            rest_logger.info('Delete Request Status: <'+str(resp.status_code)+'>')
            rest_logger.info(resp.text)
            sys.exit(1)

        return resp

