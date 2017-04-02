module Util exposing (..)

import Http
import Json.Encode as Encode


removeAt : Int -> List a -> List a
removeAt n l =
    (List.take n l) ++ (List.drop (n + 1) l)


splice : Int -> Int -> List a -> List a -> List a
splice from extent xs l =
    (List.take from l) ++ xs ++ (List.drop (from + extent) l)


insert : Int -> a -> List a -> List a
insert at elem l =
    splice at 0 [ elem ] l


nth : Int -> List a -> Maybe a
nth n l =
    List.head <| List.drop n l


slice : Int -> Int -> List a -> List a
slice begin len l =
    List.take (len - begin) <| List.drop begin l


augment : b -> List a -> List ( a, b )
augment b l =
    List.map (\x -> ( x, b )) l



-- Single is a selection of a single position, and Range is
--   inclusive on both ends. So Single x == Range x x.


type Selection
    = Single Int
    | Range Int Int


inSelection : Selection -> Int -> Bool
inSelection s i =
    case s of
        Single n ->
            i == n

        Range from to ->
            (i >= from) && (i <= to)


extent : Selection -> Int
extent s =
    case s of
        Single _ ->
            1

        Range from to ->
            to - from + 1


sliceSel : Selection -> List a -> List a
sliceSel s l =
    case s of
        Single x ->
            slice x 1 l

        Range from _ ->
            slice from (extent s) l


processResult : (String -> a) -> Result Http.Error a -> a
processResult default res =
    case res of
        Err e ->
            case e of
                Http.BadUrl url ->
                    default ("Error: The url " ++ url ++ " doesn't exist!")

                Http.Timeout ->
                    default "Error: Timeout!"

                Http.NetworkError ->
                    default "Error: network error"

                Http.BadStatus r ->
                    default ((toString r.status.code) ++ " : " ++ r.status.message ++ " " ++ r.body)

                Http.BadPayload s _ ->
                    default (s ++ " was the error from Elm itself.")

        Ok t ->
            t


fnil : a -> Maybe a -> a
fnil x mx =
    case mx of
        Nothing ->
            x

        Just a ->
            a


type Remote e a
    = Unfetched
    | Fetching
    | Failure e
    | Success a


emptyJsonBody : Http.Body
emptyJsonBody =
    Http.jsonBody (Encode.object [])
