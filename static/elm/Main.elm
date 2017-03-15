module Main exposing (..)

import Html exposing (Html, div, text, textarea, button, node)
import Html.Events exposing (onClick, onInput)
import Html.Attributes exposing (attribute)
import Json.Decode as Json
import Json.Encode as Encode
import Http


type alias Elem =
    { tag : String, attrs : List ( String, String ), body : List Template }


type Template
    = Body String
    | Tag Elem


decodeTemplate : Json.Decoder Template
decodeTemplate =
    Json.oneOf [ Json.map Tag <| Json.lazy (\_ -> decodeElem), Json.map Body Json.string ]


decodeElem : Json.Decoder Elem
decodeElem =
    Json.map3 Elem
        (Json.field "tag" Json.string)
        (Json.field "attrs" (Json.keyValuePairs Json.string))
        (Json.field "body" (Json.list (Json.lazy (\_ -> decodeTemplate))))


template2Html : Template -> Html Msg
template2Html template =
    case template of
        Body str ->
            text str

        Tag { tag, attrs, body } ->
            node tag
                (List.map (\item -> (attribute (Tuple.first item) (Tuple.second item))) attrs)
                (List.map template2Html body)


result2Html : Result Http.Error Template -> Html Msg
result2Html res =
    case res of
        Err e ->
            case e of
                Http.BadUrl url ->
                    text ("Error: The url " ++ url ++ " doesn't exist!")

                Http.Timeout ->
                    text "Error: Timeout!"

                Http.NetworkError ->
                    text "Error: network error"

                Http.BadStatus r ->
                    text ((toString r.status.code) ++ " : " ++ r.status.message ++ " " ++ r.body)

                Http.BadPayload s _ ->
                    text (s ++ " was the error from Elm itself.")

        Ok t ->
            template2Html t


type alias Block =
    { name : String, contents : String, editing : Bool, template : Html Msg }


type alias Model =
    List Block


model : Model
model =
    []


type Msg
    = AddBlock
    | ChangeBlockContents Int String
    | ChangeBlockType Int String
    | ChangeBlockTemplate Int (Result Http.Error Template)
    | ToggleEdit Int


changeAt : Int -> (a -> a) -> Int -> a -> a
changeAt pos f i a =
    if pos == i then
        (f a)
    else
        a


getTemplate : Int -> String -> Cmd Msg
getTemplate i string =
    let
        url =
            "/render"

        request =
            Http.post url
                (Http.jsonBody
                    (Encode.object [ ( "text", Encode.string string ) ])
                )
                decodeTemplate
    in
        Http.send (ChangeBlockTemplate i) request


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        AddBlock ->
            ( model ++ [ { name = "", contents = "", editing = True, template = (text "") } ], Cmd.none )

        ChangeBlockContents i c ->
            ( List.indexedMap (changeAt i (\a -> { a | contents = c })) model
            , getTemplate i c
            )

        ChangeBlockTemplate i t ->
            ( List.indexedMap (changeAt i (\a -> { a | template = (result2Html t) })) model
            , Cmd.none
            )

        ChangeBlockType i t ->
            ( List.indexedMap (changeAt i (\a -> { a | name = t })) model, Cmd.none )

        ToggleEdit i ->
            ( List.indexedMap (changeAt i (\a -> { a | editing = not a.editing })) model
            , Cmd.none
            )


viewBlock : Int -> Block -> Html Msg
viewBlock i block =
    div [ attribute "class" "block" ]
        [ if block.editing then
            (textarea [ onInput (\s -> ChangeBlockContents i s) ] [ text block.contents ])
          else
            block.template
        , (button [ ToggleEdit i |> onClick ]
            [ text
                (if block.editing then
                    "Done"
                 else
                    "Edit"
                )
            ]
          )
        ]


view : Model -> Html Msg
view model =
    div []
        ((List.indexedMap viewBlock model) ++ [ button [ onClick AddBlock ] [ text "Add Block" ] ])


main : Program Never Model Msg
main =
    Html.program
        { view = view
        , update = update
        , subscriptions = \_ -> Sub.none
        , init = ( model, Cmd.none )
        }
