import time
import logging

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(name)s %(levelname)s %(message)s",
                    datefmt = '%Y-%m-%d  %H:%M:%S %a',    #注意月份和天数不要搞乱了，这里的格式化符与time模块相同
                    filename = 'spider.log',
                    filemode = 'a'
                    )

def log(msg):
    logging.info(msg)
    
