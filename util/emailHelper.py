#!/usr/bin/python
# -*- coding: UTF-8 -*-
import smtplib
from email.header import Header
from email.mime.text import MIMEText

from Config import SMTP_EXMAIL_QQ_COM, NO_REPLY_TATATIMES_COM, MAILPASS, NOREPLAYEMAIL, MANAGER_TATATIMES_COM, RECIEVERS
from util.timeHelper import getYesteday


def send(msg):
    mail_host= SMTP_EXMAIL_QQ_COM  #设置服务器
    mail_user= NO_REPLY_TATATIMES_COM  #用户名
    mail_pass= MAILPASS  #口令

    sender = NOREPLAYEMAIL
    receivers = [MANAGER_TATATIMES_COM, RECIEVERS]  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱



    # 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
    message = MIMEText(msg, 'html', 'utf-8')
    message['From'] = Header("广告平台", 'utf-8')
    message['To'] =  Header('老大们', 'utf-8')

    subject = "塔塔日报-" + getYesteday()
    message['Subject'] = Header(subject, 'utf-8')


    try:

        smtp = smtplib.SMTP()
        smtp.connect(mail_host)
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.set_debuglevel(1)
        smtp.login(mail_user, mail_pass)
        smtp.sendmail(sender, receivers, message.as_string())
        smtp.quit()

        # smtpObj = smtplib.SMTP()
        # smtpObj.connect(mail_host, 465)  # 25 为 SMTP 端口号
        # smtpObj.login(mail_user, mail_pass)
        # smtpObj.sendmail(sender, receivers, message.as_string())
        print "邮件发送成功"
    except smtplib.SMTPException:
        print "Error: 无法发送邮件"


def send_email(msg, receivers, fromHeader = 'no-reply', toHeader = '' ,subject = '无主题'):

    mail_host= SMTP_EXMAIL_QQ_COM  #设置服务器
    mail_user= NO_REPLY_TATATIMES_COM  #用户名
    mail_pass= MAILPASS  #口令

    sender = NOREPLAYEMAIL
    assert  isinstance(receivers, list)  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱, 需要时个list



    # 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
    message = MIMEText(msg, 'html', 'utf-8')
    message['From'] = Header(fromHeader, 'utf-8')
    message['To'] =  Header(toHeader, 'utf-8')

    # subject = "塔塔日报-" + getYesteday()
    message['Subject'] = Header(subject, 'utf-8')


    try:

        smtp = smtplib.SMTP()
        smtp.connect(mail_host)
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.set_debuglevel(1)
        smtp.login(mail_user, mail_pass)
        smtp.sendmail(sender, receivers, message.as_string())
        smtp.quit()

        # smtpObj = smtplib.SMTP()
        # smtpObj.connect(mail_host, 465)  # 25 为 SMTP 端口号
        # smtpObj.login(mail_user, mail_pass)
        # smtpObj.sendmail(sender, receivers, message.as_string())
        print "邮件发送成功"
    except smtplib.SMTPException:
        print "Error: 无法发送邮件"

