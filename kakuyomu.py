import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

WORK_TOC_ELE = ".NewBox_box__45ont.NewBox_padding-px-m__OQCYI"
WORK_TOC_CONTENT_ELE = ".WorkTocAccordion_contents__6nJhY"
WORK_CHAPTER_TITLE_ELE = ".WorkTocSection_title__H2007"
WORK_CHAPTER_LINK_ELE = ".WorkTocSection_link__ocg9K"

HIDE_SVG = "Icons_icon__kQc4i"
SHOW_SVG = "Icons_icon__kQc4i Icons_flip___IDrT"

# for single section
WORK_CHAPTER_BOX = ".NewBox_box__45ont"
WORK_CHAPTER_BOX_TITLE_ELE = ".Typography_lineHeight-1s__3iKaG.Base_inline__bKcc9"
WORK_CHAPTER_BOX_LINK_ELE = ".WorkTocSection_link__ocg9K"


PREFS = {
    "profile.default_content_setting_values": {
        "images": 2
    }
}

driver = None

def create_driver():
    """Create and return a Selenium Chrome driver instance."""
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("prefs", PREFS)
    chrome_options.add_argument("--headless")
    driver_instance = webdriver.Chrome(options=chrome_options)

    return driver_instance

def get_driver():
    """
    Return the global Selenium driver instance.
    """
    global driver
    if driver is None:
        driver = create_driver()

    return driver

def close_driver():
    """
    Close the global Selenium driver.
    """
    global driver
    if driver is not None:
        driver.quit()
        driver = None

def is_hidden(svg_class: str) -> bool:
    """
    Check if the SVG icon indicates that the dropdown is not yet expanded.
    """
    if svg_class == SHOW_SVG:
        return False
    elif svg_class == HIDE_SVG:
        return True
        
    return False

def get_table_of_contents(url: str) -> list:
    """
    Get the table of contents from a Kakuyomu work.
    Returns a list of sections with chapters.
    """
    drv = get_driver()
    drv.get(url)
    time.sleep(5)

    table_of_contents = []
    main_chapters = []
    
    boxes = drv.find_elements(By.CSS_SELECTOR, WORK_TOC_ELE)
    if not boxes:
        boxes = drv.find_elements(By.CSS_SELECTOR, WORK_CHAPTER_BOX)

        for box in boxes:
            try:
                link_elements = box.find_elements(By.CSS_SELECTOR, WORK_CHAPTER_BOX_LINK_ELE)
                title_elements = box.find_elements(By.CSS_SELECTOR, WORK_CHAPTER_BOX_TITLE_ELE)
                for i in range(min(len(title_elements), len(link_elements))):
                    title_text = title_elements[i].text.strip()
                    link_href = link_elements[i].get_attribute("href")
                    if title_text:
                        main_chapters.append({
                            "title": title_text,
                            "link": link_href
                        })
            except NoSuchElementException:
                continue

    if main_chapters:
        table_of_contents.append({
            "section": "Oneshot",
            "chapters": main_chapters
        })

    for box in boxes:
        try:
            drop_down_button = box.find_element(By.TAG_NAME, "button")
        except NoSuchElementException:
            continue

        try:
            svg_element = box.find_element(By.TAG_NAME, "svg")
            button_svg = svg_element.get_attribute("class")
        except NoSuchElementException:
            continue

        try:
            section_name_elem = box.find_element(By.TAG_NAME, "h3")
            section_name = section_name_elem.text.strip()
        except NoSuchElementException:
            continue

        try:
            work_chapter = box.find_element(By.CSS_SELECTOR, WORK_TOC_CONTENT_ELE)
        except NoSuchElementException:
            continue

        if is_hidden(button_svg):
            drop_down_button.click()

        title_elements = work_chapter.find_elements(By.CSS_SELECTOR, WORK_CHAPTER_TITLE_ELE)
        link_elements = work_chapter.find_elements(By.CSS_SELECTOR, WORK_CHAPTER_LINK_ELE)

        section_chapters = []
        for i, title_elem in enumerate(title_elements):
            title_text = title_elem.text.strip()
            link_href = link_elements[i].get_attribute("href") if i < len(link_elements) else None
            section_chapters.append({
                "title": title_text,
                "link": link_href
            })

        if section_chapters:
            table_of_contents.append({
                "section": section_name,
                "chapters": section_chapters
            })

    return table_of_contents

# WIP
def get_work_information(url: str) -> dict:
    """
    Get work information such as the total star count from Kakuyomu.
    """
    drv = get_driver()
    drv.get(url)
    time.sleep(5)

    total_star = None
    hover_elements = drv.find_elements(By.CSS_SELECTOR, ".WorkSubHeader_hover__BX4qY")
    if hover_elements:
        try:
            total_star_parent = hover_elements[0].find_element(
                By.CSS_SELECTOR,
                ".Layout_layout__5aFuw.Layout_items-normal__4mOqD.Layout_justify-normal__zqNe7.Layout_direction-row__boh0Z.Layout_gap-5s__RcxLn"
            )
            total_star_element = total_star_parent.find_element(
                By.CSS_SELECTOR,
                ".LayoutItem_layoutItem__cl360.LayoutItem_alignSelf-normal__dQu_8.LayoutItem_flex-1__hhrWm"
            )
            total_star = total_star_element.text.strip()
        except NoSuchElementException:
            total_star = None

    return {"star": total_star}

#TODO
def get_chapter_content(chapter_url: str) -> dict:
    """
    Get the content of a specific chapter from Kakuyomu.
    Returns a dictionary with the chapter title and its content.
    """
