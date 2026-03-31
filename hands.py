from playwright.sync_api import sync_playwright

def get_page_text(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_load_state("networkidle")
        
        text = page.inner_text("body")
        
        browser.close()
        return text

text = get_page_text("https://himalayas.app/companies/crowdstrike/jobs/data-engineer-go-to-market")
print(text[:1000])