import sys
import traceback
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ERROR_LOG = os.path.join(BASE_DIR, "error.log")

def global_exception_handler(exc_type, exc_value, exc_traceback):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tb_lines = traceback.format_tb(exc_traceback)
    
    with open(ERROR_LOG, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} | {exc_type.__name__}: {exc_value}\n")
        f.write(''.join(tb_lines))
        f.write("\n" + "-"*50 + "\n")
    
    print(f"[EXCEPTION] {exc_type.__name__}: {exc_value}")

sys.excepthook = global_exception_handler
