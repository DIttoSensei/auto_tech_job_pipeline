from playwright.sync_api import sync_playwright

def scrape_page(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_load_state("networkidle")
        text = page.inner_text("body")
        browser.close()
    
    with open("page_text.txt", "w", encoding="utf-8") as f:
        f.write(text)
    
    print("Page scraped and saved to page_text.txt")

scrape_page("https://himalayas.app/companies/nagarro/jobs/managing-consultant-sap-hana-database-m-f-d-5352684949")