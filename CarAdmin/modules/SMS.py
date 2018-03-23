#!/usr/bin/env python
# -*- coding: utf-8 -*-
from aliyunsdkdysmsapi.request.v20170525 import SendSmsRequest
from aliyunsdkdysmsapi.request.v20170525 import QuerySendDetailsRequest
from aliyunsdkcore.client import AcsClient
import uuid
from flask import current_app

class sendSMS(object):
    def __init__(self,type, number, msg):

        self.TemplateCode = current_app.config.get('SMS_MODEL_ID_CODE')
        self.para = msg
        if type=='noti_v':
            self.TemplateCode = current_app.config.get('SMS_MODEL_NOTI_CODE_V')
        if type=='noti_a':
            self.TemplateCode = current_app.config.get('SMS_MODEL_NOTI_CODE_A')


        self.access_key_id = current_app.config.get('SMS_ACCESS_KEY')
        self.access_key_secret = current_app.config.get('SMS_ACCESS_SECRET')
        self.server_address = current_app.config.get('SMS_URL')
        self.region = "cn-hangzhou"  # 暂时不支持多region
        self.num = int(number)
        self.SignName = current_app.config.get('SMS_SIGN_NAME').encode('utf-8')
        self.acs_client = AcsClient(self.access_key_id, self.access_key_secret, self.region)
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