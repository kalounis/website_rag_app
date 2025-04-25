import logging
from time import sleep

import streamlit as st
from bs4 import BeautifulSoup
from playwright.sync_api import TimeoutError, sync_playwright

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class WebCrawler:
    def __init__(
        self,
        base_url=st.secrets["BASE_URL"],
        cookie_class=".CybotCookiebotDialogBodyButton",
    ) -> None:
        self.base_url = base_url
        self.url = f"{self.base_url}/help"
        self.cookie_class = cookie_class

    def open_page(self, url: str):
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url)
        self.deny_cookies(page, self.cookie_class)
        return browser, page

    def deny_cookies(self, page, web_class: str) -> None:
        try:
            page.wait_for_selector(web_class, timeout=5000)
            cookie_button = page.locator(web_class).first
            cookie_button.click()
            sleep(2)
        except TimeoutError:
            logger.info("No cookie banner or already denied")

    def get_tabs(self, page):
        page.wait_for_timeout(2000)
        page.wait_for_selector(".tab")
        tabs = page.locator(".tab")
        tab_count = tabs.count()
        return tabs, tab_count

    def retrieve_page_content(self, new_page):
        soup = BeautifulSoup(new_page.content(), "html.parser")
        return soup.get_text(separator="\n", strip=True)

    def retrieve_links_content(self, answer_block, browser, section, question_text):
        link_elements = answer_block.locator("a")
        links = []

        for j in range(link_elements.count()):
            href = self._get_full_url(link_elements.nth(j))
            if href:
                page_data = self._fetch_link_data(browser, href, section, question_text)
                if page_data:
                    links.append(page_data)

        return links

    def _get_full_url(self, link_element) -> str:
        href = link_element.get_attribute("href")
        if href and href.startswith("/"):
            return f"{self.base_url}{href}"
        return href

    def _fetch_link_data(
        self, browser, href: str, section: str, question: str
    ) -> dict | None:
        new_page = browser.new_page()
        try:
            new_page.goto(href)
            self.deny_cookies(new_page, self.cookie_class)
            sleep(2)
            page_text = self.retrieve_page_content(new_page)

            return {
                "url": href,
                "cleaned_content": page_text,
                "section": section,
                "related_question": question,
            }

        except Exception as e:
            logger.warning(f"Error opened link : {href} - {e}")
            return None
        finally:
            new_page.close()

    def _click_tab_and_get_text(self, page, tabs, index):
        current_tab = tabs.nth(index)
        tab_text = current_tab.inner_text()
        current_tab.click()
        sleep(2)
        return tab_text

    def _get_questions(self, page):
        page.wait_for_selector(".accordian-header-font")
        return page.locator(".accordian-header-font")

    def _extract_qa(self, page, index):
        questions = page.locator(".accordian-header-font")
        question_elem = questions.nth(index)
        question_text = question_elem.inner_text()

        question_elem.click()
        sleep(1)

        answer_block = question_elem.locator("~ .accordian-body-font")
        answer_text = ""

        try:
            answer_block.wait_for(state="visible", timeout=10000)
            answer_text = answer_block.inner_text().strip()
        except Exception as e:
            logger.warning(f"Retrieve response error {index + 1} : {e}")

        return question_text, answer_text, answer_block

    def extract_faq_data(self):
        rag_data = []
        browser, page = self.open_page(self.url)

        tabs, tab_count = self.get_tabs(page)

        for t in range(tab_count):
            tab_text = self._click_tab_and_get_text(page, tabs, t)
            questions = self._get_questions(page)

            for i in range(questions.count()):
                question_text, answer_text, answer_block = self._extract_qa(page, i)
                links = self.retrieve_links_content(
                    answer_block, browser, tab_text, question_text
                )

                rag_data.append(
                    {
                        "section": tab_text,
                        "question": question_text,
                        "answer": answer_text,
                        "links": links,
                    }
                )

        browser.close()
        return rag_data
