## selenium_2captcha
Captcha solving by 2captcha.com integrated in the selenium testing framework

# Usage
```python
import selenium_2captcha
from selenium import webdriver

browser = webdriver.Firefox()
browser.get('https://www.google.com/recaptcha/api2/demo')

# blocks untill the captcha is solved (and returns True if succesful)
selenium_2captcha.solve_recaptcha_v2(browser, 'apikeyhere')
```
