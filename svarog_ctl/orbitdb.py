"""
OrbitDatabase is responsible for downloading and maintaining TLE orbital data.
"""

import datetime
import logging
import os
import time
import requests
import requests.exceptions

from orbit_predictor.sources import NoradTLESource
from orbit_predictor.predictors.base import CartesianPredictor

from svarog_ctl.tle import Tle

from .globalvars import APP_NAME, VERSION, CONFIG_DIRECTORY
from .configuration import open_config
from .utils import url_to_filename

TLE_SOURCES = [
    "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle" # Can be an url
    # "file://local.txt" # can also be a local file
]

def _get_create_time(path):
    stat = os.stat(path)
    ctime = stat.st_ctime
    return ctime

def _is_in_source(source, sat_id):
    try:
        source.get_tle(sat_id, datetime.datetime.now(datetime.timezone.utc))
        return True
    except LookupError:
        return False

class OrbitDatabase:
    """
    OrbitDatabase is a simple database that downloads TLE orbital data from
    configurable Internet sources and local files.
    """

    def __init__(self, urls=None, max_period=7*24*60*60):
        self.max_period = max_period
        if urls is None:
            urls = TLE_SOURCES
        self.urls = urls

        self.tle_names = {}
        self.tle_norad = {}

        # Store all information in the ${DATADIR}/tle directory.
        cfg = open_config()
        logging.debug("Loaded config: %s", repr(cfg))
        self.datadir = os.path.join(cfg['datadir'] if 'datadir' in cfg else CONFIG_DIRECTORY, 'tle')
        os.makedirs(self.datadir, exist_ok = True)

    def _get_tle_from_url(self, url):
        if url[:7] == "file://":
            fname = self.datadir + os.path.sep + url[7:]
            logging.debug("Reading file [%s]", fname)

            with open(fname, "r", encoding="utf-8") as f:
                content = f.read()
                f.close()
                logging.debug("Loaded %d bytes from file %s", len(content), fname)
                return content

        headers = { 'user-agent': APP_NAME + " " + VERSION, 'Accept': 'text/plain' }
        try:
            response = requests.get(url, headers=headers, timeout=10)
        except requests.exceptions.RequestException as error:
            logging.error("Exception requesting TLE: %s", error)
            raise
        return response.content.decode("UTF-8")

    def _fetch_tle_and_save(self, url, tle_path):
        logging.info("Downloading %s to local file %s", url, tle_path)

        content = self._get_tle_from_url(url)
        with open(tle_path, "w", encoding="utf-8") as f:
            f.write(content)
        return tle_path

    def _get_tle_path_from_url(self, url):
        tle_filename = url_to_filename(url)

        tle_path = os.path.join(self.datadir, tle_filename)
        return tle_path

    def _is_out_of_date(self, path):
        ctime = _get_create_time(path)
        now = time.time()
        return now > ctime + self.max_period

    def _get_current_tle_file(self, url: str, force_fetch=False):
        tle_path = self._get_tle_path_from_url(url)
        tle_path_exists = os.path.exists(tle_path)
        if not force_fetch and tle_path_exists and not self._is_out_of_date(tle_path):
            logging.info("%s is up-to-date, skipping download.", tle_path)
            return tle_path

        try:
            return self._fetch_tle_and_save(url, tle_path)
        except:
            if not force_fetch and tle_path_exists:
                return tle_path
            raise

    def get_predictor(self, name: str) -> CartesianPredictor:
        """Returns a prediction for specified satellite"""
        for url in self.urls:
            path = self._get_current_tle_file(url)
            source = NoradTLESource.from_file(path)
            if _is_in_source(source, name):
                return source.get_predictor(name)
        raise LookupError(f"Could not find {name} in orbit data.")

    def refresh_satellites(self, sat_ids):
        """Refresh satellite info from remote sources and local files."""
        all_sat_ids = set(sat_ids)
        found_sat_ids = set()
        for url in self.urls:
            sats_to_search = all_sat_ids.difference(found_sat_ids)
            if len(sats_to_search) == 0:
                return

            path = self._get_current_tle_file(url, force_fetch=True)
            source = NoradTLESource.from_file(path)

            for sat_id in sats_to_search:
                if _is_in_source(source, sat_id):
                    found_sat_ids.add(sat_id)

        if all_sat_ids != found_sat_ids:
            raise LookupError(f"Could not find {', '.join(all_sat_ids.difference(found_sat_ids))} in orbit data.")

    def refresh_urls(self, force_fetch = False):
        """Downloads all defined TLE information from TLE_SOURCES and other defined sources."""
        urls = self.urls

        for url in urls:
            self._get_current_tle_file(url, force_fetch=force_fetch)
            self.parse_tlebulk(self._get_tle_path_from_url(url))

    def parse_all(self):
        """Parses all files."""
        for url in self.urls:
            path = self._get_current_tle_file(url)
            self.parse_tlebulk(path)

    def parse_tlebulk(self, file: str = None):
        """Parses loaded TLE data, as downloaded from TLE_SOURCES. The file is essentially a
           lot of TLE lines concatenated together."""

        cnt = 0
        with open(file, encoding="utf-8") as f:
            lines = f.readlines()
        for i in range(int(len(lines) / 3) ):
            name = lines[3*i].strip()
            line1 = lines[3*i+1].strip()
            line2 = lines[3*i+2].strip()
            self.add_tle(line1, line2, name)
            cnt += 1
        logging.info("Loaded %d TLEs.", cnt)

    def add_tle(self, line1: str, line2: str, name: str):
        """Adds a new TLE entry from strings."""
        t = Tle(line1, line2, name)
        self.tle_names[name] = t
        self.tle_norad[t.norad] = t

    def get_name(self, l: str) -> Tle:
        """Attempts to return a TLE by its name, e.g. get_name("NOAA 18") """
        return self.tle_names[l]

    def get_norad(self, l: int) -> Tle:
        """Attempts to return a TLE by its norad number, e.g. get_name(12345) """
        return self.tle_norad[l]

    def get_name_by_norad(self, l: int) -> str:
        """Attempts to return a sat name by its norad number"""
        return self.get_norad(l).get_name()

    def count(self) -> int:
        """Returns number of currently loaded TLEs"""
        return len(self.tle_norad)

    def __str__(self):
        """This method is used when printing the orbitdb object"""
        data = []
        for url in self.urls:
            path = self._get_tle_path_from_url(url)
            exists = os.path.exists(path)
            if exists:
                out_of_date = self._is_out_of_date(path)
                creation_time = _get_create_time(path)
                now = time.time()
                age = now - creation_time

                dt = datetime.timedelta(seconds=age)
                data.append((url, f"{('Out-of-date' if out_of_date else 'Current')}: {str(dt)} ago"))
            else:
                data.append((url, "Not exists"))

        return "\n".join(f"{url} - {desc}" for url, desc in data)
