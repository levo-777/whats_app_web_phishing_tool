import asyncio
import numpy as np
import os
import cv2
import shutil
import requests
import pyzbar.pyzbar as pyzbar
from pyppeteer import launch

async def delete_img(img_name):
    if os.path.exists(img_name):
        os.remove(img_name)

async def take_screenshot(url, screenshot_img):
    browser = await launch({"headless": True})
    page = await browser.newPage()
    await page.setUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")

    await page.goto(url)
    await asyncio.sleep(5)
    await page.screenshot({'path': screenshot_img, 'fullPage': True})
    await browser.close()

async def get_qr_code(screenshot_img):
    await asyncio.sleep(1)
    try:
        img = cv2.imread(screenshot_img)
        decoded_objects = pyzbar.decode(img)
        for obj in decoded_objects:
            x, y, w, h = obj.rect
            cropped_img = img[y:y+h, x:x+w]
            qr_code_path = screenshot_img.replace("screenshot", "qr_code")
            cv2.imwrite(qr_code_path, cropped_img)
            print(f"QR code saved as {qr_code_path}")
    except Exception as e:
        print(f"CATCH ERROR | GET QR CODE: {e}")

async def replace_qr_code(qr_code_img):
    static_folder = "static"
    destination_path = os.path.join(static_folder, "qr_code.png")

    if os.path.exists(destination_path):
        os.remove(destination_path)

    shutil.copy(qr_code_img, destination_path)
    print(f"Replaced QR code in static folder: {destination_path}")

    url = "http://localhost:5000/qr_code_updated"
    try:
        response = requests.post(url)
        if response.status_code == 200:
            print("QR code update notified to Flask app.")
        else:
            print("Failed to notify Flask app.")
    except Exception as e:
        print(f"Error notifying Flask app: {e}")


async def main():
    url = "https://web.whatsapp.com"
    screenshot_img = "screenshot.png"
    qr_code_img = "qr_code.png"

    await delete_img(screenshot_img)
    await delete_img(qr_code_img)
    await take_screenshot(url, screenshot_img)
    await get_qr_code(screenshot_img)
    await replace_qr_code(qr_code_img)
    await delete_img(screenshot_img)
    await delete_img(qr_code_img)

if __name__ == '__main__':
    asyncio.run(main())
