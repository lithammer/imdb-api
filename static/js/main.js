function AppCtrl($scope, $http) {
	$scope.search = function() {
		$scope.loading = true;
		$scope.movie = null;

		$http.get('/search/' + $scope.imdbId).then(function(response) {
			$scope.loading = false;
			$scope.movie = response.data;
		});
	};
}
