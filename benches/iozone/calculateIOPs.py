#!/usr/bin/env python3
# This script calculates and displays minimum, maximum, and average 4K IOPS for all of the files in its directory. 
# Each file should be named in the format gpfs-iozone-$THREADCOUNTthreads.out where $THREADCOUNT is the number of threads used.
# Each file should contain a bunch of IOzone tests ran in throughput mode.
# This script doesn't do any error handling, so if any spooky errors come up just contact the creator @Jimmy Beckett.

import glob
import re

write_info_re = re.compile(r'\s*Each process writes a \d+ kByte file in (\d+) kByte records\s*')
min_max_avg_re = [re.compile(r'\s*' + x + '\s*throughput per process\s*=\s*(\d+)\.(\d+) kB/sec\s*') for x in ['Min', 'Max', 'Avg']]
result = []
for filename in glob.glob('gpfs-iozone-[0-9]*threads.out'):
    record_size = -1
    min_max_avg_totals = [0] * 3  # sum of all min/max/avg throughputs in the file
    count = 0  # total number of tests ran
    for line in open(filename, 'r'):
        m = write_info_re.match(line)
        if m:  # update file size and record size
            record_size = int(m.group(1))  # kBytes
        matches = [x.match(line) for x in min_max_avg_re]
        if any(matches):
            count += 1
        for i, m in enumerate(matches):
            if m:
                min_max_avg_totals[i] += float(m.group(1)) + float(m.group(2)) / 100
    count /= 3
    result.append((filename, count, [x / count / record_size for x in min_max_avg_totals]))
for r in sorted(result):  # sorted by threadcounts
    print('threadcount=' + str(int(re.match(r'.*?(\d+).*', r[0]).group(1))).rjust(3) + 
            ', num tests=' + str(count).rjust(6) + 
            ', min 4K IOPS=' + '{:.2f}'.format(r[2][0]).rjust(10) + 
            ', max 4K IOPS=' + '{:.2f}'.format(r[2][1]).rjust(10) + 
            ', avg 4K IOPS=' + '{:.2f}'.format(r[2][2]).rjust(10))
