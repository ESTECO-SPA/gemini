# GEMINI PROJECT :closed_book:
This project is a collaboration between [ESTECO](https://www.esteco.com/) and [VISCANDO](https://viscando.com/) to create an infrastructure able to connect an agent guided by a custom logic to the [ESMINI simulator](https://github.com/esmini/esmini). For this project we used a sample model logic based on an Inverse Reinforcement Learning model provided by VISCANDO. The aim of the project is to identify  technical steps and obstacles for connecting models to the ESMINI simulator (for more details see [contribution/contribution.md](contribution/contribution.md))

The infrastructure developed in this project addressed the following challenges:
- Interactive actor models, that require input from the traffic environment simulated in ESMINI
- Time-sensitive models that simulate immediate reaction of driver on the instant driving situation – requiring low delay in communication
- Computationally heavy models (for example DNN-based ones) that require multiple time steps in ESMINI to produce the action

This project has been a part of the research project [ASCETISM](https://www.vinnova.se/en/p/autonomous-and-connected-vehicle-testing-using-infrastructure-sensor-measurements/) (Autonomous and Connected Vehicle Testing using Infrastructure Sensor Measurements), funded by Swedish Innovation Agency [Vinnova](https://www.vinnova.se/en/), and a collaboration between Viscando, Asta Zero test track, Zenseact, Volvo Cars and Chalmers University of Technology, investigated how simulations and test-track testing of autonomous vehicles could be improved with help of scenarios and behavior models based on naturalistic traffic data collected by smart roadside sensors.
The final report from the project (in English) can be found [here](https://www.vinnova.se/globalassets/mikrosajter/ffi/dokument/slutrapporter-ffi/elektronik-mjukvara-och-kommunikation-rapporter/2020-05137eng.pdf).

The sample actor model attempts to drive a vehicle on a motorway on-ramp, reacting to its own motion and vehicles on the motorway, to ensure a safe merge. The model is described in detail in the ASCETISM final report.

## How To

- If you need to set up your environment to run the code, please follow these instructions: [doc/environment.md](doc/environment.md)
- For more information of the general concept, code infrastructure, and known issues see [contribution/contribution.md](contribution/contribution.md) 
- For a quick start refers to [doc/quickstart.md](doc/quickstart.md) 

## License
The source code is released under the [MIT License](https://mit-license.org/).
