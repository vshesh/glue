module App exposing (..)

import Html exposing (Html, text, div, img, button, node)
import Html.Events exposing (onClick, on, keyCode)
import Html.Attributes exposing (class)
import Block
import Util exposing (Selection(..), Remote(..), inSelection, extent)
import ExtendedEvents exposing (..)
import Http
import Dict exposing (Dict)


type alias Model =
    { blocks : List Block.Block
    , selection : Selection
    , clipboard : List Block.Block
    , names : Maybe (List String)
    }


model : Model
model =
    { blocks = [ Block.init ]
    , selection = Single 0
    , clipboard = []
    , names = Nothing
    }


type Msg
    = NoOp
    | RecieveBlockNames (Result Http.Error (Dict String String))
    | AddBlock
    | ChangeBlock Int Block.Msg
    | CopySelection
    | CutSelection
    | PasteSelection
    | ExtendSelectionUp
    | ExtendSelectionDown


changeAt : Int -> (a -> a) -> Int -> a -> a
changeAt pos f i a =
    if pos == i then
        (f a)
    else
        a


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        NoOp ->
            model ! []

        RecieveBlockNames res ->
            { model
                | names =
                    Just <|
                        case res of
                            Err _ ->
                                [ "" ]

                            Ok d ->
                                "" :: (Dict.keys d)
            }
                ! []

        AddBlock ->
            ( { model
                | blocks = model.blocks ++ [ Block.init ]
                , selection = Single (List.length model.blocks)
              }
            , Cmd.none
            )

        ChangeBlock i msg ->
            let
                ( update, cmd ) =
                    -- the fnil here is just to make the compiler happy.
                    -- it should never trigger, since `i` is going to be a valid index.
                    Block.updateBlock msg
                        (Util.fnil Block.init <| Util.nth i model.blocks)
            in
                ( { model
                    | blocks = Util.splice i 1 [ update ] model.blocks
                    , selection = Single i
                  }
                , cmd |> Cmd.map (\a -> ChangeBlock i a)
                )

        CopySelection ->
            { model | clipboard = Util.sliceSel model.selection model.blocks } ! []

        CutSelection ->
            ( case model.selection of
                Single cell ->
                    { model
                        | blocks = Util.removeAt cell model.blocks
                        , selection = Single (cell - 1)
                        , clipboard = (List.take 1 (List.drop cell model.blocks))
                    }

                Range from to ->
                    { model
                        | blocks =
                            Util.splice
                                from
                                (extent model.selection)
                                []
                                model.blocks
                        , selection = Single (from - 1)
                        , clipboard = Util.sliceSel model.selection model.blocks
                    }
            , Cmd.none
            )

        PasteSelection ->
            ( case model.selection of
                Single cell ->
                    { model
                        | blocks = Util.splice cell 0 model.clipboard model.blocks
                        , selection = Range cell (cell + (List.length model.clipboard) - 1)
                    }

                Range from to ->
                    { model
                        | blocks =
                            Util.splice
                                from
                                (extent model.selection)
                                model.clipboard
                                model.blocks
                        , selection =
                            Range from <| from + (List.length model.clipboard) - 1
                    }
            , Cmd.none
            )

        ExtendSelectionUp ->
            ( { model
                | selection =
                    let
                        bound =
                            max 0
                    in
                        case model.selection of
                            Single cell ->
                                Range (bound (cell - 1)) cell

                            Range from to ->
                                Range (bound (from - 1)) to
              }
            , Cmd.none
            )

        ExtendSelectionDown ->
            ( { model
                | selection =
                    let
                        bound =
                            min <| (List.length model.blocks) - 1
                    in
                        case model.selection of
                            Single cell ->
                                Range cell <| bound (cell + 1)

                            Range from to ->
                                Range from <| bound (to + 1)
              }
            , Cmd.none
            )


view : Model -> Html Msg
view model =
    div
        [ class "app"
        , onShiftKeyDown
            (\shifted ->
                \key ->
                    if shifted then
                        case key of
                            40 ->
                                ExtendSelectionDown

                            38 ->
                                ExtendSelectionUp

                            _ ->
                                NoOp
                    else
                        NoOp
            )
        ]
        ([ node "h1" [] [ text "Glue Editor" ]
         , div []
            [ button [ onClick CopySelection ] [ text "Copy" ]
            , button [ onClick CutSelection ] [ text "Cut" ]
            , button [ onClick PasteSelection ] [ text "Paste" ]
            ]
         ]
            ++ (List.indexedMap
                    (\i ->
                        \x ->
                            Block.viewBlock x
                                (ChangeBlock i)
                                (Util.fnil [ "" ] model.names)
                                [ if inSelection model.selection i then
                                    "selected"
                                  else
                                    "unselected"
                                ]
                    )
                    model.blocks
               )
            ++ [ button [ onClick AddBlock ] [ text "Add Block" ] ]
        )


init : String -> ( Model, Cmd Msg )
init _ =
    ( model, Block.getBlockNames RecieveBlockNames )


subscriptions : Model -> Sub a
subscriptions model =
    Sub.none
