# coding=utf-8

import yaml
from flask import jsonify



def loadConfig():
    with open('config.yaml', 'r') as f:
        data = yaml.safe_load(f)
        return data






class Resp:
    def success(msg="ok", body=None):
        return jsonify(
            {
                'code': 0,
                'msg': msg,
                'body': body
            }
        )

    def error(msg="error", body=None, code=-1):
        return jsonify(
            {
                'code': code,
                'msg': msg,
                'body': body
            }
        )


class Config:
    authcode = '142876'
    SECRET_KEY = 'REPLACE_WITH_YOUR_VALUE'
    APP_HOST = '127.0.0.1'
    APP_PORT = 5000
    APP_DEBUG = False



