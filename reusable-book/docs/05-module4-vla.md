---
id: 05-module4-vla
title: Module 4 - Vision-Language-Action (VLA)
sidebar_position: 5
---

# Module 4: Vision-Language-Action (VLA)

## The Convergence of LLMs and Robotics

Vision-Language-Action (VLA) models represent the cutting edge of robotics AI, combining:

- **Vision**: Understanding the visual world through cameras
- **Language**: Processing natural language commands
- **Action**: Executing physical tasks in the real world

This convergence enables humanoid robots to understand commands like "Clean the room" and autonomously break them down into actionable steps.

## Architecture of VLA Systems

```
┌─────────────────────────────────────────────────────────┐
│                   Natural Language Input                │
│              "Pick up the red cup from the table"      │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
         ┌─────────────────────┐
         │   Language Model    │
         │   (GPT-4, Claude)   │
         └──────────┬──────────┘
                    │
                    ▼
         ┌─────────────────────┐
         │  Task Decomposition │
         │  1. Locate red cup  │
         │  2. Navigate to table│
         │  3. Grasp cup       │
         │  4. Lift cup        │
         └──────────┬──────────┘
                    │
      ┌─────────────┴─────────────┐
      ▼                           ▼
┌──────────┐              ┌──────────────┐
│  Vision  │              │  Action      │
│  System  │◄────────────►│  Planner     │
└──────────┘              └───────┬──────┘
      │                           │
      ▼                           ▼
┌──────────────────────────────────────┐
│         ROS 2 Control System         │
└──────────────────────────────────────┘
```

## Voice-to-Action with OpenAI Whisper

### Setting Up Whisper

```bash
pip install openai-whisper
pip install pyaudio
```

### Implementing Speech Recognition

```python
import whisper
import pyaudio
import wave
import tempfile
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class VoiceCommandNode(Node):
    def __init__(self):
        super().__init__('voice_command_node')

        # Load Whisper model
        self.model = whisper.load_model("base")

        # Publisher for recognized commands
        self.command_pub = self.create_publisher(String, '/voice_commands', 10)

        # Audio settings
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.RECORD_SECONDS = 5

        self.get_logger().info('Voice Command Node Ready')

    def record_audio(self):
        """Record audio from microphone"""
        p = pyaudio.PyAudio()

        stream = p.open(format=self.FORMAT,
                       channels=self.CHANNELS,
                       rate=self.RATE,
                       input=True,
                       frames_per_buffer=self.CHUNK)

        self.get_logger().info('Listening...')

        frames = []
        for i in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
            data = stream.read(self.CHUNK)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            wf = wave.open(f.name, 'wb')
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(p.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            return f.name

    def transcribe_audio(self, audio_file):
        """Convert speech to text using Whisper"""
        result = self.model.transcribe(audio_file)
        return result["text"]

    def process_voice_command(self):
        """Main loop for processing voice commands"""
        while rclpy.ok():
            # Record audio
            audio_file = self.record_audio()

            # Transcribe
            command = self.transcribe_audio(audio_file)
            self.get_logger().info(f'Recognized: {command}')

            # Publish to command topic
            msg = String()
            msg.data = command
            self.command_pub.publish(msg)

def main():
    rclpy.init()
    node = VoiceCommandNode()

    # Start voice command processing
    node.process_voice_command()

    node.destroy_node()
    rclpy.shutdown()
```

## Cognitive Planning with LLMs

### Using OpenAI GPT-4 for Task Planning

```python
from openai import OpenAI
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped
import json

class CognitivePlannerNode(Node):
    def __init__(self):
        super().__init__('cognitive_planner')

        self.client = OpenAI()

        # Subscribe to voice commands
        self.command_sub = self.create_subscription(
            String, '/voice_commands', self.command_callback, 10
        )

        # Publishers for robot actions
        self.navigation_pub = self.create_publisher(PoseStamped, '/goal_pose', 10)
        self.manipulation_pub = self.create_publisher(String, '/manipulation_cmd', 10)
        self.speech_pub = self.create_publisher(String, '/robot_speech', 10)

        # System prompt for the robot's capabilities
        self.system_prompt = """You are the AI brain of a humanoid robot. You can:
1. Navigate to locations (navigate_to)
2. Pick up objects (pick_up)
3. Place objects (place_down)
4. Speak (say)
5. Recognize objects (identify)

Given a natural language command, break it down into a JSON sequence of actions.

Example:
Input: "Bring me the red cup from the kitchen"
Output:
{
  "plan": [
    {"action": "say", "params": {"text": "I'll get the red cup for you"}},
    {"action": "navigate_to", "params": {"location": "kitchen"}},
    {"action": "identify", "params": {"object": "red cup"}},
    {"action": "pick_up", "params": {"object": "red cup"}},
    {"action": "navigate_to", "params": {"location": "user_location"}},
    {"action": "say", "params": {"text": "Here is your red cup"}}
  ]
}
"""

    def command_callback(self, msg):
        command = msg.data
        self.get_logger().info(f'Processing command: {command}')

        # Generate action plan using GPT-4
        plan = self.generate_plan(command)

        # Execute the plan
        self.execute_plan(plan)

    def generate_plan(self, command):
        """Use GPT-4 to create an action plan"""
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": command}
            ],
            temperature=0.3
        )

        plan_text = response.choices[0].message.content
        self.get_logger().info(f'Generated plan: {plan_text}')

        # Parse JSON plan
        try:
            plan = json.loads(plan_text)
            return plan["plan"]
        except json.JSONDecodeError:
            self.get_logger().error('Failed to parse plan JSON')
            return []

    def execute_plan(self, plan):
        """Execute the action plan step by step"""
        for step in plan:
            action = step["action"]
            params = step["params"]

            self.get_logger().info(f'Executing: {action} with params {params}')

            if action == "navigate_to":
                self.navigate_to(params["location"])
            elif action == "pick_up":
                self.pick_up(params["object"])
            elif action == "place_down":
                self.place_down(params["location"])
            elif action == "say":
                self.say(params["text"])
            elif action == "identify":
                self.identify(params["object"])

            # Wait for action to complete (simplified)
            import time
            time.sleep(2)

    def navigate_to(self, location):
        """Navigate to a semantic location"""
        # In practice, use a semantic map
        location_map = {
            "kitchen": (5.0, 3.0),
            "living_room": (2.0, 1.0),
            "bedroom": (8.0, 5.0),
            "user_location": (0.0, 0.0)
        }

        if location in location_map:
            x, y = location_map[location]
            pose = PoseStamped()
            pose.header.frame_id = "map"
            pose.pose.position.x = x
            pose.pose.position.y = y
            pose.pose.orientation.w = 1.0

            self.navigation_pub.publish(pose)
            self.get_logger().info(f'Navigating to {location} at ({x}, {y})')

    def pick_up(self, object_name):
        """Pick up an object"""
        msg = String()
        msg.data = f"pick_up:{object_name}"
        self.manipulation_pub.publish(msg)
        self.get_logger().info(f'Picking up {object_name}')

    def place_down(self, location):
        """Place down held object"""
        msg = String()
        msg.data = f"place_down:{location}"
        self.manipulation_pub.publish(msg)
        self.get_logger().info(f'Placing down at {location}')

    def say(self, text):
        """Speak text using TTS"""
        msg = String()
        msg.data = text
        self.speech_pub.publish(msg)
        self.get_logger().info(f'Speaking: {text}')

    def identify(self, object_name):
        """Identify and locate an object"""
        msg = String()
        msg.data = f"identify:{object_name}"
        self.manipulation_pub.publish(msg)
        self.get_logger().info(f'Identifying {object_name}')

def main():
    rclpy.init()
    planner = CognitivePlannerNode()
    rclpy.spin(planner)
    planner.destroy_node()
    rclpy.shutdown()
```

## Vision-Language Models for Object Recognition

### Using CLIP for Zero-Shot Object Detection

```python
import torch
import clip
from PIL import Image
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image as RosImage
from cv_bridge import CvBridge
import cv2
import numpy as np

class VisionLanguageNode(Node):
    def __init__(self):
        super().__init__('vision_language_node')

        # Load CLIP model
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model, self.preprocess = clip.load("ViT-B/32", device=self.device)

        self.bridge = CvBridge()

        # Subscribe to camera
        self.image_sub = self.create_subscription(
            RosImage, '/camera/image_raw', self.image_callback, 10
        )

        # List of objects the robot can recognize
        self.object_classes = [
            "red cup", "blue bottle", "green book", "yellow banana",
            "white plate", "black phone", "person", "chair", "table"
        ]

        # Precompute text features
        text_inputs = torch.cat([clip.tokenize(f"a photo of a {c}") for c in self.object_classes]).to(self.device)
        with torch.no_grad():
            self.text_features = self.model.encode_text(text_inputs)
            self.text_features /= self.text_features.norm(dim=-1, keepdim=True)

    def image_callback(self, msg):
        # Convert ROS image to CV2
        cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")

        # Detect objects
        detections = self.detect_objects(cv_image)

        # Visualize
        self.visualize_detections(cv_image, detections)

    def detect_objects(self, image):
        """Detect objects using CLIP"""
        # Convert to PIL Image
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        # Preprocess
        image_input = self.preprocess(pil_image).unsqueeze(0).to(self.device)

        # Compute image features
        with torch.no_grad():
            image_features = self.model.encode_image(image_input)
            image_features /= image_features.norm(dim=-1, keepdim=True)

        # Compute similarities
        similarity = (100.0 * image_features @ self.text_features.T).softmax(dim=-1)

        # Get top predictions
        values, indices = similarity[0].topk(3)

        detections = []
        for value, index in zip(values, indices):
            detections.append({
                "class": self.object_classes[index],
                "confidence": value.item()
            })

        return detections

    def visualize_detections(self, image, detections):
        """Display detected objects"""
        display_image = image.copy()

        y_offset = 30
        for detection in detections:
            text = f"{detection['class']}: {detection['confidence']:.2f}"
            cv2.putText(display_image, text, (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            y_offset += 30

        cv2.imshow('Vision-Language Detection', display_image)
        cv2.waitKey(1)

def main():
    rclpy.init()
    node = VisionLanguageNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
```

## Multimodal Interaction: Speech, Gesture, Vision

### Gesture Recognition

```python
import mediapipe as mp
import cv2
from rclpy.node import Node

class GestureRecognitionNode(Node):
    def __init__(self):
        super().__init__('gesture_recognition')

        # MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils

    def recognize_gesture(self, image):
        """Recognize hand gestures"""
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Process
        results = self.hands.process(rgb_image)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw landmarks
                self.mp_draw.draw_landmarks(
                    image, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                )

                # Classify gesture
                gesture = self.classify_gesture(hand_landmarks)
                return gesture

        return "none"

    def classify_gesture(self, hand_landmarks):
        """Classify gesture based on hand landmarks"""
        # Get finger tip and base positions
        thumb_tip = hand_landmarks.landmark[4]
        index_tip = hand_landmarks.landmark[8]
        middle_tip = hand_landmarks.landmark[12]
        ring_tip = hand_landmarks.landmark[16]
        pinky_tip = hand_landmarks.landmark[20]

        # Simple gesture classification
        # Thumbs up: thumb extended, others closed
        # Point: index extended, others closed
        # Wave: hand open and moving

        # Placeholder logic
        if index_tip.y < 0.5:  # Index finger up
            return "point"
        elif thumb_tip.x < 0.3:  # Thumb up
            return "thumbs_up"
        else:
            return "open_palm"
```

## Capstone Project: The Autonomous Humanoid

### Project Description

Build a simulated humanoid robot that:

1. **Receives voice command**: "Clean the room"
2. **Plans path**: Using Nav2 to navigate around obstacles
3. **Identifies objects**: Using computer vision to find trash
4. **Manipulates objects**: Grasping and moving items
5. **Reports completion**: Using text-to-speech

### Implementation

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped
import time

class AutonomousHumanoid(Node):
    def __init__(self):
        super().__init__('autonomous_humanoid')

        # State machine
        self.state = "idle"

        # Subscribers
        self.voice_sub = self.create_subscription(
            String, '/voice_commands', self.voice_callback, 10
        )

        # Publishers
        self.nav_pub = self.create_publisher(PoseStamped, '/goal_pose', 10)
        self.speech_pub = self.create_publisher(String, '/speech', 10)
        self.manipulation_pub = self.create_publisher(String, '/manipulation', 10)

        # Timer for state machine
        self.timer = self.create_timer(0.1, self.state_machine_update)

        self.get_logger().info('Autonomous Humanoid Ready')

    def voice_callback(self, msg):
        command = msg.data.lower()

        if "clean the room" in command:
            self.state = "planning"
            self.speak("I'll clean the room for you")

    def state_machine_update(self):
        if self.state == "planning":
            self.plan_cleaning_route()
            self.state = "navigating"

        elif self.state == "navigating":
            # Check if reached goal
            if self.reached_goal():
                self.state = "searching"

        elif self.state == "searching":
            # Search for objects to clean
            if self.found_object():
                self.state = "manipulating"
            else:
                self.state = "reporting"

        elif self.state == "manipulating":
            self.pick_up_object()
            self.state = "disposing"

        elif self.state == "disposing":
            self.dispose_object()
            self.state = "searching"

        elif self.state == "reporting":
            self.speak("Room cleaning complete")
            self.state = "idle"

    def plan_cleaning_route(self):
        # Generate waypoints covering the room
        waypoints = [
            (1.0, 1.0), (3.0, 1.0), (3.0, 3.0), (1.0, 3.0)
        ]
        self.current_waypoint = 0
        self.waypoints = waypoints
        self.navigate_to_waypoint(0)

    def navigate_to_waypoint(self, index):
        if index < len(self.waypoints):
            x, y = self.waypoints[index]
            pose = PoseStamped()
            pose.header.frame_id = "map"
            pose.pose.position.x = x
            pose.pose.position.y = y
            pose.pose.orientation.w = 1.0
            self.nav_pub.publish(pose)

    def reached_goal(self):
        # Check navigation status
        # Placeholder
        return True

    def found_object(self):
        # Use vision system to detect objects
        # Placeholder
        return False

    def pick_up_object(self):
        msg = String()
        msg.data = "pick_up"
        self.manipulation_pub.publish(msg)

    def dispose_object(self):
        msg = String()
        msg.data = "dispose"
        self.manipulation_pub.publish(msg)

    def speak(self, text):
        msg = String()
        msg.data = text
        self.speech_pub.publish(msg)
        self.get_logger().info(f'Speaking: {text}')

def main():
    rclpy.init()
    robot = AutonomousHumanoid()
    rclpy.spin(robot)
    robot.destroy_node()
    rclpy.shutdown()
```

## Summary

In this module, you learned:

- **Voice-to-Action** with OpenAI Whisper
- **Cognitive planning** using LLMs (GPT-4)
- **Vision-Language models** (CLIP) for object recognition
- **Multimodal interaction** combining speech, vision, and gestures
- **Capstone project** integrating all skills

## Key Takeaways

- **VLA models** bridge the gap between language and physical action
- **LLMs can plan** complex robotic tasks from natural language
- **Voice commands** make robots more accessible and intuitive
- **Vision-Language models** enable zero-shot object recognition
- **Multimodal fusion** creates robust human-robot interaction

## Next Steps

With these four modules complete, you now have a comprehensive understanding of Physical AI and Humanoid Robotics. Continue experimenting with:

- More complex manipulation tasks
- Multi-robot coordination
- Advanced reinforcement learning
- Real-world deployment with physical robots

Congratulations on completing the Physical AI & Humanoid Robotics course!
