import logging
from logging.handlers import RotatingFileHandler
import os
import sys
from datetime import datetime
from pathlib import Path

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': r'\033[94m',
        'INFO': r'\033[92m',
        'WARNING': r'\033[93m',
        'ERROR': r'\033[91m',
        'CRITICAL': r'\033[1;91m',
        'RESET': r'\033[0m'
    }
    
    def format(self, record):
        log_message = super().format(record)
        if record.levelname in self.COLORS:
            return f"{self.COLORS[record.levelname]}{log_message}{self.COLORS['RESET']}"
        return log_message

class Logger():
    def __init__(self, name='app', log_dir='logs',) -> None:
        self.name = name
        self.log_dir = log_dir
        
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)
        
        if self.logger.handlers:
            self.logger.handlers.clear()
            
        file_handler = self._create_file_hanlder()
        self.logger.addHandler(file_handler)
        
        console_handler = self._create_console_handler()
        self.logger.addHandler(console_handler)
        
    def _create_file_hanlder(self):
        log_path = Path(self.log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        
        log_file = log_path / f'{self.name}_{timestamp}.log'
        
        file_formatter = self._create_file_formatter()
        
        file_handler = RotatingFileHandler(filename=log_file)
        file_handler.setFormatter(file_formatter)
        
        return file_handler
    
    def _create_console_handler(self):
        console_handler = logging.StreamHandler(sys.stdout)
        consle_formatter = self._create_file_formatter()
        console_handler.setFormatter(consle_formatter)
        return console_handler
    
    def _create_file_formatter(self):
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        return file_formatter
        
    def debug(self, message):
        self.logger.debug(message)
    
    def info(self, message):
        self.logger.info(message)
    
    def warning(self, message):
        self.logger.warning(message)
    
    def error(self, message):
        self.logger.error(message)
    
    def critical(self, message):
        self.logger.critical(message)
    
    def exception(self, message):
        self.logger.exception(message)
