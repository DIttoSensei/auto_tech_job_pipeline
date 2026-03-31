import os
import random
import subprocess
import time
import re
from dotenv import load_dotenv
import requests
from prompt import prompt1, prompt2, prompt3, prompt4
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

load_dotenv()

API_URL = "https://router.huggingface.co/v1/chat/completions"
headers = {"Authorization": f"Bearer {os.environ['HF_TOKEN']}"}

JOB_URL = "https://himalayas.app/companies/nagarro/jobs/managing-consultant-sap-hana-database-m-f-d-5352684949"
SESSION_FILE = "himalayas_session.json"
CV_FILE = "cv.txt"
CV_DOCX = "richard-andrew-cv.docx"

def get_cv_text():
    if not os.path.exists(CV_FILE):
        print("cv.txt not found, running cv_extractor.py...")
        subprocess.run(["python", "cv_extractor.py"])
        time.sleep(3)
    if not os.path.exists(CV_FILE):
        print("CV extraction failed. Check cv_extractor.py")
        exit()
    with open(CV_FILE, "r", encoding="utf-8") as f:
        return f.read()

def get_browser_page(playwright):
    browser = playwright.chromium.launch(
        headless=False,
        args=[
            "--dns-prefetch-disable",
            "--no-sandbox",
            "--disable-blink-features=AutomationControlled",
        ]
    )
    context = browser.new_context(
        storage_state=SESSION_FILE,
        ignore_https_errors=True,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        viewport={"width": 1366, "height": 768},
        locale="en-US",
        timezone_id="America/New_York",
        java_script_enabled=True,
        permissions=["geolocation"],
        extra_http_headers={
            "Accept-Language": "en-US,en;q=0.9",
        }
    )
    page = context.new_page()
    Stealth().apply_stealth_sync(page)
    return browser, page

def is_logged_in(page):
    try:
        return not page.get_by_text("Log in").is_visible(timeout=3000)
    except:
        return True

def ask_llama(prompt):
    response = requests.post(API_URL, headers=headers, json={
        "messages": [{"role": "user", "content": prompt}],
        "model": "meta-llama/Llama-3.1-8B-Instruct:novita"
    })
    return response.json()["choices"][0]["message"]["content"].strip()

def fill_form(page, cv_text, step_num):
    page_text = page.inner_text("body")

    # Ask AI to list all form fields
    fields_raw = ask_llama(prompt4.format(page_text=page_text))
    fields = [f.strip() for f in fields_raw.strip().split("\n") if f.strip()]
    print(f"Fields found: {fields}")

    # Handle file upload separately first
    try:
        file_input = page.locator("input[type='file']").first
        if file_input.is_visible():
            file_input.set_input_files(CV_DOCX)
            print("CV uploaded successfully")
            page.wait_for_timeout(2000)
            page.screenshot(path=f"logs/step{step_num}_upload.png")
    except:
        print("No file upload found or already uploaded")

    # Get all visible text inputs and textareas
    inputs = page.locator("input[type='text'], input[type='email'], input[type='tel'], textarea").all()
    print(f"Input elements found: {len(inputs)}")

    for i, input_el in enumerate(inputs):
        try:
            # Get placeholder or nearby label text
            placeholder = input_el.get_attribute("placeholder") or ""
            input_id = input_el.get_attribute("id") or ""
            name_attr = input_el.get_attribute("name") or ""

            # Use whatever identifier we can find
            field_hint = placeholder or input_id or name_attr or f"field {i+1}"
            print(f"Filling: {field_hint}")

            # Ask AI what to fill
            answer = ask_llama(prompt2.format(cv_text=cv_text, field_label=field_hint))
            print(f"Answer: {answer}")

            input_el.scroll_into_view_if_needed()
            input_el.click()
            page.wait_for_timeout(random.randint(300, 800))
            input_el.fill(answer)
            page.wait_for_timeout(random.randint(500, 1000))

            # Screenshot after each field
            page.screenshot(path=f"logs/step{step_num}_field_{i}.png")

        except Exception as e:
            print(f"Could not fill input {i}: {e}")

    return page

def apply_to_job(url):
    cv_text = get_cv_text()

    with sync_playwright() as p:
        browser, page = get_browser_page(p)
        page.goto(url, timeout=60000)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(3000)

        if not is_logged_in(page):
            print("Session expired. Run save_session.py to log in again.")
            browser.close()
            exit()

        # Step 1 — Click Apply now (hardcoded, always same on Himalayas)
        print("Clicking Apply now...")
        apply_btn = page.locator("button:has-text('Apply now')").first
        apply_btn.wait_for(state="visible", timeout=10000)
        page.wait_for_timeout(random.randint(1000, 3000))
        apply_btn.click()
        page.wait_for_timeout(3000)
        page.screenshot(path="logs/step1_apply_clicked.png")
        print("Screenshot saved: logs/step1_apply_clicked.png")

        # Step 2 — Click I'm ready to apply (hardcoded, always same on Himalayas)
        print("Clicking I'm ready to apply...")
        ready_btn = page.locator("a:has-text('ready to apply')").first
        ready_btn.wait_for(state="visible", timeout=10000)
        page.wait_for_timeout(random.randint(1000, 3000))

        with page.context.expect_page() as new_page_info:
            ready_btn.click()

        # Step 3 — New tab opens, AI takes over from here
        new_tab = new_page_info.value
        print("New tab opened, waiting for it to load...")

        try:
            new_tab.wait_for_load_state("domcontentloaded", timeout=20000)
        except:
            pass

        new_tab.wait_for_timeout(10000)
        new_tab.screenshot(path="logs/step2_new_tab.png")
        print("Screenshot saved: logs/step2_new_tab.png")

        # AI decision loop starts here on the new tab
        new_page_text = new_tab.inner_text("body")
        decision = ask_llama(prompt1 + new_page_text)
        print(f"AI Decision on new page: {decision}")

        step_num = 3
        while True:
            if "fill form" in decision.lower():
                print(f"Filling form on step {step_num}...")
                new_tab = fill_form(new_tab, cv_text, step_num)
                new_tab.screenshot(path=f"logs/step{step_num}_filled.png")

                # Check what is on page after filling
                new_page_text = new_tab.inner_text("body")
                decision = ask_llama(prompt1 + new_page_text)
                print(f"AI Decision after fill: {decision}")
                step_num += 1

            elif "click button" in decision.lower():
                btn_match = re.search(r'click button \(?(.+?)\)?$', decision, re.IGNORECASE)
                btn_text = btn_match.group(1).strip() if btn_match else "Next"
                print(f"Clicking button: {btn_text}...")
                try:
                    btn = new_tab.locator(f"button:has-text('{btn_text}')").first
                    btn.wait_for(state="visible", timeout=5000)
                    new_tab.wait_for_timeout(random.randint(500, 1500))
                    btn.click()
                    new_tab.wait_for_timeout(5000)
                    new_tab.screenshot(path=f"logs/step{step_num}_clicked.png")
                    new_page_text = new_tab.inner_text("body")
                    decision = ask_llama(prompt1 + new_page_text)
                    print(f"AI Decision after click: {decision}")
                    step_num += 1
                except:
                    print("Button not found or already done.")
                    break
            else:
                print("AI says done or unknown state. Stopping.")
                break

        browser.close()

# --- MAIN ---
print("Starting application process...")
apply_to_job(JOB_URL)