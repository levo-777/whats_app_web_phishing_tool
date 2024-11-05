import os
import time
import cv2
import requests
import logging
import signal
import sys
from pyzbar import pyzbar
from random import randint
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import LoggedUsers, db
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DATABASE_URI = None
engine = None
session = None
try:
    DATABASE_URI = 'sqlite:///instance/local.db'
    engine = create_engine(DATABASE_URI, echo=True)
    Session = sessionmaker(bind=engine)
except Exception as e:
    print(f"DB or SESSION {e}")

def notify_server_qr_code():
    url = "http://localhost:5000/qr_code_updated"
    try:
        response = requests.post(url)
        if response.status_code == 200:
            print("QR code update notified to Flask app.")
    except Exception as e:
        print(f"Error notifying Flask app: {e}")

def delete_img(destination_path):
    if os.path.exists(destination_path):
        os.remove(destination_path)

def check_img(destination_path):
    if os.path.exists(destination_path):
        return True
    return False

def take_screenshot(browser,path):
    browser.save_screenshot(path)

def get_local_storage_from_browser(browser):
    return browser.execute_script("return localStorage")

def check_if_user_logged_in(browser):
    try:
        local_storage = get_local_storage_from_browser(browser)
        number_string = local_storage.get('me-display-name', '')
        if number_string:
            return True
        return False
    except:
        return False

def get_phone_from_local_storage(local_storage):
    phonenumber = "+"
    for c in local_storage:
        if c == ':':
            break
        phonenumber += c
    return phonenumber

def store_logged_in_user(browser):
    try:
        local_storage = get_local_storage_from_browser(browser)
        phone_number = get_phone_from_local_storage(local_storage.get('last-wid-md',''))
        if phone_number:
            local_storage_json = json.dumps(local_storage)
            session = Session()
            user = LoggedUsers(phone_number=phone_number, local_storage=local_storage_json)
            session.add(user)
            session.commit()
            logging.info(f"Logged user {phone_number} saved to database.")
            session.close()
    except Exception as e:
        logging.error(f"Error storing user in database: {e}")

def crop_qr_code(screenshot, destination_path_screenshot):
    try:
        img = cv2.imread(destination_path_screenshot)
        decoded_objects = pyzbar.decode(img)
        for obj in decoded_objects:
            x, y, w, h = obj.rect
            cropped_img = img[y:y+h, x:x+w]
            qr_code_path = screenshot.replace("screenshot", "qr_code")
            cv2.imwrite(qr_code_path, cropped_img)
            logging.info(f"QR code saved as {qr_code_path}")
    except Exception as e:
        logging.error(f"CATCH ERROR | CROP QR CODE: {e}")

def run_scraper():
    url = "https://web.whatsapp.com"
    static_folder = "static"
    screenshot = "screenshot.png"
    qr_code = "qr_code.png"
    destination_path_screenshot = os.path.join(static_folder, screenshot)
    destination_path_qr_code = os.path.join(static_folder, qr_code)
    browser_options = Options()
    #browser_options.add_argumenoptions=fradless--")
    browser = webdriver.Firefox(options=browser_options)
    browser.get(url)
    time.sleep(3)
    while True:
        if check_if_user_logged_in(browser):
            store_logged_in_user(browser)
            break
        try:
            delete_img(destination_path_screenshot)
            time.sleep(1)

            logging.info("Taking screenshot...")
            take_screenshot(browser,destination_path_screenshot)
            logging.info("Screenshot taken.")
            time.sleep(1)
            
            delete_img(destination_path_qr_code)
            logging.info("Cropping QR code...")
            time.sleep(1)
            crop_qr_code(destination_path_screenshot, destination_path_screenshot)
            logging.info("QR code cropped.")
            if check_img(destination_path_qr_code):
                pass
                #notify_server_qr_code()
            time.sleep(1)
            delete_img(destination_path_screenshot)
            time.sleep(20)  
        except Exception as e:
            logging.error(f"Error in scrapper process: {e}")
            time.sleep(10)

if __name__ == "__main__":
    run_scraper()