#!/bin/bash
python main.py || (sleep 3600 && python main.py) # 如果command1失败，则等待一小时后再次尝试
