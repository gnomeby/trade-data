# Trade data viewer

## Technologies

* Flask
  * click - for additional flask console commands
* WebSockets for full duplex realtime communication with server
* Plotly for realtime graphics rendering
* sqlite for persistent storage of prices fluctuations

No external CDNs are used.

## Running via docker

Warning!!! Next operation will try to assign 5000 and 8765 ports on hosts machine.

```bash
docker build -t trade_data .
docker run --network=host --rm -it trade-data
```

Open in browser [localhost:5000](http://localhost:5000/).

## Persistent storage

Mount a docker volume to /opt/data folder to keep all data between container restartings.

## Install in dev mode

```bash
python3.8 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
flask init-db
```

## Run

```bash
sh init_and_start.sh
```

## Notices for using pudb debugger

Configure pudb to classic shell not bpython.

```bash
FLASK_ENV=development flask run --no-debugger --no-reload
```

## Structure

After openning Homepage or selecting a ticker in select element the browser will fetch the last cached data for the selected ticker.
The Response headers will contain cache headers for a proxy webserver and for the browser:

```python
result.headers['Cache-Control'] = 'public, smax-age=%d, max-age=%d,' % (ONE_HOUR // 4, ONE_HOUR // 4 - ONE_MINUTE)
```

After getting precached data for the ticker the browser will subscribe (using WS) to next prices fluctuations using the last received timestamp in precached data.

Then webserver push to the client a portion of all available cached data for the selected ticker.

And then client will receive all new data item in real time.

## TODO

* Switching to timeseries DB.
* Use TimeRange features in Plotly.
* Run through gunicorn
* Make instruction to run through nginx and configure nginx cache

Potential bugs:

* One overlapping value when the WebSocket server push to the client a portion of all available cached data.
