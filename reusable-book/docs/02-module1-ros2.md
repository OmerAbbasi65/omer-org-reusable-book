---
id: 02-module1-ros2
title: Module 1 - The Robotic Nervous System (ROS 2)
sidebar_position: 2
---

# Module 1: The Robotic Nervous System (ROS 2)

## Introduction to ROS 2

The Robot Operating System 2 (ROS 2) is the middleware that serves as the nervous system of modern robots. Just as our nervous system coordinates communication between the brain and body parts, ROS 2 coordinates communication between different components of a robotic system.

## Why ROS 2?

ROS 2 represents a complete redesign of the original ROS, built from the ground up to address the needs of production robotics:

- **Real-time Performance**: Critical for humanoid robots that need split-second reactions
- **Security**: Built-in DDS (Data Distribution Service) security
- **Cross-platform Support**: Works on Linux, Windows, and macOS
- **Multi-robot Systems**: Native support for robot swarms and teams

## Core Concepts

### 1. Nodes

Nodes are the fundamental building blocks of ROS 2. Each node is a process that performs a specific computation. In a humanoid robot:

- **Vision Node**: Processes camera data
- **Motion Planning Node**: Calculates joint trajectories
- **Balance Controller Node**: Maintains bipedal stability
- **Speech Recognition Node**: Processes voice commands

```python
import rclpy
from rclpy.node import Node

class HumanoidController(Node):
    def __init__(self):
        super().__init__('humanoid_controller')
        self.get_logger().info('Humanoid Controller Node Started')
```

### 2. Topics

Topics enable publish-subscribe communication between nodes. Think of topics as news channels that nodes can broadcast to or listen from.

**Common Humanoid Robot Topics**:
- `/joint_states` - Current position of all joints
- `/camera/image_raw` - Video feed from robot's cameras
- `/imu/data` - Inertial measurement unit data for balance
- `/cmd_vel` - Velocity commands for movement

```python
from sensor_msgs.msg import JointState

class JointPublisher(Node):
    def __init__(self):
        super().__init__('joint_publisher')
        self.publisher_ = self.create_publisher(JointState, 'joint_states', 10)
        self.timer = self.create_timer(0.1, self.publish_joint_state)

    def publish_joint_state(self):
        msg = JointState()
        msg.name = ['shoulder_roll', 'shoulder_pitch', 'elbow']
        msg.position = [0.0, 1.57, 0.785]
        self.publisher_.publish(msg)
```

### 3. Services

Services provide synchronous request-reply communication. Use services when you need a response:

- **Request**: "What is the current battery level?"
- **Reply**: "Battery at 75%"

```python
from std_srvs.srv import Trigger

class BatteryService(Node):
    def __init__(self):
        super().__init__('battery_service')
        self.srv = self.create_service(Trigger, 'check_battery', self.check_battery_callback)

    def check_battery_callback(self, request, response):
        response.success = True
        response.message = 'Battery at 75%'
        return response
```

### 4. Actions

Actions are for long-running tasks that need feedback. Perfect for humanoid robot tasks like:

- Walking to a destination (with progress updates)
- Picking up an object (with grasp status)
- Performing a dance routine (with completion percentage)

```python
from action_msgs.msg import GoalStatus
from nav2_msgs.action import NavigateToPose
import rclpy
from rclpy.action import ActionClient

class NavigationClient(Node):
    def __init__(self):
        super().__init__('navigation_client')
        self._action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

    def send_goal(self, x, y):
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y
        self._action_client.send_goal_async(goal_msg, feedback_callback=self.feedback_callback)

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info(f'Distance remaining: {feedback.distance_remaining}')
```

## Understanding URDF for Humanoids

The Unified Robot Description Format (URDF) is an XML format for describing a robot's physical structure. For humanoid robots, this includes:

### Basic URDF Structure

```xml
<?xml version="1.0"?>
<robot name="simple_humanoid">

  <!-- Base Link (Torso) -->
  <link name="torso">
    <visual>
      <geometry>
        <box size="0.3 0.2 0.5"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 1 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.3 0.2 0.5"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="10.0"/>
      <inertia ixx="0.1" ixy="0.0" ixz="0.0" iyy="0.1" iyz="0.0" izz="0.1"/>
    </inertial>
  </link>

  <!-- Head -->
  <link name="head">
    <visual>
      <geometry>
        <sphere radius="0.1"/>
      </geometry>
    </visual>
    <inertial>
      <mass value="2.0"/>
      <inertia ixx="0.01" ixy="0.0" ixz="0.0" iyy="0.01" iyz="0.0" izz="0.01"/>
    </inertial>
  </link>

  <!-- Neck Joint -->
  <joint name="neck_joint" type="revolute">
    <parent link="torso"/>
    <child link="head"/>
    <origin xyz="0 0 0.3" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="-1.57" upper="1.57" effort="10" velocity="1.0"/>
  </joint>

</robot>
```

### Key Components for Humanoid URDF

1. **Links**: Physical parts (head, torso, arms, legs)
2. **Joints**: Connections between links (shoulders, elbows, knees, hips)
3. **Sensors**: Cameras, IMU, force/torque sensors
4. **Actuators**: Motor specifications for each joint

## Bridging Python Agents to ROS Controllers

Modern humanoid robots use AI agents for decision-making. Here's how to bridge an AI agent to ROS 2:

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import openai

class AIRobotController(Node):
    def __init__(self):
        super().__init__('ai_robot_controller')
        self.cmd_vel_publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.openai_client = openai.OpenAI()

    def process_command(self, natural_language_command):
        # Use LLM to convert natural language to robot actions
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a robot motion controller. Convert natural language to velocity commands."},
                {"role": "user", "content": f"Command: {natural_language_command}. Reply with JSON: {{linear_x, linear_y, angular_z}}"}
            ]
        )

        # Parse LLM response and publish to ROS
        command = eval(response.choices[0].message.content)

        twist = Twist()
        twist.linear.x = command.get('linear_x', 0.0)
        twist.linear.y = command.get('linear_y', 0.0)
        twist.angular.z = command.get('angular_z', 0.0)

        self.cmd_vel_publisher.publish(twist)
        self.get_logger().info(f'Executing: {natural_language_command}')

def main():
    rclpy.init()
    controller = AIRobotController()

    # Example: Natural language control
    controller.process_command("Move forward slowly")
    controller.process_command("Turn left")
    controller.process_command("Stop")

    rclpy.spin(controller)
    controller.destroy_node()
    rclpy.shutdown()
```

## Practical Exercise: Building Your First Humanoid Controller

### Step 1: Install ROS 2

```bash
# Ubuntu 22.04
sudo apt update
sudo apt install ros-humble-desktop
source /opt/ros/humble/setup.bash
```

### Step 2: Create a Workspace

```bash
mkdir -p ~/humanoid_ws/src
cd ~/humanoid_ws/src
ros2 pkg create --build-type ament_python humanoid_controller
```

### Step 3: Write a Simple Balance Controller

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Twist
import numpy as np

class BalanceController(Node):
    def __init__(self):
        super().__init__('balance_controller')

        # Subscribe to IMU data
        self.imu_subscription = self.create_subscription(
            Imu,
            '/imu/data',
            self.imu_callback,
            10
        )

        # Publish corrective movements
        self.cmd_publisher = self.create_publisher(Twist, '/balance_cmd', 10)

        self.target_pitch = 0.0  # Upright position
        self.kp = 1.0  # Proportional gain

    def imu_callback(self, msg):
        # Extract pitch from IMU (simplified)
        pitch = self.extract_pitch(msg.orientation)

        # Calculate error
        error = self.target_pitch - pitch

        # Simple P controller for balance
        corrective_velocity = self.kp * error

        # Publish corrective command
        twist = Twist()
        twist.linear.x = corrective_velocity
        self.cmd_publisher.publish(twist)

        self.get_logger().info(f'Pitch: {pitch:.2f}, Correction: {corrective_velocity:.2f}')

    def extract_pitch(self, quaternion):
        # Convert quaternion to Euler angles
        # Simplified - use tf_transformations in real implementation
        return 0.0  # Placeholder

def main(args=None):
    rclpy.init(args=args)
    balance_controller = BalanceController()
    rclpy.spin(balance_controller)
    balance_controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Launch Files

Launch files allow you to start multiple nodes simultaneously:

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='humanoid_controller',
            executable='balance_controller',
            name='balance_controller',
            output='screen'
        ),
        Node(
            package='humanoid_controller',
            executable='vision_processor',
            name='vision_processor',
            output='screen'
        ),
        Node(
            package='humanoid_controller',
            executable='motion_planner',
            name='motion_planner',
            output='screen'
        ),
    ])
```

## Best Practices for Humanoid ROS 2 Development

1. **Modular Design**: Separate perception, planning, and control
2. **Real-time Constraints**: Use real-time executors for critical loops
3. **Quality of Service (QoS)**: Configure reliable communication for sensor data
4. **Lifecycle Management**: Implement lifecycle nodes for controlled startup/shutdown
5. **Parameter Management**: Use ROS parameters for easy tuning

## Summary

In this module, you learned:
- ROS 2 architecture and core concepts (nodes, topics, services, actions)
- How to describe humanoid robots using URDF
- Bridging Python AI agents to ROS controllers using rclpy
- Building a simple balance controller
- Best practices for humanoid robot development

In the next module, we'll explore how to simulate these robots in photorealistic environments using Gazebo and Unity.

## Key Takeaways

- **ROS 2 is the industry standard** for robot control and communication
- **Nodes communicate** through topics (pub/sub), services (request/reply), and actions (long-running tasks)
- **URDF describes** the physical structure of humanoid robots
- **Python + rclpy** makes it easy to integrate AI agents with ROS 2
- **Modular design** is crucial for complex humanoid systems
