# BTech Project:- A prototype of AGV capable of surveillance

Uses Deep-Learning model used to detect anomaly/unwanted objects in a trained Lab Environment.

Images for traning the model are taken from a LogicTech WebCam mounted on top of a TutrleBot running using RaspberryPi(for AI) and Arduino Uno(for motion) and Robot Operating System(ROS) for communication a monitoring computer.

The Bot is also feeded with a path following algorithm to move around the lab autonomosly avoiding any collision and send out WARING mesages using ROS upon detection of any anomalous object in the Field Of View by the inference model running RaspBerryPi.


