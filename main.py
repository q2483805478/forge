import string
import time

import requests
import random
import json
from selenium import webdriver
import os, subprocess, psutil
from time import ctime
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from pyquery import PyQuery as pq
from bs4 import BeautifulSoup

service = Service();
option = Options();
# 隐藏浏览器
# option.add_argument("--headless")
browser = webdriver.Edge(service=service, options=option)

apikey = 'AIzaSyCCPhaBp3ldeK6GjgFV9hfgrIzG1kpP90Y'

# forge默认密码
PASSWORD = "LANhuifang.123"


def emailInfo(id, sessauth, sessid, emailName):
    header = {
        "Cookie": "roundcube_sessid=" + sessid + "; roundcube_sessauth=" + sessauth,
        "Host": "pimar.cn",
        "Origin": "http://pimar.cn",
        "Referer": "http://pimar.cn/?_task=mail&_mbox=INBOX",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0"
    }

    r = requests.post('http://pimar.cn/?_task=mail&_uid=' + id + '&_mbox=INBOX&_framed=1&_action=preview',
                      headers=header)
    if str(r.content).__contains__("Forge - Verify Your Email ID"):
        html = BeautifulSoup(str(r.content), 'html.parser')
        print(html)
        v1mcnButton = html.select_one('.v1mcnButton')
        if v1mcnButton and 'href' in v1mcnButton.attrs:
            href_value = v1mcnButton['href']
            print(href_value)
            browser.implicitly_wait(10)
            try:
                browser.get(href_value)
                browser.find_element(By.ID, value="loginEmail").send_keys(emailName)
                browser.find_element(By.ID, value="loginPassword").send_keys(PASSWORD)
                browser.find_element(By.ID, value="btnlogin-login").click()
                time.sleep(5)
                browser.find_element(By.ID, value="username").send_keys(generate_random_string());
                time.sleep(5)
                browser.find_element(By.ID, value="registerButton").click()
                return True
            except BaseException as f:
                print(f)
                return False


def emailList(token, sessauth, sessid, emailName):
    header = {
        "Cookie": "roundcube_sessid=" + sessid + "; roundcube_sessauth=" + sessauth,
        "Host": "pimar.cn",
        "Origin": "http://pimar.cn",
        "Referer": "http://pimar.cn/?_task=mail&_mbox=INBOX",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
        "X-Roundcube-Request": token
    }
    data = {
        "_mbox": "INBOX",
        "_folderlist": "1",
        "_quota": "1",
        "_list": "1",
        "_uids": "1,2,3,4,5",
        "_remote": "1",
        "_unlock": "loading%d" % int(round(time.time() * 1000)),
    }
    r = requests.post('http://pimar.cn/?_task=mail&_action=check-recent', headers=header, data=data)
    infoList = r.json()["env"]["recent_flags"];
    if len(infoList) == 0:
        # 没有收到邮件重新刷新邮箱
        emailList(token, sessauth, sessid, emailName);
    else:
        infoIds = [];
        for key, value in infoList.items():
            infoIds.append(key)
        infoIds = bubble_sort(infoIds)
        for id in infoIds:
            result = emailInfo(id, sessauth, sessid, emailName)
            if result:
                print("注册完成")
                break;


def email(username, password):
    browser.implicitly_wait(10)
    try:
        browser.get('http://pimar.cn/')
        browser.find_element(By.ID, value="rcmloginuser").send_keys(username)
        browser.find_element(By.ID, value="rcmloginpwd").send_keys(password)
        browser.find_element(By.ID, value="rcmloginsubmit").click()

        cookies = browser.get_cookies();
        forgetToken = browser.find_element(By.NAME, value="_token").get_attribute("value")

        for cookie in cookies:
            if cookie["name"] == "roundcube_sessauth":
                roundcube_sessauth = cookie["value"];
            if cookie["name"] == "roundcube_sessid":
                roundcube_sessid = cookie["value"];
        emailList(forgetToken, roundcube_sessauth, roundcube_sessid, username)
    except BaseException as f:
        print(f)


def forgetSend(token):
    header = {
        "Origin": "https://forge.gg",
        "Referer": "https://forge.gg/",
        'Authorization': "Bearer " + token
    }
    r = requests.post('https://api.forge.gg/verification/resend-email', headers=header)
    status = r.json()["status"]
    if status == "success":
        return True
    else:
        return False


def newUser(emailname, password, emailPassword):
    details = {
        'email': emailname,
        'password': password,
        'returnSecureToken': True
    }
    r = requests.post('https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={}'.format(apikey), data=details)

    if 'idToken' in r.json().keys():
        lookupDetails = {
            'idToken': r.json()['idToken'],
        }
        print(r.json()['idToken'])
        lookup = requests.post('https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={}'.format(apikey),
                               data=lookupDetails)
        try:
            # 尝试发送5次邮箱,如果失败重新发送,成功直接结束
            for i in range(5):
                re = forgetSend(r.json()['idToken'])
                if re:
                    email(emailname, emailPassword)
                    break;
                else:
                    print("发送邮件失败第" + i + 1 + "次尝试")

        except BaseException as f:
            print(f)
    time.sleep(5000)

# 生成10位数的随机用户名
def generate_random_string(length=10):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string


# 排序算法
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] < arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr


if __name__ == '__main__':
    # email("ljzteh@klonsa.cn","988847")
    newUser("yelfpf@klonsa.cn", PASSWORD, "332465")
