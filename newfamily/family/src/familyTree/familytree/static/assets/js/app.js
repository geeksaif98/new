let evsApp = angular.module('evsApp', []);

evsApp.config(function ($interpolateProvider,$httpProvider) {
    $interpolateProvider.startSymbol('[[').endSymbol(']]');
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken'
});

evsApp.controller("userCtrl", ['$scope', '$rootScope', '$http', function ($scope, $rootScope, $http, $timeout) {

    $scope.fathers_list = [];
    $scope.mothers_list = [];

    $scope.init = function () {
        $scope.get_fathers();
    };

    $scope.user = {
        gender: 'male',
        fathe_is_family: false,
        parents_modal: function ($event) {
            let btn = $($event.currentTarget);
            let modal = $(btn.data('target'));
            modal.modal('show');
            $scope.user.parents_modal.type = btn.data('parent-type');
        },
        marriage_list: [],
        marriage_modal_data: [],
        marriage_modal: function ($event) {
            let btn = $($event.currentTarget);
            let modal = $(btn.data('target'));
            modal.modal('show');
            $scope.user.marriage_modal.type = btn.data('marriage-type');
        },
        marriage_modal_save: function ($event) {
            let btn = $($event.currentTarget);
            let modal = $(btn.data('target'));
            $scope.user.marriage_list.push({
                f_name: $scope.user.marriage_modal_data.fname,
                s_name: $scope.user.marriage_modal_data.sname,
                birthdate: $scope.user.marriage_modal_data.birthdate,
                gender: $scope.user.marriage_modal_data.gender,
                is_dead: $scope.user.marriage_modal_data.is_dead,
                status: $scope.user.marriage_modal_data.status,
                date_status: $scope.user.marriage_modal_data.date_status,
                dead_date: $scope.user.marriage_modal_data.dead_date
            });
            $scope.user.marriage_modal_data = [];
        },
        marriage_modal_remove: function ($event) {
            let btn = $($event.currentTarget);
            let index = $scope.user.marriage_list.indexOf(btn.data('row-id'));
            $scope.user.marriage_list.splice(index, 1);
        },
        submited_data: {},
        formSubmit: function ($event) {
            let form = $($event.currentTarget);
            let data = {
                national_id : $scope.user.national_id,
                f_name: $scope.user.fname,
                birthdate: $scope.user.birthdate,
                gender: $scope.user.gender,
                is_dead: $scope.user.is_dead,
                dead_date: $scope.user.dead_date,
                father: $scope.user.father,
                is_family: $scope.user.fathe_is_family,
                mother: $scope.user.mother,
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
            };
            $event.preventDefault();
            $http.post(form.attr('action'), data).then(function (output) {
                if (output.data === "INVALID DEATH OR BIRTH DATE"){
                    alert("check your dates !");
                }else if(output.data === "DONE"){
                    let id = $scope.user.national_id;
                    // window.location.href = '{% url "profile/" id %}'
                    alert("DONE")
                }

            });


        }
    };

    $scope.get_fathers = function () {
        $http.get($('#fathers-select').data('ajax-url'))
            .then(function (output) {
                $scope.fathers_list = output.data;
                $('#fathers-select').chosen('destroy');
                setTimeout(function () {
                    $('#fathers-select').chosen();
                    // $scope.get_mothers();
                }, 100);

            });
    };


    $scope.get_mothers = function () {
        $scope.config = {
            params: {
                husband_id: $scope.user.father
            }
        };
        $http.get($('#mothers-select').data('ajax-url'),$scope.config )
            .then(function (female_output) {
                $scope.mothers_list = female_output.data;
                $('#mothers-select').chosen('destroy');
                setTimeout(function () {
                    $('#mothers-select').chosen();
                }, 100);


            });
    };


}]);

evsApp.directive("formatDate", function () {
    return {
        require: 'ngModel',
        link: function (scope, elem, attr, modelCtrl) {
            modelCtrl.$formatters.push(function (modelValue) {
                if (modelValue) {
                    return new Date(modelValue);
                } else {
                    return null;
                }
            });
        }
    };
});
