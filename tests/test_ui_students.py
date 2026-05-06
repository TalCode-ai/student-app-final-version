import pytest
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException


@pytest.fixture
def driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()


# ---------- Helpers ----------

def wait_for_table(driver):
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "tbody tr"))
    )


def click_button(driver, locator):
    button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(locator)
    )
    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        button
    )
    button.click()


def accept_alert(driver):
    alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
    text = alert.text
    alert.accept()
    return text


def row_contains_text(driver, text):
    try:
        rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
        return any(text in row.text for row in rows)
    except StaleElementReferenceException:
        return False


def find_student_id(driver, name):
    try:
        rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
        for row in rows:
            if name in row.text:
                return row.find_elements(By.TAG_NAME, "td")[0].text
    except StaleElementReferenceException:
        return None
    return None


def delete_student_by_name(driver, name):
    student_id = find_student_id(driver, name)
    if student_id:
        id_box = driver.find_element(By.ID, "idBox")
        id_box.clear()
        id_box.send_keys(student_id)

        click_button(driver, (By.ID, "btDelete"))
        accept_alert(driver)


# ---------- Tests ----------

def test_open_students_page(driver):
    driver.get("http://127.0.0.1:5000")
    wait_for_table(driver)
    assert "127.0.0.1" in driver.current_url


def test_students_table_is_displayed(driver):
    driver.get("http://127.0.0.1:5000")

    table = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.TAG_NAME, "table"))
    )
    assert table.is_displayed()


def test_students_table_has_data(driver):
    driver.get("http://127.0.0.1:5000")
    wait_for_table(driver)

    rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
    assert len(rows) >= 1


def test_add_student_ui(driver):
    driver.get("http://127.0.0.1:5000")

    driver.find_element(By.ID, "nameBox").send_keys("QA Test")
    driver.find_element(By.ID, "ageBox").send_keys("25")

    click_button(driver, (By.ID, "btAdd"))

    WebDriverWait(driver, 10).until(
        lambda d: row_contains_text(d, "QA Test")
    )

    assert row_contains_text(driver, "QA Test")

    delete_student_by_name(driver, "QA Test")


def test_delete_qa_test(driver):
    driver.get("http://127.0.0.1:5000")
    wait_for_table(driver)

    driver.find_element(By.ID, "nameBox").send_keys("QA Delete Test")
    driver.find_element(By.ID, "ageBox").send_keys("25")

    click_button(driver, (By.ID, "btAdd"))

    WebDriverWait(driver, 10).until(
        lambda d: row_contains_text(d, "QA Delete Test")
    )

    student_id = find_student_id(driver, "QA Delete Test")
    assert student_id is not None

    id_box = driver.find_element(By.ID, "idBox")
    id_box.clear()
    id_box.send_keys(student_id)

    click_button(driver, (By.ID, "btDelete"))
    accept_alert(driver)

    WebDriverWait(driver, 10).until(
        lambda d: not row_contains_text(d, "QA Delete Test")
    )

    assert not row_contains_text(driver, "QA Delete Test")


def test_update_student_age(driver):
    driver.get("http://127.0.0.1:5000")
    wait_for_table(driver)

    driver.find_element(By.ID, "nameBox").send_keys("Temp User")
    driver.find_element(By.ID, "ageBox").send_keys("20")

    click_button(driver, (By.ID, "btAdd"))

    WebDriverWait(driver, 10).until(
        lambda d: row_contains_text(d, "Temp User")
    )

    student_id = find_student_id(driver, "Temp User")
    assert student_id is not None

    id_box = driver.find_element(By.ID, "idBox")
    id_box.clear()
    id_box.send_keys(student_id)

    name_input = driver.find_element(By.ID, "nameBox")
    name_input.clear()
    name_input.send_keys("Temp User")

    age_input = driver.find_element(By.ID, "ageBox")
    age_input.clear()
    age_input.send_keys("55")

    click_button(driver, (By.ID, "btUpdate"))
    accept_alert(driver)

    WebDriverWait(driver, 10).until(
        lambda d: row_contains_text(d, "Temp User") and "55" in d.page_source
    )

    assert "55" in driver.page_source

    delete_student_by_name(driver, "Temp User")


def test_add_invalid_age_qa_test(driver):
    driver.get("http://127.0.0.1:5000")
    wait_for_table(driver)

    driver.find_element(By.ID, "nameBox").send_keys("Illegal age")
    driver.find_element(By.ID, "ageBox").send_keys("15")

    click_button(driver, (By.ID, "btAdd"))

    alert_text = accept_alert(driver)
    assert "age" in alert_text.lower()


def test_add_empty_name(driver):
    driver.get("http://127.0.0.1:5000")

    driver.find_element(By.ID, "ageBox").send_keys("25")

    click_button(driver, (By.ID, "btAdd"))

    alert_text = accept_alert(driver)
    assert "name" in alert_text.lower()


def test_add_text_age(driver):
    driver.get("http://127.0.0.1:5000")

    driver.find_element(By.ID, "nameBox").send_keys("Bad Age")
    driver.find_element(By.ID, "ageBox").send_keys("abc")

    click_button(driver, (By.ID, "btAdd"))

    alert_text = accept_alert(driver)
    assert "age" in alert_text.lower()