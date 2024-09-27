"""This module contains logic to allow a superuser to revert data in Shephard
back to a specific snapshot.

See `README.md` file in this directory for instructions.
"""

import json
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.select import Select


def fill_text_field_by_id(element_id, value, driver) -> None:
    """Fill field value based on element indentifier.

    Arguments:
    element_id -- UI element identifier
    value -- value contained
    driver -- webdriver browser instance
    """
    field = driver.find_element(By.ID, element_id)
    field.clear()
    field.send_keys(value)


def main():
    shepherd_url = sys.argv[1]
    json_file = sys.argv[2]
    profile_path = sys.argv[3]
    partner = sys.argv[4]
    options = Options()
    options.set_preference("profile", profile_path)

    driver = webdriver.Firefox(options=options)

    driver.get(f"{shepherd_url}/admin/")

    with open(json_file, "r") as f:
        settings = json.load(f)["adm_advertisers"]
        for advertiser in settings:
            # get add button
            add_buttons = driver.find_elements(By.CLASS_NAME, "addlink")
            for elem in add_buttons:
                adv_add_url = f"{shepherd_url}/admin/contile/advertiser/add/"
                if elem.get_attribute("href") == adv_add_url:
                    elem.click()
                    break

            # Add Advertiser Page
            fill_text_field_by_id("id_name", advertiser, driver)
            partner_field = Select(driver.find_element(By.ID, "id_partner"))
            partner_field.select_by_visible_text(partner)

            i = 0
            for geo in settings[advertiser]:
                urls_info = settings[advertiser][geo]
                for url_info in urls_info:
                    for path in url_info["paths"]:
                        geo_field = Select(driver.find_element(By.ID, f"id_ad_urls-{i}-geo"))
                        geo_field.select_by_value(geo)

                        fill_text_field_by_id(f"id_ad_urls-{i}-domain", url_info["host"], driver)
                        fill_text_field_by_id(f"id_ad_urls-{i}-path", path["value"], driver)

                        if path["matching"] == "prefix":
                            matching_select = driver.find_element(By.ID, f"id_ad_urls-{i}-matching_1")
                            matching_select.click()

                        add_url_button = driver.find_element(By.LINK_TEXT, "Add another Advertiser url")
                        add_url_button.click()

                        i += 1

            inputs = driver.find_elements(By.CSS_SELECTOR, "input")
            for input in inputs:
                type_attribute = input.get_attribute("type")
                value_attribute = input.get_attribute("value")
                if type_attribute == "submit" and value_attribute == "Save":
                    input.click()
                    break


if __name__ == "__main__":
    main()
