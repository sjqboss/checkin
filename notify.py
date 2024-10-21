#!/usr/bin/env python3

# _*_ coding:utf-8 _*_

import base64

import hashlib

import hmac

import json

import os

import re

import threading

import time

import urllib.parse

import smtplib

from email.mime.text import MIMEText

from email.header import Header

from email.utils import formataddr

  

import requests

  

# 原先的 print 函数和主线程的锁

_print = print

mutex = threading.Lock()

  
  

# 定义新的 print 函数

def print(text, *args, **kw):

&nbsp; &nbsp; """

&nbsp; &nbsp; 使输出有序进行，不出现多线程同一时间输出导致错乱的问题。

&nbsp; &nbsp; """

&nbsp; &nbsp; with mutex:

&nbsp; &nbsp; &nbsp; &nbsp; _print(text, *args, **kw)

  
  

# 通知服务

# fmt: off

push_config = {

&nbsp; &nbsp; 'HITOKOTO': True, &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;# 启用一言（随机句子）

  

&nbsp; &nbsp; 'BARK_PUSH': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;# bark IP 或设备码，例：https://api.day.app/DxHcxxxxxRxxxxxxcm/

&nbsp; &nbsp; 'BARK_ARCHIVE': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; # bark 推送是否存档

&nbsp; &nbsp; 'BARK_GROUP': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; # bark 推送分组

&nbsp; &nbsp; 'BARK_SOUND': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; # bark 推送声音

&nbsp; &nbsp; 'BARK_ICON': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;# bark 推送图标

&nbsp; &nbsp; 'BARK_LEVEL': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; # bark 推送时效性

&nbsp; &nbsp; 'BARK_URL': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; # bark 推送跳转URL

  

&nbsp; &nbsp; 'CONSOLE': False, &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;# 控制台输出

  

&nbsp; &nbsp; 'DD_BOT_SECRET': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;# 钉钉机器人的 DD_BOT_SECRET

&nbsp; &nbsp; 'DD_BOT_TOKEN': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; # 钉钉机器人的 DD_BOT_TOKEN

  

&nbsp; &nbsp; 'FSKEY': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;# 飞书机器人的 FSKEY

  

&nbsp; &nbsp; 'GOBOT_URL': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;# go-cqhttp

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; # 推送到个人QQ：http://127.0.0.1/send_private_msg

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; # 群：http://127.0.0.1/send_group_msg

&nbsp; &nbsp; 'GOBOT_QQ': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; # go-cqhttp 的推送群或用户

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; # GOBOT_URL 设置 /send_private_msg 时填入 user_id=个人QQ

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; # &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; /send_group_msg &nbsp; 时填入 group_id=QQ群

&nbsp; &nbsp; 'GOBOT_TOKEN': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;# go-cqhttp 的 access_token

  

&nbsp; &nbsp; 'GOTIFY_URL': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; # gotify地址,如https://push.example.de:8080

&nbsp; &nbsp; 'GOTIFY_TOKEN': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; # gotify的消息应用token

&nbsp; &nbsp; 'GOTIFY_PRIORITY': 0, &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; # 推送消息优先级,默认为0

  

&nbsp; &nbsp; 'IGOT_PUSH_KEY': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;# iGot 聚合推送的 IGOT_PUSH_KEY

  

&nbsp; &nbsp; 'PUSH_KEY': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; # server 酱的 PUSH_KEY，兼容旧版与 Turbo 版

  

&nbsp; &nbsp; 'DEER_KEY': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; # PushDeer 的 PUSHDEER_KEY

&nbsp; &nbsp; 'DEER_URL': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; # PushDeer 的 PUSHDEER_URL

  

&nbsp; &nbsp; 'CHAT_URL': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; # synology chat url

&nbsp; &nbsp; 'CHAT_TOKEN': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; # synology chat token

  

&nbsp; &nbsp; 'PUSH_PLUS_TOKEN': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;# push+ 微信推送的用户令牌

&nbsp; &nbsp; 'PUSH_PLUS_USER': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; # push+ 微信推送的群组编码

  

&nbsp; &nbsp; 'WE_PLUS_BOT_TOKEN': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;# 微加机器人的用户令牌

&nbsp; &nbsp; 'WE_PLUS_BOT_RECEIVER': '', &nbsp; &nbsp; &nbsp; &nbsp; # 微加机器人的消息接收者

&nbsp; &nbsp; 'WE_PLUS_BOT_VERSION': 'pro', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;# 微加机器人的调用版本

  

&nbsp; &nbsp; 'QMSG_KEY': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; # qmsg 酱的 QMSG_KEY

&nbsp; &nbsp; 'QMSG_TYPE': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;# qmsg 酱的 QMSG_TYPE

  

&nbsp; &nbsp; 'QYWX_ORIGIN': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;# 企业微信代理地址

  

&nbsp; &nbsp; 'QYWX_AM': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;# 企业微信应用

  

&nbsp; &nbsp; 'QYWX_KEY': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; # 企业微信机器人

  

&nbsp; &nbsp; 'TG_BOT_TOKEN': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; # tg 机器人的 TG_BOT_TOKEN，例：1407203283:AAG9rt-6RDaaX0HBLZQq0laNOh898iFYaRQ

&nbsp; &nbsp; 'TG_USER_ID': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; # tg 机器人的 TG_USER_ID，例：1434078534

&nbsp; &nbsp; 'TG_API_HOST': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;# tg 代理 api

&nbsp; &nbsp; 'TG_PROXY_AUTH': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;# tg 代理认证参数

&nbsp; &nbsp; 'TG_PROXY_HOST': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;# tg 机器人的 TG_PROXY_HOST

&nbsp; &nbsp; 'TG_PROXY_PORT': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;# tg 机器人的 TG_PROXY_PORT

  

&nbsp; &nbsp; 'AIBOTK_KEY': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; # 智能微秘书 个人中心的apikey 文档地址：http://wechat.aibotk.com/docs/about

&nbsp; &nbsp; 'AIBOTK_TYPE': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;# 智能微秘书 发送目标 room 或 contact

&nbsp; &nbsp; 'AIBOTK_NAME': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;# 智能微秘书 &nbsp;发送群名 或者好友昵称和type要对应好

  

&nbsp; &nbsp; 'SMTP_SERVER': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;# SMTP 发送邮件服务器，形如 smtp.exmail.qq.com:465

&nbsp; &nbsp; 'SMTP_SSL': 'false', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;# SMTP 发送邮件服务器是否使用 SSL，填写 true 或 false

&nbsp; &nbsp; 'SMTP_EMAIL': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; # SMTP 收发件邮箱，通知将会由自己发给自己

&nbsp; &nbsp; 'SMTP_PASSWORD': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;# SMTP 登录密码，也可能为特殊口令，视具体邮件服务商说明而定

&nbsp; &nbsp; 'SMTP_NAME': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;# SMTP 收发件人姓名，可随意填写

  

&nbsp; &nbsp; 'PUSHME_KEY': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; # PushMe 的 PUSHME_KEY

&nbsp; &nbsp; 'PUSHME_URL': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; # PushMe 的 PUSHME_URL

  

&nbsp; &nbsp; 'CHRONOCAT_QQ': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; # qq号

&nbsp; &nbsp; 'CHRONOCAT_TOKEN': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;# CHRONOCAT 的token

&nbsp; &nbsp; 'CHRONOCAT_URL': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;# CHRONOCAT的url地址

  

&nbsp; &nbsp; 'WEBHOOK_URL': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;# 自定义通知 请求地址

&nbsp; &nbsp; 'WEBHOOK_BODY': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; # 自定义通知 请求体

&nbsp; &nbsp; 'WEBHOOK_HEADERS': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;# 自定义通知 请求头

&nbsp; &nbsp; 'WEBHOOK_METHOD': '', &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; # 自定义通知 请求方法

&nbsp; &nbsp; 'WEBHOOK_CONTENT_TYPE': '' &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;# 自定义通知 content-type

}

# fmt: on

  

for k in push_config:

&nbsp; &nbsp; if os.getenv(k):

&nbsp; &nbsp; &nbsp; &nbsp; v = os.getenv(k)

&nbsp; &nbsp; &nbsp; &nbsp; push_config[k] = v

  
  

def bark(title: str, content: str) -> None:

&nbsp; &nbsp; """

&nbsp; &nbsp; 使用 bark 推送消息。

&nbsp; &nbsp; """

&nbsp; &nbsp; if not push_config.get("BARK_PUSH"):

&nbsp; &nbsp; &nbsp; &nbsp; print("bark 服务的 BARK_PUSH 未设置!!\n取消推送")

&nbsp; &nbsp; &nbsp; &nbsp; return

&nbsp; &nbsp; print("bark 服务启动")

  

&nbsp; &nbsp; if push_config.get("BARK_PUSH").startswith("http"):

&nbsp; &nbsp; &nbsp; &nbsp; url = f'{push_config.get("BARK_PUSH")}'

&nbsp; &nbsp; else:

&nbsp; &nbsp; &nbsp; &nbsp; url = f'https://api.day.app/{push_config.get("BARK_PUSH")}'

  

&nbsp; &nbsp; bark_params = {

&nbsp; &nbsp; &nbsp; &nbsp; "BARK_ARCHIVE": "isArchive",

&nbsp; &nbsp; &nbsp; &nbsp; "BARK_GROUP": "group",

&nbsp; &nbsp; &nbsp; &nbsp; "BARK_SOUND": "sound",

&nbsp; &nbsp; &nbsp; &nbsp; "BARK_ICON": "icon",

&nbsp; &nbsp; &nbsp; &nbsp; "BARK_LEVEL": "level",

&nbsp; &nbsp; &nbsp; &nbsp; "BARK_URL": "url",

&nbsp; &nbsp; }

&nbsp; &nbsp; data = {

&nbsp; &nbsp; &nbsp; &nbsp; "title": title,

&nbsp; &nbsp; &nbsp; &nbsp; "body": content,

&nbsp; &nbsp; }

&nbsp; &nbsp; for pair in filter(

&nbsp; &nbsp; &nbsp; &nbsp; lambda pairs: pairs[0].startswith("BARK_")

&nbsp; &nbsp; &nbsp; &nbsp; and pairs[0] != "BARK_PUSH"

&nbsp; &nbsp; &nbsp; &nbsp; and pairs[1]

&nbsp; &nbsp; &nbsp; &nbsp; and bark_params.get(pairs[0]),

&nbsp; &nbsp; &nbsp; &nbsp; push_config.items(),

&nbsp; &nbsp; ):

&nbsp; &nbsp; &nbsp; &nbsp; data[bark_params.get(pair[0])] = pair[1]

&nbsp; &nbsp; headers = {"Content-Type": "application/json;charset=utf-8"}

&nbsp; &nbsp; response = requests.post(

&nbsp; &nbsp; &nbsp; &nbsp; url=url, data=json.dumps(data), headers=headers, timeout=15

&nbsp; &nbsp; ).json()

  

&nbsp; &nbsp; if response["code"] == 200:

&nbsp; &nbsp; &nbsp; &nbsp; print("bark 推送成功！")

&nbsp; &nbsp; else:

&nbsp; &nbsp; &nbsp; &nbsp; print("bark 推送失败！")

  
  

def console(title: str, content: str) -> None:

&nbsp; &nbsp; """

&nbsp; &nbsp; 使用 控制台 推送消息。

&nbsp; &nbsp; """

&nbsp; &nbsp; print(f"{title}\n\n{content}")

  
  

def dingding_bot(title: str, content: str) -> None:

&nbsp; &nbsp; """

&nbsp; &nbsp; 使用 钉钉机器人 推送消息。

&nbsp; &nbsp; """

&nbsp; &nbsp; if not push_config.get("DD_BOT_SECRET") or not push_config.get("DD_BOT_TOKEN"):

&nbsp; &nbsp; &nbsp; &nbsp; print("钉钉机器人 服务的 DD_BOT_SECRET 或者 DD_BOT_TOKEN 未设置!!\n取消推送")

&nbsp; &nbsp; &nbsp; &nbsp; return

&nbsp; &nbsp; print("钉钉机器人 服务启动")

  

&nbsp; &nbsp; timestamp = str(round(time.time() * 1000))

&nbsp; &nbsp; secret_enc = push_config.get("DD_BOT_SECRET").encode("utf-8")

&nbsp; &nbsp; string_to_sign = "{}\n{}".format(timestamp, push_config.get("DD_BOT_SECRET"))

&nbsp; &nbsp; string_to_sign_enc = string_to_sign.encode("utf-8")

&nbsp; &nbsp; hmac_code = hmac.new(

&nbsp; &nbsp; &nbsp; &nbsp; secret_enc, string_to_sign_enc, digestmod=hashlib.sha256

&nbsp; &nbsp; ).digest()

&nbsp; &nbsp; sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))

&nbsp; &nbsp; url = f'https://oapi.dingtalk.com/robot/send?access_token={push_config.get("DD_BOT_TOKEN")}&timestamp={timestamp}&sign={sign}'

&nbsp; &nbsp; headers = {"Content-Type": "application/json;charset=utf-8"}

&nbsp; &nbsp; data = {"msgtype": "text", "text": {"content": f"{title}\n\n{content}"}}

&nbsp; &nbsp; response = requests.post(

&nbsp; &nbsp; &nbsp; &nbsp; url=url, data=json.dumps(data), headers=headers, timeout=15

&nbsp; &nbsp; ).json()

  

&nbsp; &nbsp; if not response["errcode"]:

&nbsp; &nbsp; &nbsp; &nbsp; print("钉钉机器人 推送成功！")

&nbsp; &nbsp; else:

&nbsp; &nbsp; &nbsp; &nbsp; print("钉钉机器人 推送失败！")

  
  

def feishu_bot(title: str, content: str) -> None:

&nbsp; &nbsp; """

&nbsp; &nbsp; 使用 飞书机器人 推送消息。

&nbsp; &nbsp; """

&nbsp; &nbsp; if not push_config.get("FSKEY"):

&nbsp; &nbsp; &nbsp; &nbsp; print("飞书 服务的 FSKEY 未设置!!\n取消推送")

&nbsp; &nbsp; &nbsp; &nbsp; return

&nbsp; &nbsp; print("飞书 服务启动")

  

&nbsp; &nbsp; url = f'https://open.feishu.cn/open-apis/bot/v2/hook/{push_config.get("FSKEY")}'

&nbsp; &nbsp; data = {"msg_type": "text", "content": {"text": f"{title}\n\n{content}"}}

&nbsp; &nbsp; response = requests.post(url, data=json.dumps(data)).json()

  

&nbsp; &nbsp; if response.get("StatusCode") == 0 or response.get("code") == 0:

&nbsp; &nbsp; &nbsp; &nbsp; print("飞书 推送成功！")

&nbsp; &nbsp; else:

&nbsp; &nbsp; &nbsp; &nbsp; print("飞书 推送失败！错误信息如下：\n", response)

  
  

def go_cqhttp(title: str, content: str) -> None:

&nbsp; &nbsp; """

&nbsp; &nbsp; 使用 go_cqhttp 推送消息。

&nbsp; &nbsp; """

&nbsp; &nbsp; if not push_config.get("GOBOT_URL") or not push_config.get("GOBOT_QQ"):

&nbsp; &nbsp; &nbsp; &nbsp; print("go-cqhttp 服务的 GOBOT_URL 或 GOBOT_QQ 未设置!!\n取消推送")

&nbsp; &nbsp; &nbsp; &nbsp; return

&nbsp; &nbsp; print("go-cqhttp 服务启动")

  

&nbsp; &nbsp; url = f'{push_config.get("GOBOT_URL")}?access_token={push_config.get("GOBOT_TOKEN")}&{push_config.get("GOBOT_QQ")}&message=标题:{title}\n内容:{content}'

&nbsp; &nbsp; response = requests.get(url).json()

  

&nbsp; &nbsp; if response["status"] == "ok":

&nbsp; &nbsp; &nbsp; &nbsp; print("go-cqhttp 推送成功！")

&nbsp; &nbsp; else:

&nbsp; &nbsp; &nbsp; &nbsp; print("go-cqhttp 推送失败！")

  
  

def gotify(title: str, content: str) -> None:

&nbsp; &nbsp; """

&nbsp; &nbsp; 使用 gotify 推送消息。

&nbsp; &nbsp; """

&nbsp; &nbsp; if not push_config.get("GOTIFY_URL") or not push_config.get("GOTIFY_TOKEN"):

&nbsp; &nbsp; &nbsp; &nbsp; print("gotify 服务的 GOTIFY_URL 或 GOTIFY_TOKEN 未设置!!\n取消推送")

&nbsp; &nbsp; &nbsp; &nbsp; return

&nbsp; &nbsp; print("gotify 服务启动")

  

&nbsp; &nbsp; url = f'{push_config.get("GOTIFY_URL")}/message?token={push_config.get("GOTIFY_TOKEN")}'

&nbsp; &nbsp; data = {

&nbsp; &nbsp; &nbsp; &nbsp; "title": title,

&nbsp; &nbsp; &nbsp; &nbsp; "message": content,

&nbsp; &nbsp; &nbsp; &nbsp; "priority": push_config.get("GOTIFY_PRIORITY"),

&nbsp; &nbsp; }

&nbsp; &nbsp; response = requests.post(url, data=data).json()

  

&nbsp; &nbsp; if response.get("id"):

&nbsp; &nbsp; &nbsp; &nbsp; print("gotify 推送成功！")

&nbsp; &nbsp; else:

&nbsp; &nbsp; &nbsp; &nbsp; print("gotify 推送失败！")

  
  

def iGot(title: str, content: str) -> None:

&nbsp; &nbsp; """

&nbsp; &nbsp; 使用 iGot 推送消息。

&nbsp; &nbsp; """

&nbsp; &nbsp; if not push_config.get("IGOT_PUSH_KEY"):

&nbsp; &nbsp; &nbsp; &nbsp; print("iGot 服务的 IGOT_PUSH_KEY 未设置!!\n取消推送")

&nbsp; &nbsp; &nbsp; &nbsp; return

&nbsp; &nbsp; print("iGot 服务启动")

  

&nbsp; &nbsp; url = f'https://push.hellyw.com/{push_config.get("IGOT_PUSH_KEY")}'

&nbsp; &nbsp; data = {"title": title, "content": content}

&nbsp; &nbsp; headers = {"Content-Type": "application/x-www-form-urlencoded"}

&nbsp; &nbsp; response = requests.post(url, data=data, headers=headers).json()

  

&nbsp; &nbsp; if response["ret"] == 0:

&nbsp; &nbsp; &nbsp; &nbsp; print("iGot 推送成功！")

&nbsp; &nbsp; else:

&nbsp; &nbsp; &nbsp; &nbsp; print(f'iGot 推送失败！{response["errMsg"]}')

  
  

def serverJ(title: str, content: str) -> None:

&nbsp; &nbsp; """

&nbsp; &nbsp; 通过 serverJ 推送消息。

&nbsp; &nbsp; """

&nbsp; &nbsp; if not push_config.get("PUSH_KEY"):

&nbsp; &nbsp; &nbsp; &nbsp; print("serverJ 服务的 PUSH_KEY 未设置!!\n取消推送")

&nbsp; &nbsp; &nbsp; &nbsp; return

&nbsp; &nbsp; print("serverJ 服务启动")

  

&nbsp; &nbsp; data = {"text": title, "desp": content.replace("\n", "\n\n")}

&nbsp; &nbsp; if push_config.get("PUSH_KEY").find("SCT") != -1:

&nbsp; &nbsp; &nbsp; &nbsp; url = f'https://sctapi.ftqq.com/{push_config.get("PUSH_KEY")}.send'

&nbsp; &nbsp; else:

&nbsp; &nbsp; &nbsp; &nbsp; url = f'https://sc.ftqq.com/{push_config.get("PUSH_KEY")}.send'

&nbsp; &nbsp; response = requests.post(url, data=data).json()

  

&nbsp; &nbsp; if response.get("errno") == 0 or response.get("code") == 0:

&nbsp; &nbsp; &nbsp; &nbsp; print("serverJ 推送成功！")

&nbsp; &nbsp; else:

&nbsp; &nbsp; &nbsp; &nbsp; print(f'serverJ 推送失败！错误码：{response["message"]}')

  
  

def pushdeer(title: str, content: str) -> None:

&nbsp; &nbsp; """

&nbsp; &nbsp; 通过PushDeer 推送消息

&nbsp; &nbsp; """

&nbsp; &nbsp; if not push_config.get("DEER_KEY"):

&nbsp; &nbsp; &nbsp; &nbsp; print("PushDeer 服务的 DEER_KEY 未设置!!\n取消推送")

&nbsp; &nbsp; &nbsp; &nbsp; return

&nbsp; &nbsp; print("PushDeer 服务启动")

&nbsp; &nbsp; data = {

&nbsp; &nbsp; &nbsp; &nbsp; "text": title,

&nbsp; &nbsp; &nbsp; &nbsp; "desp": content,

&nbsp; &nbsp; &nbsp; &nbsp; "type": "markdown",

&nbsp; &nbsp; &nbsp; &nbsp; "pushkey": push_config.get("DEER_KEY"),

&nbsp; &nbsp; }

&nbsp; &nbsp; url = "https://api2.pushdeer.com/message/push"

&nbsp; &nbsp; if push_config.get("DEER_URL"):

&nbsp; &nbsp; &nbsp; &nbsp; url = push_config.get("DEER_URL")

  

&nbsp; &nbsp; response = requests.post(url, data=data).json()

  

&nbsp; &nbsp; if len(response.get("content").get("result")) > 0:

&nbsp; &nbsp; &nbsp; &nbsp; print("PushDeer 推送成功！")

&nbsp; &nbsp; else:

&nbsp; &nbsp; &nbsp; &nbsp; print("PushDeer 推送失败！错误信息：", response)

  
  

def chat(title: str, content: str) -> None:

&nbsp; &nbsp; """

&nbsp; &nbsp; 通过Chat 推送消息

&nbsp; &nbsp; """

&nbsp; &nbsp; if not push_config.get("CHAT_URL") or not push_config.get("CHAT_TOKEN"):

&nbsp; &nbsp; &nbsp; &nbsp; print("chat 服务的 CHAT_URL或CHAT_TOKEN 未设置!!\n取消推送")

&nbsp; &nbsp; &nbsp; &nbsp; return

&nbsp; &nbsp; print("chat 服务启动")

&nbsp; &nbsp; data = "payload=" + json.dumps({"text": title + "\n" + content})

&nbsp; &nbsp; url = push_config.get("CHAT_URL") + push_config.get("CHAT_TOKEN")

&nbsp; &nbsp; response = requests.post(url, data=data)

  

&nbsp; &nbsp; if response.status_code == 200:

&nbsp; &nbsp; &nbsp; &nbsp; print("Chat 推送成功！")

&nbsp; &nbsp; else:

&nbsp; &nbsp; &nbsp; &nbsp; print("Chat 推送失败！错误信息：", response)

  
  

def pushplus_bot(title: str, content: str) -> None:

&nbsp; &nbsp; """

&nbsp; &nbsp; 通过 push+ 推送消息。

&nbsp; &nbsp; """

&nbsp; &nbsp; if not push_config.get("PUSH_PLUS_TOKEN"):

&nbsp; &nbsp; &nbsp; &nbsp; print("PUSHPLUS 服务的 PUSH_PLUS_TOKEN 未设置!!\n取消推送")

&nbsp; &nbsp; &nbsp; &nbsp; return

&nbsp; &nbsp; print("PUSHPLUS 服务启动")

  

&nbsp; &nbsp; url = "http://www.pushplus.plus/send"

&nbsp; &nbsp; data = {

&nbsp; &nbsp; &nbsp; &nbsp; "token": push_config.get("PUSH_PLUS_TOKEN"),

&nbsp; &nbsp; &nbsp; &nbsp; "title": title,

&nbsp; &nbsp; &nbsp; &nbsp; "content": content,

&nbsp; &nbsp; &nbsp; &nbsp; "topic": push_config.get("PUSH_PLUS_USER"),

&nbsp; &nbsp; }

&nbsp; &nbsp; body = json.dumps(data).encode(encoding="utf-8")

&nbsp; &nbsp; headers = {"Content-Type": "application/json"}

&nbsp; &nbsp; response = requests.post(url=url, data=body, headers=headers).json()

  

&nbsp; &nbsp; if response["code"] == 200:

&nbsp; &nbsp; &nbsp; &nbsp; print("PUSHPLUS 推送成功！")

  

&nbsp; &nbsp; else:

&nbsp; &nbsp; &nbsp; &nbsp; url_old = "http://pushplus.hxtrip.com/send"

&nbsp; &nbsp; &nbsp; &nbsp; headers["Accept"] = "application/json"

&nbsp; &nbsp; &nbsp; &nbsp; response = requests.post(url=url_old, data=body, headers=headers).json()

  

&nbsp; &nbsp; &nbsp; &nbsp; if response["code"] == 200:

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; print("PUSHPLUS(hxtrip) 推送成功！")

  

&nbsp; &nbsp; &nbsp; &nbsp; else:

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; print("PUSHPLUS 推送失败！")

  
  

def weplus_bot(title: str, content: str) -> None:

&nbsp; &nbsp; """

&nbsp; &nbsp; 通过 微加机器人 推送消息。

&nbsp; &nbsp; """

&nbsp; &nbsp; if not push_config.get("WE_PLUS_BOT_TOKEN"):

&nbsp; &nbsp; &nbsp; &nbsp; print("微加机器人 服务的 WE_PLUS_BOT_TOKEN 未设置!!\n取消推送")

&nbsp; &nbsp; &nbsp; &nbsp; return

&nbsp; &nbsp; print("微加机器人 服务启动")

  

&nbsp; &nbsp; template = "txt"

&nbsp; &nbsp; if len(content) > 800:

&nbsp; &nbsp; &nbsp; &nbsp; template = "html"

  

&nbsp; &nbsp; url = "https://www.weplusbot.com/send"

&nbsp; &nbsp; data = {

&nbsp; &nbsp; &nbsp; &nbsp; "token": push_config.get("WE_PLUS_BOT_TOKEN"),

&nbsp; &nbsp; &nbsp; &nbsp; "title": title,

&nbsp; &nbsp; &nbsp; &nbsp; "content": content,

&nbsp; &nbsp; &nbsp; &nbsp; "template": template,

&nbsp; &nbsp; &nbsp; &nbsp; "receiver": push_config.get("WE_PLUS_BOT_RECEIVER"),

&nbsp; &nbsp; &nbsp; &nbsp; "version": push_config.get("WE_PLUS_BOT_VERSION"),

&nbsp; &nbsp; }

&nbsp; &nbsp; body = json.dumps(data).encode(encoding="utf-8")

&nbsp; &nbsp; headers = {"Content-Type": "application/json"}

&nbsp; &nbsp; response = requests.post(url=url, data=body, headers=headers).json()

  

&nbsp; &nbsp; if response["code"] == 200:

&nbsp; &nbsp; &nbsp; &nbsp; print("微加机器人 推送成功！")

&nbsp; &nbsp; else:

&nbsp; &nbsp; &nbsp; &nbsp; print("微加机器人 推送失败！")

  
  

def qmsg_bot(title: str, content: str) -> None:

&nbsp; &nbsp; """

&nbsp; &nbsp; 使用 qmsg 推送消息。

&nbsp; &nbsp; """

&nbsp; &nbsp; if not push_config.get("QMSG_KEY") or not push_config.get("QMSG_TYPE"):

&nbsp; &nbsp; &nbsp; &nbsp; print("qmsg 的 QMSG_KEY 或者 QMSG_TYPE 未设置!!\n取消推送")

&nbsp; &nbsp; &nbsp; &nbsp; return

&nbsp; &nbsp; print("qmsg 服务启动")

  

&nbsp; &nbsp; url = f'https://qmsg.zendee.cn/{push_config.get("QMSG_TYPE")}/{push_config.get("QMSG_KEY")}'

&nbsp; &nbsp; payload = {"msg": f'{title}\n\n{content.replace("----", "-")}'.encode("utf-8")}

&nbsp; &nbsp; response = requests.post(url=url, params=payload).json()

  

&nbsp; &nbsp; if response["code"] == 0:

&nbsp; &nbsp; &nbsp; &nbsp; print("qmsg 推送成功！")

&nbsp; &nbsp; else:

&nbsp; &nbsp; &nbsp; &nbsp; print(f'qmsg 推送失败！{response["reason"]}')

  
  

def wecom_app(title: str, content: str) -> None:

&nbsp; &nbsp; """

&nbsp; &nbsp; 通过 企业微信 APP 推送消息。

&nbsp; &nbsp; """

&nbsp; &nbsp; if not push_config.get("QYWX_AM"):

&nbsp; &nbsp; &nbsp; &nbsp; print("QYWX_AM 未设置!!\n取消推送")

&nbsp; &nbsp; &nbsp; &nbsp; return

&nbsp; &nbsp; QYWX_AM_AY = re.split(",", push_config.get("QYWX_AM"))

&nbsp; &nbsp; if 4 < len(QYWX_AM_AY) > 5:

&nbsp; &nbsp; &nbsp; &nbsp; print("QYWX_AM 设置错误!!\n取消推送")

&nbsp; &nbsp; &nbsp; &nbsp; return

&nbsp; &nbsp; print("企业微信 APP 服务启动")

  

&nbsp; &nbsp; corpid = QYWX_AM_AY[0]

&nbsp; &nbsp; corpsecret = QYWX_AM_AY[1]

&nbsp; &nbsp; touser = QYWX_AM_AY[2]

&nbsp; &nbsp; agentid = QYWX_AM_AY[3]

&nbsp; &nbsp; try:

&nbsp; &nbsp; &nbsp; &nbsp; media_id = QYWX_AM_AY[4]

&nbsp; &nbsp; except IndexError:

&nbsp; &nbsp; &nbsp; &nbsp; media_id = ""

&nbsp; &nbsp; wx = WeCom(corpid, corpsecret, agentid)

&nbsp; &nbsp; # 如果没有配置 media_id 默认就以 text 方式发送

&nbsp; &nbsp; if not media_id:

&nbsp; &nbsp; &nbsp; &nbsp; message = title + "\n\n" + content

&nbsp; &nbsp; &nbsp; &nbsp; response = wx.send_text(message, touser)

&nbsp; &nbsp; else:

&nbsp; &nbsp; &nbsp; &nbsp; response = wx.send_mpnews(title, content, media_id, touser)

  

&nbsp; &nbsp; if response == "ok":

&nbsp; &nbsp; &nbsp; &nbsp; print("企业微信推送成功！")

&nbsp; &nbsp; else:

&nbsp; &nbsp; &nbsp; &nbsp; print("企业微信推送失败！错误信息如下：\n", response)

  
  

class WeCom:

&nbsp; &nbsp; def __init__(self, corpid, corpsecret, agentid):

&nbsp; &nbsp; &nbsp; &nbsp; self.CORPID = corpid

&nbsp; &nbsp; &nbsp; &nbsp; self.CORPSECRET = corpsecret

&nbsp; &nbsp; &nbsp; &nbsp; self.AGENTID = agentid

&nbsp; &nbsp; &nbsp; &nbsp; self.ORIGIN = "https://qyapi.weixin.qq.com"

&nbsp; &nbsp; &nbsp; &nbsp; if push_config.get("QYWX_ORIGIN"):

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; self.ORIGIN = push_config.get("QYWX_ORIGIN")

  

&nbsp; &nbsp; def get_access_token(self):

&nbsp; &nbsp; &nbsp; &nbsp; url = f"{self.ORIGIN}/cgi-bin/gettoken"

&nbsp; &nbsp; &nbsp; &nbsp; values = {

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; "corpid": self.CORPID,

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; "corpsecret": self.CORPSECRET,

&nbsp; &nbsp; &nbsp; &nbsp; }

&nbsp; &nbsp; &nbsp; &nbsp; req = requests.post(url, params=values)

&nbsp; &nbsp; &nbsp; &nbsp; data = json.loads(req.text)

&nbsp; &nbsp; &nbsp; &nbsp; return data["access_token"]

  

&nbsp; &nbsp; def send_text(self, message, touser="@all"):

&nbsp; &nbsp; &nbsp; &nbsp; send_url = (

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; f"{self.ORIGIN}/cgi-bin/message/send?access_token={self.get_access_token()}"

&nbsp; &nbsp; &nbsp; &nbsp; )

&nbsp; &nbsp; &nbsp; &nbsp; send_values = {

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; "touser": touser,

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; "msgtype": "text",

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; "agentid": self.AGENTID,

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; "text": {"content": message},

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; "safe": "0",

&nbsp; &nbsp; &nbsp; &nbsp; }

&nbsp; &nbsp; &nbsp; &nbsp; send_msges = bytes(json.dumps(send_values), "utf-8")

&nbsp; &nbsp; &nbsp; &nbsp; respone = requests.post(send_url, send_msges)

&nbsp; &nbsp; &nbsp; &nbsp; respone = respone.json()

&nbsp; &nbsp; &nbsp; &nbsp; return respone["errmsg"]

  

&nbsp; &nbsp; def send_mpnews(self, title, message, media_id, touser="@all"):

&nbsp; &nbsp; &nbsp; &nbsp; send_url = (

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; f"{self.ORIGIN}/cgi-bin/message/send?access_token={self.get_access_token()}"

&nbsp; &nbsp; &nbsp; &nbsp; )

&nbsp; &nbsp; &nbsp; &nbsp; send_values = {

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; "touser": touser,

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; "msgtype": "mpnews",

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; "agentid": self.AGENTID,

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; "mpnews": {

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; "articles": [

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; {

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; "title": title,

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; "thumb_media_id": media_id,

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; "author": "Author",

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; "content_source_url": "",

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; "content": message.replace("\n", "<br/>"),

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; "digest": message,

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; }

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; ]

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; },

&nbsp; &nbsp; &nbsp; &nbsp; }

&nbsp; &nbsp; &nbsp; &nbsp; send_msges = bytes(json.dumps(send_values), "utf-8")

&nbsp; &nbsp; &nbsp; &nbsp; respone = requests.post(send_url, send_msges)

&nbsp; &nbsp; &nbsp; &nbsp; respone = respone.json()

&nbsp; &nbsp; &nbsp; &nbsp; return respone["errmsg"]

  
  

def wecom_bot(title: str, content: str) -> None:

&nbsp; &nbsp; """

&nbsp; &nbsp; 通过 企业微信机器人 推送消息。

&nbsp; &nbsp; """

&nbsp; &nbsp; if not push_config.get("QYWX_KEY"):

&nbsp; &nbsp; &nbsp; &nbsp; print("企业微信机器人 服务的 QYWX_KEY 未设置!!\n取消推送")

&nbsp; &nbsp; &nbsp; &nbsp; return

&nbsp; &nbsp; print("企业微信机器人服务启动")

  

&nbsp; &nbsp; origin = "https://qyapi.weixin.qq.com"

&nbsp; &nbsp; if push_config.get("QYWX_ORIGIN"):

&nbsp; &nbsp; &nbsp; &nbsp; origin = push_config.get("QYWX_ORIGIN")

  

&nbsp; &nbsp; url = f"{origin}/cgi-bin/webhook/send?key={push_config.get('QYWX_KEY')}"

&nbsp; &nbsp; headers = {"Content-Type": "application/json;charset=utf-8"}

&nbsp; &nbsp; data = {"msgtype": "text", "text": {"content": f"{title}\n\n{content}"}}

&nbsp; &nbsp; response = requests.post(

&nbsp; &nbsp; &nbsp; &nbsp; url=url, data=json.dumps(data), headers=headers, timeout=15

&nbsp; &nbsp; ).json()

  

&nbsp; &nbsp; if response["errcode"] == 0:

&nbsp; &nbsp; &nbsp; &nbsp; print("企业微信机器人推送成功！")

&nbsp; &nbsp; else:

&nbsp; &nbsp; &nbsp; &nbsp; print("企业微信机器人推送失败！")

  
  

def telegram_bot(title: str, content: str) -> None:

&nbsp; &nbsp; """

&nbsp; &nbsp; 使用 telegram 机器人 推送消息。

&nbsp; &nbsp; """

&nbsp; &nbsp; if not push_config.get("TG_BOT_TOKEN") or not push_config.get("TG_USER_ID"):

&nbsp; &nbsp; &nbsp; &nbsp; print("tg 服务的 bot_token 或者 user_id 未设置!!\n取消推送")

&nbsp; &nbsp; &nbsp; &nbsp; return

&nbsp; &nbsp; print("tg 服务启动")

  

&nbsp; &nbsp; if push_config.get("TG_API_HOST"):

&nbsp; &nbsp; &nbsp; &nbsp; url = f"{push_config.get('TG_API_HOST')}/bot{push_config.get('TG_BOT_TOKEN')}/sendMessage"

&nbsp; &nbsp; else:

&nbsp; &nbsp; &nbsp; &nbsp; url = (

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; f"https://api.telegram.org/bot{push_config.get('TG_BOT_TOKEN')}/sendMessage"

&nbsp; &nbsp; &nbsp; &nbsp; )

&nbsp; &nbsp; headers = {"Content-Type": "application/x-www-form-urlencoded"}

&nbsp; &nbsp; payload = {

&nbsp; &nbsp; &nbsp; &nbsp; "chat_id": str(push_config.get("TG_USER_ID")),

&nbsp; &nbsp; &nbsp; &nbsp; "text": f"{title}\n\n{content}",

&nbsp; &nbsp; &nbsp; &nbsp; "disable_web_page_preview": "true",

&nbsp; &nbsp; }

&nbsp; &nbsp; proxies = None

&nbsp; &nbsp; if push_config.get("TG_PROXY_HOST") and push_config.get("TG_PROXY_PORT"):

&nbsp; &nbsp; &nbsp; &nbsp; if push_config.get("TG_PROXY_AUTH") is not None and "@" not in push_config.get(

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; "TG_PROXY_HOST"

&nbsp; &nbsp; &nbsp; &nbsp; ):

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; push_config["TG_PROXY_HOST"] = (

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; push_config.get("TG_PROXY_AUTH")

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; + "@"

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; + push_config.get("TG_PROXY_HOST")

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; )

&nbsp; &nbsp; &nbsp; &nbsp; proxyStr = "http://{}:{}".format(

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; push_config.get("TG_PROXY_HOST"), push_config.get("TG_PROXY_PORT")

&nbsp; &nbsp; &nbsp; &nbsp; )

&nbsp; &nbsp; &nbsp; &nbsp; proxies = {"http": proxyStr, "https": proxyStr}

&nbsp; &nbsp; response = requests.post(

&nbsp; &nbsp; &nbsp; &nbsp; url=url, headers=headers, params=payload, proxies=proxies

&nbsp; &nbsp; ).json()

  

&nbsp; &nbsp; if response["ok"]:

&nbsp; &nbsp; &nbsp; &nbsp; print("tg 推送成功！")

&nbsp; &nbsp; else:

&nbsp; &nbsp; &nbsp; &nbsp; print("tg 推送失败！")

  
  

def aibotk(title: str, content: str) -> None:

&nbsp; &nbsp; """

&nbsp; &nbsp; 使用 智能微秘书 推送消息。

&nbsp; &nbsp; """

&nbsp; &nbsp; if (

&nbsp; &nbsp; &nbsp; &nbsp; not push_config.get("AIBOTK_KEY")

&nbsp; &nbsp; &nbsp; &nbsp; or not push_config.get("AIBOTK_TYPE")

&nbsp; &nbsp; &nbsp; &nbsp; or not push_config.get("AIBOTK_NAME")

&nbsp; &nbsp; ):

&nbsp; &nbsp; &nbsp; &nbsp; print(

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; "智能微秘书 的 AIBOTK_KEY 或者 AIBOTK_TYPE 或者 AIBOTK_NAME 未设置!!\n取消推送"

&nbsp; &nbsp; &nbsp; &nbsp; )

&nbsp; &nbsp; &nbsp; &nbsp; return

&nbsp; &nbsp; print("智能微秘书 服务启动")

  

&nbsp; &nbsp; if push_config.get("AIBOTK_TYPE") == "room":

&nbsp; &nbsp; &nbsp; &nbsp; url = "https://api-bot.aibotk.com/openapi/v1/chat/room"

&nbsp; &nbsp; &nbsp; &nbsp; data = {

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; "apiKey": push_config.get("AIBOTK_KEY"),

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; "roomName": push_config.get("AIBOTK_NAME"),

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; "message": {"type": 1, "content": f"【青龙快讯】\n\n{title}\n{content}"},

&nbsp; &nbsp; &nbsp; &nbsp; }

&nbsp; &nbsp; else:

&nbsp; &nbsp; &nbsp; &nbsp; url = "https://api-bot.aibotk.com/openapi/v1/chat/contact"

&nbsp; &nbsp; &nbsp; &nbsp; data = {

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; "apiKey": push_config.get("AIBOTK_KEY"),

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; "name": push_config.get("AIBOTK_NAME"),

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; "message": {"type": 1, "content": f"【青龙快讯】\n\n{title}\n{content}"},

&nbsp; &nbsp; &nbsp; &nbsp; }

&nbsp; &nbsp; body = json.dumps(data).encode(encoding="utf-8")

&nbsp; &nbsp; headers = {"Content-Type": "application/json"}

&nbsp; &nbsp; response = requests.post(url=url, data=body, headers=headers).json()

&nbsp; &nbsp; print(response)

&nbsp; &nbsp; if response["code"] == 0:

&nbsp; &nbsp; &nbsp; &nbsp; print("智能微秘书 推送成功！")

&nbsp; &nbsp; else:

&nbsp; &nbsp; &nbsp; &nbsp; print(f'智能微秘书 推送失败！{response["error"]}')

  
  

def smtp(title: str, content: str) -> None:

&nbsp; &nbsp; """

&nbsp; &nbsp; 使用 SMTP 邮件 推送消息。

&nbsp; &nbsp; """

&nbsp; &nbsp; if (

&nbsp; &nbsp; &nbsp; &nbsp; not push_config.get("SMTP_SERVER")

&nbsp; &nbsp; &nbsp; &nbsp; or not push_config.get("SMTP_SSL")

&nbsp; &nbsp; &nbsp; &nbsp; or not push_config.get("SMTP_EMAIL")

&nbsp; &nbsp; &nbsp; &nbsp; or not push_config.get("SMTP_PASSWORD")

&nbsp; &nbsp; &nbsp; &nbsp; or not push_config.get("SMTP_NAME")

&nbsp; &nbsp; ):

&nbsp; &nbsp; &nbsp; &nbsp; print(

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; "SMTP 邮件 的 SMTP_SERVER 或者 SMTP_SSL 或者 SMTP_EMAIL 或者 SMTP_PASSWORD 或者 SMTP_NAME 未设置!!\n取消推送"

&nbsp; &nbsp; &nbsp; &nbsp; )

&nbsp; &nbsp; &nbsp; &nbsp; return

&nbsp; &nbsp; print("SMTP 邮件 服务启动")

  

&nbsp; &nbsp; message = MIMEText(content, "plain", "utf-8")

&nbsp; &nbsp; message["From"] = formataddr(

&nbsp; &nbsp; &nbsp; &nbsp; (

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Header(push_config.get("SMTP_NAME"), "utf-8").encode(),

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; push_config.get("SMTP_EMAIL"),

&nbsp; &nbsp; &nbsp; &nbsp; )

&nbsp; &nbsp; )

&nbsp; &nbsp; message["To"] = formataddr(

&nbsp; &nbsp; &nbsp; &nbsp; (

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Header(push_config.get("SMTP_NAME"), "utf-8").encode(),

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; push_config.get("SMTP_EMAIL"),

&nbsp; &nbsp; &nbsp; &nbsp; )

&nbsp; &nbsp; )

&nbsp; &nbsp; message["Subject"] = Header(title, "utf-8")

  

&nbsp; &nbsp; try:

&nbsp; &nbsp; &nbsp; &nbsp; smtp_server = (

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; smtplib.SMTP_SSL(push_config.get("SMTP_SERVER"))

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; if push_config.get("SMTP_SSL") == "true"

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; else smtplib.SMTP(push_config.get("SMTP_SERVER"))

&nbsp; &nbsp; &nbsp; &nbsp; )

&nbsp; &nbsp; &nbsp; &nbsp; smtp_server.login(

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; push_config.get("SMTP_EMAIL"), push_config.get("SMTP_PASSWORD")

&nbsp; &nbsp; &nbsp; &nbsp; )

&nbsp; &nbsp; &nbsp; &nbsp; smtp_server.sendmail(

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; push_config.get("SMTP_EMAIL"),

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; push_config.get("SMTP_EMAIL"),

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; message.as_bytes(),

&nbsp; &nbsp; &nbsp; &nbsp; )

&nbsp; &nbsp; &nbsp; &nbsp; smtp_server.close()

&nbsp; &nbsp; &nbsp; &nbsp; print("SMTP 邮件 推送成功！")

&nbsp; &nbsp; except Exception as e:

&nbsp; &nbsp; &nbsp; &nbsp; print(f"SMTP 邮件 推送失败！{e}")

  
  

def pushme(title: str, content: str) -> None:

&nbsp; &nbsp; """

&nbsp; &nbsp; 使用 PushMe 推送消息。

&nbsp; &nbsp; """

&nbsp; &nbsp; if not push_config.get("PUSHME_KEY"):

&nbsp; &nbsp; &nbsp; &nbsp; print("PushMe 服务的 PUSHME_KEY 未设置!!\n取消推送")

&nbsp; &nbsp; &nbsp; &nbsp; return

&nbsp; &nbsp; print("PushMe 服务启动")

  

&nbsp; &nbsp; url = (

&nbsp; &nbsp; &nbsp; &nbsp; push_config.get("PUSHME_URL")

&nbsp; &nbsp; &nbsp; &nbsp; if push_config.get("PUSHME_URL")

&nbsp; &nbsp; &nbsp; &nbsp; else "https://push.i-i.me/"

&nbsp; &nbsp; )

&nbsp; &nbsp; data = {

&nbsp; &nbsp; &nbsp; &nbsp; "push_key": push_config.get("PUSHME_KEY"),

&nbsp; &nbsp; &nbsp; &nbsp; "title": title,

&nbsp; &nbsp; &nbsp; &nbsp; "content": content,

&nbsp; &nbsp; &nbsp; &nbsp; "date": push_config.get("date") if push_config.get("date") else "",

&nbsp; &nbsp; &nbsp; &nbsp; "type": push_config.get("type") if push_config.get("type") else "",

&nbsp; &nbsp; }

&nbsp; &nbsp; response = requests.post(url, data=data)

  

&nbsp; &nbsp; if response.status_code == 200 and response.text == "success":

&nbsp; &nbsp; &nbsp; &nbsp; print("PushMe 推送成功！")

&nbsp; &nbsp; else:

&nbsp; &nbsp; &nbsp; &nbsp; print(f"PushMe 推送失败！{response.status_code} {response.text}")

  
  

def chronocat(title: str, content: str) -> None:

&nbsp; &nbsp; """

&nbsp; &nbsp; 使用 CHRONOCAT 推送消息。

&nbsp; &nbsp; """

&nbsp; &nbsp; if (

&nbsp; &nbsp; &nbsp; &nbsp; not push_config.get("CHRONOCAT_URL")

&nbsp; &nbsp; &nbsp; &nbsp; or not push_config.get("CHRONOCAT_QQ")

&nbsp; &nbsp; &nbsp; &nbsp; or not push_config.get("CHRONOCAT_TOKEN")

&nbsp; &nbsp; ):

&nbsp; &nbsp; &nbsp; &nbsp; print("CHRONOCAT 服务的 CHRONOCAT_URL 或 CHRONOCAT_QQ 未设置!!\n取消推送")

&nbsp; &nbsp; &nbsp; &nbsp; return

  

&nbsp; &nbsp; print("CHRONOCAT 服务启动")

  

&nbsp; &nbsp; user_ids = re.findall(r"user_id=(\d+)", push_config.get("CHRONOCAT_QQ"))

&nbsp; &nbsp; group_ids = re.findall(r"group_id=(\d+)", push_config.get("CHRONOCAT_QQ"))

  

&nbsp; &nbsp; url = f'{push_config.get("CHRONOCAT_URL")}/api/message/send'

&nbsp; &nbsp; headers = {

&nbsp; &nbsp; &nbsp; &nbsp; "Content-Type": "application/json",

&nbsp; &nbsp; &nbsp; &nbsp; "Authorization": f'Bearer {push_config.get("CHRONOCAT_TOKEN")}',

&nbsp; &nbsp; }

  

&nbsp; &nbsp; for chat_type, ids in [(1, user_ids), (2, group_ids)]:

&nbsp; &nbsp; &nbsp; &nbsp; if not ids:

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; continue

&nbsp; &nbsp; &nbsp; &nbsp; for chat_id in ids:

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; data = {

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; "peer": {"chatType": chat_type, "peerUin": chat_id},

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; "elements": [

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; {

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; "elementType": 1,

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; "textElement": {"content": f"{title}\n\n{content}"},

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; }

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; ],

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; }

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; response = requests.post(url, headers=headers, data=json.dumps(data))

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; if response.status_code == 200:

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; if chat_type == 1:

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; print(f"QQ个人消息:{ids}推送成功！")

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; else:

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; print(f"QQ群消息:{ids}推送成功！")

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; else:

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; if chat_type == 1:

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; print(f"QQ个人消息:{ids}推送失败！")

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; else:

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; print(f"QQ群消息:{ids}推送失败！")

  
  

def parse_headers(headers):

&nbsp; &nbsp; if not headers:

&nbsp; &nbsp; &nbsp; &nbsp; return {}

  

&nbsp; &nbsp; parsed = {}

&nbsp; &nbsp; lines = headers.split("\n")

  

&nbsp; &nbsp; for line in lines:

&nbsp; &nbsp; &nbsp; &nbsp; i = line.find(":")

&nbsp; &nbsp; &nbsp; &nbsp; if i == -1:

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; continue

  

&nbsp; &nbsp; &nbsp; &nbsp; key = line[:i].strip().lower()

&nbsp; &nbsp; &nbsp; &nbsp; val = line[i + 1 :].strip()

&nbsp; &nbsp; &nbsp; &nbsp; parsed[key] = parsed.get(key, "") + ", " + val if key in parsed else val

  

&nbsp; &nbsp; return parsed

  
  

def parse_string(input_string, value_format_fn=None):

&nbsp; &nbsp; matches = {}

&nbsp; &nbsp; pattern = r"(\w+):\s*((?:(?!\n\w+:).)*)"

&nbsp; &nbsp; regex = re.compile(pattern)

&nbsp; &nbsp; for match in regex.finditer(input_string):

&nbsp; &nbsp; &nbsp; &nbsp; key, value = match.group(1).strip(), match.group(2).strip()

&nbsp; &nbsp; &nbsp; &nbsp; try:

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; value = value_format_fn(value) if value_format_fn else value

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; json_value = json.loads(value)

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; matches[key] = json_value

&nbsp; &nbsp; &nbsp; &nbsp; except:

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; matches[key] = value

&nbsp; &nbsp; return matches

  
  

def parse_body(body, content_type, value_format_fn=None):

&nbsp; &nbsp; if not body or content_type == "text/plain":

&nbsp; &nbsp; &nbsp; &nbsp; return value_format_fn(body) if value_format_fn and body else body

  

&nbsp; &nbsp; parsed = parse_string(body, value_format_fn)

  

&nbsp; &nbsp; if content_type == "application/x-www-form-urlencoded":

&nbsp; &nbsp; &nbsp; &nbsp; data = urllib.parse.urlencode(parsed, doseq=True)

&nbsp; &nbsp; &nbsp; &nbsp; return data

  

&nbsp; &nbsp; if content_type == "application/json":

&nbsp; &nbsp; &nbsp; &nbsp; data = json.dumps(parsed)

&nbsp; &nbsp; &nbsp; &nbsp; return data

  

&nbsp; &nbsp; return parsed

  
  

def custom_notify(title: str, content: str) -> None:

&nbsp; &nbsp; """

&nbsp; &nbsp; 通过 自定义通知 推送消息。

&nbsp; &nbsp; """

&nbsp; &nbsp; if not push_config.get("WEBHOOK_URL") or not push_config.get("WEBHOOK_METHOD"):

&nbsp; &nbsp; &nbsp; &nbsp; print("自定义通知的 WEBHOOK_URL 或 WEBHOOK_METHOD 未设置!!\n取消推送")

&nbsp; &nbsp; &nbsp; &nbsp; return

  

&nbsp; &nbsp; print("自定义通知服务启动")

  

&nbsp; &nbsp; WEBHOOK_URL = push_config.get("WEBHOOK_URL")

&nbsp; &nbsp; WEBHOOK_METHOD = push_config.get("WEBHOOK_METHOD")

&nbsp; &nbsp; WEBHOOK_CONTENT_TYPE = push_config.get("WEBHOOK_CONTENT_TYPE")

&nbsp; &nbsp; WEBHOOK_BODY = push_config.get("WEBHOOK_BODY")

&nbsp; &nbsp; WEBHOOK_HEADERS = push_config.get("WEBHOOK_HEADERS")

  

&nbsp; &nbsp; if "$title" not in WEBHOOK_URL and "$title" not in WEBHOOK_BODY:

&nbsp; &nbsp; &nbsp; &nbsp; print("请求头或者请求体中必须包含 $title 和 $content")

&nbsp; &nbsp; &nbsp; &nbsp; return

  

&nbsp; &nbsp; headers = parse_headers(WEBHOOK_HEADERS)

&nbsp; &nbsp; body = parse_body(

&nbsp; &nbsp; &nbsp; &nbsp; WEBHOOK_BODY,

&nbsp; &nbsp; &nbsp; &nbsp; WEBHOOK_CONTENT_TYPE,

&nbsp; &nbsp; &nbsp; &nbsp; lambda v: v.replace("$title", title.replace("\n", "\\n")).replace(

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; "$content", content.replace("\n", "\\n")

&nbsp; &nbsp; &nbsp; &nbsp; ),

&nbsp; &nbsp; )

&nbsp; &nbsp; formatted_url = WEBHOOK_URL.replace(

&nbsp; &nbsp; &nbsp; &nbsp; "$title", urllib.parse.quote_plus(title)

&nbsp; &nbsp; ).replace("$content", urllib.parse.quote_plus(content))

&nbsp; &nbsp; response = requests.request(

&nbsp; &nbsp; &nbsp; &nbsp; method=WEBHOOK_METHOD, url=formatted_url, headers=headers, timeout=15, data=body

&nbsp; &nbsp; )

  

&nbsp; &nbsp; if response.status_code == 200:

&nbsp; &nbsp; &nbsp; &nbsp; print("自定义通知推送成功！")

&nbsp; &nbsp; else:

&nbsp; &nbsp; &nbsp; &nbsp; print(f"自定义通知推送失败！{response.status_code} {response.text}")

  
  

def one() -> str:

&nbsp; &nbsp; """

&nbsp; &nbsp; 获取一条一言。

&nbsp; &nbsp; :return:

&nbsp; &nbsp; """

&nbsp; &nbsp; url = "https://v1.hitokoto.cn/"

&nbsp; &nbsp; res = requests.get(url).json()

&nbsp; &nbsp; return res["hitokoto"] + " &nbsp; &nbsp;----" + res["from"]

  
  

def add_notify_function():

&nbsp; &nbsp; notify_function = []

&nbsp; &nbsp; if push_config.get("BARK_PUSH"):

&nbsp; &nbsp; &nbsp; &nbsp; notify_function.append(bark)

&nbsp; &nbsp; if push_config.get("CONSOLE"):

&nbsp; &nbsp; &nbsp; &nbsp; notify_function.append(console)

&nbsp; &nbsp; if push_config.get("DD_BOT_TOKEN") and push_config.get("DD_BOT_SECRET"):

&nbsp; &nbsp; &nbsp; &nbsp; notify_function.append(dingding_bot)

&nbsp; &nbsp; if push_config.get("FSKEY"):

&nbsp; &nbsp; &nbsp; &nbsp; notify_function.append(feishu_bot)

&nbsp; &nbsp; if push_config.get("GOBOT_URL") and push_config.get("GOBOT_QQ"):

&nbsp; &nbsp; &nbsp; &nbsp; notify_function.append(go_cqhttp)

&nbsp; &nbsp; if push_config.get("GOTIFY_URL") and push_config.get("GOTIFY_TOKEN"):

&nbsp; &nbsp; &nbsp; &nbsp; notify_function.append(gotify)

&nbsp; &nbsp; if push_config.get("IGOT_PUSH_KEY"):

&nbsp; &nbsp; &nbsp; &nbsp; notify_function.append(iGot)

&nbsp; &nbsp; if push_config.get("PUSH_KEY"):

&nbsp; &nbsp; &nbsp; &nbsp; notify_function.append(serverJ)

&nbsp; &nbsp; if push_config.get("DEER_KEY"):

&nbsp; &nbsp; &nbsp; &nbsp; notify_function.append(pushdeer)

&nbsp; &nbsp; if push_config.get("CHAT_URL") and push_config.get("CHAT_TOKEN"):

&nbsp; &nbsp; &nbsp; &nbsp; notify_function.append(chat)

&nbsp; &nbsp; if push_config.get("PUSH_PLUS_TOKEN"):

&nbsp; &nbsp; &nbsp; &nbsp; notify_function.append(pushplus_bot)

&nbsp; &nbsp; if push_config.get("WE_PLUS_BOT_TOKEN"):

&nbsp; &nbsp; &nbsp; &nbsp; notify_function.append(weplus_bot)

&nbsp; &nbsp; if push_config.get("QMSG_KEY") and push_config.get("QMSG_TYPE"):

&nbsp; &nbsp; &nbsp; &nbsp; notify_function.append(qmsg_bot)

&nbsp; &nbsp; if push_config.get("QYWX_AM"):

&nbsp; &nbsp; &nbsp; &nbsp; notify_function.append(wecom_app)

&nbsp; &nbsp; if push_config.get("QYWX_KEY"):

&nbsp; &nbsp; &nbsp; &nbsp; notify_function.append(wecom_bot)

&nbsp; &nbsp; if push_config.get("TG_BOT_TOKEN") and push_config.get("TG_USER_ID"):

&nbsp; &nbsp; &nbsp; &nbsp; notify_function.append(telegram_bot)

&nbsp; &nbsp; if (

&nbsp; &nbsp; &nbsp; &nbsp; push_config.get("AIBOTK_KEY")

&nbsp; &nbsp; &nbsp; &nbsp; and push_config.get("AIBOTK_TYPE")

&nbsp; &nbsp; &nbsp; &nbsp; and push_config.get("AIBOTK_NAME")

&nbsp; &nbsp; ):

&nbsp; &nbsp; &nbsp; &nbsp; notify_function.append(aibotk)

&nbsp; &nbsp; if (

&nbsp; &nbsp; &nbsp; &nbsp; push_config.get("SMTP_SERVER")

&nbsp; &nbsp; &nbsp; &nbsp; and push_config.get("SMTP_SSL")

&nbsp; &nbsp; &nbsp; &nbsp; and push_config.get("SMTP_EMAIL")

&nbsp; &nbsp; &nbsp; &nbsp; and push_config.get("SMTP_PASSWORD")

&nbsp; &nbsp; &nbsp; &nbsp; and push_config.get("SMTP_NAME")

&nbsp; &nbsp; ):

&nbsp; &nbsp; &nbsp; &nbsp; notify_function.append(smtp)

&nbsp; &nbsp; if push_config.get("PUSHME_KEY"):

&nbsp; &nbsp; &nbsp; &nbsp; notify_function.append(pushme)

&nbsp; &nbsp; if (

&nbsp; &nbsp; &nbsp; &nbsp; push_config.get("CHRONOCAT_URL")

&nbsp; &nbsp; &nbsp; &nbsp; and push_config.get("CHRONOCAT_QQ")

&nbsp; &nbsp; &nbsp; &nbsp; and push_config.get("CHRONOCAT_TOKEN")

&nbsp; &nbsp; ):

&nbsp; &nbsp; &nbsp; &nbsp; notify_function.append(chronocat)

&nbsp; &nbsp; if push_config.get("WEBHOOK_URL") and push_config.get("WEBHOOK_METHOD"):

&nbsp; &nbsp; &nbsp; &nbsp; notify_function.append(custom_notify)

  

&nbsp; &nbsp; if not notify_function:

&nbsp; &nbsp; &nbsp; &nbsp; print(f"无推送渠道，请检查通知变量是否正确")

&nbsp; &nbsp; return notify_function

  
  

def send(title: str, content: str, ignore_default_config: bool = False, **kwargs):

&nbsp; &nbsp; if kwargs:

&nbsp; &nbsp; &nbsp; &nbsp; global push_config

&nbsp; &nbsp; &nbsp; &nbsp; if ignore_default_config:

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; push_config = kwargs &nbsp;# 清空从环境变量获取的配置

&nbsp; &nbsp; &nbsp; &nbsp; else:

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; push_config.update(kwargs)

  

&nbsp; &nbsp; if not content:

&nbsp; &nbsp; &nbsp; &nbsp; print(f"{title} 推送内容为空！")

&nbsp; &nbsp; &nbsp; &nbsp; return

  

&nbsp; &nbsp; # 根据标题跳过一些消息推送，环境变量：SKIP_PUSH_TITLE 用回车分隔

&nbsp; &nbsp; skipTitle = os.getenv("SKIP_PUSH_TITLE")

&nbsp; &nbsp; if skipTitle:

&nbsp; &nbsp; &nbsp; &nbsp; if title in re.split("\n", skipTitle):

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; print(f"{title} 在SKIP_PUSH_TITLE环境变量内，跳过推送！")

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; return

  

&nbsp; &nbsp; hitokoto = push_config.get("HITOKOTO")

&nbsp; &nbsp; content += "\n\n" + one() if hitokoto != "false" else ""

  

&nbsp; &nbsp; notify_function = add_notify_function()

&nbsp; &nbsp; ts = [

&nbsp; &nbsp; &nbsp; &nbsp; threading.Thread(target=mode, args=(title, content), name=mode.__name__)

&nbsp; &nbsp; &nbsp; &nbsp; for mode in notify_function

&nbsp; &nbsp; ]

&nbsp; &nbsp; [t.start() for t in ts]

&nbsp; &nbsp; [t.join() for t in ts]

  
  

def main():

&nbsp; &nbsp; send("title", "content")

  
  

if __name__ == "__main__":

&nbsp; &nbsp; main()
