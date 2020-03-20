from time import sleep, time

import requests


def solve_recaptcha_v2(browser, apikey=None, url=None, sitekey=None, max_duration=None):
    """
    Solve a recaptcha (version 2) that appears in the supplied browser.

    :param browser: a selenium webdriver
    :param apikey: a valid API key for 2captcha.com with sufficient balance
    :param url: URL of the page the captcha is on (optional, function will use current_url otherwise)
    :param sitekey: data-sitekey for the captcha to solve (optional, function will look for one automatically)
    :param max_duration: maximum number of seconds for the captcha solving process
    :return: True if solved
    :raises: TimeoutError, RuntimeError
    """
    start_time = int(time())
    sitekey = sitekey or browser.find_element_by_css_selector('[data-sitekey]').get_attribute('data-sitekey')
    # Submit the necessary captcha data
    submitted_captcha = requests.get('https://2captcha.com/in.php',
                                     params={
                                         "key": apikey,
                                         "method": "userrecaptcha",
                                         "googlekey": sitekey,
                                         "pageurl": url or browser.current_url,
                                         "json": 1,
                                     })
    # Get a captcha_id, that we can use in following requests
    captcha_id = submitted_captcha.json()['request']
    if captcha_id.startswith('ERROR') or captcha_id == 'IP_BANNED' or captcha_id == 'MAX_USER_TURN':
        raise RuntimeError(f"Error indication '{captcha_id}' in 2captcha.com/in.php response: {submitted_captcha.text}")
    sleep(15)  # Allow some time for the captcha to be solved
    while max_duration is None or (int(time()) - start_time) < max_duration:
        # Poll the status of the captcha with the captcha_id acquired before
        captcha_status = requests.get('https://2captcha.com/res.php',
                                      params={
                                          "key": apikey,
                                          "action": 'get',
                                          "id": captcha_id,
                                          "json": 1,
                                      })
        if captcha_status.json()['status'] == 1:
            browser.execute_script(
                f'document.getElementById("g-recaptcha-response").innerHTML="{captcha_status.json()["request"]}";'
            )
            return True
        elif captcha_status.json()['status'] != 1 and captcha_status.json()['request'] != 'CAPCHA_NOT_READY':  # [sic]
            raise RuntimeError(f"Error indication '{captcha_status.json()['request']}'"
                               f" in 2captcha.com/res.php response: {captcha_status.text}")
        else:
            sleep(3)
    raise TimeoutError(f"The specified maximum number of seconds ({max_duration}) to "
                       f"solve the recaptcha v2 has expired")
