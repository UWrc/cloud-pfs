#!/usr/bin/env python3
# This script calculates and displays minimum, maximum, and average 4K IOPS for all of the files in its directory. 
# Each file should be named in the format gpfs-iozone-$THREADCOUNTthreads.out where $THREADCOUNT is the number of threads used.
# Each file should contain a bunch of IOzone tests ran in throughput mode.
# This script doesn't do any error handling, so if any spooky errors come up contact the creator @Jimmy Beckett.

import glob
import re

record_size_re = re.compile(r'\s*Each process writes a \d+ kByte file in (\d+) kByte records\s*')
min_max_avg_re = [re.compile(r'\s*' + x + '\s*throughput per process\s*=\s*(\d+)\.(\d+) kB/sec\s*') for x in ['Min', 'Max', 'Avg']]
result = []
for filename in glob.glob('gpfs-iozone-[0-9]*threads.out'):  # iterate through all files
    record_size = -1
    min_max_avg_totals = [0] * 3  # sum of all min/max/avg throughputs in the file
    num_tests = 0  # total number of tests ran
    for line in open(filename, 'r'):
        m = record_size_re.match(line)
        if m:
            record_size = int(m.group(1))  # kBytes
        matches = [x.match(line) for x in min_max_avg_re]
        if matches[0]:  # if min is there then max and avg are there too, so increment count
            num_tests += 1
        for i, m in enumerate(matches):
            if m:
                min_max_avg_totals[i] += float(m.group(1)) + float(m.group(2)) / 100  # decimal number
    result.append((filename, num_tests, [x / num_tests / record_size for x in min_max_avg_totals]))  # convert to IOPS by dividing KBytes/Sec by KBytes/record
for r in sorted(result):  # sorted by threadcounts
    iops = ['{:.2f}'.format(r[2][i]).rjust(10) for i in range(3)]  # format each IOPS as right justified with 2 decimal places
    print('threadcount=' + str(int(re.match(r'.*?(\d+).*', r[0]).group(1))).rjust(3) +  # pull number of threads from file name
            ', num tests=' + str(num_tests).rjust(6) + 
            ', min 4K IOPS=' + iops[0] + 
            ', max 4K IOPS=' + iops[1] + 
            ', avg 4K IOPS=' + iops[2])
