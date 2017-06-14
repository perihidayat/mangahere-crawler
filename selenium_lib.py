import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_chrome_instance(page_timeout):
	driver = webdriver.Chrome('{}/chromedriver.exe'.format(os.getcwd()))
	driver.implicitly_wait(page_timeout)
	return driver


def wait_for_element(driver, xpath):
	WebDriverWait(driver, 10).until(
		EC.presence_of_element_located((By.XPATH, xpath))
	)


def quit_driver(driver):
	driver.quit()