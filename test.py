from crawler import crawler 

if __name__ == "__main__":
	# This file tests whethere the crawler stores and reads data correctly from persistant storage 
	# crawler c will crawl the urls.txt and store the data 
	# crawler a will read this data from the database 
	# if c and a have the same data at the end 
	# persistent storage is successful 
	c = crawler(None,'urls2.txt')
	c.crawl(depth=0)
	c.get_page_rank()
	c.write_to_database()
	a = crawler(None, 'urls2.txt')
	a.read_from_database()
	word_cache_success = c._word_id_cache == a._word_id_cache 
	doc_id_success = c._doc_id_cache == a._doc_id_cache 
	inverted_index_success = c._inverted_index == a._inverted_index
	links_success = c._links == a._links 
	counter_success = (c._mock_next_word_id == a._mock_next_word_id) and (c._mock_next_doc_id == a._mock_next_doc_id) 

	if word_cache_success and doc_id_success and inverted_index_success and links_success and counter_success:
		print 'PASS: Creating/updating Persistent storage'
	else:
		print 'FAIL: Creating/updating Persistent storage'

	# Verify that the page rank algorithm works correctly 
	# read from the and compare with expected outcome 
	expected_page_rank = dict( {1: 0.15000000000000002, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0})
	if c._page_rank == expected_page_rank: 
		print 'PASS: Generating page rank'
	else: 
		print 'FAIL: Generating page rank'

