<script src="http://code.jquery.com/jquery-2.1.3.min.js"></script>
<script>
$(document).ready(function() {
	$('form').submit(function(event) {
		
		var facultyId = $("#facultyId").val();
		
			event.preventDefault()
			var formdata = new FormData($('form')[0]);
			console.log(formdata);
			
			$.ajax({
			type : 'POST'
			url : '/upload'
			processData : false
			contentType : false
			succes : function() {
					alert('test')
			}
			});
			
			});

		});
</script>