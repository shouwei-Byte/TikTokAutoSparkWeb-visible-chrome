import re, os, gzip, shutil
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import SessionNotCreatedException
from selenium.webdriver.common.by import By
import schedule, requests
import time, uvicorn
from datetime import datetime
import json, base64
from fastapi import FastAPI, Header, Request, Query, Body
from fastapi.middleware.cors import CORSMiddleware
import threading, hashlib, secrets

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROME_PROFILE_DIR = os.getenv('CHROME_PROFILE_DIR', os.path.join(BASE_DIR, 'chrome-profile'))
DEFAULT_CHROME_BINARY = (
    r'C:\Program Files\Google\Chrome\Application\chrome.exe'
    if os.name == 'nt'
    else '/opt/google/chrome/chrome'
)

CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH', shutil.which('chromedriver') or '')
service = Service(executable_path=CHROMEDRIVER_PATH) if os.path.exists(CHROMEDRIVER_PATH) else None
options = webdriver.ChromeOptions()
CHROME_BINARY = os.getenv('CHROME_BINARY', DEFAULT_CHROME_BINARY)
if os.path.exists(CHROME_BINARY):
    options.binary_location = CHROME_BINARY
off_ui = False


def unban_config():
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument('log-level=3')
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.177 Safari/537.36")
    options.add_experimental_option('excludeSwitches', ['enable-automation', 'useAutomationExtension'])
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--disable-web-security')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1400,3200')
    options.add_argument(f'--user-data-dir={CHROME_PROFILE_DIR}')
    options.add_argument('--remote-debugging-port=0')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--start-maximized')
    options.add_argument("--force-device-scale-factor=0.25")


def _body_text():
    try:
        return driver.find_element(By.TAG_NAME, 'body').text or ''
    except Exception:
        return ''


def _is_two_factor_page():
    text = _body_text()
    keywords = ['二次', '身份', '认证', '验证', '验证码', '扫脸', '手机号', '获取验证码', '安全']
    return any(keyword in text for keyword in keywords) and '扫码登录' not in text


def _find_first(by, selectors):
    last_error = None
    for selector in selectors:
        try:
            elements = driver.find_elements(by, selector)
            for element in elements:
                if element.is_displayed() and element.is_enabled():
                    return element
        except Exception as exc:
            last_error = exc
    if last_error:
        raise last_error
    raise NoSuchElementException(str(selectors))


def _click_first_xpath(xpaths):
    element = _find_first(By.XPATH, xpaths)
    try:
        element.click()
    except Exception:
        driver.execute_script('arguments[0].click()', element)
    return element


def AiqingGongyu_text():
    req = requests.get('https://v2.xxapi.cn/api/aiqinggongyu')
    if req.status_code == 200:
        json_data = req.json()
        json_data = json_data['data']
        if json_data:
            return json_data
        else:
            return '鏆傛棤浠婃棩鍚嶈█'
    else:
        return '鏆傛棤浠婃棩鍚嶈█'


def Get_Cooke():
    driver.get('https://www.douyin.com/')
    for_OFF = True
    print('馃暟锔?璇风櫥褰曟姈闊砙涓斾繚鎸佹父瑙堝櫒涓哄叏灞?].....')
    while for_OFF:
        try:
            # 灏濊瘯鑾峰彇 login_type 鍏冪礌
            login_type_element = driver.find_element(By.XPATH,
                                                     '/html/body/div[2]/div[1]/div[4]/div[1]/div[1]/header/div/div/div[2]/div/pace-island/div/div[5]/div/div[1]/button/span/p')
        except NoSuchElementException:
            cooke = driver.get_cookies()
            print(f'鉁?Cooke鑾峰彇鎴愬姛,鎮ㄧ殑Cooke涓?[璇峰畬鏁村鍒跺埌cookies_list鍙橀噺涓璢:\n{cooke}')
            driver.close()
            exit()


def format_time(time_str: str) -> str:
    """
    灏嗘椂闂村瓧绗︿覆鏍煎紡鍖栦负 HH:MM 鏍煎紡
    渚嬪: "9:23" -> "09:23", "9:5" -> "09:05", "09:23" -> "09:23"
    """
    if not time_str:
        return '22:00'

    # 缁熶竴鏇挎崲涓枃鍐掑彿
    time_str = time_str.replace('锛?, ':').strip()

    try:
        # 鍒嗗壊灏忔椂鍜屽垎閽?        parts = time_str.split(':')
        if len(parts) != 2:
            print(f'鈿狅笍 鏃堕棿鏍煎紡閿欒锛屼娇鐢ㄩ粯璁ゆ椂闂?22:00')
            return '22:00'

        hour = int(parts[0])
        minute = int(parts[1])

        # 楠岃瘉鑼冨洿
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            print(f'鈿狅笍 鏃堕棿鑼冨洿閿欒锛屼娇鐢ㄩ粯璁ゆ椂闂?22:00')
            return '22:00'

        # 鏍煎紡鍖栦负涓や綅鏁板瓧
        return f"{hour:02d}:{minute:02d}"

    except ValueError:
        print(f'鈿狅笍 鏃堕棿瑙ｆ瀽閿欒锛屼娇鐢ㄩ粯璁ゆ椂闂?22:00')
        return '22:00'


class TrueString:
    def __init__(self, is_bool, string):
        self.is_bool = is_bool
        self.string = string


class UserFriendsInfo:
    def __init__(self, username, avatar, fire):
        self.username = username
        self.avatar = avatar
        self.fire = fire


class Douyin:
    friends_xpath_list = {}

    def __init__(self, driver):
        self.driver = driver  # 灏?driver 浣滀负瀹炰緥灞炴€?
    def PrintfFrinder(self):

        print(f'\n鈴笍 濂藉弸鍒楄〃 鍏辫幏鍙杮len(self.friends_xpath_list)}浣?\n------------------')
        for index, value in self.friends_xpath_list.items():
            print(index)
        print('------------------')

    def Updara_FrinderList(self):
        friends_xpath = '//div[@class="conversationConversationListwrapper"]/div/div/div'
        msg_main_list = driver.find_elements(By.XPATH, friends_xpath)
        temp_list = []
        for msg_len in range(1, len(msg_main_list) + 1):
            new_xpath = f'//div[@class="conversationConversationListwrapper"]/div/div[{msg_len + 1}]/div[1]/div[2]/div[1]/div[1]'
            avatar_xpath = f'//div[@class="conversationConversationListwrapper"]/div/div[{msg_len + 1}]/div[1]/div[1]/div/span/img'
            avatar_xpath2 = f'//div[@class="conversationConversationListwrapper"]/div/div[{msg_len + 1}]/div/div/img'
            fire_xpath = f'//div[@class="conversationConversationListwrapper"]/div/div[{msg_len + 1}]/div[1]/div[2]/div[1]/div[2]/div[1]/div/div'
            friends_get = driver.find_element(By.XPATH, value=new_xpath)
            friends_text = friends_get.text
            try:
                avatar_get = driver.find_element(By.XPATH, value=avatar_xpath)
                avatar = avatar_get.get_attribute('src')
            except:
                avatar_get = driver.find_element(By.XPATH, value=avatar_xpath2)
                avatar = avatar_get.get_attribute('src')
            self.friends_xpath_list[friends_text] = new_xpath
            try:
                fire_count = driver.find_element(By.XPATH, value=fire_xpath).text.strip()
            except:
                fire_count = ''
            temp_list.append(UserFriendsInfo(friends_text, avatar, fire_count))
        return temp_list

    def Send_Frinder(self, name: str, text: str):
        count = self.Updara_FrinderList()
        if count == 0:
            print("鈿狅笍 鏇存柊濂藉弸鍒楄〃澶辫触!")
        else:
            try:
                for index, value in self.friends_xpath_list.items():
                    if index == name:
                        friend_id = driver.find_element(By.XPATH, value=value)
                        friend_id.click()
                        time.sleep(1.5)
                        seng = driver.find_element(By.XPATH,
                                                   value='//div[@class="messageEditorimChatEditorContainer"]/div/div')
                        seng.send_keys(text)
                        seng.send_keys(Keys.ENTER)
                        return TrueString(True, None)
            except Exception as e:
                return TrueString(False, e)

    def Find_Friends(self, name: str):
        count = self.Updara_FrinderList()
        is_find = False
        if count == 0:
            return TrueString(False, '鏈垵濮嬪寲濂藉弸')
        try:
            for index, value in self.friends_xpath_list.items():
                if index == name:
                    is_find = True
            return TrueString(is_find, None)
        except Exception as e:
            return TrueString(False, e)

    def LoginInit(self):
        try:
            dle_user = driver.find_element(By.XPATH,
                                           value='//*[@id="douyin_login_comp_flat_panel"]/div/div[2]/div/div[4]/p')
            dle_user.click()
        except:
            pass


init = False
Login_is_bool = False
app = FastAPI()

# CORS 閰嶇疆
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 瀵嗙爜瀛樺偍 (鍐呭瓨涓紝鐢熶骇鐜寤鸿瀛樺叆鏂囦欢鎴栨暟鎹簱)
_password = '123456'  # 榛樿瀵嗙爜


def hash_pwd(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()


# Token瀛樺偍
_valid_tokens = set()
_last_login_ip = '鏃?


def generate_token() -> str:
    token = secrets.token_hex(32)
    _valid_tokens.add(token)
    return token


def verify_token(token: str) -> bool:
    return token in _valid_tokens


def remove_token(token: str):
    _valid_tokens.discard(token)


def require_auth(authorization: str = Header(None)):
    if not authorization or not authorization.startswith('Bearer '):
        return {'code': 401, 'data': '鏈巿鏉?}
    token = authorization[7:]
    if not verify_token(token):
        return {'code': 401, 'data': '鏈巿鏉?}
    return None


# 瀹氭椂浠诲姟瀛樺偍
scheduled_tasks = {}  # 鏍煎紡: {浠诲姟ID: job瀵硅薄}


# 瀹氭椂绾跨▼
def run_schedule():
    """鍚庡彴绾跨▼杩愯瀹氭椂浠诲姟"""
    while True:
        schedule.run_pending()
        time.sleep(1)


def start_scheduler():
    """鍚姩瀹氭椂浠诲姟璋冨害绾跨▼"""
    scheduler_thread = threading.Thread(target=run_schedule, daemon=True)
    scheduler_thread.start()
    return scheduler_thread


start_time = datetime.now()


# 鎶栭煶鎿嶄綔
@app.get('/Home')
def Home(authorization: str = Header(None)):
    auth_err = require_auth(authorization)
    if auth_err:
        return auth_err
    return {'time': start_time}


@app.get('/Api/Init')  # 鍒濆鍖栨祻瑙堝櫒
def Init(authorization: str = Header(None)):
    auth_err = require_auth(authorization)
    if auth_err:
        return auth_err

    global init, driver, douyin

    if not init:
        try:
            unban_config()
            driver = webdriver.Chrome(service=service, options=options) if service else webdriver.Chrome(options=options)
            driver.set_window_size(1400, 3200)
            driver.get('https://www.douyin.com/chat?isPopup=1 ')
            douyin = Douyin(driver)
            init = True
            start_scheduler()  # 鍚姩璋冨害绾跨▼
            return {'code': 200, 'data': 'success'}
        except SessionNotCreatedException as e:
            if "This version of Microsoft Edge WebDriver only supports" in str(e):
                return {'code': 400, 'data': '闇€瑕佹洿鏂版祻瑙堝櫒椹卞姩!'}
            return {'code': 400, 'data': f'娴忚鍣ㄤ細璇濆垱寤哄け璐? {str(e)}'}
        except Exception as e:
            return {'code': 500, 'data': f'鍒濆鍖栧け璐? {str(e)}'}
    else:
        return {'code': 200, 'data': 'init Repeated!'}


@app.get('/Api/GetInit')
def GetInit(authorization: str = Header(None)):
    auth_err = require_auth(authorization)
    if auth_err:
        return auth_err
    return {'code': 200, 'data': 'Yes' if init else 'No'}


@app.post('/Api/login')  # 鐧诲綍 浼犲叆cooke
def Login(cooke: str = Body(default=None), gzip_flag: bool = Body(default=False), authorization: str = Header(None)):
    auth_err = require_auth(authorization)
    if auth_err:
        return auth_err
    global Login_is_bool
    if cooke:
        try:
            decoded_bytes = base64.b64decode(cooke)
            if gzip_flag:
                try:
                    decoded_bytes = gzip.decompress(decoded_bytes)
                except Exception:
                    return {'code': '404',
                            'data': 'login-error-gzip decompress failed, check cookie format and gzip flag'}
            cookie_list = decoded_bytes.decode('utf-8')
            str = eval(base64.b64decode(cookie_list).decode('utf-8').replace('false', 'False').replace('true', 'True'))
            for cookie in str:
                driver.add_cookie(cookie)
        except Exception as e:
            return {'code': '404', 'data': f'login-error-cookie parse error: {str(e)}'}
        driver.refresh()
        try:
            login_type_element = driver.find_element(By.XPATH, '//*[@id="douyin_login_comp_flat_panel"]/picture')
            login_type = login_type_element.text
            return {'code': '404', 'data': 'login-error-cooker cant login'}
        except NoSuchElementException:
            Login_is_bool = True
            return {'code': '200', 'data': 'ok'}
    else:
        return {'code': '404', 'data': 'login-error-not cooker'}  # # @#z


@app.get('/Api/Pnglogin')  # 鎵爜鐧诲綍
def PngLogin(authorization: str = Header(None)):
    auth_err = require_auth(authorization)
    if auth_err:
        return auth_err
    global Login_is_bool
    time.sleep(1)
    if _is_two_factor_page():
        Login_is_bool = False
        return {'code': 202, 'data': 'two_factor_required'}
    cooke = driver.get_cookies()
    if cooke:
        try:
            login_type_element = driver.find_element(By.XPATH, '//*[@id="douyin_login_comp_flat_panel"]/picture')
            login_type = login_type_element.text
            return {'code': '404', 'data': 'login-error-qr-not-confirmed'}
        except NoSuchElementException:
            Login_is_bool = True
            return {'code': '200', 'data': 'ok'}
    else:
        return {'code': '404', 'data': 'login-error-not cooker'}  # # @#z


@app.get('/Api/GetLogin')  # 鑾峰彇鐧诲綍
def GetLogin(authorization: str = Header(None)):
    auth_err = require_auth(authorization)
    if auth_err:
        return auth_err
    return {'code': 200, 'data': 'Yes' if Login_is_bool else 'No'}


@app.get('/Api/login/Init/GetLoginPng')  # 鑾峰彇鐧诲綍鎵爜
def GetLoginPng(authorization: str = Header(None)):
    auth_err = require_auth(authorization)
    if auth_err:
        return auth_err
    try:
        Douyin.LoginInit(douyin)
        try:
            error = driver.find_element(By.XPATH, '//*[@id="animate_qrcode_container"]/div[2]/div/p[1]')
            img_element = driver.find_element(By.XPATH, '//*[@id="animate_qrcode_container"]/div[2]/img')
            img_element.click()
        except:
            pass
        img_element = driver.find_element(By.XPATH, '//*[@id="animate_qrcode_container"]/div[2]/img')
        login_src = img_element.get_attribute('src')
        try:
            is_rust = driver.find_element(By.XPATH, '//*[@id="animate_qrcode_container"]/div[2]/div')
            is_rust.click()
            time.sleep(5)
            img_element = driver.find_element(By.XPATH, '//*[@id="animate_qrcode_container"]/div[2]/img')
            login_src = img_element.get_attribute('src')
        except:
            pass
        if login_src:
            return {'code': 200, 'data': login_src}
        else:
            return {'code': 404, 'data': 'cant find LoginPng src attribute'}
    except NoSuchElementException:
        return {'code': 404, 'data': 'cant find img element'}


@app.get('/Api/login/Init/GetCooker')  # 鑾峰彇cooke
def GetCooke(password: str = Query(None), authorization: str = Header(None)):
    auth_err = require_auth(authorization)
    if auth_err:
        return auth_err
    # 楠岃瘉瀵嗙爜
    if not password or hash_pwd(password) != hash_pwd(_password):
        return {'code': 400, 'data': '瀵嗙爜閿欒'}
    if Login_is_bool:
        cooke = driver.get_cookies()
        cookie_json = json.dumps(cooke)
        cookie_base64 = base64.b64encode(cookie_json.encode('utf-8')).decode('utf-8')
        return {'code': 200, 'data': {'cooke': cookie_base64}}
    else:
        return {'code': 400, 'data': '鏈櫥褰?}


@app.get('/Api/GetFriendsList')  # 鑾峰彇濂藉弸鍒楄〃
def GetFrindesList(authorization: str = Header(None)):
    auth_err = require_auth(authorization)
    if auth_err:
        return auth_err
    try:
        friends_list = douyin.Updara_FrinderList()
        if len(friends_list) == 0:
            return {'code': 404, 'data': '鏆傛棤濂藉弸鎴栭〉闈㈡湭鍔犺浇'}
        dicts = {}
        for v in friends_list:
            dicts[v.username] = [v.avatar, v.fire]
        return {'code': 200, 'data': {'count': len(friends_list), 'list': dicts}}
    except Exception as e:
        return {'code': 404, 'data': str(e)}


@app.get('/Api/Send')
def Send(name: str, text: str, authorization: str = Header(None)):
    auth_err = require_auth(authorization)
    if auth_err:
        return auth_err
    Douyin.Updara_FrinderList(douyin)
    out = Douyin.Send_Frinder(douyin, name, text)
    if out.is_bool:
        return {'code': 200, 'data': 'Send successfully'}
    else:
        return {'code': 404, 'data': out.string}


@app.get('/Api/GetUsername')
def GetUserInfo(authorization: str = Header(None)):
    auth_err = require_auth(authorization)
    if auth_err:
        return auth_err
    if Login_is_bool:
        match = re.search(r'\\"nickname\\":\\"([^\\"]+)\\"', driver.page_source)
        if match:
            text = match.group(0)
            clean = text.replace('\\"', '"')
            data = json.loads('{' + clean + '}')
            return {'code': 200, 'data': data['nickname']}
        else:
            return {'code': 400, 'data': '宸茬櫥褰?浣嗘湭鑾峰彇鍒扮敤鎴峰悕'}
    else:
        return {'code': 400, 'data': '鏈櫥褰?}


@app.get('/Api/GetScrlk')  # 鑾峰彇鎴浘
def GetScrlk(authorization: str = Header(None)):
    auth_err = require_auth(authorization)
    if auth_err:
        return auth_err
    try:
        driver.save_screenshot("temp.png")
        with open("temp.png", "rb") as f:
            img_data = base64.b64encode(f.read()).decode('utf-8')
        os.remove("temp.png")
        return {'code': 200, 'data': img_data}
    except Exception as e:
        return {'code': 400, 'data': f'鎴浘閿欒:{e}'}


@app.get('/Api/DieLogin')  # 鍙栨秷鐧诲綍
def DieLogin(authorization: str = Header(None)):
    auth_err = require_auth(authorization)
    if auth_err:
        return auth_err
    driver.delete_all_cookies()
    driver.refresh()
    return {'code': 200, 'data': '宸叉竻闄ooke'}


@app.get('/Api/LoginPhone')
def authorization(areacode: str, phone: str, authorization: str = Header(None)):
    auth_err = require_auth(authorization)
    if auth_err:
        return auth_err
    try:
        if not _is_two_factor_page():
            Douyin.LoginInit(douyin)

        try:
            areacode_value = _find_first(By.XPATH, [
                '//*[@id="douyin_login_comp_normal_input_id"]/div[1]/div/input',
                '//input[contains(@placeholder, "区号")]',
                '//input[contains(@placeholder, "国家")]',
            ])
            areacode_value.clear()
            areacode_value.send_keys(areacode.strip())
        except Exception:
            pass

        inp = _find_first(By.XPATH, [
            '//*[@id="normal-input"]',
            '//input[contains(@placeholder, "手机号")]',
            '//input[contains(@placeholder, "手机")]',
            '//input[@type="tel"]',
            '//input[@inputmode="tel"]',
        ])
        inp.clear()
        inp.send_keys(phone)

        button = _click_first_xpath([
            '//*[@id="douyin_login_comp_button_input_id"]',
            '//*[@id="douyin_login_comp_button_input_id"]/span',
            '//button[contains(., "验证码")]',
            '//*[contains(text(), "获取验证码")]',
            '//*[contains(text(), "发送验证码")]',
        ])
        time.sleep(2)
        if button.text and any(word in button.text for word in ['重新', '秒', 's', 'S']):
            return {'code': 200, 'data': 'verify code sent'}
        return {'code': 200, 'data': 'verify code sent'}
    except Exception as e:
        return {'code': 400, 'data': str(e)}


@app.get('/Api/LoginPhoneInput')
def authorizations(code: str, authorization: str = Header(None)):
    global Login_is_bool
    auth_err = require_auth(authorization)
    if auth_err:
        return auth_err
    try:
        inp = _find_first(By.XPATH, [
            '//*[@id="button-input"]',
            '//input[contains(@placeholder, "验证码")]',
            '//input[contains(@placeholder, "短信")]',
            '//input[@inputmode="numeric"]',
        ])
        inp.clear()
        inp.send_keys(code)

        _click_first_xpath([
            '//*[@id="douyin_login_comp_btn_id"]',
            '//button[contains(., "登录")]',
            '//button[contains(., "确认")]',
            '//button[contains(., "下一步")]',
        ])
        time.sleep(3)
        if _is_two_factor_page():
            return {'code': 400, 'data': 'secondary verification is still required'}
        try:
            driver.find_element(By.XPATH, '//*[@id="douyin_login_comp_flat_panel"]/picture')
            return {'code': 400, 'data': 'login failed'}
        except Exception:
            Login_is_bool = True
            return {'code': 200, 'data': 'login success'}
    except Exception as e:
        return {'code': 400, 'data': str(e)}


@app.get('/Api/LoginDebug')
def LoginDebug(authorization: str = Header(None)):
    global Login_is_bool
    auth_err = require_auth(authorization)
    if auth_err:
        return auth_err
    if Login_is_bool == False:
        Login_is_bool = True
        return {'code': 200, 'data': 'OK'}
    else:
        return {'code': 400, 'data': '宸叉槸鐧诲綍鐘舵€?鏃犻渶璁惧畾'}


# 瀹氭椂浠诲姟鎿嶄綔
@app.get('/Time/add')
def add_time(time: str, name: str, text: str = None, authorization: str = Header(None)):
    auth_err = require_auth(authorization)
    if auth_err:
        return auth_err
    # 妫€鏌ユ槸鍚﹀凡瀛樺湪璇ュソ鍙嬬殑瀹氭椂浠诲姟
    for task_id, job in scheduled_tasks.items():
        if task_id.endswith(f"_{name}"):
            return {'code': 400, 'data': f'濂藉弸 {name} 宸叉湁瀹氭椂浠诲姟锛岃鍏堝垹闄ゆ垨淇敼'}

    temp = douyin.Find_Friends(name)
    if temp.is_bool:
        play_time = format_time(time)
        msg = AiqingGongyu_text() if text == None else text
        # 娣诲姞瀹氭椂浠诲姟骞朵繚瀛榡ob瀵硅薄
        job = schedule.every().day.at(play_time).do(douyin.Send_Frinder, name, msg)
        # 鐢熸垚鍞竴浠诲姟ID
        task_id = f"{play_time}_{name}"
        scheduled_tasks[task_id] = job
        return {'code': 200, 'data': f'宸叉坊鍔犲畾鏃朵换鍔? {play_time}', 'task_id': task_id}
    else:
        return {'code': 404, 'data': temp.string}


@app.get('/Time/del')
def del_time(task_id: str, authorization: str = Header(None)):
    auth_err = require_auth(authorization)
    if auth_err:
        return auth_err
    """鏍规嵁浠诲姟ID鍒犻櫎瀹氭椂浠诲姟"""
    if task_id in scheduled_tasks:
        job = scheduled_tasks[task_id]
        schedule.cancel_job(job)
        del scheduled_tasks[task_id]
        return {'code': 200, 'data': f'宸插垹闄や换鍔? {task_id}'}
    else:
        return {'code': 404, 'data': '浠诲姟ID涓嶅瓨鍦?}


@app.get('/Time/edit')
def edit_time(name: str, new_time: str, authorization: str = Header(None)):
    auth_err = require_auth(authorization)
    if auth_err:
        return auth_err
    """淇敼鎸囧畾濂藉弸鐨勫畾鏃朵换鍔℃椂闂?""
    # 鏌ユ壘璇ュソ鍙嬬殑鐜版湁浠诲姟
    old_task_id = None
    for task_id, job in scheduled_tasks.items():
        if task_id.endswith(f"_{name}"):
            old_task_id = task_id
            break

    if not old_task_id:
        return {'code': 404, 'data': f'濂藉弸 {name} 娌℃湁瀹氭椂浠诲姟'}

    # 鍙栨秷鏃т换鍔?    old_job = scheduled_tasks[old_task_id]
    schedule.cancel_job(old_job)

    # 瑙ｆ瀽鏃т换鍔′俊鎭?    parts = old_task_id.split('_', 1)
    old_time = parts[0] if len(parts) == 2 else ""

    # 鍒涘缓鏂颁换鍔?    new_play_time = format_time(new_time)
    msg = AiqingGongyu_text()  # 鑾峰彇鏂扮殑鍚嶈█
    new_job = schedule.every().day.at(new_play_time).do(douyin.Send_Frinder, name, msg)

    # 鐢熸垚鏂颁换鍔D骞舵浛鎹?    new_task_id = f"{new_play_time}_{name}"
    scheduled_tasks[new_task_id] = new_job
    del scheduled_tasks[old_task_id]

    return {
        'code': 200,
        'data': f'宸插皢 {name} 鐨勫畾鏃朵换鍔′粠 {old_time} 淇敼涓?{new_play_time}',
        'old_time': old_time,
        'new_time': new_play_time,
        'task_id': new_task_id
    }


@app.get('/Time/getlist')
def get_time_list(authorization: str = Header(None)):
    auth_err = require_auth(authorization)
    if auth_err:
        return auth_err
    """鑾峰彇褰撳墠鎵€鏈夊畾鏃朵换鍔″垪琛?""
    tasks = []
    for task_id, job in scheduled_tasks.items():
        # 瑙ｆ瀽浠诲姟ID鑾峰彇淇℃伅
        parts = task_id.split('_', 1)
        if len(parts) == 2:
            time_str, name = parts
            tasks.append({
                'task_id': task_id,
                'time': time_str,
                'name': name,
                'next_run': str(job.next_run) if job.next_run else None
            })
    return {'code': 200, 'data': {'count': len(tasks), 'tasks': tasks}}


# 鍚庡彴鐧诲綍
@app.get('/Api/Login/Admin')
def admin_login(username: str, password: str, request: Request = None):
    global _last_login_ip
    if username == 'admin' and hash_pwd(password) == hash_pwd(_password):
        _last_login_ip = request.client.host if request else '127.0.0.1'
        token = generate_token()
        return {'code': 200, 'data': token}
    else:
        return {'code': 400, 'data': '鐧诲綍澶辫触'}


@app.get('/Api/GetLastLoginIP')
def get_last_login_ip(authorization: str = Header(None)):
    auth_err = require_auth(authorization)
    if auth_err:
        return auth_err
    return {'code': 200, 'data': _last_login_ip}


# 閫€鍑虹櫥褰?@app.get('/Api/logout')
def logout(authorization: str = Header(None)):
    auth_err = require_auth(authorization)
    if auth_err:
        return auth_err
    token = authorization[7:]
    remove_token(token)
    return {'code': 200, 'data': '宸查€€鍑虹櫥褰?}


# 瀵嗙爜淇敼
@app.get('/Api/ChangePassword')
def change_password(old_password: str, new_password: str, authorization: str = Header(None)):
    auth_err = require_auth(authorization)
    if auth_err:
        return auth_err
    global _password
    if hash_pwd(old_password) != hash_pwd(_password):
        return {'code': 400, 'data': '鍘熷瘑鐮侀敊璇?}
    _password = new_password
    return {'code': 200, 'data': '瀵嗙爜淇敼鎴愬姛'}


if __name__ == "__main__":
    port = int(os.getenv('PORT', '9844'))
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=port,
        reload=False
    )

