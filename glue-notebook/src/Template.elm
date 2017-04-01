module Template exposing (..)

import Json.Decode as Decode
import Json.Encode as Encode
import Html exposing (Html, text, node)
import Html.Attributes exposing (attribute)
import Util
import Http


type alias Elem =
    { tag : String
    , attrs : List ( String, String )
    , body : List Template
    }


type Template
    = Body String
    | Tag Elem


decodeTemplate : Decode.Decoder Template
decodeTemplate =
    Decode.oneOf [ Decode.map Tag <| Decode.lazy (\_ -> decodeElem), Decode.map Body Decode.string ]


decodeElem : Decode.Decoder Elem
decodeElem =
    Decode.map3 Elem
        (Decode.field "tag" Decode.string)
        (Decode.field "attrs" (Decode.keyValuePairs Decode.string))
        (Decode.field "body" (Decode.list (Decode.lazy (\_ -> decodeTemplate))))


template2Html : Template -> Html a
template2Html template =
    case template of
        Body str ->
            text str

        Tag { tag, attrs, body } ->
            node tag
                (List.map (\item -> (attribute (Tuple.first item) (Tuple.second item))) attrs)
                (List.map template2Html body)
