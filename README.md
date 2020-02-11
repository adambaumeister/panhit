# Panhit README

## Run
```
docker run -p 443:443 -p 80:80 -v [local-volume-path]:/database -v [path-to-cert]:/etc/ssl/certs/nginx.crt -v [path-to-key]:/etc/ssl/private/nginx.key  --name panhit panhit
```
