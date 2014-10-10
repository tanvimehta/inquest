
from bottle import route, get, post, request, run, static_file # or route

wordList = []
@route('/static/<filename>') 
def server_static(filename):
    return static_file(filename, root='static/')

@get('/')
def inquest() :
    return """ <head> <link rel="stylesheet" type="text/css" href="/static/inquest.css"> </head>
        <body>
        <div id = "page">
            <div id="titlebar">
                <img src="/static/search.jpg" alt="Inquest Logo">
                <h1>Inquest</h1>
            </div>
            <form action = "/" method = "post" id = "query">
                    <p><span class = "textbox"><input type = "text" name = "keywords" id = "search-query"/></span></p>
                    <p><input type = "submit" name = "search" value = "Search"/>
            </form>
        </div>
        </body>"""

@post('/')
def do_inquest() :
    global wordList
    query = request.forms.get('keywords')
    words = query.split()
    words.sort()
    resultsTable = "<h3>" + query + "</h3><table><tr><td>Word</td><td>Count</td></tr>"
    leftIndex = 0
    count = 0
    if len(words) == 1:
        resultsTable = resultsTable + "<tr><td>" + words[0] + "</td>" + "<td>1</td></tr>"
        updateWordList(words[0],1)

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
    
    updateWordList(words[len(words)-1],)
    resultsTable = resultsTable + "<tr><td>" + words[len(words)-1] + "</td>" + "<td>" + str(count) + "</td></tr>"
    wordList = wordList + [words[len(words) - 1], len(words) - leftIndex]
    resultsTable = resultsTable + "</table>"
    return "<body>" + resultsTable + "</body>"

def getKey(item):
    return item[0]

def getValue(item):
    return item[1]

def updateWordList (word, count):
    if any (word in tuple for tuple in wordList):
        

# l = [[2, 3], [6, 7], [3, 34], [24, 64], [1, 43]]
# sorted(l, key=getKey)
# [[1, 43], [2, 3], [3, 34], [6, 7], [24, 64]]

run(host='localhost', port=8080, debug=True)

