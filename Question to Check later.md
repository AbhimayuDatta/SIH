#ASSAM_FLOOD_ISSUEE  [[ASSAM FLOOD ALERT SYSTEM]]
1. Isn't Cumulative rainfall same as last hour rainfall and several hours of rainfall and Antecedent rainfall from pervious days?
2. What tech or sensors or device china use to measure all this parameters from the Rainfall-threshold warning?
3.Give me detailed Comaparision between China's Local Warning and meteorological warning to that of India's.
3. Give a Comparision Between Japan's River-specific flood Forecast and India's River-specific flood forecast 
4. Does there any Kind of real-time risk maps in india if yes then which ones and if no explain the Japan's one in more details.


## Answer -

Yes—these terms overlap, but they are **different time windows and concepts**. India already has many of the same components as China and Japan, although the systems are divided between IMD, CWC, state authorities, and local administrations rather than being presented as one unified national flood-risk platform.

## 1. Cumulative, hourly, and antecedent rainfall

### The distinction

| Term | Meaning | Example |
|---|---|---|
| Last-hour rainfall | Rainfall accumulated during the most recent one-hour window | Rain from 5:00–6:00 PM |
| Several-hours rainfall | Rainfall accumulated over a short window such as 3, 6, or 12 hours | Rain from noon–6:00 PM |
| Cumulative rainfall | A general term meaning rainfall added over a selected period | 6-hour, 24-hour, or 72-hour total |
| Antecedent rainfall | Rainfall that occurred before the current event and affected the condition of the catchment | Rain during the previous 1–7 days |

So, **last-hour rainfall and several-hours rainfall are types of cumulative rainfall**. “Cumulative rainfall” does not specify the time window unless you write it explicitly.

Antecedent rainfall is also cumulative rainfall mathematically, but it is used differently in hydrology. It describes the catchment’s previous wetness and storage condition.

### Example

Suppose a sensor records:

- Previous 5 days: 180 mm.
- Last 24 hours: 100 mm.
- Last 6 hours: 70 mm.
- Last hour: 35 mm.

Then:

- 180 mm is antecedent rainfall.
- 100 mm is 24-hour cumulative rainfall.
- 70 mm is 6-hour cumulative rainfall.
- 35 mm is 1-hour cumulative rainfall and rainfall intensity over that one-hour period.

The same rain gauge can calculate all of these using rolling windows:

```text
R1h  = rain during the last 1 hour
R3h  = rain during the last 3 hours
R6h  = rain during the last 6 hours
R24h = rain during the last 24 hours
R72h = rain during the last 72 hours
```

A simple antecedent-rainfall indicator is the **antecedent precipitation index**:

\[
API_t = P_t + kAPI_{t-1}
\]

where:

- \(P_t\) is the current rainfall.
- \(k\) is a decay factor between 0 and 1.
- \(API\) becomes smaller over time if no new rain occurs.

This is more realistic than treating all rain from five days ago as equally important. Rain from yesterday usually matters more than rain from five days ago.

### Why all windows are useful

Two storms can have the same 24-hour total but produce different flood risks:

- A short, intense cloudburst creates rapid runoff and flash flooding.
- Moderate rain spread over 24 hours may soak the soil but produce a slower river rise.
- Several wet days followed by intense rainfall can produce flooding because the soil and small channels have little remaining storage.

India’s Flash Flood Guidance system follows this general principle. It estimates the rainfall required over a small watershed to produce minor flooding at its outlet, considering rainfall duration and catchment storage. [mausam.imd.gov](https://mausam.imd.gov.in/imd_latest/contents/pdf/hydrology_sop.pdf)

## 2. China’s rainfall-threshold technology

China does not use one special “cumulative rainfall sensor.” Instead, it uses ordinary physical sensors and calculates the different rainfall parameters in software.

### Main observation technologies

| Parameter | Typical technology | What it measures |
|---|---|---|
| Rainfall amount | Tipping-bucket rain gauge | Rainfall volume over time |
| Rainfall intensity | Tipping-bucket or weighing gauge | Rate of rainfall, such as mm/hour |
| River level | Radar, ultrasonic, pressure, or float water-level sensor | Water-surface elevation |
| River discharge | Velocity sensor plus river cross-section model | Flow volume per second |
| Soil wetness | Soil-moisture probe or model estimate | Water stored in the soil |
| Weather structure | Weather radar | Spatial distribution and intensity of rain |
| Large-scale rainfall | Meteorological satellite | Cloud and rainfall information over broad regions |
| Forecast rainfall | Numerical weather model | Expected rainfall in future hours or days |
| Local visual confirmation | CCTV or river camera | Debris, overtopping, blocked channels, and sensor verification |

China’s Ministry of Water Resources describes an integrated system using satellites and radar for atmospheric rainfall, ground rain gauges for precipitation, and hydrological stations for river levels and flow. [english.www.gov](https://english.www.gov.cn/news/202607/19/content_WS6a5c2a6ec6d00ca5f9a0c4d9.html)

### Automatic rain gauges

A common instrument is an **automatic tipping-bucket rain gauge**:

1. Rain enters a calibrated funnel.
2. The water fills a small bucket.
3. When the bucket reaches a fixed volume, it tips.
4. Each tip becomes a measured amount of rainfall.
5. The data logger calculates rainfall per minute, hour, day, or rolling window.
6. The station transmits data using cellular, radio, satellite, or another telemetry link.

The sensor does not directly know “antecedent rainfall.” The station or server stores the time series and computes:

```text
R1h, R3h, R6h, R24h, R72h, API
```

### Hydrological stations

China combines rain gauges with hydrological stations that can measure:

- Water level.
- Flow velocity.
- Discharge.
- Reservoir inflow.
- Reservoir storage.
- Temperature and sometimes sediment conditions.

A water-level sensor alone cannot always determine flood danger. The same water level may be safe at one cross-section and dangerous at another. Therefore, the station must be calibrated against:

- River cross-section.
- Nearby settlement elevation.
- Historical flood marks.
- Warning level.
- Danger level.
- Expected inundation area.

China’s modernisation programme specifically emphasizes improving hydrological sensing devices and mathematical models that analyse the collected data. [english.www.gov](https://english.www.gov.cn/news/202406/05/content_WS665f9d41c6d0868f4e8e7d27.html)

### China’s data-processing chain

A typical process is:

```text
Rain gauge + radar + satellite
             ↓
Rainfall quality control
             ↓
Rolling rainfall calculations
(R1h, R3h, R6h, R24h, R72h, API)
             ↓
Runoff and river-level model
             ↓
Compare with local threshold
             ↓
Warning level
             ↓
Government and community alert
```

For your project, the important point is that a low-cost sensor mesh can measure rainfall and water level, but it will still require software to calculate the rolling totals and a local model to decide whether those values are dangerous.

## 3. China compared with India

The following comparison is about **local flash-flood warning** and **meteorological warning**. The two categories overlap, but they have different purposes.

### Local warning

| Feature | China | India |
|---|---|---|
| Main purpose | Warn a specific village, township, small catchment, or river section | Warn districts, watersheds, river locations, local administration, and communities |
| Main trigger | Local rain gauge, water-level gauge, rainfall threshold, runoff estimate, or field observation | IMD rainfall information, Flash Flood Guidance, CWC river observations, local gauges, and state systems |
| Spatial scale | Often designed around small catchments and local settlements | IMD products commonly operate at national, regional, subdivision, district, and watershed scales; local implementation varies by state |
| Threshold design | Can use village-specific rainfall, runoff, water-level, and inundation thresholds | Uses station-specific warning/danger levels for CWC sites and watershed-based flash-flood guidance; local thresholds are not uniform everywhere |
| Decision authority | County, township, village, water-resources, and emergency authorities | CWC, IMD, State Disaster Management Authorities, district administration, irrigation departments, and local bodies |
| Last-mile communication | Sirens, village loudspeakers, door-to-door notification, mobile messages, local officials, and public displays | CAP/Sachet alerts, mobile apps, SMS or messaging, sirens, local administration, state systems, media, and community volunteers |
| Failure handling | Designed in many areas for local operation when central communications are unavailable | Often depends on coordination among multiple agencies; reliability can vary by state, terrain, connectivity, and local preparedness |
| Modelling emphasis | Increasing use of distributed hydrological models and compound rainfall-water-level indexes | IMD’s Flash Flood Guidance estimates rainfall needed to produce flooding at a watershed outlet; CWC uses hydrological and rainfall-based river forecasting |
| Typical public output | A local warning tied to a village or small basin | Weather warning, flash-flood threat/risk bulletin, river forecast, or district/local emergency alert |

India’s Flash Flood Guidance System has been operational since October 2020 and provides watershed-scale flash-flood threat and risk information, including forecasts with lead times of approximately 6–24 hours. [pib.gov](https://www.pib.gov.in/PressReleasePage.aspx?PRID=1941110)

India also has a large conventional flood-forecasting network. CWC reports monitoring flood conditions at forecasting stations and issuing forecasts to local administrations, state governments, NDMA, NDRF, and other agencies. [cwc.gov](https://www.cwc.gov.in/flood-forecasting-hydrological-observation)

### Meteorological warning

| Feature | China | India |
|---|---|---|
| Responsible meteorological body | China Meteorological Administration and associated government agencies | India Meteorological Department |
| Main output | Four-colour weather/flood warning: blue, yellow, orange, red | IMD colour-coded warnings: green, yellow, orange, red, plus rainfall forecasts, nowcasts, impact-based warnings, and flash-flood products |
| Main input | Weather radar, satellites, rain gauges, numerical weather prediction, and hydrological observations | Satellites, radar, automatic weather stations, rain gauges, numerical weather models, and hydrological data |
| Forecast scale | National, provincial, city, county, and local warning systems | National, regional, subdivision, district, station, city, and watershed products |
| What it predicts | Heavy rain, typhoons, floods, mountain torrents, and related hazards | Heavy rainfall, thunderstorms, cyclones, flash floods, landslides, and other weather hazards |
| Public meaning | Increasing colour severity, generally connected to increasingly strong emergency action | Colour plus hazard description and recommended action; impact-based warning is increasingly important |
| Hydrological confirmation | Often integrated with Ministry of Water Resources river and rainfall monitoring | Mainly coordinated between IMD’s meteorological products and CWC’s hydrological forecasts |
| Strength | Strong administrative and local flood-control structure, including small-catchment warnings | Strong national meteorological network and an operational South Asian Flash Flood Guidance System |
| Main challenge | Different warning and emergency-response levels can be confusing if treated as one scale | Information is distributed across IMD, CWC, state agencies, and districts, so users may not see one unified risk picture |

A major difference is that China’s **local warning** is often implemented directly through administrative units close to the affected settlement. In India, the technical warning may be produced centrally by IMD or CWC, but the final evacuation decision and last-mile delivery usually depend heavily on state and district authorities.

For Assam, your system should not try to replace IMD or CWC. It should work as a **local augmentation layer**:

```text
IMD rainfall and flash-flood products
        +
CWC river-level and forecast data
        +
Local sensor mesh
        +
ASDMA/district evacuation information
        ↓
Village-level risk and evacuation alert
```

## 4. Japan compared with India: river-specific forecasting

### What Japan does

Japan’s river-specific forecasting is designed around individual rivers and river sections. JMA cooperates with MLIT or prefectural authorities for rivers where flooding could cause major damage. Forecasting uses:

- Upstream rainfall.
- Radar rainfall.
- River water-level gauges.
- Flow and discharge observations.
- Rainfall forecasts.
- River routing.
- River cross-sections.
- Levees and flood-control infrastructure.
- Estimated downstream arrival time.
- Inundation assumptions for vulnerable areas.

JMA’s river forecasts are not merely statements such as “the river is high.” They estimate whether the river will approach predefined levels and whether a flood-related threshold is likely to be reached. [jma.go](https://www.jma.go.jp/jma/en/Activities/forecast.html)

Japan also distinguishes information such as:

- Flood caution level.
- Flood warning level.
- Evacuation decision level.
- Flood danger level.
- Emergency or inundation-related conditions.

These levels can be linked to specific actions, including evacuation of people who need additional time and evacuation of all residents in dangerous areas. [uncrd.un](https://uncrd.un.org/sites/default/files/2023sctw_s5_p1.pdf)

### What India does

India’s CWC river forecasting generally uses:

- River water-level stations.
- Discharge stations.
- Rainfall observations.
- Inflow forecasts from reservoirs.
- Upstream river conditions.
- Basin and catchment models.
- Warning level.
- Danger level.
- Historical river behaviour.
- Reservoir operations and releases.

CWC publishes station-specific warning and danger levels. For example, its basin information lists a forecast station’s river, warning level, danger level, and, where applicable, reservoir inflow information. [cwc.gov](https://www.cwc.gov.in/kgbo/ff_site)

CWC has also provided near-real-time and advisory flood forecasts through its flood portals and FloodWatch India. The current public system includes interactive forecast information and longer advisory forecasts for major river basins. [pib.gov](https://www.pib.gov.in/PressReleasePage.aspx?PRID=1849954)

### Detailed comparison

| Feature | Japan | India |
|---|---|---|
| Forecast unit | Individual designated river or river section | Individual forecast station, river, reservoir, basin, and selected low-lying area |
| Main agencies | JMA, MLIT, prefectural authorities, municipalities | CWC, IMD, state water departments, irrigation departments, SDMAs, district authorities |
| Warning thresholds | Flood caution, warning, evacuation decision, danger, and related levels | Warning level, danger level, highest flood level, and forecast flood condition |
| Forecast communication | River forecast, flood risk map, municipal evacuation levels, mobile/web/media channels | CWC flood portal, FloodWatch India, IMD products, CAP/Sachet, state and district channels |
| Forecast horizon | Depends on river and product; combines current observations with rainfall forecasts | Short-range station forecasts and increasingly longer advisory basin forecasts |
| Forecast-to-evacuation connection | Strongly integrated with Japan’s five-level resident action framework | Technical forecast and evacuation orders are often separate steps handled by state/district authorities |
| Spatial information | River sections and inundation-risk areas are commonly visualized on maps | Station and basin forecasts are available; map-based presentation is improving but coverage and integration vary |
| Small rivers | Smaller unforecast rivers may be handled through water-level information and real-time risk maps | Flash-flood guidance and local/state systems cover some areas, but small-river coverage is uneven |
| Infrastructure data | Flood-control infrastructure, river channels, levees, and inundation assumptions are incorporated into designated-river services | Reservoir and river observations are important, but detailed local modelling and last-mile coverage vary significantly |
| Public usability | Strong emphasis on “what should residents do now?” | Strong technical information, with practical action depending on local authorities and alert channels |

The key difference is not necessarily that Japan has sensors and India does not. India has extensive rainfall, hydrological, and meteorological observation systems. The difference is often **integration**: Japan more consistently connects a river forecast, a geographic risk map, a common alert level, and a resident action.

## 5. Does India have real-time risk maps?

### Short answer

Yes, India has real-time or near-real-time map-based flood information, but it is not yet as uniform or as integrated nationally as Japan’s Real-time Risk Map.

Important Indian examples include:

1. **FloodWatch India** by CWC.
2. **CWC flood forecasting and advisory portals**.
3. **IMD Flash Flood Guidance products**.
4. **IMD rainfall radar and nowcast maps**.
5. **India-WRIS and basin-related geospatial systems**.
6. State-level flood monitoring and inundation portals.
7. Satellite-based flood-inundation products from agencies such as NRSC/ISRO during major events.

FloodWatch India is an official CWC application intended to present real-time flood situations and forecasts; its public description includes an interactive map and forecast information for states and river locations. [play.google](https://play.google.com/store/apps/details?id=in.gov.affcwc&hl=en_IN)

However, you should distinguish three kinds of maps:

| Map type | What it shows | Is it a full risk map? |
|---|---|---|
| Observation map | Current rainfall, water level, or flood condition at stations | No; it shows measurements |
| Forecast map | Expected rainfall, river level, or flash-flood threat | Partly; it shows predicted hazard |
| Impact/risk map | Expected inundation, depth, exposure, and danger to people or infrastructure | Yes; this is the most complete form |

India has all three types in different systems and locations, but availability is not uniform for every river or village.

### How Japan’s Real-time Risk Map works

Japan’s Real-time Risk Map is a **grid-based hazard map**. Instead of showing only the location of a gauge, it divides an area into many grid cells and estimates how close the hazard is to a predefined warning criterion at each grid point. [jma.go](https://www.jma.go.jp/bosai/en_risk/)

For heavy-rain and flood-related risk, Japan’s modelling can consider:

- Rain falling onto the land.
- Water retained in the soil.
- Surface water accumulating on the ground.
- Runoff entering and travelling through rivers.
- Current rainfall.
- Forecast rainfall.
- Terrain and drainage.
- Historical disaster thresholds.

Japan describes three important calculated indices:

1. **Soil water index**: how much rain has infiltrated and accumulated in the soil.
2. **Surface water index**: how much water remains or accumulates on the ground.
3. **Runoff water index**: how much water is gathering in headwaters and travelling through rivers.

These indices are compared with thresholds derived from historical disaster data at each grid point. [gov-online.go](https://www.gov-online.go.jp/pdf/hlj/20180301/10-11.pdf)

The result is a colour-coded grid:

- Yellow: conditions approaching a warning threshold.
- Red: danger is increasing.
- Purple: very dangerous conditions, approximately corresponding to the need for evacuation from dangerous places.
- Black: an emergency condition may already exist or be imminent.

The map can therefore show that one side of a district is at high risk while another side is not, even if both locations receive the same weather warning. It is a **spatial risk estimate**, not simply a picture of current sensor values.

### Why this matters for Assam

Suppose two villages are located near the same river:

- Village A is on high ground with a nearby embankment.
- Village B is lower, closer to a channel, and has only one road to a shelter.

A district-wide “red rainfall warning” treats them similarly. A risk map can assign different danger levels because it includes:

- Local elevation.
- Drainage paths.
- Distance from the river.
- Forecast water depth.
- Road accessibility.
- Population and vulnerable groups.
- Expected arrival time of floodwater.

For your project, the practical version could begin with a much simpler local risk grid:

```text
For every village or 250 m grid cell:

risk =
    current water level factor
  + predicted water level factor
  + rainfall accumulation factor
  + upstream rainfall factor
  + elevation/inundation factor
  + evacuation-route factor
```

Do not initially attempt to create a national-scale hydrological model. Start with one catchment, such as a selected flood-prone area in Barpeta, Goalpara, Nalbari, or Cachar, and build:

1. A digital elevation and drainage map.
2. A few local rainfall and water-level stations.
3. Historical flood observations.
4. Local warning and danger thresholds.
5. A forecast for the next 1–6 hours.
6. A map showing village-level risk.
7. An alert connected to evacuation time.

## Recommended architecture for your project

A good India-focused design would combine the approaches like this:

```text
Local rain gauges
Local water-level sensors
Upstream sensor nodes
IMD rainfall/forecast data
CWC river observations and forecasts
Digital elevation model
Evacuation-route and shelter database
                 ↓
Quality control and sensor-failure detection
                 ↓
Rolling rainfall:
R1h, R3h, R6h, R24h, R72h, API
                 ↓
Local runoff and river-level prediction
                 ↓
Predicted threshold crossing time
                 ↓
Green / Yellow / Orange / Red action level
                 ↓
Siren + SMS + app + local authority dashboard
```

The most important output should not be merely:

```text
Water level: 2.8 metres
```

It should be:

```text
Orange alert:
Water is predicted to reach the local danger level in 2 hours.
Evacuate elderly residents and people needing assistance.
All residents should prepare to move to Shelter A.
```

That is the central lesson from Japan’s action-based system, while the rainfall-threshold and local-catchment approach is closer to China’s flash-flood warning practice.