SafeWalk Installation Instructions

1. Clone or copy the repository to your machine.

2. Open a terminal in the project root.
3. Create a Python virtual environment:
   python3 -m venv venv

4. Activate the virtual environment:
   source venv/bin/activate

5. Upgrade pip:
   python -m pip install --upgrade pip

6. Install the required dependencies:
   pip install -r fog_node/requirements.txt
   pip install -r sensors/requirements.txt
   pip install -r dashboard/requirements.txt

7. Make sure Mosquitto MQTT broker is installed and running on port 1883.

8. Start the sensor simulator:
   ./venv/bin/python sensors/sensor_sim.py

9. Start the fog node:
   ./venv/bin/python fog_node/fog_node.py

10. Start the dashboard:
    ./venv/bin/python dashboard/app.py

Notes:
- The sensor and fog components use MQTT on localhost:1883.
- AWS credentials must be available for the cloud backend to store incidents and send notifications.
- If you are running on EC2, make sure the instance has network access to AWS services and that the required AWS resources already exist.
