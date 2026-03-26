#!/usr/bin/env python3

import sys
import os
import requests
from jinja2 import Template
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw

BADGE_HTML_TEMPLATE = '''
<html><head>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" crossorigin="anonymous">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="">
  <link href="https://fonts.googleapis.com/css2?family=Ubuntu:ital,wght@0,400;0,500;1,400;1,500&display=swap" rel="stylesheet">
</head>
<body><div id="thm-badge" role="button" tabindex="0" aria-label="user avatar">
  <div class="thm-avatar-outer">
    <div class="thm-avatar" style="background-image: url({{ avatar }});"></div>
  </div>
  <div class="badge-user-details">
    <div class="title-wrapper">
      <span class="user_name">{{ username }}</span>
      <div>
        <i class="fa-solid fa-bolt-lightning rank-icon"></i>
        <span class="rank-title">[0x{{ level_hex }}]</span>
      </div>
    </div>
    <div class="details-wrapper">
      <div class="details-icon-wrapper">
        <i class="fa-solid fa-trophy detail-icons trophy-icon"></i>
        <span class="details-text">{{ totalPoints }}</span>
      </div>
      <div class="details-icon-wrapper">
        <i class="fa-solid fa-fire detail-icons fire-icon"></i>
        <span class="details-text">{{ streak }} days</span>
      </div>
      <div class="details-icon-wrapper">
        <i class="fa-solid fa-award detail-icons award-icon"></i>
        <span class="details-text">{{ badgesNumber }}</span>
      </div>
      <div class="details-icon-wrapper">
        <i class="fa-solid fa-door-closed detail-icons door-closed-icon"></i>
        <span class="details-text">{{ completedRoomsNumber }}</span>
      </div>
    </div>
    <a href="https://tryhackme.com/p/{{ username }}" class="thm-link" target="_blank">tryhackme.com</a>
  </div>
</div>
<style>
  body {
    width: 329px;
    height: 88px;
    margin: 0;
    background: #2e4463;
  }
  #thm-badge {
    width: 327px;
    height: 84px;
    background-image: url('https://tryhackme.com/img/thm_public_badge_bg.svg');
    background-size: cover;
    object-fit: fill;
    display: flex;
    align-items: center;
    gap: 12px;
    user-select: none;
    cursor: pointer;
    border-radius: 12px;
  }
  .thm-avatar-outer {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    margin-right: 0;
    background: linear-gradient(to bottom left, #a3ea2a, #2e4463);
    padding: 2px;
    margin-left: 10px;
  }
  .thm-avatar {
    background-size: cover;
    background-repeat: no-repeat;
    background-position: center center;
    border-radius: 50%;
    box-sizing: content-box;
    background-color: #121212;
    object-fit: cover;
    box-shadow: 0 0 3px 0 #303030;
    width: 60px;
    height: 60px;
    float: left;
  }
  .badge-user-details {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .details-icon-wrapper {
    display: flex;
    gap: 5px;
  }
  .details-wrapper {
    display: flex;
    gap: 8px;
  }
  .title-wrapper {
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .user_name {
    font-family: 'Ubuntu', sans-serif;
    font-style: normal;
    font-weight: 500;
    font-size: 14px;
    line-height: 16px;
    color: #f9f9fb;
    transform: rotate(0.2deg);
    max-width: 135px;
    text-overflow: ellipsis;
    display: block;
    white-space: nowrap;
    overflow: hidden;
  }
  .rank-icon {
    width: 8px;
    height: 10px;
    font-style: normal;
    font-weight: 900;
    font-size: 10px;
    line-height: 10px;
    text-align: center;
    color: #ffbb45;
    transform: rotate(0.2deg);
  }
  .rank-title {
    font-family: Ubuntu, sans-serif;
    font-style: normal;
    font-weight: 500;
    font-size: 12px;
    line-height: 14px;
    color: #ffffff;
    transform: rotate(0.2deg);
  }
  .detail-icons {
    font-weight: 900;
    text-align: center;
    transform: rotate(0.2deg);
  }
  .trophy-icon {
    color: #9ca4b4;
    width: 13px;
    height: 13px;
    font-style: normal;
    font-size: 11px;
    line-height: 11px;
  }
  .fire-icon {
    width: 12px;
    height: 13px;
    font-style: normal;
    font-size: 13px;
    line-height: 13px;
    color: #a3ea2a;
  }
  .award-icon {
    width: 10px;
    height: 13px;
    font-style: normal;
    font-size: 13px;
    line-height: 13px;
    color: #d752ff;
  }
  .door-closed-icon {
    width: 14px;
    height: 12px;
    font-style: normal;
    font-size: 12px;
    line-height: 12px;
    color: #719cf9;
  }
  .details-text {
    font-family: Ubuntu, sans-serif;
    font-style: normal;
    font-weight: 400;
    font-size: 11px;
    line-height: 13px;
    color: #ffffff;
    transform: rotate(0.2deg);
  }
  .thm-link {
    text-decoration: none;
    font-family: Ubuntu, sans-serif;
    font-style: normal;
    font-weight: 400;
    font-size: 11px;
    line-height: 13px;
    margin: 0;
    color: #f9f9fb;
    transform: rotate(0.2deg);
  }
  .thm-link:hover {
    text-decoration: underline;
  }
</style>
</body></html>
'''

def fetch_thm_profile(username):
    url = f"https://tryhackme.com/api/v2/public-profile?username={username}"
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()
    if data.get('status') != 'success':
        raise Exception(f"API error: {data}")
    return data['data']

def render_html(data):
    template = Template(BADGE_HTML_TEMPLATE)
    return template.render(**data)

def html_to_image(html, output_path):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 329, "height": 88})
        page.set_content(html, wait_until="networkidle")
        # Wait for fonts/icons
        page.wait_for_timeout(1000)
        # Screenshot only the badge
        badge = page.query_selector('#thm-badge')
        if badge:
            badge.screenshot(path=output_path)
        else:
            # fallback: screenshot full page
            page.screenshot(path=output_path, clip={"x":0, "y":0, "width":320, "height":88})
        browser.close()

def crop_rounded_corners(image_path, output_path, radius=12):
    img = Image.open(image_path).convert("RGBA")
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), (w, h)], radius=radius, fill=255)
    img.putalpha(mask)
    img.save(output_path)

def main():
    if len(sys.argv) != 3:
        print("Usage: python thm_badge.py <USERNAME> <OUTPUT_PATH>")
        sys.exit(1)
    username = sys.argv[1]
    output_path = sys.argv[2]
    data = fetch_thm_profile(username)
    data['level_hex'] = format(data.get('level', 0), 'x')
    html = render_html(data)
    temp_path = output_path + '.tmp.png'
    html_to_image(html, temp_path)
    crop_rounded_corners(temp_path, output_path, radius=12)
    os.remove(temp_path)
    print(f"Badge image saved to {output_path}")

if __name__ == "__main__":
    main()
