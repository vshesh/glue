module ExtendedEvents exposing (..)

import Html exposing (Attribute)
import Html.Events exposing (on, keyCode, targetValue, onWithOptions)
import Json.Decode as Decode
import Dict exposing (Dict)


onKeyUp : (Int -> msg) -> Attribute msg
onKeyUp tagger =
    on "keydown" (Decode.map tagger keyCode)


shiftKeyPressed : Decode.Decoder Bool
shiftKeyPressed =
    Decode.field "shiftKey" Decode.bool


onShiftKeyDown : (Bool -> Int -> msg) -> Attribute msg
onShiftKeyDown msg =
    on "keydown" (Decode.map2 msg shiftKeyPressed keyCode)


onShiftClick : (Bool -> msg) -> Html.Attribute msg
onShiftClick msg =
    on "click" (Decode.map msg shiftKeyPressed)


onChange : (String -> msg) -> Html.Attribute msg
onChange msg =
    on "change" (Decode.map msg targetValue)


keyCodes : Dict String Int
keyCodes =
    Dict.fromList [ ( "down-arrow", 40 ), ( "up-arrow", 38 ) ]


onLocalClick : msg -> Html.Attribute msg
onLocalClick msg =
    onWithOptions "click"
        { preventDefault = False, stopPropagation = True }
        (Decode.succeed msg)
