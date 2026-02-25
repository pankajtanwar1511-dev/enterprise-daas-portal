"""
Root conftest.py to disable ROS pytest plugins
"""
import sys

# Disable ROS pytest plugins by removing them from sys.modules before pytest loads
ros_modules = [mod for mod in list(sys.modules.keys()) if 'ros' in mod or 'ament' in mod or 'launch' in mod]
for mod in ros_modules:
    if mod in sys.modules:
        del sys.modules[mod]

def pytest_configure(config):
    """Disable ROS plugins"""
    # Unregister ROS plugins
    pm = config.pluginmanager
    ros_plugins = [
        'launch-testing-ros',
        'ament_copyright',
        'ament_flake8',
        'ament_lint',
        'ament_pep257',
        'ament_xmllint'
    ]
    for plugin_name in ros_plugins:
        if pm.has_plugin(plugin_name):
            pm.unregister(name=plugin_name)
