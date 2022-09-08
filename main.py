from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from re import findall

# urllib
# selenium

class AnyEc:
    def __init__(self, *args):
        self.ecs = args
    def __call__(self, driver):
        for fn in self.ecs:
            try:
                if fn(driver): return True
            except:
                pass


def find_in_feel_way(keyword):
    keyword = "".join(findall("\d+", keyword))

    driver = webdriver.Chrome(executable_path="./chromedriver")
    prefix = "https://www.feelway.com/tobe/page/search/result.php?searchTerm="
    postfix = "&sort=update_dt&currentPage=1"

    uri = prefix + keyword + postfix

    driver.get(uri)

    wait_driver = WebDriverWait(driver, 10)

    # 키워드 서칭이 종료될 때까지 대기한다.
    wait_driver.until(
        AnyEc(
            EC.text_to_be_present_in_element((By.ID, "wrongSearchKeyword"), keyword),
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#findTotalProductResultAll > ul"))
        )
    )

    bs_html = BeautifulSoup(driver.page_source, "html.parser")

    is_wrong_search_keyword = len(bs_html.select_one("#wrongSearchKeyword").get_text("value")) > 0

    # 해당 키워드는 존재하지 않는 물품인 경우,
    if is_wrong_search_keyword:
        driver.close()
        return []

    # 키워드에 대한 품목이 나열된 경우, 중고 상품으로 전환한다.
    driver.find_element_by_css_selector(
        f"#findTotalProductResult > div.findTotalProduct__result__filter > div:nth-child(3) > div > label:nth-child(3) > input[type=radio]"
    ).click()

    # 중고 상품의 필터링이 종료될 때까지 대기한다.
    wait_driver.until(
        AnyEc(
            EC.text_to_be_present_in_element((By.ID, "detailFilterMessage"), "선택하신 옵션(필터)에 대한 검색결과가 없습니다."),
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#findTotalProductResultAll > ul > li:nth-child(1)"))
        )
    )

    bs_html = BeautifulSoup(driver.page_source, "html.parser")

    price_tags = bs_html.select("#findTotalProductResultAll > ul > li > a.price > span > span.no")
    prices = list(map(lambda price_tag: price_tag.text, price_tags))

    driver.close()

    return prices


if __name__ == '__main__':
    print(find_in_feel_way("RM4812205598"))