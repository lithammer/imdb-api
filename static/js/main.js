$('form').submit(function(event) {
	event.preventDefault();

	var movie = $('#movie'),
		id = $('#search-id').val();

	movie.html('<img src="/static/img/loading.gif">');

	var request = $.getJSON('/movie/' + id + '/0/150', function(data) {
		var html = '';
		html += '<img src="' + data.poster + '" class="img-polaroid">';
		html += '<section class="movie-info">';
		html += '<h2>' + data.title + '</h2>';
		html += '<p>Rating: ' + data.vote_average + ' (' + data.vote_count + ' votes)</p>';
		html += '<p>Release date: ' + data.release_date + '</p>';
		html += '<p>' + data.overview + '</p>';
		html += '</section>';
		movie.html(html);
	});

	request.fail(function(jqXHR, textStatus) {
		movie.html('<div class="alert alert-error">Bad request!</div>');
	});
});
