#!/usr/bin/env bash

git pull

cd ../../
bench --site "$SITE" set-maintenance-mode on
bench --site "$SITE" build
bench --site "$SITE" migrate
bench --site "$SITE" clear-cache
bench --site "$SITE" clear-website-cache
bench restart
bench --site "$SITE" set-maintenance-mode off

# shellcheck disable=SC2164
cd ~
