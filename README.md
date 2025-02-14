# svarog-ctl

![pylint](https://github.com/gut-space/svarog-ctl/actions/workflows/pylint.yml/badge.svg)
![flake8](https://github.com/gut-space/svarog-ctl/actions/workflows/flake8.yml/badge.svg)
![python 3.11](https://github.com/gut-space/svarog-ctl/actions/workflows/pytest-3.11.yml/badge.svg)
![python 3.12](https://github.com/gut-space/svarog-ctl/actions/workflows/pytest-3.12.yml/badge.svg)
![CodeQL](https://github.com/gut-space/svarog-ctl/actions/workflows/github-code-scanning/codeql/badge.svg)
[![Coverage](https://coveralls.io/repos/github/gut-space/svarog-ctl/badge.svg?branch=master)](https://coveralls.io/github/gut-space/svarog-ctl?branch=master)

Svarog-ctl is a command-line driven automated satellite tracking software
that uses `rotctld` to control antenna rotator to track satellites fly overs.

## Status

The software is functional, but still in relatively early development. It can calculate the passes
based on either specified TLE data, or download data from Celestrak if sat name or Norad ID is
specified, then it can connect to rotctld and send commands to move the rotator.

## Setup

`svarog-ctl` requires a configured `rotctld` daemon running. Make sure your actual
rotator hardware is supported by rotctld. For testing purposes, `rotctld` can be started
with a dummy rotator: `rotctld -m 1 -t 4533`

## Usage

To predict a satellite fly-over (_pass_), several pieces of information are required.
First, observer's coordinates have to be specified (see `--lat`, `--lon` and optionally
also `--alt` parameters). The second essential parameter is to when to start the
prediction (`--time`). If time is not specified, current time stamp is used.

Also, `svarog-ctl` needs to know which sat to track. The orbit is determined using the TLE format.
There are two ways to provide this. First is to specify the two TLE lines explicitly.
Let's check KRAKSAT pass over Gdansk. The TLE available for KRAKSAT are:

```
1 44427U 98067QM  21192.54020985  .00022355  00000-0  19763-3 0  9995
2 44427  51.6376 177.8799 0003618 359.5888  93.1405 15.68562202115256
```

Gdansk is located at 53.35N 18.53E. We can use the following command to order the svarog_ctl
to follow the next pass after 18:44 on July 14th:

```shell
./svarog_ctl.py --lat 53.35 --lon 18.53 --time "2021-07-14 18:44:00" \
--tle1 "1 44427U 98067QM  21192.54020985  .00022355  00000-0  19763-3 0  9995" \
--tle2 "2 44427  51.6376 177.8799 0003618 359.5888  93.1405 15.68562202115256"
```

Alternatively, `svarog-ctl` can download TLE data from Celestrak.org website.
See the config.yml.template for direct link.

If you need to provide additional or alternative sources, see `TLE_SOURCES` in
https://github.com/gut-space/svarog-ctl/blob/master/svarog_ctl/orbitdb.py#L21
This mode of operation requires Internet access. The downloaded data is cached
for 7 days until it's refreshed.

If the sat is in the Celestrak database, it can be referenced using either its
name (`--sat`) or its NORAD ID (`--satid`).

```shell
python ./svarog_ctl.py --lat 53.5 --lon 18.5 --sat "NOAA 18"
```

```shell
python ./svarog_ctl.py --lat 53.5 --lon 18.5 --satid 25338
```

To be able to connect to `rotctld`, you also need to specify hostname (`--host`) and port
(`--port`).

By default, svarog-ctl prints everything using UTC timezone, but `--local` switch will make
it use local timezone instead.

For debugging purposes, svarog-ctl can be told to not wait till the next sat pass actually starts,
but pretent the sat is starting its flyover right now (`--now`). That is obviously useful
for testing purposes only.

## Python Usage

The rotator controller can also be easily controlled from Python. It requires the rotctld daemon
to be running. Here's example code:

```python

from svarog_ctl import rotctld

# Let's assume the rotcltd is listening on loopback on port 4533.
ctl = rotctld.Rotctld("127.0.0.1", 4533, 1)
ctl.connect()

# Let's see what kind of capabilities the rotctld reported for this rotator
print(ctl.capabilities())

# Let's check the current position.
print(ctl.get_pos())

# Ok, let's move it around.
ctl.set_pos(123.0, 45.0)
```
