var numSuggestions = 6;
var evt;
var userQuery;

window.onload = function() {
  document.getElementById("keywords").focus();
};

function autoComp() {
	var words = [];
  var url = window.location.origin;
  document.getElementById("dropdown").innerHTML = "";
  document.getElementById("dropdown").style.visibility = "hidden";
    if (document.getElementById("keywords").value != "") {
      index = getUserQuery(document.getElementById("keywords").value);
      if (index > 0 )
        userQuery = (document.getElementById("keywords").value).substring(0, index);
      else
        userQuery = document.getElementById("keywords").value;

      url = url + "/autocomplete?input="+ userQuery;
      var xmlHttp = new XMLHttpRequest();
      evt = event;
      xmlHttp.onreadystatechange=function()
        {
        if (xmlHttp.readyState==4 && xmlHttp.status==200)
          {
            words = xmlHttp.responseText;
            if (words != "") {
              wordList = words.split(";");
              showOptions(wordList, evt, userQuery);
            }
          }
        }

      xmlHttp.open("GET", url, true);
      xmlHttp.send();
  }
}

function getUserQuery(wholeQuery) {
  textComponent = document.getElementById("keywords");
  if (textComponent.selectionStart != undefined)
  {
    var startPos = textComponent.selectionStart;
    var endPos = textComponent.selectionEnd;
    selected = textComponent.value.substring(startPos, endPos)
    return wholeQuery.indexOf(selected);
  }
  else
    return -1
}

function showOptions(wordList, evt, query) {
  document.getElementById("dropdown").innerHTML = "";
  for (i = 1; i < numSuggestions; i++) {
    if (wordList[i] != undefined) {
      document.getElementById("dropdown").size = i;
      if (i <= parseInt(wordList[0]))
        document.getElementById("dropdown").innerHTML = document.getElementById("dropdown").innerHTML + "<option style=\"color:#52188C;font-weight:bolder\" value=\"word" + i + "\">" + wordList[i] + "</option>";
      else
        document.getElementById("dropdown").innerHTML = document.getElementById("dropdown").innerHTML + "<option value=\"word" + i + "\">" + wordList[i] + "</option>";

    }
    else
      break;
    document.getElementById("dropdown").style.visibility = "visible";
  }

  var key = evt.keyCode || evt.charCode;

    if( key > 48 && key < 90 ) {
    if (wordList[1] != undefined) {
      currentValue = query;
      newValue = wordList[1];
      start = currentValue.length;
      end = newValue.length;
      document.getElementById("keywords").value = newValue;
      createSelection(document.getElementById("keywords"), start, end);
    }
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
