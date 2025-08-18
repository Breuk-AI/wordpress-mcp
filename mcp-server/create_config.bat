@echo off
if not exist config.json (
    copy config.json.example config.json
    echo Created config.json - please edit it with your WordPress credentials!
) else (
    echo config.json already exists
)
