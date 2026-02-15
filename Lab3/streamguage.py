import os
import re
import numpy as np
import matplotlib.pyplot as plt


class StreamGuage:
    def __init__(self, fid, station_id, station_name, starttime, units="ft"):
        self.fid = fid
        self.station_id = station_id
        self.station_name = station_name
        self.starttime = starttime
        self.units = units

        self.time = np.array([], dtype=float)
        self.data = np.array([], dtype=float)
        self.max_guage = np.nan

    def read_guage_file(self):
        # Load date, time, and gauge height columns
        date, tstr, hgt = np.loadtxt(
            self.fid,
            skiprows=28,
            usecols=[2, 3, 5],
            dtype=str
        ).T

        # Gauge values as float
        self.data = hgt.astype(float)

        # Parse day, hour, minute
        days = np.array([int(d[-2:]) for d in date], dtype=float)
        hours = np.array([int(t[:2]) for t in tstr], dtype=float)
        mins = np.array([int(t[3:5]) for t in tstr], dtype=float)

        # Minutes from start of month
        self.time = days * 24 * 60 + hours * 60 + mins

        # Track max gauge
        self.max_guage = float(self.data.max())

    def plot(self):
        self.max_guage = float(np.max(self.data))

        plt.figure(figsize=(10, 4))
        plt.plot(self.time, self.data)
        plt.xlabel("Time [min]")
        plt.ylabel(f"Gauge height [{self.units}]")
        plt.title(
            f"Stream Gauge {self.station_id}, {self.station_name}\n"
            f"Start: {self.starttime}, Max Gauge: {self.max_guage:.2f} {self.units}\n"
            f"File: {os.path.basename(self.fid)}"
        )
        plt.tight_layout()
        plt.show()

    def convert(self):
        """
        Convert gauge heights ft to m
        """
        if self.units == "ft":
            self.data = self.data * 0.3048
            self.units = "m"
        elif self.units == "m":
            pass

        self.max_guage = float(np.max(self.data))

    def demean(self):
        """
        Subtract mean from data, demean
        """
        self.data = self.data - np.mean(self.data)
        self.max_guage = float(np.max(self.data))

    def shift_time(self, time_shift):
        """
        Shift time axis by minutes
        """
        self.time = self.time + float(time_shift)

    def main(self, time_shift=-100):
        """
        Read + raw plot
        Convert + demean + shift_time + processed plot
        """
        self.read_guage_file()
        self.plot()

        self.convert()
        self.demean()
        self.shift_time(time_shift)
        self.plot()


class NOAAStreamGuage(StreamGuage):
    # class attribute overwritten for NOAA default units
    units = "m"

    def __init__(self, fid, station_id, station_name, starttime, units="m"):
        # NOAA defaults to meters
        super().__init__(fid, station_id, station_name, starttime, units=units)

    def convert(self):
        """
        if NOAA data, are already in meters
        """
        # no conversion needed
        self.units = "m"
        if self.data.size > 0:
            self.max_guage = float(np.max(self.data))

    def read_guage_file(self):
        """
        Reuse parent reading behavior, then add NOAA specific message
        """
        super().read_guage_file()
        print("I am a NOAA stream guage")


def make_october_file(src_fid, dst_fid):
    """
    copy source to destination
    change all dates from 2024-09-xx to 2024-10-xx
    add leading 1s to the 6th row data
    """
    with open(src_fid, "r") as f:
        lines = f.readlines()

    out = []
    for line in lines:
        # change Sept to Oct
        line = line.replace("2024-09-", "2024-10-")

        # only modify actual data rows (6th)
        if line.startswith("USGS"):
            parts = line.split()
            parts[5] = "1" + parts[5]   # ex: 47.94 -> 147.94
            line = " ".join(parts) + "\n"

        out.append(line)


    with open(dst_fid, "w") as f:
        f.writelines(out)


if __name__ == "__main__":
    fid_sep = "/Users/serinawang/Downloads/phelan_creek_stream_guage_2024-09-07_to_2024-09-14.txt"
    fid_oct = "/Users/serinawang/Downloads/phelan_creek_stream_guage_2024-10-07_to_2024-10-14.txt"

    # # build October file automatically
    make_october_file(fid_sep, fid_oct)

    files = [fid_sep, fid_oct]

    # Choose an agency per run: USGS or NOAA
    agency = "NOAA"

    if agency == "USGS":
        GaugeClass = StreamGuage
        station_id = "USGS-15478040"
        station_name = "PHELAN CREEK"
        units = "ft"
    elif agency == "NOAA":
        GaugeClass = NOAAStreamGuage
        station_id = "NOAA-15478040"
        station_name = "PHELAN CREEK (NOAA)"
        units = "m"


    for fid in files:
        if "2024-10-07" in os.path.basename(fid):
            start = "2024-10-07 00:00"
        else:
            start = "2024-09-07 00:00"

        GaugeClass(
            fid=fid,
            station_id=station_id,
            station_name=station_name,
            starttime=start,
            units=units,
        ).main()
