#!/bin/bash

# copy imessage db to ./chat.db just to be safe
imessage-exporter -p ./chat.db -f txt -o out
find output -type f -name "*.txt" ! -name "*boys love*.txt" -exec rm {} +
