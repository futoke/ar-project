module Main exposing (..)

import Html exposing (..)
import Html.Events exposing (..)
import Html.Attributes exposing (..)

import List exposing (..)
import Navigation
import String


main : Program Never Model Msg
main =
    Navigation.program UrlChange
        { init = init
        , view = view
        , update = update
        , subscriptions = subscriptions
        }

-- Model


type alias Model =
    { currentRoute : Navigation.Location
    , users : List User
    }


type alias User =
    { id : Int
    , name : String
    , hobbies : List Hobby
    }


type alias Hobby =
    String


type alias RoutePath =
    List String


initialUsers : List User
initialUsers =
    [ User 1 "Fred" [ "running", "climbing" ]
    , User 2 "Joe" [ "kayaking", "poodle grooming", "goat soccer" ]
    , User 3 "Mark" [ "knitting", "kombucha making", "nya" ]
    ]


init : Navigation.Location -> ( Model, Cmd Msg )
init location =
    { currentRoute = location
    , users = initialUsers
    }
        ! []

-- Update


type Msg
    = UrlChange Navigation.Location


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        UrlChange location ->
            { model | currentRoute = location } ! []


-- Navigation


fromUrlHash : String -> RoutePath
fromUrlHash urlHash =
    urlHash |> String.split "/" |> drop 1



-- View


userFromId : List User -> String -> Maybe User
userFromId users idStr =
    let
        id =
            Result.withDefault 0 (String.toInt idStr)
    in
        List.filter (\user -> id == user.id) users
            |> head


loginPage : Html Msg
loginPage =
    div [ class "container" ]
    [ div [ class "mainbox col-md-6 col-md-offset-3 col-sm-6 col-sm-offset-3", id "loginbox" ]
        [ div [ class "panel panel-primary" ]
            [ div [ class "panel-heading" ]
                [ div [ class "panel-title text-center" ]
                    [ text "Вход в панель управления" ]
                ]
            , div [ class "panel-body" ]
                [ Html.form [ class "form-horizontal", enctype "multipart/form-data", id "form", method "POST", name "form" ]
                    [ div [ class "input-group" ]
                        [ span [ class "input-group-addon" ]
                            [ i [ class "glyphicon glyphicon-user" ]
                                []
                            ]
                        , input [ class "form-control", id "user", name "user", placeholder "Логин", type_ "text", value "" ]
                            []
                        ]
                    , div [ class "input-group" ]
                        [ span [ class "input-group-addon" ]
                            [ i [ class "glyphicon glyphicon-lock" ]
                                []
                            ]
                        , input [ class "form-control", id "password", name "password", placeholder "Пароль", type_ "password" ]
                            []
                        ]
                    , div [ class "form-group" ]
                        [ div [ class "col-sm-12 controls" ]
                            [ button [ class "btn btn-primary pull-right", type_ "submit" ]
                                [ i [ class "glyphicon glyphicon-log-in" ]
                                    []
                                , text " Войти"
                                ]
                            ]
                        ]
                    ]
                ]
            ]
        ]
    ]


aboutPage : Html Msg
aboutPage =
    h1 [] [ text "about" ]


notFoundPage : Html Msg
notFoundPage =
    h1 [] [ text "Page Not Found" ]


usersPage : Model -> Html Msg
usersPage model =
    div []
        [ h1 [] [ text "Users" ]
        , ul []
            (List.map
                (\user ->
                    li [] [ link user.name ("/#/users/" ++ toString user.id) ]
                )
                model.users
            )
        ]


userPage : Model -> String -> Html Msg
userPage model idStr =
    let
        user =
            userFromId model.users idStr
    in
        case user of
            Just u ->
                div []
                    [ h1 [] [ text ("User Profile") ]
                    , h2 []
                        [ link u.name ("/#/users/" ++ idStr ++ "/hobbies") ]
                    ]

            Nothing ->
                div []
                    [ h1 [] [ text "User not found" ]
                    ]


hobbiesPage : Model -> String -> Html Msg
hobbiesPage model idStr =
    let
        user =
            userFromId model.users idStr
    in
        case user of
            Just u ->
                div []
                    [ h1 [] [ text "User Hobbies" ]
                    , ul []
                        (List.map (\hobby -> li [] [ text hobby ]) u.hobbies)
                    ]

            Nothing ->
                text "user not found"


pageBody : Model -> Html Msg
pageBody model =
    let
        routePath =
            fromUrlHash model.currentRoute.hash
    in
        case routePath of
            [] ->
                loginPage

            [ "login" ] ->
                loginPage

            [ "about" ] ->
                aboutPage

            [ "users" ] ->
                usersPage model

            [ "users", userId ] ->
                userPage model userId

            [ "users", userId, "hobbies" ] ->
                hobbiesPage model userId

            _ ->
                notFoundPage


menuStyle : Html.Attribute Msg
menuStyle =
    style [ ( "list-style-type", "none" ) ]


menuElementStyle : Html.Attribute Msg
menuElementStyle =
    style [ ( "display", "inline" ), ( "margin-left", "10px" ) ]


link : String -> String -> Html Msg
link name url =
    a [ href url ] [ text name ]


view : Model -> Html Msg
view model =
    div [ style [ ( "margin", "20px" ) ] ]
        -- [ ul [ menuStyle ]
        --     [ li [ menuElementStyle ] [ link "Страница входа" "#/login" ]
        --     , li [ menuElementStyle ] [ link "about" "#/about" ]
        --     , li [ menuElementStyle ] [ link "users" "#/users" ]
        --     ]
        -- , pageBody model
        -- ]
        [ pageBody model ]



-- Subscriptions


subscriptions : Model -> Sub Msg
subscriptions model =
    Sub.none