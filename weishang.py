#coding:utf-8
from selenium import webdriver
import pyperclip
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup as bs
import time
import re


# 启动浏览器
def load_web():
    driver = webdriver.Chrome(executable_path=r"D:\GeckoDriver\chromedriver")
    driver.get("https://www.szwego.com/")
    # driver.maximize_window()
    driver.implicitly_wait(1)
    return driver


# 自动下翻网页
def scroll_to_bottom(driver, wpx):
    win_js = "window.scrollTo(0," + str(wpx+1000) + ")"
    driver.execute_script(win_js)
    return wpx + 1000


# 确定下滑到哪里
def down_see_o(driver, w_len):
    shopbox_len = 0
    wpx = 0
    while shopbox_len < (w_len + 3):
        wpx = scroll_to_bottom(driver, wpx)
        time.sleep(1)
        soup = bs(driver.page_source, "lxml")
        shopbox_len = len(soup.select(".weui_cells > div"))


# 控制操作box 自动
def shopbox_k(patterns, driver, w_len):
    soup = bs(driver.page_source, "lxml")
    shopbox = soup.select(".weui_cells > div")
    for i in range(w_len, 0, -1):
        shop_num = len(shopbox[i+1].select(".f-flex-1 > .f-flex-wrap"))
        img_num = len(shopbox[i+1].select(".bury_click"))
        for j in range(shop_num+img_num, 0, -1):
            shop_xpath = '/html/body/div/div[2]/div[2]/div/div[6]/div[' + str(i) + ']/div[2]/a[' + str(j) + ']/div[2]/div[2]/div[1]/div'
            print("Current location:" + str(j))
            shop_copy(patterns, driver, shop_xpath)


# 控制操作box 手动
def shopbox_s(patterns, driver, shopnum):
    for j in range(shopnum, 0, -1):
        shop_xpath = '/html/body/div/div[2]/div[2]/div/div[6]/div[1]/div[2]/a[' + str(j) + ']/div[2]/div[2]/div[1]/div'
        print("Current location:" + str(j))
        shop_copy(patterns, driver, shop_xpath)


# 操作商品
def shop_copy(patterns, driver, shop_xpath):
    try:
        element = driver.find_element_by_xpath(shop_xpath)
        driver.execute_script("arguments[0].click();", element)
    except:
        print("Entry not found!")
        return
    driver.implicitly_wait(10)
    time.sleep(3)
    isload = True
    error_num = 0
    while isload:
        try:
            soup = bs(driver.page_source, "lxml")
            shopinfo = soup.select(".weui_textarea")[0].text
            isload = False
        except:
            print('Failed to get related elements, retrying!')
            if(error_num >= 5):
                print('Timeout, refresh the page again!')
                driver.refresh()
            error_num += 1
            time.sleep(3)
    newshopinfo = puls_plice(patterns, shopinfo)
    pyperclip.copy(newshopinfo)
    driver.find_element_by_xpath('/html/body/div/div[2]/div[1]/div[1]/div/div/div/textarea[1]').clear()
    driver.find_element_by_xpath('/html/body/div/div[2]/div[1]/div[1]/div/div/div/textarea[1]').send_keys(Keys.CONTROL,'v')
    time.sleep(0.5)
    element = driver.find_element_by_xpath('/html/body/div/div[2]/div[1]/div[3]/div[1]/div/div/div')
    driver.execute_script("arguments[0].click();", element)
    time.sleep(0.5)
    while(soup.select(".f-flex > .weui_btn_plain_primary") == []):
        element = driver.find_element_by_xpath('/html/body/div/div[2]/div[8]/div[1]/button')
        driver.execute_script("arguments[0].click();", element)
        driver.implicitly_wait(10)
        time.sleep(5)
        soup = bs(driver.page_source, "lxml")

# 操作字符串
def puls_plice(patterns, shopinfo):
    oldresult = []
    for i in patterns:
        result = re.findall(i, shopinfo, re.M | re.I)
        if (result != []):
            for p in result:
                oldresult.append(p)
    print("Price before modification:", end="")
    print(oldresult)
    isInShop = re.findall("支持放店", shopinfo, re.M | re.I)
    newresult = []
    if (isInShop != []):
        if (oldresult != []):
            for j in oldresult:
                j = int(j)
                newprice = j + 100
                newresult.append(newprice)
    else:
        if (oldresult != []):
            for j in oldresult:
                j = int(j)
                if (j < 10):
                    newprice = j
                elif (j > 10 and j < 50):
                    newprice = j + 20
                elif (j >= 50 and j <= 100):
                    newprice = j + 30
                elif (j > 100 and j <= 1000):
                    newprice = j + 50
                elif (j > 1000 and j<=100000):
                    newprice = j + 100
                elif (j > 100000):
                    newprice = j
                newresult.append(newprice)
    print("Revised price:", end="")
    print(newresult)
    newshopinfo = shopinfo
    for oldprice, newprice in zip(oldresult, newresult):
        newshopinfo = newshopinfo.replace(oldprice, str(newprice))
    newshopinfo = newshopinfo.replace("本地自取", "")
    newshopinfo = newshopinfo.replace("自取", "")
    # print(newshopinfo)
    return newshopinfo


if __name__ == '__main__':
    surface = ["^(\d+)", "💰(\d+)", "(\d+)💰", "￥(\d+)", "白皮(\d+)", "皮带(\d+)", "钢带(\d+)", "白(\d+)", "银(\d+)", "金(\d+)", "金黑(\d+)", "刚(\d+)", "枚(\d+)", "玫(\d+)", "💵(\d+)", "同价(\d+)", "白壳(\d+)"]  # 表
    beauty = ["(\d+)💰","(\d+)包邮"]  # 美妆
    clothes = ["💰(\d+)", "(\d+)💰", "批(\d+)", "P(\d+)"]  # 衣服
    shoes = ["💰(\d+)", "P(\d+)", "PF(\d+)", "🈴️(\d+)", "^(\d+)","放店(\d+)","现货 (\d+)","价格：(\d+)","福利价：(\d+)"]  # 鞋
    hshops = ["￥(\d+)", "💰(\d+)", "(\d+)💰", "^(\d+)", "批(\d+)", "批:(\d+)", "P(\d+)", "PF(\d+)", "寸(\d+)", "(\d+)包邮", "￥(\d+)","🏅(\d+)"]  # 百货
    skin = ["💰(\d+)", "^(\d+)", "❤(\d+)", "❤小(\d+)", "❤大(\d+)", "(\d+)配", "♥️(\d+)", "毛呢 (\d+)", "原版(\d+)", "原版皮 (\d+)"]  # 皮具
    print('正在打开浏览器，请完成初始操作！')
    driver = load_web()
    patterns = []
    while True:
        try:
            print('1.clothes')
            print('2.make up')
            print('3.shose')
            print('4.hshops')
            print('5.surface')
            print('6.skin')
            num = int(input('Please input the commodity type to be operated：'))
            if(num == 1):
                patterns = clothes
            elif(num == 2):
                patterns = beauty
            elif (num == 3):
                patterns = shoes
            elif (num == 4):
                patterns = hshops
            elif (num == 5):
                patterns = surface
            elif (num == 6):
                patterns = skin
            # print(patterns)
            w_len = int(input('Please enter the number of days of commodity to be operated：'))
            sssssss = input('Please confirm that you have completed the initial operation, such as changing the product type in advance! Click enter to continue!')
            print('8.Automatic mode')
            print('9.Manual mode')
            num = int(input('Please select mode：'))
            if(num == 8):
                print('Start execution。。。。。。。。。。')
                down_see_o(driver, w_len)
                shopbox_k(patterns, driver, w_len)
                print('Completion of enforcement。。。。。。。。。。')
                print('Please continue。')
            elif(num == 9):
                shopnum = int(input('Please input intermittent number：'))
                print('Start execution。。。。。。。。。。')
                down_see_o(driver, w_len)
                shopbox_s(patterns, driver, shopnum)
                print('Completion of enforcement。。。。。。。。。。')
                print('Please continue。')
        except:
            aaaa = input("浏览器崩溃，请查看后回车继续。。。")
