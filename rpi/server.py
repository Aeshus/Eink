#!/usr/bin/python3
# -*- coding:utf-8 -*-
import pprint
import sys
import os
import logging
import time
import traceback
import io
import socket

from flask import Flask, request
from PIL import Image,ImageDraw,ImageFont
from waveshare_epd import epd7in5_V2

# https://forums.raspberrypi.com/viewtopic.php?t=79936
gw = os.popen('ip -4 route show default').read().split()
s  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect((gw[2], 0))
ipaddr = s.getsockname()[0]

HOST=ipaddr
# HOST="localhost"
PORT="8000"

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

logging.info("Initializing EPD")
epd = epd7in5_V2.EPD()
epd.init()

font18 = ImageFont.truetype("./Font.ttc", 18)

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return 'No image uploaded', 400

    file = request.files['image']

    if file.filename == '':
        return 'No selected image', 400

    if file:
        try:
            img = Image.open(file)

            img = img.resize((800, 480))  # Resize to 800x600

            img = img.convert('L') # monochrome
            
            img.save('/tmp/uploaded_image.bmp', 'BMP')  # Save locally

            renderImage(img)
            
            return 'Image uploaded and resized successfully!'
        except Exception as e:
            return f'Error processing image: {e}', 500

    return 'Something went wrong', 500

@app.route('/write', methods=['POST'])
def write():
    if 'text' not in request.form:
        return 'No text uploaded', 400

    text = request.form['text']

    if text:
        try:
            renderText(text)

            return 'Displaying image'
        except Exception as e:
            return f'Error processing text: {e}', 500

    return 'Something went wrong', 500


def renderImage(img):
    print("[Rendering image]");

    logging.info("Clearing the screen")
    epd.Clear()

    logging.info("Drawing image")
    Himage = Image.new('1', (epd.width, epd.height), 255) # Create all white image

    logging.info("Rendering image")
    epd.display(epd.getbuffer(Himage)) # Render image

    logging.info("Entering sleep...")
    epd.sleep()

def renderText(text):
    print(f"[Rendering \"{text}\"]")

    logging.info("Clearing the screen")
    epd.Clear()

    logging.info("Drawing image")
    Himage = Image.new('1', (epd.width, epd.height), 255) # Create all white image
    draw = ImageDraw.Draw(Himage)
    draw.text((18, 18), text, font = font18, fill = 0);

    logging.info("Rendering image")
    epd.display(epd.getbuffer(Himage)) # Render image

    logging.info("Entering sleep...")
    epd.sleep()

if __name__ == '__main__':
    renderText(f"IP: {HOST}")
    app.run(host=HOST, port=PORT, debug=False)

