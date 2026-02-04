
# Clearpath Simulator (Customized)

**Environment:** Ubuntu 22.04 LTS | ROS 2 Humble

This repository is based on the `humble` branch of the [Clearpath Robotics simulation repository](https://github.com/clearpathrobotics/clearpath_simulator) and has been customized to fit specific requirements.

## Key Modifications

### 1. Fix: Solar Farm World Resource Loading
Resolved an issue where resources (meshes, etc.) for the `solar_farm` world were not found in the ROS 2 Humble environment.
- **`clearpath_gz/CMakeLists.txt`:** Updated to ensure `meshes` and `geotif` directories are installed during the build process.
- **`clearpath_gz/launch/gz_sim.launch.py`:** Updated to explicitly add the `meshes` path to the `IGN_GAZEBO_RESOURCE_PATH` environment variable.

### 2. Configuration Improvements
- **`CMakeLists.txt`:** Added missing installation paths required for the Humble environment.
- **Launch Files:** Added environment variable setup to ensure Gazebo correctly locates resources.

### 3. Additional Worlds
- Added `project.sdf` and `project_baseline.sdf` worlds, contributed by [Kang Soon-hyuk](https://github.com/Kangsoonhyuk/FASTLIO-Offroad-Sim.git).


## Installation and Build

To build this package, run the following commands:

```bash
cd ~/clearpath_ws
colcon build --symlink-install
source install/setup.bash
```

## Robot Configuration

This repository is configured to manage the robot configuration (`robot.yaml`) internally.

1. Ensure your `robot.yaml` file is located in the `clearpath/` directory:
   - Path: `clearpath/robot.yaml`
   - This project uses the **sample A200 robot.yaml** provided by Clearpath.
   - You can download the sample configuration from the [Clearpath Config Repository](https://github.com/clearpathrobotics/clearpath_config/tree/humble/clearpath_config/sample/a200).

2. **Launch Configuration:** 
   The `simulation.launch.py` file has been updated to automatically use this `clearpath` directory as the default `setup_path`. You do not need to manually specify the path or create a `~/clearpath` directory in your home folder.


## Usage

### Basic Simulation Launch
To launch the simulation with the default settings:

```bash
ros2 launch clearpath_gz simulation.launch.py
```

### Launching the Solar Farm World
```bash
ros2 launch clearpath_gz simulation.launch.py world:=solar_farm
```

### Running on CPU (Software Rendering)
If you are running the simulation on a machine without a dedicated GPU or experiencing rendering issues, export the following environment variable before launching:

```bash
export LIBGL_ALWAYS_SOFTWARE=1
ros2 launch clearpath_gz simulation.launch.py command:=...
```


## References
- Original Repository: [https://github.com/clearpathrobotics/clearpath_simulator](https://github.com/clearpathrobotics/clearpath_simulator)
- Custom World: [https://github.com/Kangsoonhyuk/FASTLIO-Offroad-Sim.git](https://github.com/Kangsoonhyuk/FASTLIO-Offroad-Sim.git)