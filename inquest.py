
from bottle import route, get, post, request, run, static_file # or route

wordList = []
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

@route('/static/<filename>') 
def server_static(filename):
    return static_file(filename, root='static/')

@get('/')
def inquest() :
    return  searchForm + "</div>"+ createHistoryTable() + "</body>"

@get('/results')
def do_inquest() :
    global wordList
    query = request.query['keywords']
    words = query.split()
    if len(words) == 0:
        return searchForm + "<p>Please enter a search query.</p></div>" + createHistoryTable() + "</body>"
    words.sort()
    resultsTable = "<h3>Search for \"" + query + "\"</h3><table id = \"results\"><tr><td> Word</td><td> Count</td></tr>"
    leftIndex = 0
    count = 0
    if len(words) == 1:
        resultsTable = resultsTable + "<tr><td>" + words[0] + "</td>" + "<td>1</td></tr>"
        updateWordList(words[0],1)
    else:
        for index in range(0, len(words)-1):
            if words[index] != words[index+1]:
                count = index - leftIndex + 1
                leftIndex = index + 1
                resultsTable = resultsTable + "<tr><td>" + words[index] + "</td>" + "<td>" + str(count) + "</td></tr>"
                updateWordList(words[index],count)

        
        if (words[len(words)-1] != words[len(words)-2]):
            count = 1
        else:
            count = len(words) - leftIndex
        
        updateWordList(words[len(words)-1],count)
        resultsTable = resultsTable + "<tr><td>" + words[len(words)-1] + "</td>" + "<td>" + str(count) + "</td></tr>"
        resultsTable = resultsTable + "</table>"
    wordList.sort(key=lambda x: x[1],reverse=True)
    return """<head><link rel="stylesheet" type="text/css" href="/static/resultspage.css"></head><body>""" + resultsTable + "</body>"

def updateWordList (word, count):
    global wordList
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
    global wordList
    historyTable = "<h3>Search History</h3><table id = \"history\"><tr><td>Word</td><td>Count</td></tr>"
    max_output = min(20,len(wordList))
    for i in range(0, max_output):
        historyTable = historyTable + "<tr><td>" + wordList[i][0] + "</td>" + "<td>" + str(wordList[i][1]) + "</td></tr>"
    return historyTable

run(host='localhost', port=8080, debug=True)

