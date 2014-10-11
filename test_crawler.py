from crawler import crawler 
f = open('testurls.txt','w')
f.write('http://www.eecg.toronto.edu/~jzhu/csc326/csc326.html')
f.close()
c = crawler(None,'testurls.txt')
l = c.crawl(depth=0)
ii=c.get_inverted_index()
rii=c.get_resolved_inverted_index()

expected_ii = {1: set([1]), 2: set([1]), 3: set([1])}
expected_rii = {u'languages': set(['http://www.eecg.toronto.edu/~jzhu/csc326/csc326.html']), u'csc326': set(['http://www.eecg.toronto.edu/~jzhu/csc326/csc326.html']), u'programming': set(['http://www.eecg.toronto.edu/~jzhu/csc326/csc326.html'])}

if set(ii) == set(expected_ii):
    print "PASS: get_inverted_index for one website"
else: 
    print "FAIL: get_inverted_index for one website"

if set(rii) == set(expected_rii):
    print "PASS: get_resolved_inverted_index for one website"
else:
    print "FAIL: get_inverted_index for one website" 

f = open('testurls3.txt','w')
f.write('http://www.eecg.toronto.edu/~jzhu/csc326/csc326.html')
f.write('\n')
f.write('http://www.eecg.toronto.edu/~jzhu/')
f.close()
c = crawler(None,'testurls3.txt')
l = c.crawl(depth=0)
ii=c.get_inverted_index()
rii=c.get_resolved_inverted_index()

expected_ii = {1: set([1]), 2: set([1]), 3: set([1]), 4: set([2]), 5: set([2]), 6: set([2]), 7: set([2])}
expected_rii = {u'languages': set(['http://www.eecg.toronto.edu/~jzhu/csc326/csc326.html']), u'csc326': set(['http://www.eecg.toronto.edu/~jzhu/csc326/csc326.html']), u'programming': set(['http://www.eecg.toronto.edu/~jzhu/csc326/csc326.html']), u'home': set(['http://www.eecg.toronto.edu/~jzhu/']), u'jianwen': set(['http://www.eecg.toronto.edu/~jzhu/']), u'zhu': set(['http://www.eecg.toronto.edu/~jzhu/']), u'page': set(['http://www.eecg.toronto.edu/~jzhu/'])}

error = False
for i in ii:
    if i not in expected_ii:
        print "FAIL: get_inverted_index for one website" 
        error = True
print "PASS: get_inverted_index for one website"

error = False
for i in rii:
    if i not in expected_rii:
        print i
        print "FAIL: get_resolved_inverted_index for one website" 
        error = True
print "PASS: get_resolved_inverted_index for one website"


f = open('testurls2.txt','w')
f.write('')
f.close()
d = crawler(None,'testurls2.txt')
l = d.crawl(depth=0)
ii=d.get_inverted_index()
rii=d.get_resolved_inverted_index()

e_ii = {}
e_rii = {}

if set(ii) == set(e_ii):
    print "PASS: get_inverted_index for 0 website"
else: 
    print "FAIL: get_inverted_index for 0 website"

if set(rii) == set(e_rii):
    print "PASS: get_resolved_inverted_index for 0 website"
else:
    print "FAIL: get_inverted_index for 0 website" 

