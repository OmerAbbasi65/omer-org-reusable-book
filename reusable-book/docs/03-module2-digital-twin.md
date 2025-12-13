---
id: 03-module2-digital-twin
title: Module 2 - The Digital Twin (Gazebo & Unity)
sidebar_position: 3
---

# Module 2: The Digital Twin (Gazebo & Unity)

## Introduction to Robot Simulation

Before deploying a humanoid robot in the real world, we must test it in a virtual environment. Digital twins—photorealistic simulations of robots and their environments—allow us to:

- **Test safely**: No risk of hardware damage
- **Iterate quickly**: Instant resets and parameter changes
- **Generate data**: Synthetic data for training AI models
- **Validate behaviors**: Ensure safety before physical deployment

## Gazebo: Physics-First Simulation

Gazebo is the industry-standard robotics simulator, focusing on accurate physics simulation.

### Why Gazebo?

- **Accurate Physics**: Built on physics engines (ODE, Bullet, Simbody, DART)
- **Sensor Simulation**: LiDAR, cameras, IMU, force/torque sensors
- **ROS 2 Integration**: Native support for ROS 2
- **Plugin System**: Extensible with custom behaviors

### Setting Up Gazebo

```bash
# Install Gazebo Fortress (recommended for ROS 2 Humble)
sudo apt-get install ros-humble-gazebo-ros-pkgs
sudo apt-get install gazebo
```

### Simulating Physics for Humanoids

Humanoid robots face unique challenges:

1. **Bipedal Stability**: Must maintain balance on two feet
2. **Ground Contact**: Foot-ground interaction determines walking success
3. **Joint Limits**: Human-like range of motion constraints
4. **Center of Mass**: Must stay within support polygon

### Creating a Gazebo World

```xml
<?xml version="1.0"?>
<sdf version="1.6">
  <world name="humanoid_world">

    <!-- Physics Settings -->
    <physics name="default_physics" default="true" type="ode">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1.0</real_time_factor>
      <real_time_update_rate>1000</real_time_update_rate>
    </physics>

    <!-- Gravity -->
    <gravity>0 0 -9.81</gravity>

    <!-- Sun -->
    <include>
      <uri>model://sun</uri>
    </include>

    <!-- Ground Plane -->
    <include>
      <uri>model://ground_plane</uri>
    </include>

    <!-- Obstacles -->
    <model name="obstacle_box">
      <static>true</static>
      <pose>2 0 0.5 0 0 0</pose>
      <link name="box_link">
        <collision name="box_collision">
          <geometry>
            <box>
              <size>1 1 1</size>
            </box>
          </geometry>
        </collision>
        <visual name="box_visual">
          <geometry>
            <box>
              <size>1 1 1</size>
            </box>
          </geometry>
          <material>
            <ambient>1 0 0 1</ambient>
          </material>
        </visual>
      </link>
    </model>

  </world>
</sdf>
```

### SDF (Simulation Description Format)

SDF is more expressive than URDF for simulation purposes:

```xml
<?xml version="1.0"?>
<sdf version="1.6">
  <model name="simple_humanoid">

    <!-- Torso -->
    <link name="torso">
      <pose>0 0 1.0 0 0 0</pose>
      <inertial>
        <mass>50.0</mass>
        <inertia>
          <ixx>2.0</ixx>
          <ixy>0</ixy>
          <ixz>0</ixz>
          <iyy>2.0</iyy>
          <iyz>0</iyz>
          <izz>2.0</izz>
        </inertia>
      </inertial>

      <collision name="torso_collision">
        <geometry>
          <box>
            <size>0.4 0.3 0.6</size>
          </box>
        </geometry>
      </collision>

      <visual name="torso_visual">
        <geometry>
          <box>
            <size>0.4 0.3 0.6</size>
          </box>
        </geometry>
        <material>
          <ambient>0.2 0.2 0.8 1</ambient>
          <diffuse>0.2 0.2 0.8 1</diffuse>
        </material>
      </visual>

      <!-- IMU Sensor -->
      <sensor name="imu_sensor" type="imu">
        <always_on>1</always_on>
        <update_rate>100</update_rate>
        <imu>
          <angular_velocity>
            <x>
              <noise type="gaussian">
                <mean>0.0</mean>
                <stddev>0.01</stddev>
              </noise>
            </x>
          </angular_velocity>
        </imu>
      </sensor>
    </link>

    <!-- Right Leg -->
    <link name="right_thigh">
      <pose>0.1 0 0.5 0 0 0</pose>
      <inertial>
        <mass>5.0</mass>
      </inertial>
      <collision name="right_thigh_collision">
        <geometry>
          <cylinder>
            <radius>0.08</radius>
            <length>0.4</length>
          </cylinder>
        </geometry>
      </collision>
      <visual name="right_thigh_visual">
        <geometry>
          <cylinder>
            <radius>0.08</radius>
            <length>0.4</length>
          </cylinder>
        </geometry>
      </visual>
    </link>

    <!-- Hip Joint -->
    <joint name="right_hip" type="revolute">
      <parent>torso</parent>
      <child>right_thigh</child>
      <pose>0 0 0.2 0 0 0</pose>
      <axis>
        <xyz>1 0 0</xyz>
        <limit>
          <lower>-1.57</lower>
          <upper>1.57</upper>
          <effort>100</effort>
          <velocity>10</velocity>
        </limit>
        <dynamics>
          <damping>0.1</damping>
          <friction>0.1</friction>
        </dynamics>
      </axis>
    </joint>

  </model>
</sdf>
```

## Simulating Sensors

### LiDAR Sensor

```xml
<sensor name="lidar" type="gpu_lidar">
  <pose>0 0 0.1 0 0 0</pose>
  <update_rate>10</update_rate>
  <lidar>
    <scan>
      <horizontal>
        <samples>640</samples>
        <resolution>1</resolution>
        <min_angle>-3.14159</min_angle>
        <max_angle>3.14159</max_angle>
      </horizontal>
      <vertical>
        <samples>16</samples>
        <resolution>1</resolution>
        <min_angle>-0.261799</min_angle>
        <max_angle>0.261799</max_angle>
      </vertical>
    </scan>
    <range>
      <min>0.1</min>
      <max>30.0</max>
    </range>
  </lidar>
</sensor>
```

### Depth Camera (RealSense D435i)

```xml
<sensor name="depth_camera" type="depth">
  <update_rate>30</update_rate>
  <camera>
    <horizontal_fov>1.5184</horizontal_fov>
    <image>
      <width>640</width>
      <height>480</height>
      <format>R8G8B8</format>
    </image>
    <clip>
      <near>0.1</near>
      <far>10.0</far>
    </clip>
  </camera>
  <plugin name="depth_camera_controller" filename="libgazebo_ros_camera.so">
    <ros>
      <namespace>camera</namespace>
      <remapping>image_raw:=rgb/image_raw</remapping>
      <remapping>depth/image_raw:=depth/image_raw</remapping>
      <remapping>camera_info:=rgb/camera_info</remapping>
    </ros>
    <frame_name>camera_link</frame_name>
  </plugin>
</sensor>
```

### IMU (Inertial Measurement Unit)

```xml
<sensor name="imu" type="imu">
  <always_on>true</always_on>
  <update_rate>100</update_rate>
  <imu>
    <angular_velocity>
      <x>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.009</stddev>
        </noise>
      </x>
      <y>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.009</stddev>
        </noise>
      </y>
      <z>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.009</stddev>
        </noise>
      </z>
    </angular_velocity>
    <linear_acceleration>
      <x>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.017</stddev>
        </noise>
      </x>
    </linear_acceleration>
  </imu>
  <plugin name="imu_plugin" filename="libgazebo_ros_imu_sensor.so">
    <ros>
      <namespace>imu</namespace>
      <remapping>~/out:=data</remapping>
    </ros>
  </plugin>
</sensor>
```

## Unity: High-Fidelity Rendering

While Gazebo excels at physics, Unity provides photorealistic rendering for:

- **Computer vision training**: Realistic images for neural networks
- **Human-robot interaction**: Visualizing robot behavior for stakeholders
- **Virtual reality**: Immersive robot teleoperation

### Unity Robotics Hub

Unity provides official ROS integration:

```bash
# Install Unity Robotics Hub packages
# In Unity Package Manager, add:
# com.unity.robotics.ros-tcp-connector
# com.unity.robotics.urdf-importer
```

### Setting Up ROS-Unity Communication

#### Unity Side (C#):

```csharp
using UnityEngine;
using Unity.Robotics.ROSTCPConnector;
using RosMessageTypes.Geometry;

public class HumanoidController : MonoBehaviour
{
    private ROSConnection ros;
    private string topicName = "/cmd_vel";

    void Start()
    {
        ros = ROSConnection.GetOrCreateInstance();
        ros.RegisterPublisher<TwistMsg>(topicName);
        ros.Subscribe<TwistMsg>("/robot_pose", UpdateRobotPose);
    }

    void Update()
    {
        // Publish velocity commands
        TwistMsg twist = new TwistMsg
        {
            linear = new Vector3Msg { x = 1.0, y = 0, z = 0 },
            angular = new Vector3Msg { x = 0, y = 0, z = 0.5 }
        };
        ros.Publish(topicName, twist);
    }

    void UpdateRobotPose(TwistMsg pose)
    {
        // Update Unity humanoid based on ROS data
        transform.position = new Vector3(
            (float)pose.linear.x,
            (float)pose.linear.y,
            (float)pose.linear.z
        );
    }
}
```

#### ROS 2 Side (Python):

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class UnityBridge(Node):
    def __init__(self):
        super().__init__('unity_bridge')

        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.velocity_callback,
            10
        )

        self.pose_publisher = self.create_publisher(Twist, '/robot_pose', 10)

    def velocity_callback(self, msg):
        self.get_logger().info(f'Received from Unity: linear={msg.linear.x}, angular={msg.angular.z}')

        # Process and send back robot state
        pose = Twist()
        pose.linear.x = 1.0
        pose.linear.y = 2.0
        pose.linear.z = 0.5
        self.pose_publisher.publish(pose)

def main():
    rclpy.init()
    bridge = UnityBridge()
    rclpy.spin(bridge)
    bridge.destroy_node()
    rclpy.shutdown()
```

## Gazebo vs Unity: When to Use What

| Feature | Gazebo | Unity |
|---------|--------|-------|
| **Physics Accuracy** | Excellent (ODE, Bullet, DART) | Good (PhysX, but less tuned for robotics) |
| **Visual Quality** | Basic | Photorealistic |
| **ROS Integration** | Native | Via TCP connector |
| **Sensor Simulation** | Extensive (LiDAR, cameras, IMU, force/torque) | Good (cameras, basic sensors) |
| **Performance** | CPU-intensive | GPU-accelerated |
| **Use Case** | Algorithm development, testing | Data generation, visualization, VR |

**Best Practice**: Use **Gazebo for development** and **Unity for data generation and demonstration**.

## Practical Example: Simulating Bipedal Walking

### Step 1: Create Humanoid Model in Gazebo

```bash
cd ~/humanoid_ws/src
ros2 pkg create --build-type ament_python humanoid_simulation
cd humanoid_simulation
mkdir -p models/simple_humanoid
```

### Step 2: Write Walking Controller

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
import math

class BipedalWalkingController(Node):
    def __init__(self):
        super().__init__('bipedal_walking_controller')

        # Publishers for each leg joint
        self.left_hip_pub = self.create_publisher(Float64, '/left_hip_position_controller/command', 10)
        self.right_hip_pub = self.create_publisher(Float64, '/right_hip_position_controller/command', 10)
        self.left_knee_pub = self.create_publisher(Float64, '/left_knee_position_controller/command', 10)
        self.right_knee_pub = self.create_publisher(Float64, '/right_knee_position_controller/command', 10)

        # Timer for gait cycle
        self.timer = self.create_timer(0.01, self.update_gait)
        self.phase = 0.0

    def update_gait(self):
        # Simple sinusoidal gait pattern
        frequency = 1.0  # 1 Hz
        self.phase += 0.01 * frequency * 2 * math.pi

        # Left leg (swing phase)
        left_hip_angle = 0.3 * math.sin(self.phase)
        left_knee_angle = max(0, -0.6 * math.sin(self.phase))

        # Right leg (stance phase - opposite)
        right_hip_angle = 0.3 * math.sin(self.phase + math.pi)
        right_knee_angle = max(0, -0.6 * math.sin(self.phase + math.pi))

        # Publish commands
        self.left_hip_pub.publish(Float64(data=left_hip_angle))
        self.left_knee_pub.publish(Float64(data=left_knee_angle))
        self.right_hip_pub.publish(Float64(data=right_hip_angle))
        self.right_knee_pub.publish(Float64(data=right_knee_angle))

def main():
    rclpy.init()
    controller = BipedalWalkingController()
    rclpy.spin(controller)
    controller.destroy_node()
    rclpy.shutdown()
```

### Step 3: Launch Simulation

```python
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # Start Gazebo
        ExecuteProcess(
            cmd=['gazebo', '--verbose', 'humanoid_world.sdf'],
            output='screen'
        ),

        # Start walking controller
        Node(
            package='humanoid_simulation',
            executable='bipedal_walking_controller',
            name='walking_controller',
            output='screen'
        ),
    ])
```

## Collision Detection and Ground Contact

Critical for bipedal locomotion:

```xml
<collision name="foot_collision">
  <geometry>
    <box>
      <size>0.2 0.1 0.05</size>
    </box>
  </geometry>
  <surface>
    <friction>
      <ode>
        <mu>1.0</mu>
        <mu2>1.0</mu2>
      </ode>
    </friction>
    <contact>
      <ode>
        <kp>1000000.0</kp>
        <kd>100.0</kd>
        <max_vel>0.01</max_vel>
        <min_depth>0.001</min_depth>
      </ode>
    </contact>
  </surface>
</collision>
```

## Summary

In this module, you learned:

- **Gazebo simulation** for accurate physics testing
- **SDF and world creation** for humanoid environments
- **Sensor simulation** (LiDAR, cameras, IMU)
- **Unity integration** for photorealistic rendering
- **Bipedal walking simulation** basics

Next, we'll explore NVIDIA Isaac for AI-powered perception and training.

## Key Takeaways

- **Simulation is essential** before real-world deployment
- **Gazebo provides accurate physics** for algorithm development
- **Unity offers photorealistic visuals** for data generation
- **Sensor simulation** enables testing perception pipelines
- **Digital twins** accelerate development and reduce risk
