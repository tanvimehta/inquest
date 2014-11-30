var numSuggestions = 5;
function autoComp() {
	var words = [];
  var url = window.location.origin;
  document.getElementById("dropdown").innerHTML = "";
  document.getElementById("dropdown").style.visibility = "hidden";
    if (document.getElementById("keywords").value != "") {
      url = url + "/autocomplete?input="+ document.getElementById("keywords").value;
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
  document.getElementById("dropdown").innerHTML = "";
  for (i = 0; i < numSuggestions; i++) {
    if (wordList[i] != undefined) {
      document.getElementById("dropdown").size = i + 1;
      document.getElementById("dropdown").innerHTML = document.getElementById("dropdown").innerHTML + "<option value=\"word" + i + "\">" + wordList[i] + "</option>";
    }
    else
      break;
  }
  
  if (wordList[0] != undefined) {
    currentValue = document.getElementById("keywords").value;
    newValue = wordList[0];
    start = currentValue.length;
    end = newValue.length - 1;
    document.getElementById("keywords").value = newValue;
    createSelection(document.getElementById("keywords"), start, end);
  }
}

function applySelect() {
  var drop = document.getElementById("dropdown");
  document.getElementById("keywords").value = drop.options[drop.selectedIndex].text;
}

function createSelection(field, start, end) {
    if( field.createTextRange ) {
      var selRange = field.createTextRange();
      selRange.collapse(true);
      selRange.moveStart('character', start);
      selRange.moveEnd('character', end);
      selRange.select();
      field.focus();
    } else if( field.setSelectionRange ) {
      field.focus();
      field.setSelectionRange(start, end);
    } else if( typeof field.selectionStart != 'undefined' ) {
      field.selectionStart = start;
      field.selectionEnd = end;
      field.focus();
    }
  }
