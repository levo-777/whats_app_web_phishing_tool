import os
import time
import cv2
import requests
import logging
import sys
from pyzbar import pyzbar
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def notify_server_qr_code(url):
    url = "http://localhost:5000/qr_code_updated"
    try:
        response = requests.post(url)
        if response.status_code == 200:
            logging.info("QR code update notified to Flask app.")
    except Exception as e:
        logging.error("Error notifying Flask app: {e}")

def notify_server_user_logged_in(url):
    url = "http://localhost:5000/user_logged_in"
    try:
        response = requests.post(url)
        if response.status_code == 200:
            logging.info("User Log In update notified to Flask app.")
    except Exception as e:
        logging.error("Error notifying Flask app: {e}")

def delete_img(destination_path):
    if os.path.exists(destination_path):
        os.remove(destination_path)

def check_img(destination_path):
    if os.path.exists(destination_path):
        return True
    return False

def refresh(browser):
    browser.refresh()

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

def crop_qr_code(browser,screenshot, destination_path_screenshot):
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
        refresh(browser)
        logging.error(f"CATCH ERROR | CROP QR CODE: {e}")

def check_if_page_needs_reload(browser, path):
    take_screenshot(browser, path)
    try:
        img = cv2.imread(path)
        decoded_objects = pyzbar.decode(path)
        if(len(decoded_objects) > 0):
            return False
        else:
            logging.info("Reloading Page...")
            return True
    except Exception as e:
            logging.error(f"CATCH ERROR | Reload Page {e}")
            return True

def send_qr_code_to_server():
    url = "http://localhost:5000/upload"
    try:
        with open('qr_code.png', "rb") as f:
            image_data = f.read()
            response = requests.post(url,files={"file": ('qr_code.png', image_data)})
            if response.status_code == 200:
                logging.info("Successfully sent QR Code to the Server")
            else:
                logging.info("An error occured | SEND_IMAGE_TO_SERVER | ", response.status_code)
    except Exception as e:
        logging.error(f"CATCH ERROR | SEND IMG TO SERVER {e}")

def run_scraper():
    url = "https://web.whatsapp.com"
    screenshot = "screenshot.png"
    qr_code = "qr_code.png"
    browser_options = Options()
    browser = webdriver.Firefox(options=browser_options)
    browser.get(url)
    time.sleep(3)
    while True:
        if check_if_user_logged_in(browser):
            local_storage = get_local_storage_from_browser(browser)
            phone_number = "+" + local_storage.get('last-wid-md', '').split(":")[0]
            logging.info(f"User LogIn #{phone_number}")
            os.system("python3 scraper.py")
            break
        try:
            delete_img(screenshot)
            time.sleep(1)

            logging.info("Taking screenshot...")
            take_screenshot(browser,screenshot)
            logging.info("Screenshot taken.")
            time.sleep(1)
            
            delete_img(qr_code)
            logging.info("Cropping QR code...")
            crop_qr_code(browser, screenshot, screenshot)
            logging.info("QR code cropped.")
            if check_img(qr_code):
                send_qr_code_to_server()
                notify_server_qr_code()
            time.sleep(1)
            delete_img(screenshot)
            time.sleep(15)  
        except Exception as e:
            logging.error(f"Error in scrapper process: {e}")
            time.sleep(10)

if __name__ == "__main__":
    run_scraper()