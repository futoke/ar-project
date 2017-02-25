var app = angular.module("app", [
    // 'ngFileUpload',
    // "ui.thumbnail",
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
                    // Get file name.
                    scope.fileRead.name = changeEvent.target.files[0].name;
                });

                var reader = new FileReader();
                reader.onload = function (loadEvent) {
                    scope.$apply(function () {
                        // Get file content.
                        var filetype = changeEvent.target.files[0].type;
                        // Resize image.
                        if (filetype == 'image/jpeg' || filetype == 'image/png') {
                            resizeService.resizeImage(loadEvent.target.result, {
                                height: 100,
                                width: 100,
                                sizeScale: 'ko'
                            })
                            .then(function(image) {
                                scope.fileRead.content = image;
                            });
                        } else {
                            scope.fileRead.content = loadEvent.target.result;
                        }
                    });
                };
                reader.readAsDataURL(changeEvent.target.files[0]);
            });
        }
    };
}]);

app.controller("ModelsTableCtrl", function ($scope, $http, $log, uuid, resizeService) {

    $http.get("/load_models").then(successCallback, errorCallback);

    function successCallback(response) {
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

        // Maybe check the changes here.

        var now = new Date();
        $scope.models[index].date = now.toLocaleDateString();
        $scope.models[index].time = now.toLocaleTimeString();

        var url = "/save_model/" + $scope.models[index].id;
        $http.post(url, $scope.models[index]);
    };

    $scope.cancelModel = function (index) {
        // Load only meta data without content!
        var url = "/load_model/" + $scope.models[index].id;
        $http.get(url).then(successCallback, errorCallback);

        function successCallback(response) {
            $scope.models[index] = response.data;
        }
        function errorCallback(error) {
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
            preview: {
                name: "",
                content: ""
            },
            zipfile: {name: "", content: ""}
        };
        $scope.models.push($scope.inserted);

        $http.post("/add_model", $scope.inserted);
    };
});