import time
from selenium import webdriver


# 创建浏览器对象
driver = webdriver.Chrome()
driver.get('https://passport.lagou.com/login/login.html?')
# # 查找节点 
ID = driver.find_element_by_xpath("//input[@type='text']")
password = driver.find_element_by_xpath("//input[@type='password']")
time.sleep(2)
#输入用户名
ID.send_keys('用户名')
time.sleep(2)
#输入密码
password.send_keys('密码')
login = driver.find_element_by_xpath("//input[@type='submit']")

#登录
login.click()
