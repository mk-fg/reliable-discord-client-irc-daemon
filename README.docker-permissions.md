# Permission issues with docker

Common issue with unprivileged containers running in docker might look like this:

```
Failed to create initial configuration file [ config.ini ]:
  [PermissionError] [Errno 13] Permission denied: 'config.ini'
```

Unfortunately it's somewhat complicated, and I don't know good-and-easy fix for this.\
This small document tries to explain what the issue is and how to address it.

Docker has complicated relationship with user/group permissions on its "volume"
directories, which exist on host, but need to be accessible to its containers,
with user/group values (or uid/gid - same thing) that are configured in those.

Complicating matters further, docker can be configured to use uid/gid
namespacing mode ("[userns-remap]"), which makes container see different
uid/gid values than host system, i.e. uid=123 inside container can be uid=2498479
on the host system where your shell is and where you actually see it.

rdircd runs with default uid/gid either specified in [Dockerfile] (set via
UID=55373 and GID=55373 lines there currently), or can be set manually to
something else, either in that Dockerfile, or also via `args: [UID=..., GID=...]`
line in [docker-compose.yml].

Again, note that those are uid/gid values *inside* the container, which can be
different on host system if something like userns-remap mode is enabled in
docker/podman/etc. It can be enabled by default there.

rdircd in this docker configuration needs its volume directory to be writable,
to create and change files in there.

[docker-compose.yml] file has two examples for how to specify rdircd
config files volume, depending on which fix for the issue above can be
slightly different - see either of the first two sections below for each:

- [With default `config:/config` volume spec]
- [When using e.g `./conf:/config` local directory]

Common workaround for this issue in docker containers is to run root entrypoint
wrapper script, which will chown/chmod volumes as necessary, then drop privileges
for running the actual app, which has its own issues (like granting root privileges
to anything in a container) and doesn't work for userns-remapping case anyhow,
so is not used here.

This is written as of early 2024 with docker 24.0.x in mind, so it's possible
that all this is handled better by other container runtimes (e.g. [podman])
and especially future versions of those, with e.g. uid/gid remapping done on
overlayfs level, so maybe also check for more modern solutions for such issues.

[docker-compose.yml]: docker-compose.yml
[Dockerfile]: Dockerfile
[With default `config:/config` volume spec]: #hdr-if_you_re_using_default_volume_spec_in_d.9MBw
[When using e.g `./conf:/config` local directory]: #hdr-when_using_local_directory_instead_of_ab.ioHM
[podman]: https://podman.io/


<a name=hdr-if_you_re_using_default_volume_spec_in_d.9MBw></a>
## If you're using default `config:/config` volume spec in docker-compose.yml

Then that "named docker volume" SHOULD be created by docker with correct uid/gid
set for the container on first `docker-compose up` invocation.

Then if you change these uid/gid values after that volume is already created,
it **won't** change permissions on this volume, so either:

- Don't change container uid/gid after creating the volume.
- If there's no valuable data stored there, use `docker-compose down -v` to
  remove volumes, so it'd re-create those from scratch with correct new uid/gid.
- Run "chown" on the volume directory on the host system to correct uid/gid.

If there's no userns-remap'ping involved, last option (chown to new uid/gid),
after a failed "docker-compose up" invocation, can be done like this:

```
% docker-compose run -u root --entrypoint sh rdircd \
    -c 'chown root:rdircd . && chmod 770 . && ls -lah .'

total 23K
drwxrwx---    2 root     rdircd      3.4K May 24 10:05 .
drwxr-xr-x    1 root     root        3.4K May 24 10:05 ..
-rw-------    1 rdircd   rdircd     14.4K May 24 10:05 config.ini
```

(`root:rdircd` and mode=770 there is so that rdircd user doesn't have access to
changing permissions and other metadata on the volume dir itself, and can only
manage stuff under it)

If userns remapping is enabled, command above shouldn't work, and you might need
to use "chown" and "chmod" commands from the host system.
See [userns-remap] documentation for more details, but quick-and-dirty way to see
what's the uid/gid on the host in such case and do the chmod/chown like above,
can be something like this:

```
user% docker-compose run -u root --entrypoint sleep rdircd infinity

root# ps -o uid= $(pgrep -f 'sleep infinity')
2498479

root# docker volume inspect -f '{{.Mountpoint}}' rdircd_config
/var/lib/docker/volumes/rdircd_config/_data

root# chown root:2498479 /var/lib/docker/volumes/rdircd_config/_data
root# chmod 770 /var/lib/docker/volumes/rdircd_config/_data

root# pkill -9 -f 'sleep infinity'
```

Maybe there's a special docker command to do this stuff

[userns-remap]: https://docs.docker.com/engine/security/userns-remap/


<a name=hdr-when_using_local_directory_instead_of_ab.ioHM></a>
## When using local directory instead of above, e.g `./conf:/config` in docker-compose.yml

Then this "conf" directory under current dir (where you run docker-compose command)
can either exist already or will be auto-created by docker-compose.

At least as of docker 24.0.x, it will always be auto-created with incorrect
permissions - "root" uid/gid and default 755 mode, i.e. always inaccessible
for writing to a container.

Simple fix is to just chown/chmod that dir to correct permissions (with sudo or root),
e.g. when using default uid/gid of 55373 from [Dockerfile] and no userns-remapping:

```
# mkdir -p conf && chown -R 55373:55373 conf
# chown root:55373 conf && chmod 770 conf
```

(same as in other example above `root:55373` and mode=770 are so that rdircd
user doesn't have access to changing permissions and other metadata on the
volume dir itself, and can only manage stuff under it)

If uid/gid in docker configuration change, run above commands with new container
gid on it - should work fine with the new host/configuration after that.

Enabled [userns-remap] (or similar feature in other OCI runtimes) only
complicates this by needing to use different uid/gid in chown command,
than one specified in the Dockerfile or docker-compose.yml.

Similar to previous section, I'd probably determine it via something like this:

```
% docker-compose run -u root --entrypoint sleep rdircd infinity
% ps -o uid= $(pgrep -f 'sleep infinity')
2498479
```

I.e. run "sleep infinity" in a container, then check what is its uid on the host
system, and use that with chown/chmod commands from example above.
