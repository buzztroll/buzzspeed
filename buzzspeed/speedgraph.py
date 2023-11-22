import datetime
import docopt
import json
import os
import matplotlib.pyplot as plt
import numpy
import statistics


g_usage = f'''
Usage: 
  speedgraph.py [options] <src_dir>

Options:
  -h --help           Show this screen.
  --start=<str>       The date to begin graphing (YYYY-MM-DD_hh:mm)
  --end=<str>         The date to stop graphing (YYYY-MM-DD_hh:mm)
  --outfile=<path>    The base path and file name for the output file. It will be appended
                      with the graph type (ping.png, download.png, or upload.png) [default: graph]
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


def list_avg(l):
    total = 0.0
    for i in l:
        total += i
    return total / len(l)


def moving_average(value_list, window_size=15):
    window = []
    back = int(window_size / 2)
    list_len = len(value_list)
    floating_range = [0] * list_len

    for i in range(0, list_len+back):
        if i < list_len:
            v = value_list[i]
            window.append(v)
        if i > window_size:
            window.pop(0)
        avg = list_avg(window)
        if i < window_size:
            floating_range[i] = avg
        else:
            floating_range[i-back] = avg

    return floating_range


def make_xfer_graph(time_data, ydata, outfile, ylabel, title):
    fig, ax1 = plt.subplots(figsize=(12, 9))

    list_len = len(time_data)

    median_vals = [statistics.median(ydata)] * list_len
    mean_vals = [statistics.mean(ydata)] * list_len
    ninety_vals = [numpy.percentile(ydata, 90)] * list_len
    ten_vals = [numpy.percentile(ydata, 10)] * list_len

    first_time = time_data[0]
    last_time = time_data[-1]

    tick_space = int(len(time_data) / 3)
    xticks = time_data[0::tick_space]
    ax1.set_xticks([t.timestamp() - first_time.timestamp() for t in xticks])
    ax1.set_xticklabels([t.strftime("%m/%d %H:%M") for t in xticks])
    ax1.grid(axis='y')

    ax1.set(xlabel="time", ylabel=ylabel, title=title)
    mv_avgs = moving_average(ydata)
    ax1.plot(time_data, ydata, marker='x', label=title, color='b')
    ax1.plot(time_data, mv_avgs, label="moving average", color='r')
    ax1.plot(time_data, median_vals, label="median", color='y')
    ax1.plot(time_data, mean_vals, label="average", color='g')
    ax1.plot(time_data, ninety_vals, label="90th")
    ax1.plot(time_data, ten_vals, label="10th", color='c')
    plt.legend(loc='upper left')
    plt.title(f"{title} from {first_time.strftime('%m/%d %H:%M')} to {last_time.strftime('%m/%d %H:%M')}")

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

    if start_timestr:
        start_time = datetime.datetime.strptime(start_timestr, "%Y-%m-%d_%H:%M").timestamp()
    else:
        start_time = 0

    if end_timestr:
        endtime = datetime.datetime.strptime(end_timestr, "%Y-%m-%d_%H:%M").timestamp()
    else:
        endtime = datetime.datetime.now().timestamp()

    points = get_datapoints(data_dir, start_time, endtime)

    time_data = [i.timestamp for i in points]

    ping_data = [i.ping for i in points]
    make_xfer_graph(time_data, ping_data, f"{outfile}-ping.png", "ms", "ping times")

    dl_data = [i.download for i in points]
    make_xfer_graph(time_data, dl_data, f"{outfile}-download.png", "mbps", "download speeds")

    ul_data = [i.upload for i in points]
    make_xfer_graph(time_data, ul_data, f"{outfile}-upload.png", "mbps", "upload speeds")
