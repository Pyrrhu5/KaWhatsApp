#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
from time import sleep
import pickle

try:
	from selenium import webdriver
	from selenium.common.exceptions import NoSuchElementException
	from googletrans import Translator	
except ModuleNotFoundError:
	print("Missing dependency. Run:\npip install -r requirements.txt")
	exit(1)


APP_PATH = os.path.dirname(os.path.abspath(__file__))
WEBDRIVER = os.path.join(APP_PATH, "assets", "geckodriver_linux64")
WHATSAPP_URL = "https://web.whatsapp.com/"
ALPHABET_RANGE = range(4304, 4304 + 33)

translator = Translator()


def wait_for_element(element2Find, browser):
	try:
		browser.find_element_by_class_name(element2Find)
	except NoSuchElementException:
		isFound = False

	while not isFound:
		try:
			browser.find_element_by_class_name(element2Find)
		except NoSuchElementException:
			isFound = False
			sleep(.25)
		else:
			isFound = True

	print("Page loaded.")
	return


def load_cookies(browser):
	cookiesPath = os.path.join(APP_PATH, "assets", "cookies.pkl")
	if os.path.exists(cookiesPath):
		with open(cookiesPath, "rb") as f:
			cookies = pickle.load(f)
			for c in cookies:
				browser.add_cookie(c)


def save_cookies(browser):
	cookiesPath = os.path.join(APP_PATH, "assets", "cookies.pkl")
	with open(cookiesPath, "wb") as f:
		pickle.dump(browser.get_cookies(), f)


def on_start():
	browser = webdriver.Firefox(executable_path = WEBDRIVER)
	browser.get(WHATSAPP_URL)
	load_cookies(browser)

	return browser


def on_exit(browser):
	save_cookies(browser)
	browser.close()
	print("Bye.")
	sleep(1)
	exit(0)


def is_logged_in(browser):
	wait_for_element("web", browser)
	print("Asserting if user is logged in.")	

	while True:
			# with QR Code
		try:
			browser.find_element_by_class_name("landing-main")
			return False
		except NoSuchElementException:
			try:
				browser.find_element_by_id("side")
				return True
			except NoSuchElementException:
				return None
	

def translate_conversation(browser):
	separator = "="*20

	for msgParent in browser.find_elements_by_class_name("message-in"):
		try:
			msgParent = msgParent.find_element_by_class_name("copyable-text")
			msgParent = msgParent.find_element_by_class_name("selectable-text")
			msgParent = msgParent.find_element_by_tag_name("span")
			txt = msgParent.text
			# avoid already translated, smiley, images and none georgian
			if separator not in txt and len(txt) != 0 and ord(txt[0]) in ALPHABET_RANGE:
				translated = translator.translate(txt, src='ka', dest='en')
				browser.execute_script("arguments[0].innerHTML += '<br>' + arguments[2] + '<br>' + arguments[1] + '<br>' + arguments[2];", msgParent, translated.text, separator)
		except NoSuchElementException:
				continue


if __name__ == "__main__":
	try:
		browser = on_start()
		# wait for connection
		wait_for_element("_1KyAW", browser)
		print("Connected.")
		# conversation tab
		wait_for_element("z_tTQ", browser)
		print("Conversation opened.")
		# start translation routine	
		while True:
			translate_conversation(browser)
	except KeyboardInterrupt:
		print("Bye.")
		sleep(1)
		exit(0)