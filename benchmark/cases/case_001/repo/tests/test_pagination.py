from src.pagination import page_count

def test_partial_page_rounds_up(): assert page_count(21,10)==3
def test_exact_multiple_has_no_extra_page(): assert page_count(20,10)==2
def test_empty_collection(): assert page_count(0,10)==0
