# Flight Path Generation for Drone-Based Methane Detection

This Python software library generates a flight path for the automated detection of methane leaks on a wellpad. For a more detailed description of the algorithm, please refer to the [project description](projectdescription.pdf).

## Before Flight
* [Before Flight Example](main.py): sample path generation
* [Distribution Set Up](DistributionSetUp.py): sample probability distribution setup and graph
* [Probability Distribution Generation](ProbDist.py): generates probability distribution specifying regions where methane leaks are likely
* [Initial Waypoint Assignment](initialwaypoint.py): utilizes this probability distribution to create drone waypoints
* [Path Generation](PathGeneration.py): generates optimal path through waypoints
* [Traveling Salesman Problem Solver](tsp_solver): orders waypoints for shortest flight path

## During Flight
* [During Flight Controller](inflight.py): intakes data during flight, computes the confusion matrix, and triggers the generation of flux planes 
* [Confusion Matrix Calculation](confusionmat.py): computes the confusion matrix
* [Flux Plane Generation](fluxplane.py): generates a flux plane

## Other Files
* [Methane Flow Model](concentrationmodel.py): flow model specified by EPA model and Hogkinson et al.
* [Flight Data](flightdata.py): imports flight data from .kml and .csv files
