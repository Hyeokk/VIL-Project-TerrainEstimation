# BSD 3-Clause License
#
# Copyright (c) 2023, Dahlem Center for Machine Learning and Robotics, Freie Universität Berlin
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Modifications:
# 2026-01-23: Enforced live mode and topic remapping for FAST_LIO integration.
#             Author: Hyeokk

import os

import numpy as np
import math
import tf_transformations
import launch
import launch_ros
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch.actions import IncludeLaunchDescription

def generate_launch_description():

	rviz_config_dir = PathJoinSubstitution([FindPackageShare('groundgrid'), 'param/groundgrid.rviz'])
	rviz2 = launch_ros.actions.Node(
		package='rviz2',
        namespace='',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_dir]
	)

	launch_dir = PathJoinSubstitution([FindPackageShare('groundgrid'), 'launch'])

	dataset_name_arg = launch.actions.DeclareLaunchArgument(
		name='dataset_name',
		default_value='live',
		description='Name of the dataset'
	)

	tf_camera_init_odom = launch_ros.actions.Node(
		package='tf2_ros',
		executable='static_transform_publisher',
		name='camera_init_odom',
		arguments=['0', '0', '0', '0', '0', '0', 'camera_init', 'odom']
	)
	tf_body_velodyne = launch_ros.actions.Node(
		package='tf2_ros',
		executable='static_transform_publisher',
		name='body_velodyne',
		arguments=['0', '0', '0', '0', '0', '0', 'body', 'velodyne']
	)
	tf_body_base_link = launch_ros.actions.Node(
		package='tf2_ros',
		executable='static_transform_publisher',
		name='body_base_link',
		arguments=['0', '0', '0', '0', '0', '0', 'body', 'base_link']
	)

	launch_description = launch.LaunchDescription([
		dataset_name_arg,
		tf_camera_init_odom,
		tf_body_velodyne,
		tf_body_base_link,
		IncludeLaunchDescription(
			PathJoinSubstitution([launch_dir, 'GroundGrid.launch.py']),
			launch_arguments={
				'dataset_name': launch.substitutions.LaunchConfiguration('dataset_name'),
				'pointcloud_topic': '/cloud_registered',
				'odometry_topic': '/Odometry'
			}.items()
		),
		rviz2
	])

	return launch_description

if __name__ == '__main__':
	generate_launch_description()
