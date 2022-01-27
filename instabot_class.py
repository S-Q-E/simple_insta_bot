import os.path
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from data import username, password, users
import time
import random


class InstaBot:
    """
    Simple Instagram bot which can put likes, grab users from page and search post with hashtags
    """
    def __init__(self, username, password):
        self.username = username
        self.password = password
        options = Options()

        # disabling webdriver mode
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        # if you want to off headless mode, just comment line below
        options.add_argument('--headless')
        self.browser = webdriver.Chrome(r'C:\Users\User\Desktop\scraping\chromedriver.exe', options=options)

    def close_browser(self):
        """
        Method close browser and all tabs
        :return: None
        """
        self.browser.close()
        self.browser.quit()

    def login(self):
        """
        This method log in to your account
        :return: None
        """
        self.browser.get('https://instagram.com')
        time.sleep(random.randrange(2,5))

        username_input = self.browser.find_element_by_name('username')
        username_input.clear()
        username_input.send_keys(username)

        time.sleep(random.randrange(1, 3))

        password_input = self.browser.find_element_by_name('password')
        password_input.clear()
        password_input.send_keys(password)

        password_input.send_keys(Keys.ENTER)
        time.sleep(random.randrange(4, 6))

    def like_photo_by_hashtag(self, hashtag: str):
        """
        This method linking all post with hashtag
        :param hashtag: write here the hashtag you are interested in
        :return: None
        """
        self.browser.get(f'https://www.instagram.com/explore/tags/{hashtag}/')
        time.sleep(random.randrange(2, 6))

        for i in range(1, 5):
            self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(random.randrange(2, 5))

        hrefs = self.browser.find_elements_by_tag_name('a')

        post_urls = [item.get_attribute('href') for item in hrefs if '/p/' in item.get_attribute('href')]

        for url in post_urls[:4]:
            try:
                self.browser.get(url)
                time.sleep(3)
                print(url)
                like_button = self.browser.find_element_by_xpath(
                    '//*[@id="react-root"]/section/main/div/div[1]/article/div/div[2]/div/div[2]/section[1]/span['
                    '1]/button').click()
                time.sleep(random.randrange(2, 6))
            except Exception as ex:
                print(f"Exception in liking photo: {ex}")
                self.close_browser()

    def xpath_exists(self, xpath):
        """
        This method checking existing xpath
        :param xpath: put here xpath of HTML element
        :return: Bool
        """
        try:
            self.browser.find_element_by_xpath(xpath)
            exist = True
        except NoSuchElementException:
            exist = False
        return exist

    def liking_post(self, userpost):
        """
        Method can like user post
        :param userpost: user post link
        :return: None
        """
        self.browser.get(userpost)
        time.sleep(2)

        wrong_page = '/html/body/div[1]/section/main/div/div/h2'
        if self.xpath_exists(wrong_page):
            print('No such post. Check URL')
            self.close_browser()
        else:
            print('Post available! Liking...')
            time.sleep(random.randrange(1,4))
            like_button = self.browser.find_element_by_xpath(
                '//*[@id="react-root"]/section/main/div/div[1]/article/div/div[2]/div/div[2]/section[1]/span['
                '1]/button').click()
            time.sleep(3)
            print(f'Post {userpost} liked')

    def put_many_likes(self, userpage):
        """
        This method grab all post links in the user page and like them
        :param userpage: like of the user page on IG
        :return: None
        """
        self.browser.get(userpage)
        time.sleep(2)
        self.get_all_post_url(userpage)
        file_name = userpage.split('/')[-2]
        time.sleep(2)
        with open(f"{file_name}_set.txt", 'r') as file:
            urls_list = file.readlines()

            for post_url in urls_list[:5]:
                try:
                    self.browser.get(post_url)
                    time.sleep(3)
                    like_button = self.browser.find_element_by_xpath(
                        '//*[@id="react-root"]/section/main/div/div[1]/article/div/div[2]/div/div[2]/section[1]/span['
                        '1]/button').click()
                    # time.sleep(3)
                    print(f'Post {post_url} liked')
                except Exception as ex:
                    print(ex)
                    self.browser.close()

    def download_user_content(self, userpage):
        """
        This method download all user's content
        :param userpage: link of the user page
        :return: None
        """
        self.get_all_post_url(userpage)
        file_name = userpage.split('/')[-2]
        time.sleep(4)
        self.browser.get(userpage)
        time.sleep(4)

        if os.path.exists(f"{file_name}"):
            print('Directory alredy exists')
        else:
            os.mkdir(file_name)

        img_and_video_src_urls = []

        with open(f"{file_name}_set.txt") as file:
            urls_list = [line.strip() for line in file]
            for post_url in urls_list[:3]:
                try:
                    self.browser.get(post_url)
                    time.sleep(random.randrange(5, 20))
                    img_xpath = '/html/body/div[1]/section/main/div/div[1]/article/div/div[1]/div/div[1]/div[2]/div/div/div/ul/li[2]/div/div/div/div[1]/img'
                    video_xpath = '/html/body/div[1]/section/main/div/div[1]/article/div/div[2]/div/div/div[1]/div/div/video'

                    post_id = post_url.split("/")[-2]
                    if self.xpath_exists(img_xpath):
                        img_src_url = self.browser.find_element_by_xpath(img_xpath).get_attribute('src')
                        img_and_video_src_urls.append(img_src_url)

                        # Getting images
                        get_img = requests.get(img_src_url)
                        time.sleep(random.randrange(10, 15))
                        with open(f"{file_name}/{post_id}_img.jpg", "wb") as img_file:
                            img_file.write(get_img.content)
                            print(f'{post_url} download successfully!')
                    elif self.xpath_exists(video_xpath):
                        video_src_url = self.browser.find_element_by_xpath(video_xpath).get_attribute('src')
                        img_and_video_src_urls.append(video_src_url)

                        # Getting video
                        get_video = requests.get(video_src_url, stream=True)
                        time.sleep(random.randrange(10,15))
                        with open(f"{file_name}/{post_id}_vid.mp4", "wb") as video_file:
                            for chunk in get_video.iter_content(chunk_size=1024*1024):
                                if chunk:
                                    video_file.write(chunk)
                                    print(f'{post_url} download successfully!')
                    else:
                        print("Can't handle links")
                        img_and_video_src_urls.append(f"{post_url} Not such link")
                    # print(f'{post_url} download successfully!')
                except Exception as ex:
                    print(ex)
                    self.browser.close()
            self.close_browser()
        with open('img_and_video_scr_urls.txt', 'a') as file:
            for i in img_and_video_src_urls:
                file.write(i + '\n')

    def get_all_post_url(self, user_page):
        """
        This method getting all posts links of the user's page
        and put them on .txt file
        :param user_page: link of the user page
        :return:
        """
        self.browser.get(user_page)
        time.sleep(2)

        wrong_page = '/html/body/div[1]/section/main/div/div/h2'
        if self.xpath_exists(wrong_page):
            print('No such user. Check URL')
            self.close_browser()
        else:
            print('User found!')
            time.sleep(random.randrange(1, 4))

            posts_count = int(self.browser.find_element_by_xpath('/html/body/div[1]/section/main/div/header/section/ul/li[1]/span/span').text)

            loops_count = round(posts_count/12)

            posts_urls = []

            for i in range(0, loops_count):
                hrefs = self.browser.find_elements_by_tag_name('a')
                post_urls = [item.get_attribute('href') for item in hrefs if '/p/' in item.get_attribute('href')]

                for href in post_urls:
                    posts_urls.append(href)

                self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                time.sleep(random.randrange(2, 5))
                print(f"Iteration #{i}")

            file_name = user_page.split('/')[-2]
            with open(f'{file_name}.txt', 'a') as file:
                for post_url in posts_urls:
                    file.write(post_url + '\n')

            set_posts_urls = set(posts_urls)
            set_posts_urls = list(set_posts_urls)

            with open(f"{file_name}_set.txt", 'a') as f:
                for post in set_posts_urls:
                    f.write(post + '\n')

    def get_all_followers(self, user_page):
        """
        Method get all user's followers, put them in .txt file and follow them
        :param user_page: link of user page
        :return: None
        """
        self.browser.get(user_page)
        time.sleep(2)
        file_name = user_page.split('/')[-2]

        # Creating directory
        if os.path.exists(f"{file_name}"):
            print(f'Directory {file_name} already exists')
        else:
            print(f"{file_name} directory created!")
            os.mkdir(file_name)

        wrong_page = '/html/body/div[1]/section/main/div/div/h2'
        if self.xpath_exists(wrong_page):
            print(f'No {file_name} user. Check URL')
            self.close_browser()
        else:
            print(f'User {file_name} found!')
            time.sleep(random.randrange(1, 4))

        followers_button = self.browser.find_element_by_xpath('/html/body/div[1]/section/main/div/header/section/ul'
                                                              '/li[2]/a')
        followers_count = followers_button.text
        followers_count = followers_count.split(" ")
        followers_count = int("".join(followers_count[0:2]))
        print(f"Followers after: {followers_count}")

        print(f"{file_name} have {followers_count} followers")
        time.sleep(2)

        loops_count = round(int(followers_count/12))
        print(f"Iteration #{loops_count}")
        time.sleep(2)

        followers_button.click()
        time.sleep(4)

        followers_ul = self.browser.find_element_by_xpath('/html/body/div[6]/div/div/div[2]')

        try:
            followers_urls = []
            for i in range(1, loops_count + 1):
                self.browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", followers_ul)
                time.sleep(random.randrange(2, 5))
                print(f"Iteration #{i}")

            all_urls_div = followers_ul.find_elements_by_tag_name('li')

            for url in all_urls_div:
                url = url.find_element_by_tag_name('a').get_attribute('href')
                followers_urls.append(url)

            with open(f'{file_name}/{file_name}.txt', 'a') as txt_file:
                for link in followers_urls:
                    txt_file.write(link + "\n")

            with open(f"{file_name}/{file_name}.txt") as file:
                users_list = [line.strip() for line in file]

                for user in users_list[0:3]:
                    try:
                        try:
                            with open(f"{file_name}/{file_name}_subscribe_list.txt") as subscribe_list_file:
                                lines = [line.strip() for line in subscribe_list_file]
                                if user in lines:
                                    print(f"You already subscribed to {user}, get the next user")
                                    continue
                        except Exception as ex:
                            print("The file with links not created yet")
                            print(ex)

                        self.browser.get(user)
                        page_owner = user.split('/')[-2]

                        if self.xpath_exists('//*[@id="react-root"]/section/main/div/header/section/div[1]/div[1]/div'):
                            print("This is our profile, go to the nex iteration")
                        elif self.xpath_exists(
                            '/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/div['
                            '2]/div/span/span[1]/button '
                        ):
                            print(f"We've already subscribed to {page_owner} skipping iteration")
                        else:
                            time.sleep(random.randrange(2, 5))

                            if self.xpath_exists(
                                '/html/body/div[1]/section/main/div/div/article/div[1]/div/h2'
                            ):
                                try:
                                    follow_button = self.browser.find_element_by_xpath(
                                        '/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/div/button'
                                    ).click()
                                    print(f"Follow to {page_owner} requested")
                                except Exception as ex:
                                    print(ex)
                            else:
                                try:
                                    if self.xpath_exists('/html/body/div[1]/section/main/div/header/section/div['
                                                         '1]/div[1]/div/div/div/span/span[1]/button'):
                                        follow_button = self.browser.find_element_by_xpath('/html/body/div['
                                                                                           '1]/section/main/div'
                                                                                           '/header/section/div['
                                                                                           '1]/div['
                                                                                           '1]/div/div/div/span/span['
                                                                                           '1]/button').click()
                                        print(f'Subscribed to {page_owner}. Account is open!')
                                    else:
                                        print("Can't find such button!")
                                except Exception as ex:
                                    print(ex)
                            with open(f"{file_name}/{file_name}_subscribe_list.txt", 'a') as subscribe_list_file:
                                subscribe_list_file.write(user + "\n")

                            time.sleep(random.randrange(5, 30))

                    except Exception as ex:
                        print(ex)
                        self.close_browser()
        except Exception as ex:
            print(ex)
            self.browser.close()
            self.browser.quit()

    def send_direct_message(self, usernames="", message="", img_path=''):
        """
        This method can send DM to list of users
        :param usernames: list of IG usernames
        :param message: Your message
        :param img_path: your image path
        :return: None
        """
        direct_message_button = '/html/body/div[1]/section/nav/div[2]/div/div/div[3]/div/div[2]/a'

        if not self.xpath_exists(direct_message_button):
            print('Direct message button not found')
            self.close_browser()
        else:
            print('Sending message....')
            direct_message = self.browser.find_element_by_xpath(direct_message_button).click()
            time.sleep(random.randrange(2, 5))

        if self.xpath_exists('/html/body/div[6]/div/div/div'):
            self.browser.find_element_by_xpath('/html/body/div[6]/div/div/div/div[3]/button[2]').click()
            time.sleep(random.randrange(2, 5))

        send_message_button = self.browser.find_element_by_xpath('/html/body/div[1]/section/div/div[2]/div/div/div['
                                                                 '2]/div/div[3]/div/button').click()
        time.sleep(random.randrange(2, 5))

        for user in usernames:
            recipient_input = self.browser.find_element_by_xpath('/html/body/div[6]/div/div/div[2]/div[1]/div/div[2]/input')
            recipient_input.send_keys(user)
            time.sleep(random.randrange(2, 5))

            recipient_choose = self.browser.find_element_by_xpath('/html/body/div[6]/div/div/div[2]/div[2]').find_element_by_tag_name('button').click()
            time.sleep(random.randrange(2, 5))

        next_button = self.browser.find_element_by_xpath('/html/body/div[6]/div/div/div[1]/div/div[2]/div/button').click()
        time.sleep(random.randrange(2, 4))

        if message:
            message_input = self.browser.find_element_by_xpath('/html/body/div[1]/section/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[2]/textarea')
            message_input.send_keys(message)
            time.sleep(random.randrange(3, 6))
            message_input.send_keys(Keys.ENTER)
            print(f"Message {message} sent to {username}!")
            time.sleep(random.randrange(2, 5))

        if img_path:
            send_img_input = self.browser.find_element_by_xpath('/html/body/div[1]/section/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/form/input')
            send_img_input.send_keys(img_path)
            print(f"Image for {usernames} sent successfully")
            time.sleep(random.randrange(5, 10))

        self.close_browser()


