#!/usr/bin/env python3
import pyautogui


scr = pyautogui.screenshot(region=(0,0,1920,1080))

scr.save("sample2.png")
