# Developer: Hamdy Abou El Anein
# Contact: contact@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
FROM debian:trixie-slim
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends qemu-system-x86 novnc websockify python3 ca-certificates git curl procps util-linux && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --uid 1000 --shell /bin/bash demo
COPY demo/run.py /opt/daylight-demo/run.py
COPY release/current.json /opt/daylight-demo/release.json
RUN python3 /opt/daylight-demo/run.py --download-only --cache /opt/daylight-demo/image && cp -a /usr/share/novnc /opt/daylight-demo/www && printf '%s\n' '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="refresh" content="0;url=vnc.html?autoconnect=true&amp;resize=scale"><title>Daylight live demo</title><a href="vnc.html?autoconnect=true&amp;resize=scale">Connect to the Daylight live session</a></html>' > /opt/daylight-demo/www/index.html
USER demo
ENV HOME=/home/demo
EXPOSE 6080
CMD ["python3","/opt/daylight-demo/run.py","--cache","/opt/daylight-demo/image","--listen","0.0.0.0"]
