function AppCtrl($scope, $http) {
	$scope.search = function() {
		$scope.loading = true;
		$scope.movie = null;

		$http.get('/search/' + $scope.imdbId.match(/tt[\d]{7}/)[0]).then(function(response) {
			$scope.loading = false;
			$scope.movie = response.data;
		});
	};
}
