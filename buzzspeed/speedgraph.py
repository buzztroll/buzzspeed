import datetime
import docopt
import json
import os
import matplotlib.pyplot as plt


g_usage = f'''
Usage: 
  speedgraph.py [options] <src_dir>

Options:
  -h --help           Show this screen.
  --start=<str>       The date to begin graphing (YYYY-MM-DD_hh:mm)
  --end=<str>         The date to stop graphing (YYYY-MM-DD_hh:mm)
  --outfile=<path>    The image file that will created [default: graph.png]
  --ping              Make transfer graph (will not make transfer graph)
'''


def bps_to_mps(b):
    return (b * 8.0) / (1024.0*1204.0)


class DataPoint(object):
    def __init__(self, file_path):
        # ts 2023-11-19T21:16:01.213086Z
        with open(file_path, 'r') as fptr:
            d = json.load(fptr)
            self.name = d['server']['name']
            self.ping = d['ping']
            self.download = bps_to_mps(d['download'])
            self.upload = bps_to_mps(d['upload'])
            self.timestamp = datetime.datetime.strptime(d['timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ")


def make_xfer_graph(point_list, outfile, ping_only=False):
    fig, ax1 = plt.subplots(figsize=(12, 9))

    first_time = point_list[0].timestamp
    last_time = point_list[-1].timestamp

    times = [p.timestamp for p in point_list]

    xticks = times[0::10]
    ax1.set_xticks([t.timestamp() - first_time.timestamp() for t in xticks])
    ax1.set_xticklabels([t.strftime("%m/%d %H:%M") for t in xticks])
    ax1.set(xlabel='time', ylabel='mbps', title='Transfer Speeds')
    ax1.grid(axis='y')

    if not ping_only:
        dls = [p.download for p in point_list]
        uls = [p.upload for p in point_list]
        ax1.plot([t.timestamp() - first_time.timestamp() for t in times], dls, marker='o', label="Download", color='r')
        ax1.plot([t.timestamp() - first_time.timestamp() for t in times], uls, marker='x', label="Upload", color='b')
        plt.legend(loc='upper center')
        plt.title(f"Transfer speed from {first_time.strftime('%m/%d %H:%M')} to {last_time.strftime('%m/%d %H:%M')}")
    else:
        pings = [p.ping for p in point_list]
        ax1.plot([t.timestamp() - first_time.timestamp() for t in times], pings, marker='x', label="Upload", color='b')
        plt.legend(loc='upper center')
        plt.title(f"Ping times from {first_time.strftime('%m/%d %H:%M')} to {last_time.strftime('%m/%d %H:%M')}")

    fig.savefig(outfile)


def get_datapoints(dir_path, start, end):
    point_list = []
    dir_list = os.listdir(dir_path)
    for f in dir_list:
        if f.endswith('.json'):
            try:
                dp = DataPoint(os.path.join(dir_path, f))
                ts = dp.timestamp.timestamp()
                if ts >= start and ts <= end:
                    point_list.append(dp)
            except Exception as ex:
                print(f"Failed to process {f} : {str(ex)}")

    point_list = sorted(point_list, key=lambda x: x.timestamp.timestamp(), reverse=False)
    return point_list


def main():
    args = docopt.docopt(g_usage)

    data_dir = args['<src_dir>']
    outfile = args['--outfile']
    start_timestr = args['--start']
    end_timestr = args['--end']
    ping_graph = args['--ping']

    if start_timestr:
        start_time = datetime.datetime.strptime(start_timestr, "%Y-%m-%d_%H:%M").timestamp()
    else:
        start_time = 0

    if end_timestr:
        endtime = datetime.datetime.strptime(end_timestr, "%Y-%m-%d_%H:%M").timestamp()
    else:
        endtime = datetime.datetime.now().timestamp()

    points = get_datapoints(data_dir, start_time, endtime)
    make_xfer_graph(points, outfile, ping_graph)
