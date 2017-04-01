module Util exposing (..)

import Http


removeAt : Int -> List a -> List a
removeAt n l =
    (List.take n l) ++ (List.drop (n + 1) l)


splice : Int -> Int -> List a -> List a -> List a
splice from extent xs l =
    (List.take from l) ++ xs ++ (List.drop (from + extent) l)


nth : Int -> List a -> Maybe a
nth n l =
    List.head <| List.drop n l


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
