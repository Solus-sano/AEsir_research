import logging
import os

COLOR_RESET = "\033[0m"
COLOR_BLUE = "\033[34m"
COLOR_GREEN = "\033[32m"
COLOR_YELLOW = "\033[33m"
COLOR_RED = "\033[31m"
COLOR_MAGENTA = "\033[35m"
COLOR_CYAN = "\033[36m"
COLOR_WHITE = "\033[37m"

class ColoredFormatter(logging.Formatter):
    def __init__(self, fmt, use_color=True):
        super().__init__(fmt)
        self.use_color = use_color

    def format(self, record):
        record.levelname_color = self.get_color_by_level(record.levelno) + record.levelname + COLOR_RESET
        record.asctime_color = COLOR_BLUE + self.formatTime(record, self.datefmt) + COLOR_RESET
        record.location_color = COLOR_GREEN + f"{record.filename}:{record.lineno} [{record.funcName}]" + COLOR_RESET
        return super().format(record)

    def get_color_by_level(self, levelno):
        if levelno == logging.DEBUG:
            return COLOR_CYAN
        elif levelno == logging.INFO:
            return COLOR_GREEN
        elif levelno == logging.WARNING:
            return COLOR_YELLOW
        elif levelno == logging.ERROR:
            return COLOR_RED
        elif levelno == logging.CRITICAL:
            return COLOR_MAGENTA
        else:
            return COLOR_WHITE  # 默认颜色





class Log_Provider:
    def __init__(self, log_file="app.log"):
        self.log_file = log_file
        self.configure_logging(log_file)
        
    def configure_logging(self, log_file="app.log"):
        """
        Args:
            log_file (str, optional): 日志文件名。默认为 "app.log"。
        """
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        log_file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d [%(funcName)s] - %(message)s')
        colored_formatter = ColoredFormatter('%(asctime_color)s - %(levelname_color)s - %(location_color)s - %(message)s')

        file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8') 
        file_handler.setFormatter(log_file_formatter)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(colored_formatter)


        logging.basicConfig(level=logging.INFO,  
                            handlers=[file_handler, stream_handler])
        
    def get_logger(self, name):
        return logging.getLogger(name)
    
log = Log_Provider()

if __name__ == "__main__":
    logger = log.get_logger(__name__)
    logger.debug("这是一个debug级别的日志消息")
    logger.info("这是一个info级别的日志消息")
    logger.warning("这是一个warning级别的日志消息")
    logger.error("这是一个error级别的日志消息")
    logger.critical("这是一个critical级别的日志消息")

    def example_function():
        logger.info("这是在 example_function 函数内部的日志消息")

    example_function()