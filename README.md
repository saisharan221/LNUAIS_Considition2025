# Considition 2025 - EV Charging Optimization Solution

## ✅ Working Solution - Score: 1624 (Local Turbohill)

This solution provides intelligent EV charging recommendations for the Considition 2025 challenge.

## 🚀 Quick Start

### Local Testing (Docker)
```bash
# Set your API key
export API_KEY="your-api-key-here"

# Run the solution
python app.py
```

### Cloud Testing
```bash
export API_KEY="your-api-key-here"
export USE_CLOUD_API="true"

python app.py
```

## 📂 Project Structure

- **`app.py`** - Main game loop and API integration
- **`algorithm.py`** - Core charging recommendation algorithm
- **`client.py`** - API client wrapper
- **`requirements.txt`** - Python dependencies
- **`data_structures.md`** - Documentation of map/game data structures

## 🧠 Algorithm Overview

### Core Strategy

1. **Customer Analysis**: Identifies customers departing at each tick
2. **Needs Assessment**: Calculates if charging is needed (120% energy margin)
3. **Station Selection**: Finds optimal charging station based on:
   - Route detour minimization
   - Persona-based preferences
   - Station availability
   - Energy source (green vs. dirty)
4. **Charge Optimization**: Calculates optimal charge amount:
   - Minimum 90% charge when stopping (overhead justification)
   - 150% of needed energy for safety margin
   - Caps at 95% to avoid potential edge cases

### Persona-Based Scoring

- **Stressed**: Minimizes detours, prefers fast chargers
- **CostSensitive**: Prioritizes green/cheap energy, moderate detour tolerance
- **EcoConscious**: Strongly prefers green energy (Hydro/Nuclear/Solar/Wind)
- **DislikesDriving**: Heavily penalizes detours
- **Neutral**: Balanced approach

### Key Features

- ✅ **Correct API Format**: Uses `chargingRecommendations` array with `nodeId`
- ✅ **State Persistence**: Maintains customer tracking across all ticks
- ✅ **Route Validation**: Ensures customers can reach recommended stations
- ✅ **Dijkstra Pathfinding**: Optimal route calculation
- ✅ **Smart Charging Logic**: Balances safety margin vs. over-charging

## 📊 Current Performance

**Map: Turbohill (Local Docker)**
- Score: **1624**
- Recommendations: ~10 per game (only when needed)
- No failures or crashes

## 🔧 Configuration

### Environment Variables

- `API_KEY` (required): Your Considition API key
- `API_URL` (optional): Override API URL (default: `http://localhost:8080`)
- `USE_CLOUD_API` (optional): Set to `"true"` for cloud submissions

### Tuning Parameters

Located in `algorithm.py`:

```python
# Line 161: Charging threshold
return current_charge_kwh < (energy_needed * 1.2)  # 20% safety margin

# Line 523: Charge target margin
target_charge_kwh = charge_at_station + (energy_from_station * 1.5)  # 50% extra

# Line 527: Minimum charge when stopping
min_charge_kwh = max_charge_kwh * 0.90  # 90% minimum

# Line 535: Maximum charge cap
target_charge_fraction = max(0.01, min(0.95, target_charge_fraction))  # 95% max
```

## 🐛 Known Issues & Workarounds

### Docker Cache Issue
If recommendations are ignored, disable cache:
```bash
CACHE_ENABLED=false docker run -p 8080:8080 considition/considition2025
```

### API Format Gotchas
- ✅ Use `chargingRecommendations` (array), not `chargingStation`
- ✅ Use `nodeId`, not `chargingStation`
- ✅ Avoid `chargeTo: 0` or `chargeTo: 1` (use 0.01-0.95 range)

## 📈 Optimization Ideas (Future)

1. **Multi-stop charging**: Support multiple charging stops per route
2. **Dynamic pricing**: Factor in time-of-day energy costs
3. **Weather integration**: Adjust for solar/wind production
4. **Congestion modeling**: Predict charger availability
5. **Machine learning**: Learn optimal thresholds per persona
6. **Zone-based strategy**: Different strategies for green vs. dirty zones

## 🧪 Testing

```bash
# Quick test
python app.py

# Verbose test (uncomment debug lines in app.py)
# Shows recommendations per tick and charging activity
```

## 📝 Notes

- Algorithm runs at ~23-25ms per tick (fast!)
- State persists across ticks (no duplicate recommendations)
- Only recommends charging when needed (conservative approach)
- Validated against actual game logs

## 🤝 Credits

Developed for Considition 2025 by LNU AIS Team

