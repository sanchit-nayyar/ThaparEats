from selenium import webdriver
import time

ffx = webdriver.Firefox()
ffx.get('https://webkiosk.thapar.edu/index.jsp?_ga=2.47888167.1679932621.1542041253-847389414.1540468662')
ffx.find_element_by_name('MemberCode').send_keys('101603302')
ffx.find_element_by_name('Password').send_keys('101601857')
ffx.find_element_by_name('BTNSubmit').click()

print ffx.current_url

# time.sleep(5)

ffx.close()

#https://webkiosk.thapar.edu/StudentFiles/StudentPage.jsp