# Panhit README

## Running PANhit
Panhit is available as a docker image, available from DockerHub 
```
docker run -p 443:443 -p 80:80 -v [local-volume-path]:/database -v [path-to-cert]:/etc/ssl/certs/nginx.crt -v [path-to-key]:/etc/ssl/private/nginx.key  --name panhit panhit
```

### Docker options
**exposed volumes**

PANhit relies on two JSON databases that, by default, are stored in the path /database.

Mount this somewhere persistent with -v
```bash
-v /dockervol/panhit/db:/database
```

**Exposed ports**

PANhit runs behind NGINX and by default binds to port 80 and 443.

