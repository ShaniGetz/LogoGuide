angular.module('LogoGuide', ['ngMaterial'])

    .config(function ($mdThemingProvider) {
        $mdThemingProvider.theme('default')
            .primaryPalette('pink', {
                'default': '500'
            })
            .accentPalette('orange', {
                'default': '500'
            })
    })

    .run([
        function () {

            // global constants

        }])

    .controller('LogoGuideController', function ($scope, $http, $timeout) {

        var DEFAULT_BUTTON_TITLE = "Start";
        var AGAIN_BUTTON_TITLE = "Again!";
        var AWAITING_INPUT_STATUS = 0;
        var LOADING_STATUS = 1;
        var ANSWERED_STATUS = 2;
        var base_url = "http://127.0.0.1:8000";

        var SERIF_ICON = "assets/serif.png";
        var SANS_SERIF_ICON = "assets/sans-serif.png";
        var ROUND_ICON = "assets/round.png";
        var SHARP_ICON = "assets/sharp.png";

        $scope.query = {};
        $scope.noCache = true;

        $scope.status = AWAITING_INPUT_STATUS;
        $scope.goTitle = DEFAULT_BUTTON_TITLE;
        $scope.presentResults = false; // For animation.
        $scope.answer = "";
        $scope.guidelines = "";
        $scope.formattedGuidelines = "";
        $scope.selectedItem = null;
        $scope.sourceText = null;
        $scope.destinationText = null;


        var formatResult = function (vec, is_animal, animal) {
            var res = [];
            if (vec[0][0] === 1) {
                var fontGuideline = 'A ';
                var fontIcon;
                var fontFeature = vec[0][2];
                if (fontFeature === 0) {
                    fontGuideline += 'serif font ';
                    fontIcon = SERIF_ICON;
                } else {
                    fontGuideline += 'san-serif font ';
                    fontIcon = SANS_SERIF_ICON;
                }
                fontGuideline += "logotype.";
                res.push([fontIcon, fontGuideline]);

                if (vec[0][1] === 1) {
                    var symbolGuideline = "A ";
                    var symbolFeature = vec[0][3];
                    var styleIcon;
                    if (symbolFeature === 0) {
                        symbolGuideline += 'rounded ';
                        styleIcon = ROUND_ICON;
                    } else {
                        symbolGuideline += 'sharped ';
                        styleIcon = SHARP_ICON;
                    }
                    var animalGuideline = "";
                    var suggestAnimalGuideline = "";
                    if (animal) {
                        if(is_animal === 1){
                            animalGuideline += " of a " + animal;
                        }
                        if(is_animal === 0){
                            suggestAnimalGuideline += "If you would like a symbol of an animal, choose: " + animal;
                        }
                    }
                    symbolGuideline += 'shaped symbol' + animalGuideline + ' as a logomark.';
                    res.push([styleIcon, symbolGuideline]);
                    if (suggestAnimalGuideline.length > 0) {
                        res.push(["", suggestAnimalGuideline])
                    }
                }

                return res;
            }
        };

        var formatNN = function (nn) {
            for (var i = 0; i < nn.length; i++) {
                nn[i][1] *= 1000;
                nn[i][1] = Math.round(nn[i][1]);
            }
            nn.sort(function (a,b) {
                return a[1]-b[1];
            });
            return nn;
        };

        var formatNA = function (na) {
            na.sort(function(a, b) {
                return b[1] - a[1];
            });
            for (var i = 0; i < na.length; i++) {
                na[i][1] *= 100;
                na[i][1] = Math.round(na[i][1]);
            }
            return na;
        };

        $scope.start = function (event) {
            if ($scope.status === AWAITING_INPUT_STATUS) {
                var url = base_url + '/logoguide/';
                var params = {
                    description: $scope.query.description,
                };
                if (!params.description || params.description.length === 0) {
                    $scope.status = ANSWERED_STATUS;
                    $scope.answer = "You forgot to type a description!";
                    return;
                }
                $http.get(url, {params: params})
                    .then(function (response) {
                            // success
                            $scope.guidelines = response.data['guidelines'];
                            $scope.is_animal = response.data['is_animal'];
                            $scope.animal = response.data['animal'];
                            $scope.nn = response.data['nearest_neighbors'];
                            $scope.na = response.data['nearest_animals'];
                            if ($scope.guidelines) {
                                if ($scope.guidelines.length === 0) {
                                    $scope.answer = "There was a problem.";
                                } else {
                                    $scope.answer = "Your logo should have:";
                                    $scope.formattedGuidelines = formatResult($scope.guidelines, $scope.is_animal, $scope.animal);
                                    $scope.formattedNN = formatNN($scope.nn);
                                    if ($scope.na) {
                                        $scope.formattedNA = formatNA($scope.na);
                                    }
                                }
                            } else {
                                $scope.status = ANSWERED_STATUS;
                                $scope.answer = "Error";
                                $scope.guidelines = "";
                                return;
                            }
                            $scope.status = ANSWERED_STATUS;
                            $scope.goTitle = AGAIN_BUTTON_TITLE;
                            $timeout(function () {
                                $scope.presentResults = true;
                            }, 500);
                        },
                        function (err) {
                            // error, probably because there is no path
                            $scope.status = ANSWERED_STATUS;
                            $scope.answer = "There was an error :(";
                            $scope.guidelines = "";
                            $scope.goTitle = AGAIN_BUTTON_TITLE;
                            $timeout(function () {
                                $scope.presentResults = true;
                            }, 500);
                        });
            } else if ($scope.status === ANSWERED_STATUS) {
                $scope.status = AWAITING_INPUT_STATUS;
                $scope.goTitle = DEFAULT_BUTTON_TITLE;
                $scope.presentResults = false;
            }
        };
    });
