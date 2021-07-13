# svarog-ctl

Svarog-ctl is a command-line driven automated satellite tracking software
that uses `rotctld` to control antenna rotors to track satellites fly overs.

## Status

The software is in development. It's not fully functional yet. It can calculate the passes,
but is not able to send commands to rotctld yet.

## Setup

`svarog-ctl` requires a configured `rotctld` daemon running. Details TBD.

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

Gdansk's is 53.35N 18.53E. We can use the following command to order the svarog_ctl
to follow the next pass after 18:44 on July 14th:

```shell
./svarog_ctl.py --lat 53.35 --lon 18.53 --time "2021-07-14 18:44:00" \
--tle1 "1 44427U 98067QM  21192.54020985  .00022355  00000-0  19763-3 0  9995" \
--tle2 "2 44427  51.6376 177.8799 0003618 359.5888  93.1405 15.68562202115256"
```

Alternatively, `svarog-ctl` can download TLE data from [Celestrak](https://celestrak.com/NORAD/elements/active.txt).
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

