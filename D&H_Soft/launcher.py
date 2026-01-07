import os
import subprocess
import sys
import time

def run_command(command, description):
    print(f"\n🔹 {description}...")
    try:
        subprocess.check_call(command, shell=True)
        print(f"✅ {description} সফলভাবে সম্পন্ন হয়েছে।")
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} ব্যর্থ হয়েছে: {e}")
        sys.exit(1)

def main():
    print("🚀 Django Launcher শুরু হচ্ছে...")

    # Step 1: Create DB if not exists
    run_command("python manage.py create_db", "ডাটাবেজ তৈরি/চেক")

    # Step 2: Run migrations
    run_command("python manage.py migrate", "মাইগ্রেশন")

    # Step 3: Run server
    print("\n🌐 সার্ভার চালু হচ্ছে...")
    time.sleep(1)
    subprocess.call("python manage.py runserver", shell=True)

if __name__ == "__main__":
    main()
