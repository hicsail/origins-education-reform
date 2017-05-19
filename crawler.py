from selenium import webdriver
from selenium.webdriver.common.keys import Keys

driver = webdriver.Chrome()

driver.get("http://www.deutschestextarchiv.de/book/download_xml/lessing_fabeln_1759")

driver.close()