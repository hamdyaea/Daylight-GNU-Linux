# Daylight in a browser — actual AMD64 live ISO

This is a real Linux guest, not an HTML reconstruction of a desktop. QEMU executes the published AMD64 ISO; noVNC displays its console in a browser. The exact ISO filename, byte size and SHA256 are pinned in `release/current.json`. Downloads are verified before execution.

## Private Codespaces demo

Use the website's **Try online** button or select `.devcontainer/demo/devcontainer.json` when creating a Codespace. The container installs QEMU/noVNC, verifies and caches the release ISO, starts an unprivileged guest and forwards port 6080. Keep that port **private**. GitHub login and the owner account's available Codespaces quota are required. Do not add secrets to a disposable demonstration environment.

The guest ends after 20 minutes. This does **not** delete or necessarily stop the Codespace. Stop and delete it in GitHub when finished; compute and retained storage can consume quota or incur charges. No hosted paid instance or public listener is provisioned automatically by the repository.

## Local resource-limited container

Run on a disposable AMD64 test computer, not the productive Raspberry Pi:

```sh
docker build -f demo/Dockerfile -t daylight-browser-demo .
docker run --rm --name daylight-browser-demo \
  --cpus=2 --memory=3g --memory-swap=3g --pids-limit=128 \
  --cap-drop=ALL --security-opt=no-new-privileges --read-only \
  --tmpfs /tmp:rw,nosuid,nodev,size=256m \
  -p 127.0.0.1:6080:6080 daylight-browser-demo
```

Open `http://127.0.0.1:6080/`. Stop with Ctrl-C or `docker stop daylight-browser-demo`. There are no host-volume mounts or device passthrough. The Linux guest has no network card, persistent disk or access to a host disk. The container retains ordinary networking for its HTTP frontend; the guest does not. Image download occurs during the build, not through a guest network adapter.

## Security boundary

This configuration is for a private disposable demo, **not an anonymous public multi-tenant hosting service**. QEMU TCG is an emulator and QEMU explicitly does not provide its virtualization security guarantees for TCG. The surrounding disposable environment, unprivileged user, limited resources, read-only container filesystem and private authentication boundary are necessary additional controls; they are not a proof against every escape.

For a public service, use dedicated disposable KVM guests with an authenticated/session-isolated broker, strict quotas, host hardening and abuse controls. Never expose the raw VNC, WebSocket or QMP interface on the production Pi. This project does not create such a shared public service.

DistroSea's operator controls whether Daylight is listed. A prepared demo does not establish acceptance by DistroSea. v86 cannot execute the current 64-bit ISO; a 32-bit browser port would be a separately identified edition.

Primary references: https://www.qemu.org/docs/master/system/security.html ; https://novnc.com/info.html ; https://docs.github.com/en/billing/concepts/product-billing/github-codespaces
