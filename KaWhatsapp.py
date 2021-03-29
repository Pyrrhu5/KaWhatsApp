#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
from time import sleep
import pickle
import re
import subprocess
from functools import wraps

try:
	from selenium import webdriver
	from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException 
	from googletrans import Translator	
except ModuleNotFoundError as e:
	print("Missing dependency. Run:\npip install -r requirements.txt")
	print(e)
	exit(1)


# ==============================================================================
#                                    GLOBALS
# ==============================================================================

APP_PATH		= os.path.dirname(os.path.abspath(__file__))

WHATSAPP_URL	= "https://web.whatsapp.com/"

translator = Translator()

# ==============================================================================
#                                     UTILS
# ==============================================================================

def deactivated(func):
	"""Decorator to suspend a function"""
	@wraps(func)
	def wrap(*ags, **kwargs):
		return

	return wrap


# ==============================================================================
#                                 BROWSER UTILS
# ==============================================================================

def wait_for_element(element2Find, browser):
	"""Blocks the execution until an element is found on page."""

	print(f"Waiting for element '{element2Find}' to be on page...")

	while True:
		try:
			browser.find_element_by_class_name(element2Find)
		except NoSuchElementException:
			sleep(.25)
		else:
			break

	print(f"Element '{element2Find}' found.")
	return


@deactivated
def load_cookies(browser):
	cookiesPath = os.path.join(APP_PATH, "assets", "cookies.pkl")
	if os.path.exists(cookiesPath):
		print("Loading cookies...")
		with open(cookiesPath, "rb") as f:
			cookies = pickle.load(f)
			for c in cookies:
				browser.add_cookie(c)
		browser.refresh()
	else: print("No cookie to load.")


@deactivated
def save_cookies(browser):
	print("Saving cookies...")
	cookiesPath = os.path.join(APP_PATH, "assets", "cookies.pkl")
	with open(cookiesPath, "wb") as f:
		pickle.dump(browser.get_cookies(), f)


# ==============================================================================
#                                 BROWSER CONFIG
# ==============================================================================

@deactivated # Not maintaining whatsapp sessions
def set_firefox():
	driver	= os.path.join(APP_PATH, "assets", "geckodriver_linux64")
	fp.set_preference("network.cookie.cookieBehavior", 0)
	
	# start browser
	browser = webdriver.Firefox(executable_path = driver, firefox_profile=fp)
	load_cookies(browser)
	browser.get(WHATSAPP_URL)

	return browser



	pass	


def set_brave():
	option = webdriver.ChromeOptions()
	
	# Get the browser executable
	option.binary_location = subprocess.check_output(["which", "brave-browser"]).decode("utf-8").strip()

	# Create/load a custom user data directory
	# to maintain connection to whatsapp between sessions
	dataDir = os.path.join(APP_PATH, "BrowserData")
	option.add_argument("--user-data-dir=" + dataDir)
	if not os.path.exists(dataDir):
		os.mkdir(dataDir) 

	driver = os.path.join(APP_PATH, "assets", "chromedriver_linux64")
	# Launch the browser
	browser = webdriver.Chrome(
		executable_path = driver,
		options = option
	)
	load_cookies(browser)
	browser.get(WHATSAPP_URL)

	return browser


def set_browser():
	return set_brave()


def on_exit(browser):
	save_cookies(browser)
	print("Bye.")
	sleep(1)
	exit(0)


# ==============================================================================
#                                    WHATSAPP
# ==============================================================================

def is_logged_in(browser):
	wait_for_element("web", browser)
	print("Asserting if user is logged in...")	

	while True:
		# with QR Code
		try:
			browser.find_element_by_class_name("landing-main")
			return False
		except NoSuchElementException:
			try:
				browser.find_element_by_id("side")
				print("Logged-in.")
				return True
			except NoSuchElementException:
				return None
	

def is_georgian(txt: str) -> bool:
	"""Detects if a text is in Georgian by its UTF8 char range."""
	return re.search(r"[\u10D0-\u10F1]+", txt) is not None


def translate_conversation(browser):
	separator = "="*20
	n = 0 # number of elements translated

	for msgParent in browser.find_elements_by_class_name("message-in"):
		try:
			msgParent = msgParent.find_element_by_class_name("copyable-text")
			msgParent = msgParent.find_element_by_class_name("selectable-text")
			msgParent = msgParent.find_element_by_tag_name("span")
			txt = msgParent.text
			# avoid already translated, smiley, images and none-georgian
			if txt and separator not in txt and is_georgian(txt):
				try:
					translated = translator.translate(txt, src='ka', dest='en')
				except Exception as e:
					print(f"Translator lib error for {txt}")
					print(e)
				else:
					browser.execute_script("arguments[0].innerHTML += '<br>' + arguments[2] + '<br>' + arguments[1] + '<br>' + arguments[2];", msgParent, translated.text, separator)
				n += 1
		except NoSuchElementException:
			continue
		except StaleElementReferenceException:
			continue
	if n != 0:
		print(f"{n} elements translated.")


# ==============================================================================
#                                      MAIN
# ==============================================================================

if __name__ == "__main__":
	try:
		print("Starting...")
		browser = set_browser()
		# wait for connection
		print("Waiting for log-in...")
		# use <header>'s class of the side bar (profile picture, status etc.)
		wait_for_element("_1R3Un", browser)
		print("Connected.")
		print("Waiting to open a conversation...")
		# conversation tab
		# Right-side panel main <div> => 
		wait_for_element("_11liR", browser)
		print("Conversation open.")
		# start translation routine	
		while True:
			translate_conversation(browser)
			sleep(1)
	except KeyboardInterrupt:
		on_exit(browser)
