var topWords = {};
var sortable = [];

function printResult() {
	var query = document.getElementById('search-query').value;
	var words = query.match(/\S+/g);
	var body = document.getElementById("page");

	if (words != null) {
		if (words.length > 1) {
			resultsTable = "<h3>" + query + "</h3>" + "<table id = \"results\" border = \"1\"><tr><td>Word</td><td>Count</td></tr>";
				words.sort();

				leftIndex = 0;
				for (index = 0; index < words.length; index++) {
					if (words[index] != words[index+1]) {
						count = index - leftIndex + 1;
						updateTopList(words[index], count);
						leftIndex = index + 1;
						resultsTable = resultsTable.concat("<tr><td>" + words[index] + "</td>" + "<td>" + count + "</td></tr>");
					}
				}
				
				resultsTable = resultsTable.concat("</table>");
		} else {
			resultsTable = "<h3>" + query + "</h3>";
		}

		keywordsTable = getKeywordsTable();
		body.innerHTML = resultsTable + keywordsTable;
	}
}

function updateTopList(word, count) {
	if (word in topWords) {
		currentCount = topWords[word];
		topWords[word] += count;
	} else {
		topWords[word] = count;
	}
	sortTopWords();
}

function sortTopWords() {
	sortable = [];
	for (var word in topWords)
    	sortable.push([word, topWords[word]])
	sortable.sort(function(a, b) {return a[1] - b[1]})
	alert(sortable);
}

function getKeywordsTable() {
	keywordsTable = "<h2>Top 20 Keywords</h2>" + "<table id = \"history\" border = \"1\"><tr><td>Word</td><td>Count</td></tr>"
	for (index = 0; index < sortable.length; index++) {
		word = sortable[index];
		keywordsTable = keywordsTable.concat("<tr><td>" + word[0] + "</td>" + "<td>" + word[1] + "</td></tr>")
	}
	keywordsTable = keywordsTable.concat("</table>")
	return keywordsTable;
}