<script>
// Get the modal
var modal1 = document.getElementById('id01');

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal1) {
        modal1.style.display = "none";
    }
}

var modal2 = document.getElementById('id02');

window.onclick = function(event){
	if (event.target == modal2){
		modal2.style.display = "none";
	}
}

$(document).ready(function(){
	$.ajaxSetup({ cache: false });
	$('#search').keypress(function(){
	$('#result').html('');
	var searchField = $('#search').val();
	var expression = new RegExp(searchField, "i");
	$.getJSON('http://signals.pythonanywhere.com/codes?val=', function(data) {
		if(searchField.length > 2){
			$.each(data, function(key, value){
				if (value.code.search(expression) != -1 || value.value.search(expression) != -1)
				{
					setTimeout(function(){$('#result').append('<li class="list-group-item link-class">'+value.code+' | <span class="text-primary">'+value.value+'</span></li>')},0);
				}
			});
		}
	});
 });
 
 $('#result').on('click', 'li', function() {
  var click_text = $(this).text().split('|');
  $('#search').val($.trim(click_text[0]));
  $("#result").html('');
 });
});

/*function register(){
	var xhr = new XMLHttpRequest();
	var url = "http://signals.pythonanywhere.com/register";
	xhr.open("POST", url, true);
	xhr.setRequestHeader("Content-type", "application/json");
	xhr.onreadystatechange = function () {
		if (xhr.readyState === 4 && xhr.status === 200) {
			var json = JSON.parse(xhr.responseText);
			console.log(json.uname + ", you are registered");
		}
	};
	var uname = document.getElementById('u2');
	var pwd = document.getElementById('p2');
	var data = JSON.stringify({"username": uname, "password": pwd});
	xhr.send(data);
}*/
</script>