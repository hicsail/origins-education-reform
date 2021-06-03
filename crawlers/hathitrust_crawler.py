from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, argparse, csv, tqdm, common, os

def download_files(driver, urls):
    for url in tqdm.tqdm(urls):
        download_link = parse_url(url.strip())
        
        link_list = driver.find_elements_by_tag_name("a")
        for link in link_list:
            if link.get_attribute('href') == download_link:
                link.click()
                time.sleep(5)
    driver.close()

def login_to_htid(driver):
    driver.get("https://babel.hathitrust.org/Shibboleth.sso/Login?entityID=https://shib.bu.edu/idp/shibboleth&target=https://babel.hathitrust.org/cgi/mb")
    wait = WebDriverWait(driver, 10, poll_frequency=1)
    wait.until(lambda driver: "babel.hathitrust.org" in driver.current_url)

def download_files(driver, htids):
    for htid in htids:
        url = "https://babel.hathitrust.org/cgi/imgsrv/download/plaintext?id=" + htid
        driver.get(url)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", help="Input CSV file with list of HathiTrust IDs", action="store")
    parser.add_argument("output", help="Output directory for .txt files", action="store")
    args = parser.parse_args()

    outdir = os.path.normpath(args.output)
    if not os.path.isdir(outdir):
        os.mkdir(outdir)

    chrome_opts = webdriver.ChromeOptions()
    prefs = {"download.default_directory": os.path.abspath(outdir)}
    chrome_opts.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=chrome_opts)

    htids = open(args.csv).readlines()
    htids = [x.strip() for x in htids]

    login_to_htid(driver)
    download_files(driver, htids)