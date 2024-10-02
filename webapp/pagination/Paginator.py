import math


class Paginator:
    def __init__(self, page: int, items_per_page: int, count_of_items: int):
        self.amount_of_pages = get_page_amount(items_per_page, count_of_items)
        self.target_page = 1 if (page < 1 or page < self.amount_of_pages) else page
        self.previous_page = True if self.target_page != 1 else False
        self.next_page = True if self.target_page != self.amount_of_pages else False


def get_page_amount(items_per_page: int, count_of_items: int) -> int:
    pages_count_float = count_of_items / items_per_page
    pages_count_int = int(math.ceil(pages_count_float))
    return pages_count_int if pages_count_int != 0 else 1
