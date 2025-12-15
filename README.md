# Logistics Optimization Portfolio Project

## Specification and Requirements

### Summary
 --    A (hypothetical) logistics company that serves Regina, SK reached out on the basis of creating a new solution to optimize their delivery service. They're looking for an end-to-end product that automates their route planning for their fleet of 20+ delivery vehicles. This new system must ingest delivery orders; optimize routes based on time, distance, or traffic; assign these routes to drivers, and track delivery completion in real time. 

#### Key User Roles
    1. The Dispatcher (Admin Web View) needs a "command center" to see all trucks and orders.
    2. The Driver (Mobile/Tablet View) needs a simple hands-free interface to their next stop.
    3. The Customer (Notification Recipient) needs to know when their package is arriving.

### Functional Requirements

#### The Optimization Engine
    - Multi-stop routing: The system must calculate the most efficient order to visit them.
    - Constraints:
        - Time Windows: Some business in the warehouse district are only open 0800 to 1600.
        - Vehicle Capacity: Don't overload the delivery vans, assign heavy pallets to the 5-tons.
        - Start/End Point: All trucks starts and ends in the HQ on Park Street (somewhere in Regina,SK),

#### Dispatcher Dashboard
    - Interactive Map: visual dispaly of Regina with all active truucks and pending stops overlaid.
    - Drag-and-Drop Assignment: Ability to manually move a stop from Driver A to Driver B if a truck breaksdown.
    - Status Monitoring: Color-coded status for On-Time, Delayed, or At Risk.

#### Driver Interface
    - Turn-by-turn Navigation: Deep-linking to Google Maps or Waze.
    - Proof of Delivery: Digital Signal capture and photo upload.
    - Status Updates: One-tap buttons for "Arrived", "Unloading", and "Complete."

#### The "Regina Factor"
    - Weather Integration: If Environment Canada issues a snowfall warning, the algorithm should automatically add a 20% buffer to travel times.
    - Traffic Avoidance: Avoid Ring Road during 1630 to 1530 rush hour if possible.


### Technical Expectations:

#### Tech stack
    - Prefers React/Next.js for front end, Node/Python for back end.
#### Database
    - Real time data sync is crucial
#### Scalability
    - The architecture must support multiple hubs.
    


### Success Metrics:
- Reduce average daily mileage per driver by 15%,
- Reduce dispatcher planning time from to 2 hours to 15 minutes,
- Increase on-time delivery rate to 98%


## Project directory hierarchy:
 infrastructure/ — Container orchestration and database setup

     docker-compose.yml — (Implemented) DB, PgAdmin, OSRM

 backend/ — Core application logic and routing

     pipeIngest.py — (Implemented) ETL pipeline

     osrm_router.py — (Implemented) OSRM wrapper

     logic_solver.py — (In Progress) VRP optimization engine

 api/ — (TODO) REST/Graph API

     weather_service.py — (TODO) Environment Canada connector

 frontend/ — (TODO) User interfaces

     dispatcher-dashboard/ — (TODO) React-based admin panel

     driver-app/ — (TODO) Mobile-first driver view

 config/ — Project configuration

     mise.toml

     requirements.txt

     .gitignore