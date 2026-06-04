#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scheduler - Chạy fetch_meter_data.py hằng ngày lúc 23:00
Chạy: python3 scheduler.py
"""

import schedule
import time
import subprocess
import os
from datetime import datetime

# Thời gian chạy (HH:MM định dạng 24h)
RUN_TIME = "23:00"

# Đường dẫn tới script fetch_meter_data.py
SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "fetch_meter_data.py")

def run_fetch():
    """Chạy fetch_meter_data.py"""
    print()
    print("=" * 80)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - BẮT ĐẦU LẤY DỮ LIỆU")
    print("=" * 80)
    
    try:
        result = subprocess.run([
            "python3",
            SCRIPT_PATH
        ], capture_output=True, text=True, timeout=300)
        
        print(result.stdout)
        
        if result.returncode == 0:
            print()
            print("✅ HOÀN TẤT THÀNH CÔNG")
            print(f"⏰ Lần tới: {schedule.next_run().strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print()
            print("❌ LỖI:")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout - script chạy quá lâu")
    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")

def main():
    print()
    print("=" * 80)
    print("🔋 SCHEDULER - LẤY DỮ LIỆU CÔNG TƠ HẰNG NGÀY")
    print("=" * 80)
    print(f"Sẽ chạy lúc: {RUN_TIME} hàng ngày")
    print(f"Script: {SCRIPT_PATH}")
    print()
    print("Nhấn Ctrl+C để dừng")
    print("=" * 80)
    print()
    
    # Schedule
    schedule.every().day.at(RUN_TIME).do(run_fetch)
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print()
        print("=" * 80)
        print("⏹️  Scheduler dừng")
        print("=" * 80)
