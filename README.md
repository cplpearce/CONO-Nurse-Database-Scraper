# CONO-Nurse-Database-Scraper
#### Pulls healthcare specialists information from the Ontario public health care worker resgistry to collate retired/inactive specialists whom could add to the efforts of fighting COVID-19

#### Pulls all active/retired nurses from https://registry.cno.org/

#### Requires Selenium

#### import block:
```
from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException
import time
import json
import re
```
