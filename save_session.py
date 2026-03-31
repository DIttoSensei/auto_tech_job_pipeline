from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    
    page.goto("https://himalayas.app/login")
    page.wait_for_load_state("networkidle")
    
    print("Log in manually in the browser window...")
    print("Press ENTER here once you are fully logged in")
    input()
    
    context.storage_state(path="himalayas_session.json")
    print("Session saved to himalayas_session.json")
    browser.close()