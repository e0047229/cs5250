"""
CS5250 Assignment 4, Scheduling policies simulator
Sample skeleton program
Author: Minh Ho
Input file:
    input.txt
Output files:
    FCFS.txt
    RR.txt
    SRTF.txt
    SJF.txt

Apr 10th Revision 1:
    Update FCFS implementation, fixed the bug when there are idle time slices between processes
    Thanks Huang Lung-Chen for pointing out
Revision 2:
    Change requirement for future_prediction SRTF => future_prediction shortest job first(SJF), the simpler non-preemptive version.
    Let initial guess = 5 time units.
    Thanks Lee Wei Ping for trying and pointing out the difficulty & ambiguity with future_prediction SRTF.
"""

import sys
from collections import deque
from heapq import heappush, heappop

input_file = 'input.txt'


class Process:
    last_scheduled_time = 0

    def __init__(self, id, arrive_time, burst_time):
        self.id = id
        self.arrive_time = arrive_time
        self.burst_time = burst_time
        self.remaining_time = burst_time

    # for printing purpose
    def __repr__(self):
        return '[id %d : arrive_time %d,  burst_time %d]' % (self.id, self.arrive_time, self.burst_time)


def FCFS_scheduling(process_list):
    # store the (switching time, process_id) pair
    schedule = []
    current_time = 0
    waiting_time = 0
    for process in process_list:
        if current_time < process.arrive_time:
            current_time = process.arrive_time
        schedule.append((current_time, process.id))
        process_time = current_time - process.arrive_time
        waiting_time += process_time
        current_time += process.burst_time
    average_waiting_time = waiting_time / float(len(process_list))
    return schedule, average_waiting_time


# Input: process_list, time_quantum (Positive Integer)
# Output_1 : Schedule list contains pairs of (time_stamp, process_id) indicating the time switching to that process_id
# Output_2 : Average Waiting Time
def RR_scheduling(process_list, time_quantum):
    schedule = []
    current_time = 0
    waiting_time = 0

    # initial process
    ptr = 0
    q = deque()
    q.append(process_list[ptr])
    # round robin
    while len(q) > 0:
        current_process = q.popleft()
        schedule.append((current_time, current_process.id))

        if not current_process.remaining_time:
            current_process.remaining_time = current_process.burst_time
        process_time = min(time_quantum, current_process.remaining_time)
        current_time += process_time
        current_process.remaining_time -= process_time
        if current_process.remaining_time > 0:
            q.append(current_process)
        else:
            waiting_time += (current_time - current_process.arrive_time - current_process.burst_time)

        while process_list[ptr].arrive_time <= current_time:
            if ptr > 0:
                print("process", ptr, process_list[ptr].arrive_time)
                q.append(process_list[ptr])
            ptr += 1

    average_waiting_time = waiting_time / float(len(process_list))
    return schedule, average_waiting_time


def SRTF_scheduling(process_list):
    h = []  # a Min Heap to store processes order by remaining time
    schedule = []
    current_time = 0
    waiting_time = 0
    for process in process_list:
        # print("add process", process.arrive_time)
        process.remaining_time = process.burst_time
        heappush(h, (process.remaining_time, process))
        srt_process = heappop(h)[1]
        while srt_process.arrive_time > current_time:
            current_time += 1
        srt_process.remaining_time -= 1
        # print("current time", current_time, "arrive time", srt_process.arrive_time)
        current_time += 1
        # print(process.id, "burst_time", process.burst_time, "remaining_time", process.remaining_time)
        if srt_process.remaining_time > 0:
            heappush(h, (srt_process.remaining_time, srt_process))
        else:
            waiting_time += (current_time - srt_process.arrive_time - srt_process.burst_time)
            # print("waiting time", waiting_time, "current time", current_time,
            #       "arrive time", srt_process.arrive_time, "burst time", srt_process.burst_time)

    while len(h) > 0:
        srt_process = heappop(h)[1]
        schedule.append((current_time, srt_process.id))
        current_time += srt_process.remaining_time
        waiting_time += (current_time - srt_process.arrive_time - srt_process.burst_time)

    # print("total waiting time", waiting_time)
    average_waiting_time = waiting_time / float(len(process_list))
    return schedule, average_waiting_time


def SJF_scheduling(process_list, alpha):
    schedule = []
    current_time = 0
    waiting_time = 0

    predict = {}
    h = []
    ptr = 0
    while ptr < len(process_list):
        while process_list[ptr].arrive_time < current_time:
            process = process_list[ptr]
            if process.id in predict:
                process.predict_time = round(alpha * process.burst_time + (1 - alpha) * predict[process.id])
            else:
                process.predict_time = 5  # initial guess burst time = 5 for all processes
            predict[process.id] = process.predict_time
            heappush(h, (process.predict_time, process))
            ptr += 1

        current_process = heappop(h)[1]
        while current_time < current_process.arrive_time:
            current_time += 1
        schedule.append((current_time, current_process.id))
        current_time += current_process.burst_time
        waiting_time += (current_time - current_process.arrive_time - current_process.burst_time)

    average_waiting_time = waiting_time / float(len(process_list))
    return schedule, average_waiting_time


def read_input():
    result = []
    with open(input_file) as f:
        for line in f:
            array = line.split()
            if len(array) != 3:
                print("wrong input format")
                exit()
            result.append(Process(int(array[0]), int(array[1]), int(array[2])))
    return result


def write_output(file_name, schedule, avg_waiting_time):
    with open(file_name, 'w') as f:
        for item in schedule:
            f.write(str(item) + '\n')
        f.write('average waiting time %.2f \n' % avg_waiting_time)


def main(argv):
    process_list = read_input()
    print("printing input ----")
    for process in process_list:
        print(process)
    print("simulating FCFS ----")
    FCFS_schedule, FCFS_avg_waiting_time = FCFS_scheduling(process_list)
    write_output('FCFS.txt', FCFS_schedule, FCFS_avg_waiting_time)
    print("simulating RR ----")
    RR_schedule, RR_avg_waiting_time = RR_scheduling(process_list, time_quantum=2)
    write_output('RR.txt', RR_schedule, RR_avg_waiting_time)
    print("simulating SRTF ----")
    SRTF_schedule, SRTF_avg_waiting_time = SRTF_scheduling(process_list)
    write_output('SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time)
    print("simulating SJF ----")
    SJF_schedule, SJF_avg_waiting_time = SJF_scheduling(process_list, alpha=0.5)
    write_output('SJF.txt', SJF_schedule, SJF_avg_waiting_time)
    print("DONE")


if __name__ == '__main__':
    main(sys.argv[1:])
