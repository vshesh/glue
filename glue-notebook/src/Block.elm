module Block exposing (..)

import Html exposing (..)
import Html.Events exposing (onInput, onClick, onDoubleClick, onWithOptions)
import ExtendedEvents exposing (..)
import Html.Attributes exposing (attribute, classList)
import Http
import Dict exposing (Dict)
import Json.Encode as Encode
import Json.Decode as Decode
import Util
import Template


type alias Block =
    { name : Maybe String
    , contents : String
    , editing : Bool
    , template : Template.Template
    }


type Msg
    = NoOp
    | ChangeName String
    | ChangeContents String
    | ToggleEdit
    | ChangeTemplate (Result Http.Error Template.Template)


updateBlock : Msg -> Block -> ( Block, Cmd Msg )
updateBlock msg block =
    case msg of
        NoOp ->
            block ! []

        ChangeName name ->
            ( { block | name = Just name }
            , getTemplate (Just name) block.contents ChangeTemplate
            )

        ChangeContents contents ->
            ( { block | contents = contents }
            , getTemplate block.name contents ChangeTemplate
            )

        ToggleEdit ->
            ( { block | editing = not block.editing }, Cmd.none )

        ChangeTemplate res ->
            ( { block | template = Util.processResult Template.Body res }, Cmd.none )


init : Block
init =
    { name = Nothing, contents = "", editing = True, template = Template.Body "" }


getTemplate : Maybe String -> String -> (Result Http.Error Template.Template -> b) -> Cmd b
getTemplate name text msg =
    let
        url =
            "/render"

        request =
            Http.post url
                (Http.jsonBody
                    (Encode.object
                        [ ( "text", Encode.string text )
                        , ( "name", Encode.string <| Util.fnil "" name )
                        ]
                    )
                )
                Template.decodeTemplate
    in
        Http.send msg request


getBlockNames : (Result Http.Error (Dict String String) -> msg) -> Cmd msg
getBlockNames msg =
    let
        url =
            "/blocknames"

        decodeBlockNames =
            Decode.field "blocks" <| Decode.dict Decode.string

        request =
            Http.post url (Http.jsonBody (Encode.object [])) decodeBlockNames
    in
        Http.send msg request


viewBlock : Block -> (Msg -> a) -> List String -> List String -> Html a
viewBlock block msg names extraClasses =
    div
        [ classList <| List.map (\x -> ( x, True )) <| [ "block" ] ++ extraClasses
        , onDoubleClick <| msg ToggleEdit
        , onClick <| msg NoOp
        ]
        [ if block.editing then
            (textarea [ onInput <| msg << ChangeContents ] [ text block.contents ])
          else
            Template.template2Html block.template
        , (node "span"
            [ attribute "class" "config" ]
            [ select
                [ onChange <| msg << ChangeName ]
              <|
                List.map (\x -> option [] [ text x ]) names
            , (button
                [ onLocalClick <| msg ToggleEdit ]
                [ text
                    (if block.editing then
                        "Done"
                     else
                        "Edit"
                    )
                ]
              )
            ]
          )
        ]
