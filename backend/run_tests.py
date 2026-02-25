#!/usr/bin/env python3
"""
Test runner script that bypasses ROS pytest plugins
"""
import sys
import os

# Remove ROS paths from Python path to prevent plugin loading
sys.path = [p for p in sys.path if '/opt/ros' not in p]

# Remove ROS environment variables
ros_env_vars = [k for k in os.environ.keys() if k.startswith(('ROS_', 'AMENT_'))]
for var in ros_env_vars:
    del os.environ[var]

# Now run pytest
import pytest

if __name__ == '__main__':
    # Run pytest with coverage
    sys.exit(pytest.main([
        'tests/',
        '-v',
        '--cov=app',
        '--cov-report=term-missing',
        '--cov-report=html',
        '--tb=short',
        '-p', 'no:rostest',
        '-p', 'no:launch_testing',
    ]))
