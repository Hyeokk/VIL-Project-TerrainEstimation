
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

### 4. Robot Description & Physics Tuning
- **Custom URDF:** Implemented `urdf/custom_a200.urdf.xacro` to include `robot.yaml` sensors (LiDAR, Camera, IMU) and customized physical properties.
- **Speed Tuning:** 
  - **URDF Limits:** Increased velocity interface limits from `+/- 1.0` to `+/- 10.0` in `a200.urdf.xacro` to prevent hardware layer throttling.
  - **Controller Config:** Increased `max_velocity` in `control.yaml` to `20.0` m/s.
  - **Wheel Slip:** Set lateral and longitudinal slip compliance to `0.0` to maximize traction.
- **Gazebo GUI Note:** The "Key Publisher" plugin in Gazebo defaults to a low speed (often ~0.5) on every launch. **You must manually set the "Linear" value to `5.0` or higher in the GUI** to move at high speeds.

## Installation and Build

### 1. Clone the Repository
Go to your ROS 2 workspace `src` directory and clone this repository.

```bash
cd ~/<your_workspace>/src
git clone https://github.com/Hyeokk/VIL-Project-Simulation.git clearpath_simulator
```

### 2. Build the Package
Return to the workspace root and build:

```bash
cd ~/<your_workspace>
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

### 1. Standard Launch (Default URDF)
Uses the auto-generated description from the standard `robot.yaml`.
**Note:** Physical properties (speed, friction) are set to default values.

```bash
ros2 launch clearpath_gz simulation.launch.py world:=project
```

### 2. Custom Launch (High Speed & Sensors)
**Recommended for development.**
Uses the customized URDF (`custom_a200.urdf.xacro`) which includes:
- All sensors (LiDAR, Camera, IMU)
- Tuned physical properties (Higher speed limit, Zero wheel slip)

```bash
ros2 launch clearpath_gz simulation.launch.py world:=project use_auto_generated:=false
```

### 3. Launching Specific Worlds
To launch the `solar_farm` world with the custom settings:

```bash
ros2 launch clearpath_gz simulation.launch.py world:=solar_farm use_auto_generated:=false
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