#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from aliyunsdkdysmsapi.request.v20170525 import SendSmsRequest
from aliyunsdkdysmsapi.request.v20170525 import QuerySendDetailsRequest
from aliyunsdkcore.profile import region_provider
from aliyunsdkcore.client import AcsClient
import uuid
from config import *
try:
    reload(sys)
    sys.setdefaultencoding('utf8')
except NameError:
    pass
except Exception as err:
    raise err
class sendSMS(object):
    def __init__(self,type, number, msg):

        self.TemplateCode = SMS_MODEL_ID_CODE
        self.para = msg
        if type=='depart':
            self.TemplateCode = SMS_MODEL_DEPART
        if type=='back':
            self.TemplateCode = SMS_MODEL_BACK
        if type=='noti_v':
            self.TemplateCode = SMS_MODEL_NOTI_CODE_V
        if type=='noti_a':
            self.TemplateCode = SMS_MODEL_NOTI_CODE_A


        self.access_key_id = SMS_ACCESS_KEY
        self.access_key_secret = SMS_ACCESS_SECRET
        self.server_address = SMS_URL
        self.region = SMS_REGION
        self.product_name = SMS_PRODUCT_NAME

        self.num = int(number)
        self.SignName = SMS_SIGN_NAME.encode('utf-8')
        self.acs_client = AcsClient(self.access_key_id, self.access_key_secret, self.region)
        region_provider.add_endpoint(self.product_name, self.region, self.server_address)
        self.uuid = uuid.uuid1()
    def send(self):
        smsRequest = SendSmsRequest.SendSmsRequest()
        smsRequest.set_TemplateCode(self.TemplateCode)
        if self.para is not None:
            smsRequest.set_TemplateParam(self.para)
        smsRequest.set_OutId(self.uuid)
        smsRequest.set_SignName( self.SignName)
        smsRequest.set_PhoneNumbers(self.num )
        smsResponse = self.acs_client.do_action_with_exception(smsRequest)
        return smsResponse