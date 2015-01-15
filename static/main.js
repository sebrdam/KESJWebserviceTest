(function () {

  'use strict';

  angular.module('KESJApp', [])

  .controller('kesjAppController', ['$scope', '$log', '$http', '$timeout', function($scope, $log, $http, $timeout) {
    $scope.getResults = function(data1) {

      $log.log("test")

      // get the component from the input
      //var userInput = document.getElementById("form").name
	var userInput = data1

        var timeout = ""

        var poller = function() {
          // fire the request
          $http.get('/results/' + userInput).
            success(function(data, status, headers, config) {
              if(status === 202) {
                $log.log(data, status)
              } else if (status === 200){
                $log.log(data)
                $scope.component = data;
                $timeout.cancel(timeout);
                return false;
              }
              // continue to call the poller() function every 2 seconds
              // until the timout is cancelled
              timeout = $timeout(poller, 2000);
            });
        };
        poller();
      }



$scope.getResults1 = function(bas) {

//test	
var basje = bas

	$log.log(basje)

}

$scope.getResults2 = function() {
	var users = {
  1: {
    name: 'john',
    email: 'john@email.com'
  },
  2: {
    name: 'peter',
    email: 'peter@email.com'
  },
  3: {
    name: 'max',
    email: 'max@email.com'
  }
};

  
    $scope.users = users;
  }







    }
  

  ]);



}());