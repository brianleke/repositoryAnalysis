app.controller("resultsController", function($scope, JsonReader) {
    $scope.initializeValues = function(){
    	JsonReader.read().then(function(response){
    		var obtainedResults = response.data;
    		$scope.compromisedResults = obtainedResults.filter(function(obtainedResult){
    			return obtainedResult.results.length > 0;
    		});
    	});
    };

}).factory('JsonReader', function($http){
	return {
		read: function(){
			return $http.get('results.json');
		}
	}
});