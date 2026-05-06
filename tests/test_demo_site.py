import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.fixture
def driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()


@pytest.fixture
def user_data():
    return {
        "username": f"amir_test_{int(time.time())}",
        "password": "123456"
    }


def test_register_new_user(driver, user_data):
    driver.get("https://parabank.parasoft.com/parabank/register.htm")

    driver.find_element(By.ID, "customer.firstName").send_keys("Amir")
    driver.find_element(By.ID, "customer.lastName").send_keys("Schwartz")
    driver.find_element(By.ID, "customer.address.street").send_keys("Herzel 10")
    driver.find_element(By.ID, "customer.address.city").send_keys("Raanana")
    driver.find_element(By.ID, "customer.address.state").send_keys("Israel")
    driver.find_element(By.ID, "customer.address.zipCode").send_keys("12345")
    driver.find_element(By.ID, "customer.phoneNumber").send_keys("0501234567")
    driver.find_element(By.ID, "customer.ssn").send_keys("123456789")

    driver.find_element(By.ID, "customer.username").send_keys(user_data["username"])
    driver.find_element(By.ID, "customer.password").send_keys(user_data["password"])
    driver.find_element(By.ID, "repeatedPassword").send_keys(user_data["password"])

    driver.find_element(By.CSS_SELECTOR, "input[value='Register']").click()

    assert "Your account was created successfully" in driver.page_source


def test_login(driver, user_data):
    driver.get("https://parabank.parasoft.com/parabank/index.htm")

    wait = WebDriverWait(driver, 10)

    wait.until(
        EC.visibility_of_element_located((By.NAME, "username"))
    ).send_keys(user_data["username"])

    driver.find_element(By.NAME, "password").send_keys(user_data["password"])

    driver.find_element(By.CSS_SELECTOR, "input[value='Log In']").click()

    wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, "//*[contains(text(),'Accounts Overview')]")
        )
    )

    assert "Accounts Overview" in driver.page_source