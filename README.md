# Waves - Simple audio recordings hosting server

Waves is a simple audio recordings hosting server.
It aims to provide a simple way to host and share audio recordings such as dj mixes with friends.

## Quick start

Download and prepare the theme assets with:
```shell
curl -L -o html5up-stellar.zip https://html5up.net/stellar/download \
&& unzip -q html5up-stellar.zip -d html5up-stellar \
&& cp -rf html5up-stellar/assets static/ \
&& rm -rf html5up-stellar html5up-stellar.zip
```

Update the requirements with:
```shell
uv export --no-dev > requirements.txt
```

Code style:
```shell
black .
```
