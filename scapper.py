import asyncio
import os
import cv2
import time
import signal
import sys
import logging
from pyppeteer import launch
import pyzbar.pyzbar as pyzbar
from multiprocessing import Process

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def delete_img(destination_path):
    if os.path.exists(destination_path):
        os.remove(destination_path)

async def take_screenshot(url, path):
    browser = await launch({"headless": True})
    page = await browser.newPage()
    await page.setUserAgent("Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0")
    await page.goto(url)
    await asyncio.sleep(5)
    await page.screenshot({'path': path, 'fullPage': True})
    await browser.close()

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

def run_scrapper():
    url = "https://web.whatsapp.com"
    static_folder = "static"
    screenshot = "screenshot.png"
    qr_code = "qr_code.png"
    destination_path_screenshot = os.path.join(static_folder, screenshot)
    destination_path_qr_code = os.path.join(static_folder, qr_code)

    while True:
        try:
            delete_img(destination_path_screenshot)
            time.sleep(1)
            #delete_img(destination_path_qr_code)
            #time.sleep(1)

            logging.info("Taking screenshot...")
            asyncio.run(take_screenshot(url, destination_path_screenshot))
            logging.info("Screenshot taken.")
            time.sleep(1)
            
            delete_img(destination_path_qr_code)
            logging.info("Cropping QR code...")
            crop_qr_code(destination_path_screenshot, destination_path_screenshot)
            logging.info("QR code cropped.")
            time.sleep(1)

            delete_img(destination_path_screenshot)
            time.sleep(20)  
        except Exception as e:
            logging.error(f"Error in scrapper process: {e}")
            time.sleep(10)

def signal_handler(sig, frame):
    logging.info("Terminating scrapper...")
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    run_scrapper()
