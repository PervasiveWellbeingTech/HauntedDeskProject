# Haunted Desk Project

Automated desk that goes up and down on its own periodically.
The goal here is to collect data from several desks for analysis.

## Global architecture

*put schema here*

An Arduino module is connected to each desk that we want to control. This module will make the desk to move and record the raw data of
these movements.  
A RaspberryPi is associated to several Arduino modules, in order to collect the raw data files and save them locally.  
All the RaspberryPi send their data to a Google Drive to bring everything together in one place.  

Workflow (we consider here one desk with its Arduino module and one RaspberryPi, to simplify):
- during the day, the Arduino module controls its desk
- at night, the RaspberryPi collects the file saved by the Arduino module during the day
- the RaspberryPi synchronizes its files with the Google Drive

See below for a detailed workflow.

## Detailed workflow

*todo*
