#!/usr/bin/env bash

activado=''
while read line; do
    activado='1'
    export "$line"
done < <(ccdecrypt -c secrets.env.cpt)

test "$activado" || { echo "No se pasó correctamente la contraseña"; exit 1; }

docker-compose up
