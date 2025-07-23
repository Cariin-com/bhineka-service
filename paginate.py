from bs4 import BeautifulSoup

def get_total_pages_from_soup(soup):
    pagination = soup.find("ul", class_="pagination")
    if not pagination:
        return 1
    page_numbers = []
    for a in pagination.find_all("a", class_="page-link"):
        if a.text.strip().isdigit():
            page_numbers.append(int(a.text.strip()))
    if page_numbers:
        return max(page_numbers)
    return 1
