
# Copyright (C) 2011 by Peter Goodman
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import urllib2
import urlparse
from BeautifulSoup import *
from collections import defaultdict
import re
from pagerank import page_rank
import sqlite3 as lite

def attr(elem, attr):
    """An html attribute from an html element. E.g. <a href="">, then
    attr(elem, "href") will get the href or an empty string."""
    try:
        return elem[attr]
    except:
        return ""

WORD_SEPARATORS = re.compile(r'\s|\n|\r|\t|[^a-zA-Z0-9\-_]')
DESC_WORDS = 20

class crawler(object):
    """Represents 'Googlebot'. Populates a database by crawling and indexing
    a subset of the Internet.

    This crawler keeps track of font sizes and makes it simpler to manage word
    ids and document ids."""

    def __init__(self, db_conn, url_file):
        """Initialize the crawler with a connection to the database to populate
        and with the file containing the list of seed URLs to begin indexing."""
        self._url_queue = [ ]
        self._doc_id_cache = { }
        self._word_id_cache = { }
        self._document_index = { }
        self._lexicon = [ ]
        self._doc_id_word_list = { }
        self._inverted_index = { }
        self._word_index = { }
        self._doc_id_url = { }
        self._links = [ ]
        self._links_dict = { }
        self._next_link_id = 1
        self._descriptions = { }
        self._inv_word_id_cache = { }
        self._page_rank = defaultdict(lambda: float(initial_pr))

        # functions to call when entering and exiting specific tags
        self._enter = defaultdict(lambda *a, **ka: self._visit_ignore)
        self._exit = defaultdict(lambda *a, **ka: self._visit_ignore)

        # add a link to our graph, and indexing info to the related page
        self._enter['a'] = self._visit_a

        # record the currently indexed document's title an increase
        # the font size
        def visit_title(*args, **kargs):
            self._visit_title(*args, **kargs)
            self._increase_font_factor(7)(*args, **kargs)

        # increase the font size when we enter these tags
        self._enter['b'] = self._increase_font_factor(2)
        self._enter['strong'] = self._increase_font_factor(2)
        self._enter['i'] = self._increase_font_factor(1)
        self._enter['em'] = self._increase_font_factor(1)
        self._enter['h1'] = self._increase_font_factor(7)
        self._enter['h2'] = self._increase_font_factor(6)
        self._enter['h3'] = self._increase_font_factor(5)
        self._enter['h4'] = self._increase_font_factor(4)
        self._enter['h5'] = self._increase_font_factor(3)
        self._enter['title'] = visit_title

        # decrease the font size when we exit these tags
        self._exit['b'] = self._increase_font_factor(-2)
        self._exit['strong'] = self._increase_font_factor(-2)
        self._exit['i'] = self._increase_font_factor(-1)
        self._exit['em'] = self._increase_font_factor(-1)
        self._exit['h1'] = self._increase_font_factor(-7)
        self._exit['h2'] = self._increase_font_factor(-6)
        self._exit['h3'] = self._increase_font_factor(-5)
        self._exit['h4'] = self._increase_font_factor(-4)
        self._exit['h5'] = self._increase_font_factor(-3)
        self._exit['title'] = self._increase_font_factor(-7)

        # never go in and parse these tags
        self._ignored_tags = set([
            'meta', 'script', 'link', 'meta', 'embed', 'iframe', 'frame', 
            'noscript', 'object', 'svg', 'canvas', 'applet', 'frameset', 
            'textarea', 'style', 'area', 'map', 'base', 'basefont', 'param',
        ])

        # set of words to ignore
        self._ignored_words = set([
            '', 'the', 'of', 'at', 'on', 'in', 'is', 'it',
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
            'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
            'u', 'v', 'w', 'x', 'y', 'z', 'and', 'or',
        ])

        # TODO remove me in real version
        self._mock_next_doc_id = 1
        self._mock_next_word_id = 1

        # keep track of some info about the page we are currently parsing
        self._curr_depth = 0
        self._curr_url = ""
        self._curr_doc_id = 0
        self._font_size = 0
        self._curr_words = None
        self._curr_title = ""
        self._cur_desc = ""
        self._open_para = False
        self._cur_desc_word = 0

        # get all urls into the queue
        try:
            with open(url_file, 'r') as f:
                for line in f:
                    self._url_queue.append((self._fix_url(line.strip(), ""), 0))
        except IOError:
            pass
    
    # TODO remove me in real version
    def _mock_insert_document(self, url):
        """A function that pretends to insert a url into a document db table
        and then returns that newly inserted document's id."""
        ret_id = self._mock_next_doc_id
        self._mock_next_doc_id += 1
        return ret_id
    
    # TODO remove me in real version
    def _mock_insert_word(self, word):
        """A function that pretends to inster a word into the lexicon db table
        and then returns that newly inserted word's id."""
        ret_id = self._mock_next_word_id
        self._mock_next_word_id += 1
        return ret_id
    
    def word_id(self, word):
        """Get the word id of some specific word."""
        if word in self._word_id_cache:
            return self._word_id_cache[word]
        
        # TODO: 1) add the word to the lexicon, if that fails, then the
        #          word is in the lexicon
        #       2) query the lexicon for the id assigned to this word, 
        #          store it in the word id cache, and return the id.

        word_id = self._mock_insert_word(word)
        self._word_id_cache[word] = word_id
        self._inv_word_id_cache[word_id] = word
        return word_id
    
    def document_id(self, url):
        """Get the document id for some url."""
        if url in self._doc_id_cache:
            return self._doc_id_cache[url]
        
        # TODO: just like word id cache, but for documents. if the document
        #       doesn't exist in the db then only insert the url and leave
        #       the rest to their defaults.
        
        doc_id = self._mock_insert_document(url)
        self._doc_id_cache[url] = doc_id
        return doc_id
    
    def _fix_url(self, curr_url, rel):
        """Given a url and either something relative to that url or another url,
        get a properly parsed url."""

        rel_l = rel.lower()
        if rel_l.startswith("http://") or rel_l.startswith("https://"):
            curr_url, rel = rel, ""
            
        # compute the new url based on import 
        curr_url = urlparse.urldefrag(curr_url)[0]
        parsed_url = urlparse.urlparse(curr_url)
        return urlparse.urljoin(parsed_url.geturl(), rel)

    def add_link(self, from_doc_id, to_doc_id):
        """Add a link into the database, or increase the number of links between
        two pages in the database."""
        self._links.append((from_doc_id, to_doc_id))
        # TODO

    def _visit_title(self, elem):
        """Called when visiting the <title> tag."""
        title_text = self._text_of(elem).strip()
        self._curr_title = title_text
        print "document title="+ repr(title_text)

        # TODO update document title for document id self._curr_doc_id
    
    def _visit_a(self, elem):
        """Called when visiting <a> tags."""

        dest_url = self._fix_url(self._curr_url, attr(elem,"href"))

        #print "href="+repr(dest_url), \
        #      "title="+repr(attr(elem,"title")), \
        #      "alt="+repr(attr(elem,"alt")), \
        #      "text="+repr(self._text_of(elem))

        # add the just found URL to the url queue
        self._url_queue.append((dest_url, self._curr_depth))
        
        # add a link entry into the database from the current document to the
        # other document
        self.add_link(self._curr_doc_id, self.document_id(dest_url))

        # TODO add title/alt/text to index for destination url
    
    def _add_words_to_document(self):
        # TODO: knowing self._curr_doc_id and the list of all words and their
        #       font sizes (in self._curr_words), add all the words into the
        #       database for this document
        self._doc_id_word_list[self._curr_doc_id] = self._curr_words
        self._doc_id_url[self._curr_doc_id] = self._curr_url

        print "    num words="+ str(len(self._curr_words))

    def _increase_font_factor(self, factor):
	"""Increade/decrease the current font size."""
        def increase_it(elem):
            self._font_size += factor
        return increase_it
    
    def _visit_ignore(self, elem):
        """Ignore visiting this type of tag"""
        pass

    def _add_text(self, elem):
        """Add some text to the document. This records word ids and word font sizes
        into the self._curr_words list for later processing."""
        #words = WORD_SEPARATORS.split(elem.string.lower())
        words = WORD_SEPARATORS.split(elem.string)
        global DESC_WORDS
        for word in words:
            word = word.strip()

            if (self._open_para == True) and (self._cur_desc_word < DESC_WORDS):
                self._cur_desc = self._cur_desc + " " + word
                self._cur_desc_word = self._cur_desc_word + 1
            if (self._cur_desc_word >= DESC_WORDS):
                self._cur_desc_word = 0
                self._open_para = False  

            word = word.lower()
            if word in self._ignored_words:
                continue
            self._lexicon.append(word)
            wordid = self.word_id(word)
            if not self._inverted_index.has_key(wordid):          
                self._inverted_index[wordid] = set()
            self._inverted_index[wordid].add(self._curr_doc_id)
            self._word_index[wordid] = word
                
            self._curr_words.append((self.word_id(word), self._font_size))
        
    def _text_of(self, elem):
        """Get the text inside some element without any tags."""
        if isinstance(elem, Tag):
            text = [ ]
            for sub_elem in elem:
                text.append(self._text_of(sub_elem))
            
            return " ".join(text)
        else:
            return elem.string

    def _index_document(self, soup):
        """Traverse the document in depth-first order and call functions when entering
        and leaving tags. When we come accross some text, add it into the index. This
        handles ignoring tags that we have no business looking at."""
        class DummyTag(object):
            next = False
            name = ''
        
        class NextTag(object):
            def __init__(self, obj):
                self.next = obj
        
        tag = soup.html
        stack = [DummyTag(), soup.html]

        while tag and tag.next:
            tag = tag.next

            # html tag
            if isinstance(tag, Tag):

                if tag.parent != stack[-1]:
                    self._exit[stack[-1].name.lower()](stack[-1])
                    stack.pop()

                tag_name = tag.name.lower()  

                if tag_name == 'p':
                    self._open_para = True

                if tag_name in self._ignored_tags:
                    if tag.nextSibling:
                        tag = NextTag(tag.nextSibling)
                    else:
                        self._exit[stack[-1].name.lower()](stack[-1])
                        stack.pop()
                        tag = NextTag(tag.parent.nextSibling)
                    
                    continue
                
                # enter the tag
                self._enter[tag_name](tag)
                stack.append(tag)

            # text (text, cdata, comments, etc.)
            else:
                self._add_text(tag)

    def crawl(self, depth=2, timeout=3):
        """Crawl the web!"""
        seen = set()

        while len(self._url_queue):

            url, depth_ = self._url_queue.pop()

            # skip this url; it's too deep
            if depth_ > depth:
                continue

            doc_id = self.document_id(url)

            # we've already seen this document
            if doc_id in seen:
                continue

            seen.add(doc_id) # mark this document as haven't been visited
            
            socket = None
            try:
                socket = urllib2.urlopen(url, timeout=timeout)
                soup = BeautifulSoup(socket.read())

                self._curr_depth = depth_ + 1
                self._curr_url = url
                self._curr_doc_id = doc_id
                self._font_size = 0
                self._curr_words = [ ]
                self._index_document(soup)
                self._add_words_to_document()
                self._document_index[doc_id] = repr(self._curr_title)
                self._descriptions[doc_id] = self._cur_desc 
                self._cur_desc = ""
                print "    url="+repr(self._curr_url)

            except Exception as e:
                print e
                pass
            finally:
                if socket:
                    socket.close()

    def get_inverted_index(self):
        return self._inverted_index

    def get_resolved_inverted_index(self):
        resolved_inverted_index = dict()
        for i in self._inverted_index:
            word = self._word_index[i]
            url_set = set()
            for j in self._inverted_index[i]:
                url_set.add(self._doc_id_url[j])
            resolved_inverted_index[word] = url_set
        return resolved_inverted_index

    def get_page_rank(self):
        link_page_rank = page_rank(self._links)
        # inv_dict = dict((v,k) for k, v in self._links_dict.iteritems())
        # for l_id, rank in link_page_rank.iteritems(): 
        #     link_url = inv_dict[l_id]
        #     if link_url in self._doc_id_cache:
        #         doc_id = self._doc_id_cache[link_url]
        #         self._page_rank[doc_id] = rank
        # for d_url in self._doc_id_cache: 
        #     doc_id = self._doc_id_cache[d_url]
        #     if doc_id not in self._page_rank: 
        #         self._page_rank[doc_id] = 0
        for doc_id, rank in link_page_rank.iteritems():
            self._page_rank[doc_id] = rank

        for url, doc_id in self._doc_id_cache.iteritems():
            if doc_id not in self._page_rank: 
                self._page_rank[doc_id] = 0


    def write_to_database(self):
        con = lite.connect('keywords.db')
        cur = con.cursor()

        # Create Lexicon in database
        cur.execute('CREATE TABLE IF NOT EXISTS lexicon(word_id INTEGER PRIMARY KEY, word TEXT);')
        for word, wordid in self._word_id_cache.iteritems(): 
            cur.execute('INSERT OR IGNORE INTO lexicon VALUES (?, ?)',(wordid, word))

        #create page rank in database
        cur.execute('CREATE TABLE IF NOT EXISTS page_rank(doc_id INTEGER PRIMARY KEY, rank REAL);')
        for doc_id, rank in self._page_rank.iteritems(): 
            cur.execute('INSERT OR IGNORE INTO page_rank VALUES (?,?)', (doc_id, rank))

        # Crate document_index in database
        cur.execute('CREATE TABLE IF NOT EXISTS document_index(doc_id INTEGER PRIMARY KEY, url TEXT, title TEXT, description TEXT);')
        for url, doc_id in self._doc_id_cache.iteritems(): 
            title = 'None'
            desc = 'None'
            if doc_id in self._document_index: 
                title = self._document_index[doc_id]
            if doc_id in self._descriptions: 
                desc = self._descriptions[doc_id]
            cur.execute('INSERT OR IGNORE INTO document_index VALUES (?, ?, ?, ?)',(doc_id, url, title, desc))

        # Create inverted index in database
        cur.execute('CREATE TABLE IF NOT EXISTS inverted_index(word_id INTEGER PRIMARY KEY, doc_id_set TEXT);')
        for word_id, doc_id_set in self._inverted_index.iteritems(): 
            doc_id_set_str = repr(doc_id_set)
            cur.execute('INSERT OR REPLACE INTO inverted_index VALUES (?, ?)',(word_id, doc_id_set_str))

        # Create other tables that are needed just in backend 
        cur.execute('CREATE TABLE IF NOT EXISTS links(from_id INTEGER, to_id INTEGER)')
        for (from_id, to_id) in self._links:
            cur.execute('INSERT OR IGNORE INTO links VALUES (?, ?)',(from_id, to_id))

        cur.execute('CREATE TABLE IF NOT EXISTS links_dict(link_id INTEGER PRIMARY KEY, url TEXT)')
        for url, link_id in self._links_dict.iteritems():
            cur.execute('INSERT OR IGNORE INTO links_dict VALUES (?, ?)',(link_id, url))


        cur.execute('DROP TABLE IF EXISTS counters')
        con.commit()
        
        cur.execute('CREATE TABLE IF NOT EXISTS counters(id INTEGER PRIMARY KEY, value INTEGER)')
        cur.execute('INSERT INTO counters(value) VALUES (?)', (self._mock_next_word_id,))
        cur.execute('INSERT INTO counters(value) VALUES (?)', (self._mock_next_doc_id,))
        cur.execute('INSERT INTO counters(value) VALUES (?)', (self._next_link_id,))


        con.commit()
        con.close()

    def read_from_database(self):
        con = lite.connect('keywords.db')
        cur = con.cursor()

        cur.execute('SELECT * FROM lexicon')
        inv_word_id_cache = cur.fetchall()
        self._word_id_cache = dict((v,k) for (k,v) in inv_word_id_cache)

        cur.execute('SELECT * FROM document_index')
        inv_doc_id_cache = cur.fetchall()
        self._doc_id_cache = dict((v,k) for (k,v,l, m) in inv_doc_id_cache)
        self._document_index = dict((k,l) for (k,v,l, m) in inv_doc_id_cache)
        self._descriptions = dict((k,m) for (k,v,l, m) in inv_doc_id_cache)

        cur.execute('SELECT * FROM inverted_index')
        ii_cache= cur.fetchall()
        for wordid, doc_id_set_str in ii_cache: 
            doc_id_set = eval(doc_id_set_str)
            self._inverted_index[wordid] = doc_id_set

        cur.execute('SELECT * FROM links')
        self._links = cur.fetchall()

        cur.execute('SELECT * FROM links_dict')
        inv_links_dict = cur.fetchall()
        self._links_dict = dict((v,k) for (k,v) in inv_links_dict)

        cur.execute('SELECT * FROM counters')
        (count_id, count) = cur.fetchone()
        self._mock_next_word_id = count 
        (count_id, count) = cur.fetchone()
        self._mock_next_doc_id = count 
        (count_id, count) = cur.fetchone()
        self._next_link_id = count 
        con.commit()
        con.close()


if __name__ == "__main__":
    bot = crawler(None, "urls.txt")
    bot.crawl(depth=1)

