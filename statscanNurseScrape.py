from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException
import time
import json
import re

option = webdriver.ChromeOptions()
option.add_argument("--incognito")

browser = webdriver.Chrome(executable_path="/home/ironmantle/Documents/chromeDriver/chromedriver", chrome_options=option)

browser.get("https://registry.cno.org/")

timeout = 10

try:
    # wait for the checkbox (DOM last to load) and click it
    WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.ID, "chkAcceptTerms")))
    findEULACheckBox = browser.find_element_by_id("chkAcceptTerms")
    time.sleep(1)
    findEULACheckBox.click()

    WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.ID, "submitButton")))

    # look for the submit button and click it
    startSearchingBox = browser.find_element_by_id("submitButton")
    startSearchingBox.click()

    WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//input[@value='NUMBER']")))

    listBadTags = [
        "<b>",
        "</b>",
        ]
    
    dateCleaner = [
        "<strong>.+</strong>"
    ]

    medicalStaff = {}

    staffNum = 0

    # test RN nums
    listKnownNums = [14056148, 14056158]

    with open("RegisteredNurses.json", "a") as jsonDoc:
   
        # for number in our list
        for regNum in range(14030010, 99999999):

            try:

                # find the registration number radio
                WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//*[@value='NUMBER']")))
                registrationNumberRadio = browser.find_element_by_xpath("//input[@value='NUMBER']")
                registrationNumberRadio.click()
                WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.ID, "RegistrationNumberCNO")))

                # find the text box to enter the current id
                searchBox = browser.find_element_by_id("RegistrationNumberCNO")
                searchBox.click()
                searchBox.send_keys(str(regNum).zfill(8))

                # hit the search button
                submitSearchButton = browser.find_element_by_xpath("//input[@class='btn btn-primary'][@value='Search']")
                submitSearchButton.click()

                try:
                    browser.find_element_by_xpath("//*[contains(text(), 'Your search did not return any results')]")
                    # go back to the start and search again
                    browser.get("https://registry.cno.org/Search/Search")
                    continue
                
                except:            

                    staffNum += 1

                    medicalStaff[staffNum] = {}
                    
                    print("Found record matching CNO: {}!".format(regNum))

                    # wait for the req divs to load
                    WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='tab-content hidden-xs']")))
                    # rn name
                    medicalStaffName = browser.find_elements_by_tag_name("h1")[1].text

                    medicalStaff[staffNum]["Name"] = medicalStaffName
                    medicalStaff[staffNum]["Registration Number"] = regNum
    
                    #   G E N E R A L   T A B   #

                    tempList = []
                    jobDetails = []
                    medicalStaff[staffNum]["General Information"] = {}
                    counter = 1

                    try:
                        tabDivGeneral = browser.find_element_by_xpath("//div[@id='general']")
                        for div in tabDivGeneral.find_elements_by_xpath("//div[@id='general']/div[@class='well'][@style='']"):
                            divTitle = div.find_element_by_tag_name("h3")
                            if divTitle.text == "" or divTitle.text == "Former Names": break
                            medicalStaff[staffNum]["General Information"]["Employment Type {}".format(counter)] = {}
                            medicalStaff[staffNum]["General Information"]["Employment Type {}".format(counter)]["Job Title"] = divTitle.text
                            for td in div.find_elements_by_tag_name("td"):
                                tempList.append(td.text)
                            iterableList = iter(tempList)
                            for item in iterableList:
                                medicalStaff[staffNum]["General Information"]["Employment Type {}".format(counter)][item] = next(iterableList)

                            counter += 1             
                    except:
                        pass

                    #   C O N T A C T   I N F O R M A T I O N   #

                    medicalStaff[staffNum]["Last Employment"] = {}
                    try:
                        address = browser.find_element_by_xpath("//*[@id='contactInformation']/div[@class='well']/div[@class='row']/div[@class='col-md-6']")
                        startDate = browser.find_element_by_xpath("//*[@id='contactInformation']/div[@class='well']/div[@class='row']/div[@class='col-md-3'][1]").get_attribute("innerText")
                        startDate = re.search("(\\d{4})", startDate).group(1)
                        endDate = browser.find_element_by_xpath("//*[@id='contactInformation']/div[@class='well']/div[@class='row']/div[@class='col-md-3'][2]").get_attribute("innerText")
                        try:
                            endDate = re.search("(\\d{4})", endDate).group(1)
                        except AttributeError:
                            endDate = "Currently Employed"
                        address = str(address.get_attribute("innerText"))
                        for badTag in listBadTags:
                            address = address.replace(badTag, "")
                        address = re.sub(r"\n", "", address)
                        address = re.sub(r" +", " ", address)

                        medicalStaff[staffNum]["Last Employment"]["Address"] = address
                        medicalStaff[staffNum]["Last Employment"]["Start Date"] = startDate
                        medicalStaff[staffNum]["Last Employment"]["End Date"] = endDate
                    
                    except:
                        continue

                    #   W R I T E   T O   D I C T   #

                    print(medicalStaff[staffNum])
                    json.dump(medicalStaff[staffNum], jsonDoc)

                    #   R E S T A R T   #

                    browser.get("https://registry.cno.org/Search/Search")
            except:
                browser.get("https://registry.cno.org/Search/Search")
                continue
        browser.quit()

except TimeoutException:
    print("Timed out waiting for page to load")
    browser.quit()

finally:
    browser.quit()
