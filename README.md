# svarog-ctl

Svarog-ctl is a command-line driven automated satellite tracking software
that uses `rotctld` to control antenna rotors to track satellites fly overs.

## Status

The software is in development. It's not fully functional yet.


## Usage:

```shell
python ./svarog_ctl.py --lat 53.5 --lon 18.5 --sat "NOAA 18"
```

```shell
python ./svarog_ctl.py --lat 53.5 --lon 18.5 --satid 25338
```

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
