module Block exposing (..)

import Html exposing (..)
import Html.Events exposing (onInput, onClick)
import Html.Attributes exposing (attribute)
import Http
import Json.Encode as Encode
import Util
import Template


type alias Block =
    { name : Maybe String
    , contents : String
    , editing : Bool
    , template : Template.Template
    }


type Msg
    = ChangeName String
    | ChangeContents String
    | ToggleEdit
    | ChangeTemplate (Result Http.Error Template.Template)


updateBlock : Msg -> Block -> ( Block, Cmd Msg )
updateBlock msg block =
    case msg of
        ChangeName name ->
            ( { block | name = Just name }, getTemplate (Just name) block.contents ChangeTemplate )

        ChangeContents contents ->
            ( { block | contents = contents }, getTemplate block.name contents ChangeTemplate )

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


viewBlock : Block -> (String -> a) -> (String -> a) -> a -> Html a
viewBlock block inputMsg nameMsg editMsg =
    div [ attribute "class" "block" ]
        [ if block.editing then
            (textarea [ onInput inputMsg ] [ text block.contents ])
          else
            Template.template2Html block.template
        , (node "span"
            [ attribute "class" "config" ]
            [ (input
                [ onInput <| nameMsg ]
                [ text
                    (case block.name of
                        Nothing ->
                            ""

                        Just s ->
                            s
                    )
                ]
              )
            , (button [ onClick <| editMsg ]
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
