import weibo
import mail
import time
import config

def main():
    myConfig = config.Config()
    myWeibo = weibo.Weibo(myConfig)
    myMail = mail.Mail(myConfig)
    thread_pool = [myWeibo, myMail]
    for t in thread_pool:
        t.start()
        time.sleep(10)
    for t in thread_pool:
        t.join()
    print('###Everything has been done, now you can exit.###\n')
    while True:
         time.sleep(1)
    

if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        print(ex)
        exit(1)
        
        
