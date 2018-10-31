#!/usr/bin/env python3
# This script calculates and displays minimum, maximum, and average 4K IOPS for all of the files in its directory. 
# Each file should be named in the format gpfs-iozone-$THREADCOUNTthreads.out where $THREADCOUNT is the number of threads used.
# Each file should contain a bunch of IOzone tests ran in throughput mode.
# This script doesn't do any error handling, so if any spooky errors come up contact the creator @Jimmy Beckett.

import glob
import re
from statistics import stdev, mean

record_size_re = re.compile(r'\s*Each process writes a \d+ kByte file in (\d+) kByte records\s*')
min_max_avg_re = [re.compile(r'\s*' + x + '\s*throughput per process\s*=\s*(\d+)\.(\d+) kB/sec\s*') for x in ['Min', 'Max', 'Avg']]
threadcount_re = re.compile(r'.*?(\d+).*')
column_width = 40
for c in ['threadcount', 'min 4K IOPS / stdev', 'max 4K IOPS / stdev', 'avg 4K IOPS / stdev']:
    print(c.ljust(column_width), end='')
print()
for filename in sorted(glob.glob('gpfs-iozone-[0-9]*threads.out'), 
        key=lambda x: int(threadcount_re.match(x).group(1))):  # iterate through all files matching this pattern in sorted order
    record_size = -1
    min_max_avg = [[] for i in range(3)]
    for line in open(filename, 'r'):
        m = record_size_re.match(line)
        if m:
            record_size = int(m.group(1))  # kBytes
        for i, m in enumerate([x.match(line) for x in min_max_avg_re]):
            if m:
                min_max_avg[i].append(float(m.group(1)) + float(m.group(2)) / 100)  # decimal number
    print(str(int(threadcount_re.match(filename).group(1))).ljust(column_width), end='')  # print threadcount
    for x in [(mean(min_max_avg[i]) / record_size, stdev(min_max_avg[i]) / record_size) for i in range(3)]:
        print(('{:.2f}'.format(x[0]).ljust(11) + ' / ' + '{:.2f}'.format(x[1]).ljust(11)).ljust(column_width), end='')
    print()
