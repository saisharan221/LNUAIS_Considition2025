## **1. Simulation Basics**

- **Discrete time**: 1 tick = 5 minutes, **288 ticks/day**.
    
- You run maps locally via Docker or competitively via the cloud API.
    
- Each tick, the engine:
    
    1. Spawns customers (per map rules).
        
    2. Updates customer state machines (movement, charging).
        
    3. Updates zones’ energy supply, handles brownouts.
        
    4. Computes revenue + scoring.
        

---

## **2. Game Entities**

### **Map Contents**

- **Road network** (nodes, edges)
    
- **Charging stations**:
    
    - Regular
        
    - Green (boost eco scoring)
        
- **EVs** with limited battery
    
- **Customers** with personas
    
- **Zones** (energy aggregation)
    

### **Customers**

Customer lifecycle:

- Home → TransitioningToEdge → Traveling → TransitioningToNode → DestinationReached
    
- OR: WaitingForCharger → Charging → DoneCharging → Travel again
    
- Failure: **FailedToCharge** (if supply shortage)
    

**Important scoring rule:**  
**A customer gives _zero_ completion points unless they charge at least once.**

### **Personas**

Affects behavior + scoring:

- **CostSensitive** – penalizes expensive charging.
    
- **DislikesDriving** – prefers short travel time.
    
- **EcoConscious** – rewards green-energy charging.
    
- **Stressed** – strongly prefers fastest travel.
    
- **Neutral** – baseline.
    

---

## **3. Scoring**

Final score =

### **(1) kWh Revenue**

- Income from energy delivered to customers at stations.
    
- **Brownouts reduce supply → reduce revenue.**
    

### **(2) Customer Completion Score**

- Earned only if the customer:  
    **(a) charges at least once**  
    **(b) reaches destination**
    
- Bonus/penalties depend on persona, time, cost, and charging decisions.
    

API returns:

- Total score
    
- kWhRevenue
    
- CustomerCompletionScore
    
- Per-customer scorecards
    
- Achievements (cloud only)
    

---

## **4. Energy Grid & Weather**

### **Weather**

- Each tick: weather generated via multi-octave noise.
    
- Includes: CloudCover, WindStrength, WeatherType.
    
- Solar only produces during **06:00–18:00**.
    
- Wind varies constantly.
    
- Good weather = more green energy = higher eco scoring.
    

### **Zones**

- Aggregate charging demand within zone.
    
- Request energy from grid.
    
- Receive full or reduced supply (brownout).
    
- Revenue only from supplied energy (not requested).
    

---

## **5. APIs**

### **Local**

- Run via Docker: `considition/considition2025:latest`
    
- `/api/map-config?mapName=X`
    
- `/api/map?mapName=X`
    
- `/api/game`
    

### **Cloud**

- Same endpoints, but requires:
    
    - **x-api-key**
        
    - Only accepts **released** maps.
        
    - Cannot submit `playToTick`.
        

---

## **6. Testing + Pitfalls**

### **Common Issues**

- Brownouts → massive revenue loss.
    
- Customers who **never charge** → **0 completion score**.
    
- Customers can **run out of battery** if misrouted.
    
- If cloud returns **422**, check validation errors.
    
- If map not released → cloud rejects → must use local Docker.
    

### **Testing Strategy**

- Use `/api/map-config` to understand map parameters.
    
- Locally modify MapConfig (volatility, weather) for stress testing.
    
- Disable cache if state behaves oddly.
    

---

## **7. Competition Format**

### **Final Night**

- New secret final map revealed on Nov 13.
    
- Warmup at 17:45; finale at 19:15.
    
- **45 minutes** to run algorithm against API.
    
- Map locks at end; highest score wins.
    
- Public Twitch broadcast & visualizer available.