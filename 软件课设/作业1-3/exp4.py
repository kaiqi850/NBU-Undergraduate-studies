# 安装必要的库
# pip install opencv-python
# pip install numpy
# pip install selenium

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from time import sleep
from urllib import request
import cv2
import numpy as np

# 用于显示图片
def show(name):
    cv2.imshow('Show', name)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# 初始化 Selenium WebDriver
driver = webdriver.Chrome()
driver.maximize_window()
driver.implicitly_wait(5)
url = 'https://juejin.im/'

# 实现登录功能
def get_login(driver, url):
    driver.get(url)
    driver.find_element(By.XPATH, '//button[@class="login-button"]').click()
    driver.find_element(By.XPATH, '//span[@class ="clickable"]').click()
    driver.find_element(By.XPATH, '//input[@name="loginPhoneOrEmail"]').send_keys('填入自己的账号')
    driver.find_element(By.XPATH, '//input[@name="loginPassword"]').send_keys('填入自己的密码')
    driver.find_element(By.XPATH, '//button[@class="btn"]').click()
    sleep(2)
    return driver

driver = get_login(driver, url)

# 定义图片存储路径
blockJpg = 'image/block.jpg'
templateJpg = 'image/template.jpg'

# 获取验证码中的图片
def get_image(driver):
    bj = driver.find_element(By.XPATH, '//img[@class="sc-gZMcBi YkDbM sc-ifAKCX hCcViW"]').get_attribute('src')
    yd = driver.find_element(By.XPATH, '//img[@class="captcha_verify_img_slide react-draggable sc-gqjmRU irZaUl"]').get_attribute('src')
    req = request.Request(bj)
    bg = open(templateJpg, 'wb+')
    bg.write(request.urlopen(req).read())
    bg.close()
    req = request.Request(yd)
    bk = open(blockJpg, 'wb+')
    bk.write(request.urlopen(req).read())
    bk.close()
    return templateJpg, blockJpg

bkg, blk = get_image(driver)

# 计算缺口位置
def get_distance(bkg, blk):
    block = cv2.imread(blk, 0)
    tp = cv2.imread(bkg, 0)
    cv2.imwrite(templateJpg, tp)
    cv2.imwrite(blockJpg, block)

    block = cv2.imread(blockJpg)
    block = cv2.cvtColor(block, cv2.COLOR_BGR2GRAY)
    block = abs(255 - block)
    cv2.imwrite(blockJpg, block)
    block = cv2.imread(blockJpg)
    tp = cv2.imread(templateJpg)

    result = cv2.matchTemplate(block, tp, cv2.TM_CCOEFF_NORMED)
    _, _, _, max_loc = cv2.minMaxLoc(result)
    x = max_loc[0]

    if x < 20:  # 若位置不对，刷新验证码
        elem = driver.find_element(By.XPATH, '//a[@class="secsdk_captcha_refresh refresh-button___StyledA-sc-18f114n-0 jgMJRc"]')
        sleep(1)
        elem.click()
        bkg, blk = get_image(driver)
        x, tp = get_distance(bkg, blk)
    return x, tp

distance, temp = get_distance(bkg, blk)

# 模拟人为拖动滑块
def get_tracks(dis):
    v = 0
    m = 0.3
    tracks = []
    current = 0
    mid = dis * 4 / 5
    while current <= dis:
        if current < mid:
            a = 2
        else:
            a = -3
        v0 = v
        s = v0 * m + 0.5 * a * (m ** 2)
        current += s
        tracks.append(round(s))
        v = v0 + a * m
    return tracks

double_distance = int(distance * 1.231884058)
tracks = get_tracks(double_distance)
tracks.append(-(sum(tracks) - double_distance))

element = driver.find_element(By.XPATH, '//div[@class="secsdk-captcha-drag-icon sc-ckVGcZ gZcwqQ"]')
ActionChains(driver).click_and_hold(on_element=element).perform()
for track in tracks:
    ActionChains(driver).move_by_offset(xoffset=track, yoffset=0).perform()
sleep(0.5)
ActionChains(driver).release(on_element=element).perform()
show(temp)
