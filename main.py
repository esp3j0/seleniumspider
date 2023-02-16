import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from os import popen
from time import sleep
from os import system,path
import threading
import concurrent.futures


class pdb_proteintoolweb:
    pdburl = "https://alphafold.ebi.ac.uk/files/AF-{}-F1-model_v4.pdb"
    pdbs = "./pdbs/{}.pdb"
    sum_pdb_len = 0
    thread_list = []
    nl = []
    sem = threading.Semaphore(10)
    
    def get_names(self):
        f = open('./namelist.txt')
        for name in f.readlines():
            self.nl.append(name.replace('\n',''))
    
    def getpdb(self,asd):
        req = requests.get(self.pdburl.format(asd))
        with open(self.pdbs.format(asd), "wb") as f:
            f.write(req.content)
        sleep(2)
        self.sum_pdb_len = self.sum_pdb_len - 1
        print("下载"+asd+"完成,还剩"+str(self.sum_pdb_len)+"个")
        self.sem.release()
        
        
    def threads_get_pdbs(self):
        for name in self.nl:
            t = threading.Thread(target=self.getpdb,args=(name,))
            self.sum_pdb_len = self.sum_pdb_len + 1
            self.thread_list.append(t)
        for t in self.thread_list:
            self.sem.acquire()
            t.start()
        for t in self.thread_list:
            t.join()
            
    def clean(self):
        system("mv ./pdbs/* ./pre_pdbs/")
        
    def __init__(self) -> None:
        self.clean()
        self.get_names()
        self.threads_get_pdbs()

class Contact_maps_proteintoolsweb:
    sum_csv_len = 0
    pdb_list = []
    hub = 'http://localhost:4444/wd/hub'
    contact_map_url = "https://proteintools.uni-bayreuth.de/contacts/"
    pdb_upload_floder = './pdbs/{}'
    csv_save_floder = "./csvs/"
    sem = threading.Semaphore(5)
    def get_pdbs(self):
        a = popen("ls ./pdbs/")
        for i in a.readlines():
            self.pdb_list.append(i.replace("\n",""))
    def new_driver(self,name):
        name = name.replace('\n','')
        firefox_options = webdriver.FirefoxOptions()
        firefox_options.set_preference('browser.download.folderList', 2)
        firefox_options.set_preference('browser.download.manager.showWhenStarting', False)
        firefox_options.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/zip')
        firefox_options.set_preference('browser.download.dir', '/home/seluser/csvs/{}/'.format(name[:-4]))
        #self.firefox_options.set_preference('browser.download.dir', '/home/seluser/csvs/')
        driver = webdriver.Remote(
        command_executor = self.hub,
        options=firefox_options
        )
        driver.implicitly_wait(7200)
        return driver
    def wait_downlaod(self,name):
        timeout = 0
        mx_timeout = 45
        while(True):
            timeout += 1
            if timeout > mx_timeout:
                return False
            if path.exists("./csvs/{}/contact_maps_table.csv".format(name.replace(".pdb",""))):
                break
            else:
                sleep(5)
        while(True):
            timeout += 1
            if timeout > mx_timeout:
                return False
            presize = path.getsize("./csvs/{}/contact_maps_table.csv".format(name.replace(".pdb","")))
            sleep(10)
            nowsize = path.getsize("./csvs/{}/contact_maps_table.csv".format(name.replace(".pdb","")))
            print(name+"presize is :"+str(presize))
            print(name+"nowsize is :"+str(nowsize))
            if(nowsize!=0 and presize == nowsize):
                sleep(15)
                return True
    
    def get_contact_map(self,name):
        try:
            name.replace('\n','')
            driver = self.new_driver(name)
            print(name)
            driver.get(self.contact_map_url)
            upload = driver.find_element(By.ID,"customFile")
            upload.send_keys(self.pdb_upload_floder.format(name))
            submit = driver.find_element(By.ID,"btnFetch")
            submit.click()
            wait = WebDriverWait(driver, 70)
            download = driver.find_element(By.XPATH,"/html/body/div[1]/div[2]/a")
            download.click()
            if(self.wait_downlaod(name)):
            #if(WebDriverWait(driver, 60).until(lambda driver: os.path.exists('/path/to/download/file') and os.path.getsize('/path/to/download/file') > 0)):
                self.sum_csv_len = self.sum_csv_len - 1
                print(name+"已完成,剩余"+str(self.sum_csv_len)+"个")
                driver.quit()
                system("sed -i '/"+name.replace(".pdb","")+"/d' namelist.txt")
                self.sem.release()
                print("121行"+str(self.sem._value))
                return name
            else:
                print(name+"下载失败,line 126")
                system("echo "+name.replace(".pdb","")+">> failednamelist.txt")
                system("rm -rf ./csvs/{}".format(name.replace(".pdb","")))
                driver.quit()
                self.sem.release()
                print("129行"+str(self.sem._value))

                return name
        except Exception as ex:
            print("出现异常%s"%ex)
            print("except"+name)
            system("echo "+name.replace(".pdb","")+">> failednamelist.txt")
            system("rm -rf ./csvs/{}".format(name.replace(".pdb","")))
            driver.quit()
            self.sem.release()
            print("139行"+str(self.sem._value))

            return name
    
        
    
    def csv_thread(self):
        get_csvs_thread_list = []
        for name in self.pdb_list:
            self.sum_csv_len = self.sum_csv_len + 1
        for name in self.pdb_list:
            self.sem.acquire()
            print("151行"+str(self.sem._value))

            t = threading.Thread(target=self.get_contact_map,args=(name,))
            get_csvs_thread_list.append(t)
            t.start()
        for t in get_csvs_thread_list:
            t.join()
    def clean(self):
        system("rm -rf ./pre_csvs/*")
        system("mv ./csvs/* ./pre_csvs/")
    def __init__(self) -> None:
        #self.clean()
        self.get_pdbs()
        self.csv_thread()



if __name__ == '__main__':
    pdb_proteintoolweb()
    Contact_maps_proteintoolsweb()
    
    
    
    
    
    
    
    
    
        
    
    

        
        



        
        
        

            
        
    
    
