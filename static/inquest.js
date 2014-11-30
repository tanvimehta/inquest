
function autoComp() {
	var words = [];
  var url = "";
  document.getElementById("dropdown").innerHTML = "";
  document.getElementById("dropdown").style.visibility = "hidden";
    if (document.getElementById("keywords").value != "") {
      url = "http://localhost:8080/autocomplete?input=" + document.getElementById("keywords").value;
      var xmlHttp = new XMLHttpRequest();
      xmlHttp.onreadystatechange=function()
        {
        if (xmlHttp.readyState==4 && xmlHttp.status==200)
          {
            words = xmlHttp.responseText;
            if (words != "") {
              wordList = words.split(";");
              showOptions(wordList);
            }
          }
        }

      xmlHttp.open("GET", url, true);
      xmlHttp.send();
  }
}

function showOptions(wordList) {
  document.getElementById("dropdown").style.visibility = "visible";
  for (i = 0; i < 5; i++) {
    document.getElementById("dropdown").innerHTML = document.getElementById("dropdown").innerHTML + "<option value=\"word" + i + "\">" + wordList[i] + "</option>";
  }
}

function applySelect() {
  var drop = document.getElementById("dropdown");
  document.getElementById("keywords").value = drop.options[drop.selectedIndex].text;
}
