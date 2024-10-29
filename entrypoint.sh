#!/bin/sh

yoyo apply --database postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_HOST:$POSTGRES_PORT/$POSTGRES_DB ./migrations

python main.py
