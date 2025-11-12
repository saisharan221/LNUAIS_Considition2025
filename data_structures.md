# Considition 2025 Data Structures

This document outlines the expected data structures for the Considition 2025 game.
Please provide examples of these structures from the actual API/documentation.

## Map Object Structure

```python
# Example needed:
map_obj = {
    "ticks": 288,  # Total game ticks
    "evs": [...],  # List of electric vehicles
    "customers": [...],  # List of customers
    "chargingStations": [...],  # Charging stations
    "locations": [...],  # All locations on the map
    # ... other fields
}
```

### Questions:
1. What fields does an EV have? (id, startLocation, batteryCapacity, speed, etc.)
2. What fields does a Customer have? (id, pickupLocation, destination, spawnTick, etc.)
3. What fields do ChargingStations have? (location, type, charging rate, etc.)
4. What fields do Locations have? (id, coordinates, connections/routes, etc.)

## Customer Recommendation Format

```python
# Example needed:
recommendation = {
    "customerId": "customer_123",
    "evId": "ev_456",
    "route": ["location_1", "location_2", "charging_station_1", "location_3"],
    # ... other fields
}
```

### Questions:
1. What is the exact format expected by the API?
2. Are there fields for charging decisions?
3. How are routes specified? (list of location IDs, or something else?)

## Game Response Structure

```python
# Example needed:
game_response = {
    "score": 12345,
    "map": {...},  # Updated map state
    # ... other fields
}
```

### Questions:
1. What information about EV states is returned?
2. How do we know current battery levels?
3. How do we track customer statuses?
4. Are there any error messages or validation feedback?

## Game Rules Needed

1. **Battery & Charging:**
   - Battery capacity per EV?
   - Battery consumption rate (per distance/time)?
   - Charging rates (normal vs green stations)?
   - How long does charging take?

2. **Scoring:**
   - How are points calculated?
   - Customer completion bonus?
   - Penalties for delays/failures?
   - Green energy bonuses?

3. **Routes & Movement:**
   - How is distance calculated?
   - Movement speed?
   - Can EVs change routes mid-journey?

4. **Timing:**
   - 1 tick = 5 minutes
   - 288 ticks per day
   - When do customers spawn?
   - Time windows for pickups/deliveries?

## Next Steps

Once you provide this information, I can:
1. Implement proper data structure parsing
2. Build the routing algorithm with charging logic
3. Implement scoring optimization
4. Test the solution in simulation

