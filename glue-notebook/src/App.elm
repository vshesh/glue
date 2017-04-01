module App exposing (..)

import Html exposing (Html, text, div, img, button)
import Html.Events exposing (onClick)
import Block
import Util


type Selection
    = Single Int
    | Range Int Int


type alias Model =
    { blocks : List Block.Block
    , selection : Selection
    , clipboard : List Block.Block
    }


model : Model
model =
    { blocks = [], selection = Single 0, clipboard = [] }


type Msg
    = AddBlock
    | ChangeBlock Int Block.Msg
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
                    Block.updateBlock msg (Util.fnil Block.init <| Util.nth i model.blocks)
            in
                ( { model | blocks = Util.splice i 1 [ update ] model.blocks }
                , cmd |> Cmd.map (\a -> ChangeBlock i a)
                )

        CutSelection ->
            ( case model.selection of
                Single cell ->
                    { blocks = Util.removeAt cell model.blocks
                    , selection = Single (cell - 1)
                    , clipboard = (List.take 1 (List.drop cell model.blocks))
                    }

                Range from to ->
                    { blocks = Util.splice from (to - from + 1) [] model.blocks
                    , selection = Single (from - 1)
                    , clipboard = (List.take (to - from + 1) (List.drop from model.blocks))
                    }
            , Cmd.none
            )

        PasteSelection ->
            ( case model.selection of
                Single cell ->
                    { model
                        | blocks = Util.splice cell 0 model.clipboard model.blocks
                    }

                Range from to ->
                    { model | blocks = Util.splice from (to - from + 1) model.clipboard model.blocks }
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
                            min (List.length model.blocks)
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
    div []
        ((List.indexedMap
            (\i ->
                \x ->
                    Block.viewBlock x
                        (\s -> ChangeBlock i <| Block.ChangeContents s)
                        (\s -> ChangeBlock i <| Block.ChangeName s)
                        (ChangeBlock i Block.ToggleEdit)
            )
            model.blocks
         )
            ++ [ button [ onClick AddBlock ] [ text "Add Block" ] ]
        )


init : String -> ( Model, Cmd Msg )
init _ =
    ( model, Cmd.none )


subscriptions : Model -> Sub Msg
subscriptions model =
    Sub.none
