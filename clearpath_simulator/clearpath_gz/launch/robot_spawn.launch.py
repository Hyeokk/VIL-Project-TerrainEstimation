# Copyright 2021 Clearpath Robotics, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# @author Roni Kreinin (rkreinin@clearpathrobotics.com)

from clearpath_config.clearpath_config import ClearpathConfig

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    GroupAction,
    IncludeLaunchDescription,
    RegisterEventHandler,
    OpaqueFunction
)
from launch.conditions import IfCondition, UnlessCondition
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    EnvironmentVariable,
    LaunchConfiguration,
    PathJoinSubstitution,
    Command,
    FindExecutable
)

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

import os


ARGUMENTS = [
    DeclareLaunchArgument('rviz', default_value='false',
                          choices=['true', 'false'],
                          description='Start rviz.'),
    DeclareLaunchArgument('use_sim_time', default_value='true',
                          choices=['true', 'false'],
                          description='use_sim_time'),
    DeclareLaunchArgument('world', default_value='warehouse',
                          description='Gazebo World'),
    DeclareLaunchArgument('setup_path',
                          default_value=[EnvironmentVariable('HOME'), '/clearpath/'],
                          description='Clearpath setup path'),
    DeclareLaunchArgument('generate',
                          default_value='true',
                          choices=['true', 'false'],
                          description='Generate parameters and launch files'),
    DeclareLaunchArgument('use_auto_generated',
                          default_value='true',
                          choices=['true', 'false'],
                          description='Use auto-generated URDF from robot.yaml'),
    DeclareLaunchArgument('custom_description_path',
                          default_value=PathJoinSubstitution([
                              FindPackageShare('clearpath_gz'),
                              'urdf',
                              'custom_a200.urdf.xacro'
                          ]),
                          description='Path to custom URDF file')
]

for pose_element in ['x', 'y', 'yaw']:
    ARGUMENTS.append(DeclareLaunchArgument(pose_element, default_value='0.0',
                     description=f'{pose_element} component of the robot pose.'))

ARGUMENTS.append(DeclareLaunchArgument('z', default_value='0.15',
                 description='z component of the robot pose.'))


def launch_setup(context, *args, **kwargs):
    setup_path = LaunchConfiguration('setup_path')
    world = LaunchConfiguration('world')
    use_sim_time = LaunchConfiguration('use_sim_time')
    x, y, z = LaunchConfiguration('x'), LaunchConfiguration('y'), LaunchConfiguration('z')
    yaw = LaunchConfiguration('yaw')
    generate = LaunchConfiguration('generate')

    # Parse robot YAML into config
    clearpath_config = ClearpathConfig(os.path.join(
        str(setup_path.perform(context)), 'robot.yaml'))

    namespace = clearpath_config.system.namespace
    if namespace in ('', '/'):
        robot_name = 'robot'
    else:
        robot_name = namespace + '/robot'

    # Directories
    pkg_clearpath_viz = FindPackageShare('clearpath_viz')

    # Paths
    rviz_launch = PathJoinSubstitution(
        [pkg_clearpath_viz, 'launch', 'view_robot.launch.py'])
    launch_file_platform_service = PathJoinSubstitution([
        setup_path, 'platform/launch', 'platform-service.launch.py'])
    launch_file_sensors_service = PathJoinSubstitution([
        setup_path, 'sensors/launch', 'sensors-service.launch.py'])
    launch_file_manipulators_service = PathJoinSubstitution([
        setup_path, 'manipulators/launch', 'manipulators-service.launch.py'])

    group_action_spawn_robot = GroupAction([

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([launch_file_platform_service]),
            launch_arguments=[
              ('prefix', ['/world/', world, '/model/', robot_name, '/link/base_link/sensor/'])]
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([launch_file_sensors_service]),
            launch_arguments=[
              ('prefix', ['/world/', world, '/model/', robot_name, '/link/base_link/sensor/'])]
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([launch_file_manipulators_service]),
        ),

        # Spawn robot
        Node(
            package='ros_gz_sim',
            executable='create',
            namespace=namespace,
            arguments=['-name', robot_name,
                       '-x', x,
                       '-y', y,
                       '-z', z,
                       '-Y', yaw,
                       '-topic', 'robot_description'],
            output='screen'
        ),
    ])

    node_generate_description = Node(
        package='clearpath_generator_common',
        executable='generate_description',
        name='generate_description',
        output='screen',
        condition=IfCondition(generate),
        arguments=['-s', setup_path]
    )

    node_generate_semantic_description = Node(
        package='clearpath_generator_common',
        executable='generate_semantic_description',
        name='generate_semantic_description',
        output='screen',
        condition=IfCondition(generate),
        arguments=['-s', setup_path]
    )

    node_generate_launch = Node(
        package='clearpath_generator_gz',
        executable='generate_launch',
        name='generate_launch',
        output='screen',
        condition=IfCondition(generate),
        arguments=['-s', setup_path]
    )

    node_generate_param = Node(
        package='clearpath_generator_gz',
        executable='generate_param',
        name='generate_launch',
        output='screen',
        condition=IfCondition(generate),
        arguments=['-s', setup_path]
    )

    event_generate_description = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=node_generate_description,
            on_exit=[node_generate_semantic_description]
        )
    )

    event_generate_semantic_description = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=node_generate_semantic_description,
            on_exit=[node_generate_launch]
        )
    )

    event_generate_launch = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=node_generate_launch,
            on_exit=[node_generate_param]
        )
    )

    # RViz
    rviz = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([rviz_launch]),
        launch_arguments=[
            ('namespace', namespace),
            ('use_sim_time', use_sim_time)],
        condition=IfCondition(LaunchConfiguration('rviz')),
    )

    # Custom Description Content
    use_auto_generated = LaunchConfiguration('use_auto_generated')
    custom_description_path = LaunchConfiguration('custom_description_path')

    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name='xacro')]),
            ' ',
            custom_description_path,
            ' ',
            'namespace:=', namespace,
            ' ',
            'is_sim:=true'
        ]
    )

    # Wrapper for Auto Spawn with Condition
    spawn_robot_auto = GroupAction(
        actions=[group_action_spawn_robot],
        condition=IfCondition(use_auto_generated)
    )

    # Update event to use unconditional wrapper
    event_generate_param = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=node_generate_param,
            on_exit=[spawn_robot_auto]
        )
    )

    # Automatically generated logic
    do_generate = GroupAction(
        actions=[
            node_generate_description,
            event_generate_description,
            event_generate_semantic_description,
            event_generate_launch,
            event_generate_param,
            rviz
        ],
        condition=IfCondition(LaunchConfiguration('generate'))
    )

    # Fallback Spawn (Auto Generated, No Generation)
    do_spawn_auto_fallback = GroupAction(
        actions=[spawn_robot_auto],
        condition=UnlessCondition(LaunchConfiguration('generate'))
    )

    # Custom Spawn Services (Duplicate platform logic without RSP)
    pkg_clearpath_control = FindPackageShare('clearpath_control')
    
    launch_file_teleop_base = PathJoinSubstitution([
        pkg_clearpath_control, 'launch', 'teleop_base.launch.py'])
    launch_file_teleop_joy = PathJoinSubstitution([
        pkg_clearpath_control, 'launch', 'teleop_joy.launch.py'])
    launch_file_localization = PathJoinSubstitution([
        pkg_clearpath_control, 'launch', 'localization.launch.py'])

    # Bridge Nodes (Copied from platform-service.launch.py)
    node_cmd_vel_bridge = Node(
        name='cmd_vel_bridge',
        executable='parameter_bridge',
        package='ros_gz_bridge',
        namespace=namespace,
        output='screen',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist[ignition.msgs.Twist',
            '/model/' + robot_name + '/cmd_vel@geometry_msgs/msg/Twist]ignition.msgs.Twist'
        ],
        remappings=[
            ('/cmd_vel', 'cmd_vel'),
            ('/model/' + robot_name + '/cmd_vel', 'platform/cmd_vel_unstamped')
        ],
        parameters=[{'use_sim_time': use_sim_time}]
    )

    node_odom_base_tf_bridge = Node(
        name='odom_base_tf_bridge',
        executable='parameter_bridge',
        package='ros_gz_bridge',
        namespace=namespace,
        output='screen',
        arguments=[
            '/model/' + robot_name + '/tf@tf2_msgs/msg/TFMessage[ignition.msgs.Pose_V'
        ],
        remappings=[
            ('/model/' + robot_name + '/tf', 'tf')
        ],
        parameters=[{'use_sim_time': use_sim_time}]
    )

    # Custom Spawn (Manual URDF)
    do_spawn_custom = GroupAction(
        actions=[
            # Robot State Publisher
            Node(
                package='robot_state_publisher',
                executable='robot_state_publisher',
                name='robot_state_publisher',
                output='screen',
                parameters=[{'use_sim_time': use_sim_time,
                             'robot_description': robot_description_content}]
            ),
            # Spawn Robot
            Node(
                package='ros_gz_sim',
                executable='create',
                namespace=namespace,
                arguments=['-name', robot_name,
                           '-x', x,
                           '-y', y,
                           '-z', z,
                           '-Y', yaw,
                           '-topic', 'robot_description'],
                output='screen'
            ),
            # Spawners
            Node(
                package='controller_manager',
                executable='spawner',
                arguments=['joint_state_broadcaster'],
                output='screen',
            ),
            Node(
                package='controller_manager',
                executable='spawner',
                arguments=['platform_velocity_controller'],
                output='screen',
            ),
            # Teleop (TwistMux)
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource([launch_file_teleop_base]),
                launch_arguments=[
                  ('setup_path', setup_path),
                  ('use_sim_time', use_sim_time),
                ]
            ),
            # Joystick
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource([launch_file_teleop_joy]),
                launch_arguments=[
                  ('setup_path', setup_path),
                  ('use_sim_time', use_sim_time),
                ]
            ),
            # Localization (EKF)
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource([launch_file_localization]),
                launch_arguments=[
                  ('setup_path', setup_path),
                  ('use_sim_time', use_sim_time),
                  ('enable_ekf', 'true')
                ]
            ),
            # Bridges
            node_cmd_vel_bridge,
            node_odom_base_tf_bridge,
            # Sensors and Manipulators (Assuming no RSP)
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource([launch_file_sensors_service]),
                launch_arguments=[
                  ('prefix', ['/world/', world, '/model/', robot_name, '/link/base_link/sensor/'])]
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource([launch_file_manipulators_service]),
            ),
        ],
        condition=UnlessCondition(use_auto_generated)
    )

    return [
        do_generate,
        do_spawn_auto_fallback,
        do_spawn_custom
    ]


def generate_launch_description():
    # Define LaunchDescription variable
    ld = LaunchDescription(ARGUMENTS)
    ld.add_action(OpaqueFunction(function=launch_setup))
    return ld
