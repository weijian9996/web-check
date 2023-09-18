import pyautogui
import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import requests
from bs4 import BeautifulSoup
# from threading import Thread , Lock
from plyer import notification
import email.message
import smtplib
import os
from dotenv import load_dotenv

load_dotenv()
class Main():
    def __init__(self):
        self.initial_x,self.initial_y =pyautogui.position()
        self.timeout = 10
        self.last_active = time.time()
        self.scheduler = BackgroundScheduler()
        self.status = False   # False = Idling , True = In Use
        self.scheduler.add_job(self.initialize,'cron',day_of_week='wed',hour=9)
        self.scheduler.add_job(self.run_task,'cron',day_of_week='wed',hour=9)
        self.scheduler.start()
    

    def initialize(self):
        self.complete = False
        print('Server Check started')

    def run(self):
        try:
            print('Running')
            while True:
                current_x,current_y = pyautogui.position()

                if (current_x,current_y) != (self.initial_x,self.initial_y):
                    self.status = True
                    self.last_active = time.time

                else:
                    if time.time() - self.last_active > self.timeout:
                        self.status = False

                self.initial_x, self.initial_y = current_x,current_y

                time.sleep(1)

        except (KeyboardInterrupt,SystemExit):
            print('Exit')
            self.scheduler.shutdown()

    def run_task(self):
        check = self.task()
        if check:
            self.notify()
        else:
            time.sleep()
            self.run_task()
            
    def notify(self,):
        if self.status:
                notification.notify(
                title='Maple Server Check',
                message='Server Check is Completed',
                timeout=5
                )
        else:
            msg = email.message.EmailMessage()
            msg['From'] = os.getenv('EMAIL_USERNAME')
            msg['To'] = 'weijianpro@gmail.com'
            msg['Subject'] = 'Maple Server Check'
            msg.set_content('Server Check is Completed')

            # SSL port = 465 ,none SSL port = 587
            server =smtplib.SMTP_SSL('smtp.gmail.com',465)
            server.login(os.getenv('EMAIL_USERNAME'),os.getenv('EMAIL_PASS'))
            server.send_message(msg)
            server.close()

    def task(self):
        url = 'http://www.maplesea.com/notices'

        response = requests.get(url)

        if response.status_code ==200:
            soup = BeautifulSoup(response.text,'lxml')
            title = soup.find("li",attrs={'class':'title_links'})
            link = title.find('a')
            check=link.string.strip()

            if "[Completed]" in check:
                # send notification here or email
                print('Server Checked Completed')
                return True
            else:
                return False


    def job(self):
        print(datetime.now())

        
main=Main()
if __name__ == '__main__':
    # t = Thread(target=main.check_schedule)
    # t.setDaemon(True)
    # t.start()

    main.run()

