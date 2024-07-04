#!/bin/bash

/home/gpuserver/workspace/LiveAttendance/venv/bin/python3.9 /home/gpuserver/workspace/LiveAttendance/registration_app.py &

/home/gpuserver/workspace/LiveAttendance/venv/bin/python3.9 /home/gpuserver/workspace/LiveAttendance/real_time_attendance.py &

wait