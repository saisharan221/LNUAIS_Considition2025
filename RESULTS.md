# Considition 2025 - Algorithm Results

## 📊 Current Standings (Local Docker)

| Map | Our Score | Leader | % of Leader | Customer | KWH |
|-----|-----------|--------|-------------|----------|-----|
| **Turbohill** | 2,482 | 8,979 | **28%** | 874 | 1,608 |
| **Clutchfield** | 13,423 | 40,571 | **33%** | 6,030 | 7,393 |
| **Batterytown** | 14,936 | 43,129 | **35%** | 7,712 | 5,240 |

## 🚀 Improvement Timeline

### Initial (Conservative Strategy)
- Turbohill: 1,624 points
- Only charged ~10 customers who "needed" it
- Very conservative thresholds

### After Aggressive Optimization
- **Turbohill: 2,482** (+44% improvement!)
- **Clutchfield: 13,423** (+30% improvement!)  
- **Batterytown: 14,936** (+15% improvement!)

## 🔑 Key Optimizations Applied

1. **Aggressive Charging Threshold**
   - Before: Charge if < 120% of needed energy
   - After: Charge if < 200% of needed energy
   - Result: ~70% customer coverage (vs ~5% before)

2. **Maximum Charge Targets**
   - Before: Charge to 90% minimum
   - After: Charge to 95-99%
   - Result: More KWH revenue per customer

3. **Reachability-First Station Selection**
   - Before: Selected best persona match, checked reachability later
   - After: Filter unreachable stations FIRST, then optimize
   - Result: +15-30% score improvement

4. **Lower Detour Penalties**
   - Before: Heavy penalties (2x for Stressed, 1x for Neutral)
   - After: Light penalties (0.5x for Stressed, 0.3x for Neutral)
   - Result: More stations considered viable

5. **Charge Everyone**
   - Before: Only charge if `needs_charging()` returns true
   - After: Attempt to charge ALL departing customers
   - Result: Maximum KWH revenue

## 📈 What Separates Us from Top 3?

### Current Gap
- Top teams: 38,000-43,000 KWH revenue
- Our KWH: 5,000-7,000
- **Gap: ~5-6x lower KWH revenue!**

### Top Team Strategies (Hypothesis)
1. **Multi-stop charging**: Charge at 2-3 stations per route
2. **Zero customer completion focus**: Sacrifice completion for KWH
3. **Pricing optimization**: Charge when/where energy is most expensive
4. **Better coverage**: Charge 100% of customers (we're at 70%)

## 🎯 Next Steps

### To Implement
1. **Multi-Stop Charging (Priority 1)**
   ```python
   chargingRecommendations: [
       {nodeId: "5.3", chargeTo: 0.9},
       {nodeId: "6.2", chargeTo: 0.95},
       {nodeId: "7.1", chargeTo: 0.99}
   ]
   ```

2. **Get remaining 30% coverage**
   - 61 customers can't reach ANY station
   - Need earlier/multiple charging opportunities

3. **Test on Cloud API**
   ```bash
   export API_KEY="your-key"
   export USE_CLOUD_API="true"
   python app.py
   ```

## 💡 Insights from Leaderboard

### Turbohill (Balanced Map)
- Leaders: ~3k customer + ~6k KWH
- Strategy: Balance both metrics
- Our approach: Good fit (28% of leader)

### Clutchfield & Batterytown (KWH-Heavy Maps)
- Leaders: 0-16k customer + 38-43k KWH
- Strategy: KWH revenue dominates (5-6x more valuable!)
- Our approach: Good customer completion, but LOW KWH

### Pattern Analysis
- **Small maps (Turbohill)**: Customer completion matters (~35% of score)
- **Large maps (Clutch/Battery)**: KWH revenue dominates (~90% of score)
- **Winning formula**: Maximize charging volume!

## 🏆 Competition Strategy

### Before Submission
1. ✅ Test all three maps locally
2. ✅ Verify score consistency across runs
3. ⏳ Implement multi-stop charging (big KWH boost!)
4. ⏳ Test on cloud API
5. ⏳ Submit and monitor leaderboard

### During Competition
- Monitor leaderboard for pattern changes
- A/B test: aggressive vs. balanced strategies per map
- Iterate on charging thresholds (currently 200%, try 300%?)
- Consider map-specific strategies

## 📝 Notes

- Algorithm is **stable** (no crashes, consistent scores)
- **70% customer coverage** is good, but leaves room for improvement
- **Reachability checks** were crucial (+15-30% improvement)
- Top teams likely using **advanced strategies** we haven't implemented yet
- **Cloud API** may behave differently than local Docker

---

**Last Updated:** 2025-11-12  
**Status:** ✅ Ready for cloud testing and competition!

