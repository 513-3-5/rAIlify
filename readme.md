# rAIlify
rAIlify is a challenge pitched by Siemens at the 2024 [BaselHack](https://www.baselhack.ch/). 

![Logo derailed](assets/img/logo_png_w_bg.png)


### Task of Challenge (User Story)
As a railway engineer at Siemens Mobility, I want to utilize a digital node-edge model of my railway network. Unfortunately, information gets delivered in old school vectorized PDF and TIFF formats. I’m far too lazy to manually engineer that huge variety of visual data.

Help me to recognize tracks, switches , signals, annotations and other entities and to arrange them in a standardized model for my work. Bring us on the engineering fast track when we e.g. have to modernize interlockings or determine optimized and safe routes through the rail network. This is much more than just image recognition! The real challenge lies in the variability of how plans are drawn and how information is arranged.

My vision is to use the extracted topology data as input for further sophisticated railway solutions. To have a digital model that spans the entire engineering process and life cycle.

### Workflow Diagram
![Workflow Diagram](documentation/Dataflow_diagram_png.png)

### Team Members 
* Amar Tabakovic
* Johannes Casaburi
* Adrian Altermatt
* Zora Fuchs
* Sarah Rebecca Meyer
* Patrick Schwartz
* Noah Grun

## Setup

### Visualiztion

#### Requirements

- Ruby installed (https://www.ruby-lang.org/en/documentation/installation/)
- Graphviz installed (https://graphviz.org/download/)

#### installation

1. Navigate to visualization folder: `cd code/visualization`
2. Install libraries: `bundle install`

#### Run

The application can be run with multiple files. The results will be stored in the `output` folder.

- Run application: `ruby visualizer.rb path/filename1.json path/filename2.json ...`
- Run with given example files: `ruby visualizer.rb input/example.json input/tiefengrund.json`
