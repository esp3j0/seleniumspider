from selenium import webdriver
from time import sleep
firefox_options = webdriver.FirefoxOptions()
firefox_options.set_preference('browser.download.dir', '/downloads')
firefox_options.set_preference('browser.download.folderList', 2)
firefox_options.set_preference('browser.download.manager.showWhenStarting', False)
#firefox_options.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/zip')
driver = webdriver.Remote(
    command_executor='http://kali.lan:4444/wd/hub',
    options=firefox_options
)



driver.get("https://proteintools.uni-bayreuth.de/contacts/")
upload = driver.find_element_by_id("customFile")
upload.send_keys('./pdbs/P41903.pdb')
submita = driver.find_element_by_id("btnFetch")

submita.click()
sleep(20)
downlaod = driver.find_element_by_xpath("/html/body/div[1]/div[2]/a")
downlaod.click()
sleep(20)
driver.quit()
