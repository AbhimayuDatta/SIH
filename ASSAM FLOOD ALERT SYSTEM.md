 #ASSAM_FLOOD_ISSUEE [[ASSAM FLOOD SOLUTIONS]]
**Plan** :
Creating a sensor mesh  that are extended to the high risk areas, like Barpeta, Goalpara, Nalbari, and Silchar (Cachar), so that they can evacute to safety when there is a sudden rise in the water level. 

***Problems***
 1. Building the peer to peer connection between the sensors. [[MESH NETWORKING]]
 2. Deciding what is the *Dangerous* increase rate of water level is ? [[PHYSICAL ISSUES]]
 3. What is the right amount of time people need to evacute to a safe place ? [[PHYSICAL ISSUES]]
 4. How to build a reliable autonomous system that will decide when to alert and when not to ? [[MESH NETWORKING]]
 5. How will we power the sensors ? [[PHYSICAL ISSUES]]
 6. What kind protocol to use for communication in between the sensors ? [[MESH NETWORKING]]
 7. a warning threshold should not be based only on the riverbank height. It should also consider the elevation of nearby houses, roads, shelters, embankments, and evacuation routes, Feasbility Problem.

**Rough Sketch of the Project**

Sudden rise in water level ---> checks data of previous 5 and next 5 sensors ---> compares this average data with the *Dangerous-level* ---> If the average rate of the rise in water(ARRV) level is is less than the *Dangerous-level* , then the spike is logged but no alert is generated else if the ARRV is higher than *Dangerous-level* then an danger alerted is generated and a panic signal is send throughout the Mesh-Network from there ---> The people from the risk areas could evacute to safety ---> The data is also send to the [National Disaster Management Authority](https://en.wikipedia.org/wiki/National_Disaster_Management_Authority_\(India\)) and [Assam State Disaster Management Authority (ASDMA)](https://asdma.assam.gov.in/) .

# Refinements in the sketch 

- Instead of ARRV being the main and only parameter to decide the evacutiona of multi people and livestocks, It's better to follow something like this - 

	Risk = f(
	    current water level,
	    rate of rise,
	    predicted water level,
	    upstream rainfall,
	    cumulative rainfall,
	    soil saturation,
	    river travel time,
	    local elevation,
	    population vulnerability
	)

- A practical 4-stage plan - 

| Project level | Condition | System action | 
|---|---|---|
| Green | Normal conditions | Continue monitoring |
| Yellow | Rainfall or water level rising, but evacuation is not yet needed | Notify authorities and prepare residents |
| Orange | Forecast water level may reach danger level within the evacuation time | Ask vulnerable residents to evacuate; activate shelters |
| Red | Water level is at or above danger level, or flooding is imminent | Issue immediate evacuation/safety alert |

## - Use Of Hydro-logical Topography -

- Prioritize upstream sensors that drain toward the target village.
    
- Give more weight to sensors in the same river basin.
    
- Use downstream sensors mainly for confirmation.
    
- Include rainfall sensors upstream of the village.
    
- Account for the travel time of the flood wave.
    
- Treat isolated sensor readings as suspicious until confirmed.

## A "Maybe" better "Five sensor before and after" idea 

If two or more trusted upstream sensors agree,
and forecast water level exceeds the village threshold
within the evacuation time,
then issue an alert.


