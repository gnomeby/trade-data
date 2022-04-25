# Trade data viewer

## Install

```bash
python3.8 -m venv .venv
source .venv/bin/activate
```

## Run

```bash
sh init_and_start.sh
```

## Debugger

Configure pudb to classic shell not bpython.

```bash
FLASK_ENV=development flask run --no-debugger --no-reload
```

## Structure

After openning Homepage or selecting a ticker in select element the browser will fetch the last cached data for the selected ticker.
The Response headers will contain cache headers for proxy webserver and for the browser:

```python
result.headers['Cache-Control'] = 'public, smax-age=%d, max-age=%d,' % (ONE_HOUR // 4, ONE_HOUR // 4 - ONE_MINUTE)
```

After getting precached data for the ticker the browser will subscribe to next prices fluctuations using the last received timestamp in precached data.

# TODO

* Switching to timeseries DB.
* Use TimeRange in Plotly.
