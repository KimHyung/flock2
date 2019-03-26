"""Simulate one or more Tello drones in Gazebo, using ArUco markers and fiducial_vlam for localization"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess


def generate_launch_description():
    # 1 or more drones:
    drones = ['drone1', 'drone2']

    tello_gazebo_path = get_package_share_directory('tello_gazebo')
    tello_description_path = get_package_share_directory('tello_description')

    world_path = os.path.join(tello_gazebo_path, 'worlds', 'fiducial.world')
    map_path = os.path.join(tello_gazebo_path, 'worlds', 'fiducial_map.yaml')

    # Global entities
    entities = [
        # Launch Gazebo, loading tello.world
        ExecuteProcess(cmd=[
            'gazebo',
            '--verbose',
            '-s', 'libgazebo_ros_init.so',      # Publish /clock
            '-s', 'libgazebo_ros_factory.so',   # Provide gazebo_ros::Node
            world_path
        ], output='screen'),

        # Load and publish a known map
        Node(package='fiducial_vlam', node_executable='vmap_node', output='screen',
             node_name='vmap_node', parameters=[{
                'use_sim_time': True,                           # Use /clock if available
                'marker_length': 0.1778,                        # Marker length
                'marker_map_load_full_filename': map_path,      # Load a pre-built map from disk
                'make_not_use_map': 0                           # Don't save a map to disk
            }]),

        # Rviz
        ExecuteProcess(cmd=['rviz2', '-d', 'install/flock2/share/flock2/launch/two.rviz'], output='screen'),

        # Joystick driver, generates /namespace/joy messages
        Node(package='joy', node_executable='joy_node', output='screen',
             node_name='joy_node', parameters=[{
                'use_sim_time': True
            }]),

        # Flock controller
        Node(package='flock2', node_executable='flock_base', output='screen',
             node_name='flock_base', parameters=[{
                'use_sim_time': True,
                'drones': drones
            }]),
    ]

    # Per-drone entities
    for idx, namespace in enumerate(drones):
        suffix = '_' + str(idx + 1)
        urdf_path = os.path.join(tello_description_path, 'urdf', 'tello' + suffix + '.urdf')

        entities.extend([
            # Add a drone to the simulation
            Node(package='tello_gazebo', node_executable='inject_entity.py', output='screen',
                 arguments=[urdf_path, '0', str(idx), '1']),

            # Localize this drone against the map
            Node(package='fiducial_vlam', node_executable='vloc_node', output='screen',
                 node_name='vloc_node', node_namespace=namespace, parameters=[{
                    'use_sim_time': True,                       # Must be True or False
                    'publish_tfs': 1,                           # Must be 1 or 0
                    'base_frame_id': 'base_link' + suffix,
                    'map_init_pose_z': -0.035,
                    'camera_frame_id': 'camera_link' + suffix
                }]),

            # Drone controller
            Node(package='flock2', node_executable='drone_base', output='screen',
                 node_name='drone_base', node_namespace=namespace, parameters=[{
                    'use_sim_time': True
                }]),

            # Odometry filter
            # Node(package='odom_filter', node_executable='filter_node', output='screen',
            #      node_name='filter_node', node_namespace=namespace, parameters=[{
            #         'use_sim_time': True,
            #         'map_frame': 'map',
            #         'base_frame': 'base_link' + suffix
            #     }]),
        ])

    return LaunchDescription(entities)
