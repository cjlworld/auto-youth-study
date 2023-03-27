import re
import os
import requests
import json
import yaml
import time
import random
from dingtalkchatbot.chatbot import DingtalkChatbot

getToken_url = 'https://qczj.h5yunban.com/qczj-youth-learning/cgi-bin/login/we-chat/callback'
getUserInfo_url = 'https://qczj.h5yunban.com/qczj-youth-learning/cgi-bin/user-api/course/last-info'
getClass_url = 'https://qczj.h5yunban.com/qczj-youth-learning/cgi-bin/common-api/course/current'
checkin_url = 'https://qczj.h5yunban.com/qczj-youth-learning/cgi-bin/user-api/course/join'
getPersonalInfo_url = 'https://qczj.h5yunban.com/qczj-youth-learning/cgi-bin/user-api/info'

headers = {
    'Content-Type': 'text/plain'
}


def getYmlConfig(yaml_file='config.yml'):
    with open(yaml_file, 'r', encoding='utf-8') as f:
        file_data = f.read()
    return dict(yaml.load(file_data, Loader=yaml.FullLoader))


def getToken(openId):
    # 根据openId获得token
    try:
        token = requests.get(url=getToken_url, params=openId, headers=headers)
        Token_raw = token.text
        Token = re.findall('[A-Z0-9]{8}[-][A-Z0-9]{4}[-][A-Z0-9]{4}[-][A-Z0-9]{4}[-][A-Z0-9]{12}', Token_raw)[0]
        print('获取Token为:' + Token)
        accessToken = {
            'accessToken': Token
        }
        return accessToken
    except:
        print('获取Token失败，请检查openId是否正确')


def getinfo(accessToken):
    # 根据accessToken获得用户信息
    try:
        getUserInfo = requests.get(getUserInfo_url, params=accessToken, headers=headers)
        userInfo = getUserInfo.json()
        cardNo = userInfo["result"]["cardNo"]
        nid = userInfo["result"]["nid"]
        getClass = requests.get(getClass_url, params=accessToken, headers=headers)
        Class = getClass.json()
        classId = Class["result"]["id"]
        infos: list = userInfo['result']['nodes']
        Faculty = [item['title'] for item in infos]
        print('签到课程为：' + classId, '\n您填写的个人信息为：' + cardNo, '\n您的签到所属组织为：' + str(Faculty))
        checkinData = {
            'course': classId,
            'subOrg': None,
            'nid': nid,
            'cardNo': cardNo
        }
        return checkinData
    except Exception as e:
        if "is not subscriptable" in str(e):
            print("openid出错,无法获得您的信息")
        print(f'获取历史信息失败，请您手动打卡：{e}')


def signup(accessToken, checkinData):
    # 根据token和data完成打卡
    checkin = requests.post(checkin_url, params=accessToken, data=json.dumps(checkinData), headers=headers)
    result = checkin.json()

    if result["status"] == 200:
        print("签到成功")
        return 1
    else:
        print('出现错误，错误码：' + str(result["status"]))
        print('错误信息：' + str(result["message"]))
        return result["message"]


def getPersonalInfo(accessToken):
    # 获得个人信息
    info = requests.get(url=getPersonalInfo_url, params=accessToken, headers=headers).json()
    print('查询积分结果:', info['result']['score'])
    return info['result']
    # return info['result']['score']

def sendDing(text):
    DING_WEBHOOK = os.getenv("DING_WEBHOOK") # webhook
    DING_SECRET = os.getenv("DING_SECRET")  # 加签

    dingbot = DingtalkChatbot(DING_WEBHOOK, secret = DING_SECRET) # init
    dingbot.send_markdown(title = "青年大学习学习报告已送达, 送报员 905 持续为您服务！", text = text, is_at_all = False)
    
if __name__ == "__main__":
    config = getYmlConfig()
    for index, eachuser in enumerate(config['users']):
        print(eachuser['user']['name'], 'openId为 ', eachuser['user']['openid'])
        openid = {
            'appid': 'wx56b888a1409a2920',
            'openid': eachuser['user']['openid']
        }
        accesstoken = getToken(openid) # 用 openid 获取 token 
        checkindata = getinfo(accesstoken) # 用 token 获取个人信息
        if checkindata is not None:
            personalInfo_0 = getPersonalInfo(accesstoken)
            resStatus = signup(accesstoken, checkindata) # 打卡
            personalInfo_1 = getPersonalInfo(accesstoken) # 获取积分
            sendDing("青年大学习学习成功: \n\n- 打卡前的分数为: {:d} \n- 当前分数为: {:d}. \n\n 送报员 905 祝您生活愉快! ".format(personalInfo_0['score'],personalInfo_1['score']))
            # 需要自行配置接口
#             sendMail(eachuser,personalInfo,resStatus)
            # 需要自行配置发送邮箱
#             sendMail(eachuser['user']['mail'], "邮件标题", "邮件内容")
        else:
            sendDing("青年大学习学习失败，获取个人信息失败，请尽快查看错误。")
        print('===========================================')