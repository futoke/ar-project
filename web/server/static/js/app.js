var app = angular.module("app", [
    // 'ngFileUpload',
    // "angular-thumbnails",
    "angular-uuid",
    "images-resizer"
]);


app.directive("fileRead", ["resizeService", function(resizeService) {
    return {
        scope: {
            fileRead: "="
        },
        link: function (scope, element, attributes) {
            element.bind("change", function (changeEvent) {
                scope.fileRead = {};

                scope.$apply(function () {
                    // Get image name.
                    scope.fileRead.name = changeEvent.target.files[0].name;
                });

                var reader = new FileReader();
                reader.onload = function (loadEvent) {
                    scope.$apply(function () {
                        // Get image content.
                        scope.fileRead.content = loadEvent.target.result;

                        // Resize images.
                        resizeService.resizeImage(loadEvent.target.result, {
                            height: 100,
                            sizeScale: 'ko'
                        }).then(function (image) {
                            scope.fileRead.thumbnail = image;
                        });
                    });
                };
                reader.readAsDataURL(changeEvent.target.files[0]);
            });
        }
    };
}]);

app.controller("ModelsTableCtrl", function ($scope, $http, $log, uuid) {
    $http.get("/load_models").then(successCallback, errorCallback);

    function successCallback(response) {
        console.log(response);
        $scope.models = response.data;
    }
    function errorCallback(error){
        console.log(error);
    }

    $scope.is_edited = false;

    $scope.editModel = function (index) {
        if (!$scope.is_edited) {
            $scope.is_edited = true;
            $scope.models[index].is_edited = true;
        }
    };

    $scope.saveModel = function (index) {
        $scope.is_edited = false;
        $scope.models[index].is_edited = false;

        var now = new Date();
        $scope.models[index].date = now.toLocaleDateString();
        $scope.models[index].time = now.toLocaleTimeString();

        var url = "/save_model/" + $scope.models[index].id;
        $http.post(url, $scope.models[index]);
    };

    $scope.cancelModel = function (index) {
        var url = "/load_model/" + $scope.models[index].id;
        $http.get(url).then(successCallback, errorCallback);

        function successCallback(response) {
            $scope.models[index] = response.data;
        }
        function errorCallback(error){
            console.log(error);
        }
        $scope.is_edited = false;
        $scope.models[index].is_edited = false;
    };

    $scope.removeModel = function (index) {
        var url = "/remove_model/" + $scope.models[index].id;
        $http.post(url, $scope.models[index]);

        $scope.models.splice(index, 1);
    };

    $scope.addModel = function () {
        $scope.inserted = {
            id: uuid.v4(),
            is_edited: false,
            name: "",
            date: {},
            time: {},
            preview: {},
            mesh: {},
            texture: {}
        };
        $scope.models.push($scope.inserted);

        $http.post("/add_model", $scope.inserted);
    };

    // $scope.statuses = [
    //     {
    //         value: 1,
    //         text: 'status1'
    //     },
    //     {
    //         value: 2,
    //         text: 'status2'
    //     },
    //     {
    //         value: 3,
    //         text: 'status3'
    //     },
    //     {
    //         value: 4,
    //         text: 'status4'
    //     }
    // ];
    // $scope.groups = [];
    // $scope.loadGroups = function () {
    //     // return $scope.groups.length ? null : $http.get('/groups').success(function (data) {
    //     //     $scope.groups = data;
    //     // });
    //     $scope.groups = {};
    // };
    // $scope.showGroup = function (user) {
    //     if (user.group && $scope.groups.length) {
    //         var selected = $filter('filter')($scope.groups, {
    //             id: user.group
    //         });
    //         return selected.length ? selected[0].text : 'Not set';
    //     } else {
    //         return user.groupName || 'Not set';
    //     }
    // };
    // $scope.showStatus = function (user) {
    //     var selected = [];
    //     if (user.status) {
    //         selected = $filter('filter')($scope.statuses, {
    //             value: user.status
    //         });
    //     }
    //     return selected.length ? selected[0].text : 'Not set';
    // };
    // $scope.checkName = function (data, id) {
    //     if (id === 2 && data !== 'awesome') {
    //         return "Username 2 should be `awesome`";
    //     }
    // };
    // $scope.saveUser = function (data, id) {
    //     //$scope.user not updated yet
    //     angular.extend(data, {
    //         id: id
    //     });
    //     // return $http.post('/saveUser', data);
    // };
    // // remove user
    // $scope.removeUser = function (index) {
    //     $scope.users.splice(index, 1);
    // };
    // // add user
    // $scope.addUser = function () {
    //     $scope.inserted = {
    //         id: $scope.users.length + 1,
    //         name: '',
    //         status: null,
    //         group: null
    //     };
    //     $scope.users.push($scope.inserted);
    // };
});