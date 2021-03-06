from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import flow_from_clientsecrets
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
import httplib2
import cgi 
import os 
import bottle 
import beaker
from beaker.middleware import SessionMiddleware 
from bottle import route, get, post, request, run, static_file, error # or route
import sqlite3 as lite
import trie_implementation as trie

session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 300,
    'session.data_dir': './data',
    'session.auto': True
}
app = SessionMiddleware(bottle.app(), session_opts)

CLIENT_ID = '278908014431-lj5cbvaltqh8vpl9u697r12qibo67kf9.apps.googleusercontent.com'
CLIENT_SECRET = '83bnG_gonLkb1Pg8hTMfGKJs'
REDIRECT_URI = 'http://ec2-54-172-218-21.compute-1.amazonaws.com:80/redirect'

wordlistdict = {}
credentials_dict = {}
curr_email = ""
logged_in = False
recent_list_dict = {}
curpage_dict = {}
totalpage_dict = {}
result_dict = {}
NUM_LINKS_PER_PAGE = 10
mytrie = {}
#list_sessions = []

global credentials 

# Following are all the HTML components

searchButton = """<form autocomplete="off" action = "/results" method = "get" id = "query">
                    <span class = "textbox"><input onkeyup="autoComp()" type = "text" name = "keywords" id = "keywords"/><input type = "submit" name = "search" value = "Search"/></span>
                    <select size = 5 id="dropdown" onchange="applySelect()"></select>
                   </form>"""

loginForm = """<head><script type="text/javascript" src="/static/inquest.js"></script><link rel="stylesheet" type="text/css" href="/static/inquest.css"><link rel="shortcut icon" href="static/favicon.ico"></head>
        <body>
        <div id = "page">
            <div id="titlebar">
                <img src="/static/search.jpg" alt="Inquest Logo">
                <h1>Inquest</h1>
            </div>
            <form action = "/authenticate" method = "get" id = "login">
                    <p><input type = "submit" name = "login" value = "login"/>
            </form>
            <form action = "/guest" method = "get" id = "query">
                    <p><input type = "submit" name = "guest" value = "Guest"/>
            </form>"""

searchForm = """<head> <script type="text/javascript" src="/static/inquest.js"></script><link rel="stylesheet" type="text/css" href="/static/inquest.css"><link rel="shortcut icon" href="static/favicon.ico"></head>
        <body>
        <div id = "page">
            <div id="titlebar">
                <img src="/static/search.jpg" alt="Inquest Logo">
                <h1>Inquest</h1>
            </div>
            """ + searchButton

signoutbutton = """
    <form action = "/signout" method = "get" id = "signout">
            <input type = "submit" name = "signout" value = "Signout"/>
    </form>"""

guestbackbutton = """
    <form action = "/guest" method = "get" id = "guestbackbutton">
            <p><input id = "back" type = "submit" name = "Back" value = "Inquest"/>
    </form>"""

logged_inbackbutton = """
    <form action = "/logged_in" method = "get" id = "loginbackbutton">
            <p><input id = "back" type = "submit" name = "Back" value = "Inquest"/>
    </form>"""

prev_page_button = """
    <form action = "/prev_page" method = "get" id = "prev_page_button">
            <p><input id = "prev" type = "submit" name = "Prev Page" value = "Prev"/>
    </form>"""

next_page_button = """
    <form action = "/next_page" method = "get" id = "next_page_button">
            <p><input id = "next" type = "submit" name = "Next Page" value = "Next"/>
    </form>"""

home_button = """
    <form action = "/" method = "get" id = "home_button">
            <p><input type = "submit" name = "Back to Home" value = "Back to Home"/>
    </form>"""

def create_page_link_btn(page_num):
    return """<form action = "/get_page_num" method = "get">
            <button><input id = "pageNum" type = "submit" name = "page_num" value = " """ + str(page_num) +  """ "/>
    </form>"""

@error(404)
def error404(error):
    no_page = "<h3> Nothing on this page </h3>"
    return """<head><link rel="stylesheet" type="text/css" href="/static/errorpage.css"><link rel="shortcut icon" href="static/favicon.ico"></head><body>""" + no_page + home_button + "</body>"

@error(501)
def error404(error):
    no_page = "<h3> This Method is not supported </h3>"
    return """<head><link rel="stylesheet" type="text/css" href="/static/errorpage.css"><link rel="shortcut icon" href="static/favicon.ico"></head><body>""" + no_page + home_button + "</body>"

@route('/static/<filename>') 
def server_static(filename):
    return static_file(filename, root='static/')

@get('/authenticate')
def authenticate():
    flow = flow_from_clientsecrets("client_secrets.json",
    scope='https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email',
    redirect_uri=REDIRECT_URI)
    uri = flow.step1_get_authorize_url()
    bottle.redirect(str(uri))

@route('/redirect')
def redirect_page():
    global credentials_dict

    code = request.query.get('code', '')
    flow = OAuth2WebServerFlow( client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    scope='https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email',
    redirect_uri=REDIRECT_URI)
    credentials = flow.step2_exchange(code)
    token = credentials.id_token['sub']

    http = httplib2.Http()
    http = credentials.authorize(http)
    users_service = build('oauth2', 'v2', http=http)
    user_document = users_service.userinfo().get().execute()
    user_email = user_document['email']
    str_email = str(user_email)
    if str_email not in credentials_dict: 
        credentials_dict[str_email] = credentials

    s = bottle.request.environ.get('beaker.session')    
    if s is None:
        return 'I am None'

    s['user'] = str_email
    s.save()

    return  searchForm  +"""<div class = "sobutton"> Welcome " """ + str_email + "\"" + signoutbutton +  "</div></div>"+ createRecentTable() + "</body>"

@get('/autocomplete')
def autocomp(): 
    s = bottle.request.environ.get('beaker.session')
    cur_email = ''
    modify_word_list = False
    num_recent_words_in_list = 0
    if 'user' in s:
        cur_email = s['user'] 
        if cur_email in recent_list_dict:
            modify_word_list = True

    in_put = request.query['input']
    dont_check_alpha = not in_put.isalpha()
    wordList = trie.get_words_from_trie(mytrie, in_put)
    if len(wordList) == 0: 
        return ''
    else: 
        if modify_word_list == True: 
            modified_word_list = []
            recent_list = recent_list_dict[cur_email]
            for i in recent_list: 
                if i in wordList: 
                    wordList.remove(i)
                    modified_word_list.append(i)
                    num_recent_words_in_list = num_recent_words_in_list + 1
            wordList = modified_word_list + wordList
        min_results = min(5, len(wordList))
        word_str = str(num_recent_words_in_list) + ';'
        count = 0
        i = 0
        while count < min_results and i < len(wordList): 
            if wordList[i].isalpha() or dont_check_alpha:
                word_str = word_str + wordList[i]
                if count < (min_results - 1):
                    word_str = word_str + ';'
                count = count + 1
            i = i+1

        return word_str

@get('/signout')
def signout():
    s = bottle.request.environ.get('beaker.session')
    s.delete()
    bottle.redirect('/')

@get('/')
def login():
    s = bottle.request.environ.get('beaker.session')

    if 'user' in s:
        bottle.redirect('/logged_in')
    else:
        return loginForm

@get('/logged_in')
def inquest() :
    sobutton = ""
    s = bottle.request.environ.get('beaker.session')
    if 'user' in s: 
        email = s['user']
        sobutton = signoutbutton
    else: 
        email = "Guest"
    return searchForm +  """<div class = "sobutton">""" + "Welcome \"" + email + "\"" +  sobutton + "</div></div>"+ createRecentTable() + "</body>"

@get('/guest')
def guest():
    s = bottle.request.environ.get('beaker.session')
    s['logged_in'] = 'False'
    s['user'] = "Guest"
    s.save()
    return searchForm

@get('/next_page')
def next_page():
    s = bottle.request.environ.get('beaker.session')
    curr_email = "Guest"
    logged_in = False
    result = []
    if 'user' in s: 
        curr_email = s['user']
        logged_in = curr_email != 'Guest'
    if 'results' in s: 
        result = s['results']
        curr_page = s['curr_page']
        total_page = s['total_page']
        query = s['query']
        if (curr_page + 1) <= total_page:
            curr_page = curr_page + 1
            s['curr_page'] = curr_page
        s.save()
        return print_result_page(query, curr_email, logged_in, result, curr_page)

    else: # redirect to error page 
        s.save()
        return error404('Invalid request')


@get('/prev_page')
def prev_page(): 
    s = bottle.request.environ.get('beaker.session')
    curr_email = "Guest"
    logged_in = False
    result = []
    if 'user' in s: 
        curr_email = s['user']
        logged_in = curr_email != 'Guest'
    if 'results' in s: 
        result = s['results']
        curr_page = s['curr_page']
        total_page = s['total_page']
        query = s['query']
        if (curr_page - 1) >= 0:
            curr_page = curr_page - 1
            s['curr_page'] = curr_page
        s.save()
        return print_result_page(query, curr_email, logged_in, result, curr_page)

    else: # redirect to error page 
        s.save()
        return error404('Invalid request')

@get('/get_page_num')
def get_page_num():
    str_page_num = request.query['page_num']
    page_num = int(str_page_num)
    curr_page = page_num - 1
    s = bottle.request.environ.get('beaker.session')
    curr_email = "Guest"
    logged_in = False
    result = []
    if 'user' in s: 
        curr_email = s['user']
        logged_in = curr_email != 'Guest'
    if 'results' in s: 
        result = s['results']
        total_page = s['total_page']
        query = s['query']
        s['curr_page'] = curr_page
        s.save()
        return print_result_page(query, curr_email, logged_in, result, curr_page)

    else: # redirect to error page 
        s.save()
        return error404('Invalid request')

def print_result_page(query, curr_email, logged_in, results, curr_page):
    global NUM_LINKS_PER_PAGE
    sobutton = ""
    back = guestbackbutton
    npb = ""
    ppb = ""
    if logged_in:
        sobutton = signoutbutton
        back = logged_inbackbutton

    total_urls = len(results)
    starting_pt = curr_page * NUM_LINKS_PER_PAGE
    if starting_pt >= total_urls : 
        return error404('Invalid request')

    remaining = total_urls - starting_pt 
    to_print = min(remaining, NUM_LINKS_PER_PAGE)
    total_page = total_urls / NUM_LINKS_PER_PAGE
    if total_urls == total_page * NUM_LINKS_PER_PAGE: 
        total_page = total_page - 1
    if curr_page < total_page: 
        npb = next_page_button
    if curr_page > 0: 
        ppb = prev_page_button

    # Results Page!!!!!!
    resultsPage = """<div id = 'whole'><img src="/static/search.jpg" alt="Inquest Logo"><span id = 'whole'>""" + back + """<form autocomplete="off" action = "/results" method = "get" id = "query">
    <input onkeyup = "autoComp()" type = "text" value = """ + query + """ name = "keywords" id = "keywords">
    <input id = "searchButton" type = "submit" name = "search" value = "Search"/></form><h5>Hello """ + curr_email + """!</h5></span></div>
    <div id="so">""" + sobutton + """</div><p><select onchange="applySelect()" size = 5 id = "dropdown"></select></p>""" 

    resultsPage = resultsPage + """<div class="blank_space" ><p></p> </div> """
    #+ curr_email + sobutton + back
    for i in range(0,to_print):
        title = results[starting_pt + i][3] 
        url = results[starting_pt + i][2]
        description = results[starting_pt + i][4]
        if title == 'None':
            title = 'No Title'
        if title != 'Calculator Results':     
            title = eval(title)

        if description == 'None':
            description = 'No description'

        if len(description) > 250: 
            description = description[:250] + ' ...'

        resultsPage = resultsPage + """<div class="entry">
        <div class="entryheading">
        <a href = """ + url + """><h2 class="entrytitle">""" + title + """</h2></a>
        <div class="entryurl">""" + url + """</div>
        </div>
        <div class="entrycontents">""" + description + """</div></div>"""

    # Pagination
    if total_page > 0:
        resultsPage = resultsPage + "<br><br><table id = pagination><tr><td> " + ppb + "</td>"
        for i in range(0,total_page+1):
            if i == curr_page:
                resultsPage = resultsPage + """<td id="curr">""" + str(i+1) + "</td>"
            else:
                resultsPage = resultsPage + "<td>" + create_page_link_btn(i+1) + "</td>" 
        resultsPage = resultsPage + "<td> " + npb + "</td></tr>"

    return """<head><script type="text/javascript" src="/static/inquest.js"></script><link rel="stylesheet" type="text/css" href="/static/resultspage.css"><link rel="shortcut icon" href="static/favicon.ico"></head><body>""" + resultsPage + "</body>" 

@get('/results')
def do_inquest() :
    global NUM_LINKS_PER_PAGE
    global wordlistdict
    global recent_list_dict

    s = bottle.request.environ.get('beaker.session')
    wordList = []
    recent_list = []
    curr_email = ""
    logged_in = False
    
    # check if logged in or not 
    if 'user' in s:
        curr_email = s['user']
        logged_in = True
    if curr_email == 'Guest':
        logged_in = False

    query = request.query['keywords']
    words = query.split()

    #if logged in create a history table
    if logged_in:
        reverse_words = words[:]
        reverse_words.reverse()
        if curr_email in wordlistdict: 
            wordList = wordlistdict[curr_email]
            recent_list = recent_list_dict[curr_email]
        
        recent_list = reverse_words + recent_list
        if len(recent_list) > 10:
            recent_list = recent_list[0:10]
        recent_list_dict[curr_email] = recent_list


    #if no input, print error message
    if len(words) == 0:
        s.save()
        return searchForm + "<p>Please enter a search query .</p></div>" + createRecentTable()  + "</body>"
    else: 
        
        result = []
        value = mathOperations(words);
        if value != "":
            result.append((-1, 100, '', 'Calculator Results', value ))
            #return searchForm + "<p>" + value + "</p></div>" + createRecentTable()  + "</body>"

        searched = words[0]
        if not os.path.isfile('keywords.db'):
            s.save()
            return searchForm + "<p>No Match Found. Please try other keywords.</p></div>" + createRecentTable() + "</body>"

        con = lite.connect('keywords.db')
        cur = con.cursor()
        cur.execute('SELECT word_id FROM lexicon WHERE word = ?',(searched,))
        word_id_set = cur.fetchone()
        if word_id_set != None:
            word_id = word_id_set[0]
            cur.execute('SELECT doc_id_set FROM inverted_index WHERE word_id = ?',(word_id,))
            doc_id_set_str_set = cur.fetchone()
            doc_id_str = doc_id_set_str_set[0]
            doc_id_set = eval(doc_id_str)
            for doc_id_r in doc_id_set: 
                cur.execute('SELECT rank FROM page_rank WHERE doc_id = ?',(doc_id_r,))
                rank_set = cur.fetchone()
                rank = rank_set[0]
                cur.execute('SELECT url, title, description FROM document_index WHERE doc_id = ?',(doc_id_r,))
                url_set = cur.fetchone()
                url = url_set[0]
                title = url_set[1]
                description = url_set[2]
                result.append((doc_id_r, rank, url, title, description))
            result.sort(key=lambda x: x[1], reverse = True)
            s['results'] = result
            s['curr_page'] = 0
            s['total_page'] = (len(result) / NUM_LINKS_PER_PAGE)
            s['query'] = query
            s.save() 

            # The following maintains the word list. Might be used in lab 4
            words.sort()
            leftIndex = 0
            count = 0
            if len(words) == 1:
                updateWordList(wordList, words[0],1)
            else:
                for index in range(0, len(words)-1):
                    if words[index] != words[index+1]:
                        count = index - leftIndex + 1
                        leftIndex = index + 1
                        updateWordList(wordList, words[index],count)

                
                if (words[len(words)-1] != words[len(words)-2]):
                    count = 1
                else:
                    count = len(words) - leftIndex
                
                updateWordList(wordList, words[len(words)-1],count)
            wordList.sort(key=lambda x: x[1],reverse=True)
            wordlistdict[curr_email] = wordList

            return print_result_page(query, curr_email, logged_in, result, 0)
            

        else: 
            s.save()
            return searchForm + "<p>No Match Found. Please try other keywords.</p></div>" + createRecentTable() + "</body>"

def mathOperations(words):
    i = 0
    isCalc = True
    calcList = []
    while i < len(words):
        if isint(words[i]):
            calcList = calcList + [int(words[i])]
        elif isfloat(words[i]):
            calcList = calcList + [float(words[i])]
        else:
            isCalc = False
            break
        if i+1 < (len(words) - 1):
            if is_operator(words[i+1]):
                calcList = calcList + [words[i+1]]
            else:
                isCalc = False
                break
        i += 2

    i = 1
    if isCalc is False:
        return ""
    else:
        try:
            value = calcList[0]
            while i < (len(calcList) - 1):
                if calcList[i] == "+":
                    value = value + calcList[i+1]
                elif calcList[i] == "-":
                    value = value - calcList[i+1]
                elif calcList[i] == "*":
                    value = value * calcList[i+1]
                elif calcList[i] == "/":
                    value = value / calcList[i+1]
                elif calcList[i] == "%":
                    value = value % calcList[i+1]
                elif calcList[i] == "^":
                    value = value ** calcList[i+1]
                i += 2
        except ValueError:
            return ""
        except TypeError:
            return ""
        except ZeroDivisionError:
            return ""
        else: 
            return str(value)

def isfloat(x):
    try:
        a = float(x)
    except ValueError:
        return False
    else:
        return True

def isint(x):
    try:
        a = int(x)
    except ValueError:
        return False
    else:
        return True

def is_operator(s):
    if s == "+" or s == "-" or s == "/" or s == "*" or s == "^" or s == "%":
        return True

    return False

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def updateWordList (wordList, word, count):
    tmpList = []
    updated = False 
    for (w, c) in wordList: 
        if w == word:
            tmpList.append((w, c + count))
            updated = True
        else: 
            tmpList.append((w, c))

    if updated == False:
        tmpList.append((word,count))
    wordList[:] = tmpList

def createHistoryTable ():
    s = bottle.request.environ.get('beaker.session')
    global wordlistdict
    logged_in = False
    curr_email = ''
    if ['user'] in s: 
        curr_email = s['user']
        logged_in = True
    
    if logged_in == False: 
        return 
    elif curr_email in wordlistdict:
        wordList = wordlistdict[curr_email]
        historyTable = "<h3>Search History for \"" + curr_email + "\"</h3><table id = \"history\"><tr><td>Word</td><td>Count</td></tr>"
        max_output = min(20,len(wordList))
        for i in range(0, max_output):
            historyTable = historyTable + "<tr><td>" + wordList[i][0] + "</td>" + "<td>" + str(wordList[i][1]) + "</td></tr>"
        s.save()
        return historyTable
    else: 
        s.save()
        return "" 

def createRecentTable ():
    s = bottle.request.environ.get('beaker.session')
    global recent_list_dict
    logged_in = False
    curr_email = ''
    if 'user' in s:
        curr_email = s['user']
        logged_in = True
    if logged_in == False:
        return 
    elif curr_email in recent_list_dict:
        recent_list = recent_list_dict[curr_email]
        historyTable = "<h3>Search History for \"" + curr_email + "\"</h3><table id = \"history\"><tr><td>Recently Searched Words</td></tr>"
        for i in recent_list:
            historyTable = historyTable + "<tr><td>" + i + "</td></tr>"
        s.save()
        return historyTable
    else: 
        s.save()
        return "" 

def main():
    global mytrie
    if os.path.isfile('keywords.db'):
        con = lite.connect('keywords.db')
        cur = con.cursor()
        wordlist = []
        cur.execute('SELECT word FROM lexicon')
        word_set = cur.fetchall()
        for i in word_set: 
            clean_word = str(i[0])
            wordlist.append(clean_word)

        mytrie = trie.add_words_to_trie(wordlist)

    run(app=app,host='0.0.0.0', port=80, debug=True)

if __name__ == '__main__':
    main()


