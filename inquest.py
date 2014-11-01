
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
from bottle import route, get, post, request, run, static_file # or route

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
#list_sessions = []

global credentials 

loginForm = """<head> <link rel="stylesheet" type="text/css" href="/static/inquest.css"></head>
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

searchForm = """<head> <link rel="stylesheet" type="text/css" href="/static/inquest.css"></head>
        <body>
        <div id = "page">
            <div id="titlebar">
                <img src="/static/search.jpg" alt="Inquest Logo">
                <h1>Inquest</h1>
            </div>
            <form action = "/results" method = "get" id = "query">
                    <p><span class = "textbox"><input type = "text" name = "keywords" id = "keywords"/></span></p>
                    <p><input type = "submit" name = "search" value = "Search"/>
            </form>"""

signoutbutton = """
    <form action = "/signout" method = "get" id = "signout">
            <p><input type = "submit" name = "signout" value = "Signout"/>
    </form>"""

guestbackbutton = """
    <form action = "/guest" method = "get" id = "guestbackbutton">
            <p><input type = "submit" name = "Back" value = "Back"/>
    </form>"""

logged_inbackbutton = """
    <form action = "/logged_in" method = "get" id = "loginbackbutton">
            <p><input type = "submit" name = "Back" value = "Back"/>
    </form>"""

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
    #curr_email = str_email
    #logged_in = True

    return  searchForm + signoutbutton + "Welcome \"" + str_email + "\"" "</div>"+ createRecentTable() + "</body>"

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
    s = bottle.request.environ.get('beaker.session')
    if 'user' in s: 
        email = s['user']
    else: 
        email = "Guest"
    return searchForm + signoutbutton + "Welcome \"" + email + "\"" "</div>"+ createRecentTable() + "</body>"

@get('/guest')
def guest():
    s = bottle.request.environ.get('beaker.session')
    s['logged_in'] = 'False'
    s['user'] = "Guest"
    s.save()
    return searchForm

@get('/results')
def do_inquest() :
    global wordlistdict
    global recent_list_dict
    s = bottle.request.environ.get('beaker.session')
    wordList = []
    recent_list = []
    sobutton = ""
    curr_email = ''
    if 'user' in s:
        curr_email = s['user']
        logged_in = True
    if curr_email == 'Guest':
        logged_in = False

    query = request.query['keywords']
    words = query.split()

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

        sobutton = signoutbutton

    if len(words) == 0:
        s.save()
        return searchForm + "<p>Please enter a search query.</p></div>" + createRecentTable() + "</body>"
    words.sort()
    resultsTable = "<h3>Search for \"" + query + "\"</h3><table id = \"results\"><tr><td> Words</td><td> Count</td></tr>" + curr_email + sobutton
    leftIndex = 0
    count = 0
    if len(words) == 1:
        resultsTable = resultsTable + "<tr><td>" + words[0] + "</td>" + "<td>1</td></tr>"
        updateWordList(wordList, words[0],1)
    else:
        for index in range(0, len(words)-1):
            if words[index] != words[index+1]:
                count = index - leftIndex + 1
                leftIndex = index + 1
                resultsTable = resultsTable + "<tr><td>" + words[index] + "</td>" + "<td>" + str(count) + "</td></tr>"
                updateWordList(wordList, words[index],count)

        
        if (words[len(words)-1] != words[len(words)-2]):
            count = 1
        else:
            count = len(words) - leftIndex
        
        updateWordList(wordList, words[len(words)-1],count)
        resultsTable = resultsTable + "<tr><td>" + words[len(words)-1] + "</td>" + "<td>" + str(count) + "</td></tr>"
        resultsTable = resultsTable + "</table>"
    wordList.sort(key=lambda x: x[1],reverse=True)
    wordlistdict[curr_email] = wordList
    if logged_in: 
        back = logged_inbackbutton
    else: 
        back = guestbackbutton
    s.save()
    return """<head><link rel="stylesheet" type="text/css" href="/static/resultspage.css"></head><body>""" + resultsTable + back + "</body>"

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


run(app=app,host='0.0.0.0', port=80, debug=True)

