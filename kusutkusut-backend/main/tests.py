from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import os
import tempfile
import shutil


class FootballNewsFrontPageTest(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options: Options = Options()
        cls.user_data_dir = tempfile.mkdtemp()

        if os.getenv("CI", "false") == "true":
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")

        options.add_argument(f"--user-data-dir={cls.user_data_dir}")
        options.add_argument("--no-sandbox")
        options.browser_version = "139"

        # This example uses Google Chrome. You can use different browser such as Microsoft Edge or Firefox by changing the webdriver instance.
        cls.selenium: WebDriver = webdriver.Chrome(
            options=options, service=ChromeService(ChromeDriverManager().install())
        )

        cls.selenium.implicitly_wait(5)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()

        if os.path.exists(cls.user_data_dir):
            shutil.rmtree(cls.user_data_dir, ignore_errors=True)

        super().tearDownClass()

    def setUp(self):
        # By default, point the base URL to the locally running project when DJANGO_BASE_URL is unset
        # The DJANGO_BASE_URL can be used to point to the project running on a different server, e.g., deployment server
        self.base_url = os.getenv("DJANGO_BASE_URL", self.live_server_url)
        print(f"Base URL for tests: {self.base_url}")

    def tearDown(self):
        return super().tearDown()

    def test_h1_should_contain_football_news(self) -> None:
        self.selenium.get(self.base_url)

        h1 = self.selenium.find_element(By.TAG_NAME, "h1")

        self.assertIn("Football News", h1.text)
