#!/bin/sh

exec './HoneyComb-redistributable/service/honeycomb.py' > /tmp/honeycomb.log &
exec './HoneyComb-redistributable/service/honeycomb_html.py' > /tmp/honeycomb.log&
exec './HoneyComb-redistributable/service/honeycomb_websocket.py' > /tmp/honeycomb.log &
