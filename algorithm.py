"""
Considition 2025 Algorithm - Balanced Optimization
---------------------------------------------------
Electric Vehicle Charging Recommendation System
Optimized for balanced customer completion (60%) and kWh revenue (40%)
"""

import heapq
import math


class ConsiditionAlgorithm:
    def __init__(self, map_obj):
        """
        Initialize the algorithm with map data.
        
        Args:
            map_obj: The map object containing all game state information
        """
        self.map_obj = map_obj
        self.graph = {}
        self.nodes = {}
        self.node_positions = {}  # Cache node positions for A* heuristic
        self.charging_stations = {}
        self.zones = {}
        self.customers = []
        
        # Balanced optimization weights
        self.completion_weight = 0.6
        self.revenue_weight = 0.4
        
        self.initialize_game_state()
    
    def initialize_game_state(self):
        """Extract and initialize game state from map object."""
        # Build graph from nodes and edges
        nodes_list = self.map_obj.get("nodes", [])
        edges_list = self.map_obj.get("edges", [])
        zones_list = self.map_obj.get("zones", [])
        
        # Index nodes and cache positions
        for node in nodes_list:
            node_id = node.get("id")
            self.nodes[node_id] = node
            self.graph[node_id] = []
            
            # Cache node positions for A* heuristic
            pos_x = node.get("posX", 0)
            pos_y = node.get("posY", 0)
            self.node_positions[node_id] = (pos_x, pos_y)
            
            # Track charging stations
            target = node.get("target", {})
            if target.get("Type") == "ChargingStation":
                self.charging_stations[node_id] = target
            
            # Collect all customers
            customers_at_node = node.get("customers", [])
            for customer in customers_at_node:
                customer["homeNode"] = node_id
                self.customers.append(customer)
        
        # Build adjacency list for graph (unidirectional - edges go from -> to)
        for edge in edges_list:
            from_node = edge.get("fromNode")
            to_node = edge.get("toNode")
            length = edge.get("length")
            
            if from_node in self.graph:
                self.graph[from_node].append({
                    "to": to_node,
                    "distance": length
                })
        
        # Index zones
        for zone in zones_list:
            zone_id = zone.get("id")
            self.zones[zone_id] = zone
        
        # Track customer states
        self.customer_states = {}
        for customer in self.customers:
            customer_id = customer.get("id")
            if customer_id:
                # Ensure customer_id is string for consistent key type
                customer_id = str(customer_id)
                self.customer_states[customer_id] = {
                    "recommended": False,
                    "state": customer.get("state", "Home"),
                    "charging_stops": []  # Track planned charging stops
                }
    
    def euclidean_distance(self, node1_id: str, node2_id: str) -> float:
        """
        Calculate Euclidean distance between two nodes.
        Used as heuristic for A* pathfinding.
        
        Args:
            node1_id: First node ID
            node2_id: Second node ID
            
        Returns:
            Euclidean distance or float('inf') if positions not available
        """
        pos1 = self.node_positions.get(node1_id)
        pos2 = self.node_positions.get(node2_id)
        
        if pos1 is None or pos2 is None:
            return float('inf')
        
        x1, y1 = pos1
        x2, y2 = pos2
        
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    
    def get_shortest_path_distance(self, start_node: str, end_node: str) -> float:
        """
        Calculate shortest path distance using A* algorithm with Euclidean heuristic.
        
        Args:
            start_node: Starting node ID
            end_node: Ending node ID
            
        Returns:
            Shortest distance or None if no path exists
        """
        if start_node == end_node:
            return 0.0
        
        if start_node not in self.graph or end_node not in self.graph:
            return None
        
        # A* algorithm
        # f(n) = g(n) + h(n) where:
        # g(n) = actual distance from start to node n
        # h(n) = Euclidean distance from node n to goal (heuristic)
        
        g_scores = {node: float('inf') for node in self.graph}
        g_scores[start_node] = 0.0
        
        # Priority queue: (f_score, g_score, node)
        f_start = self.euclidean_distance(start_node, end_node)
        pq = [(f_start, 0.0, start_node)]
        visited = set()
        
        while pq:
            f_score, g_score, current_node = heapq.heappop(pq)
            
            if current_node in visited:
                continue
            
            visited.add(current_node)
            
            if current_node == end_node:
                return g_score
            
            for neighbor in self.graph.get(current_node, []):
                neighbor_node = neighbor["to"]
                edge_dist = neighbor["distance"]
                new_g_score = g_score + edge_dist
                
                if new_g_score < g_scores[neighbor_node]:
                    g_scores[neighbor_node] = new_g_score
                    h_score = self.euclidean_distance(neighbor_node, end_node)
                    f_score = new_g_score + h_score
                    heapq.heappush(pq, (f_score, new_g_score, neighbor_node))
        
        # No path found
        return None if g_scores[end_node] == float('inf') else g_scores[end_node]
    
    def zone_has_green_energy(self, zone) -> bool:
        """Check if a zone has green energy sources."""
        green_sources = {"Hydro", "Nuclear", "Wind", "Solar"}
        energy_sources = zone.get("energySources", [])
        
        for source in energy_sources:
            if source.get("type") in green_sources:
                return True
        
        return False
    
    def is_green_energy_station(self, station_id: str) -> bool:
        """Check if a charging station is in a green energy zone."""
        station_node = self.nodes.get(station_id, {})
        zone_id = station_node.get("zoneId")
        zone = self.zones.get(zone_id, {})
        return self.zone_has_green_energy(zone)
    
    def is_daylight_hours(self, tick: int) -> bool:
        """
        Check if tick is during daylight hours (06:00-18:00).
        Tick 0 = 00:00, so 06:00 = tick 72, 18:00 = tick 216.
        """
        hour_tick = tick % 288  # Wrap around for 24-hour cycle
        return 72 <= hour_tick <= 216
    
    def calculate_completion_score(
        self, 
        station_id: str, 
        station_info: dict,
        detour: float,
        charge_speed: float,
        persona: str
    ) -> float:
        """
        Calculate completion score for a station.
        Higher score = better for completion.
        
        Args:
            station_id: Station node ID
            station_info: Station information
            detour: Detour distance in km
            charge_speed: Charging speed per charger
            persona: Customer persona
            
        Returns:
            Completion score (higher is better)
        """
        # Base completion score (inverse of detour)
        # Shorter detour = better completion
        detour_score = max(0, 1000.0 - (detour * 10.0))
        
        # Charging speed (faster = better completion)
        speed_score = charge_speed * 0.5
        
        # Station availability (more chargers = better completion)
        available = station_info.get("amountOfAvailableChargers", 1)
        total = station_info.get("totalAmountOfChargers", 1)
        availability_ratio = available / max(total, 1)
        availability_score = availability_ratio * 200.0
        
        # Persona adjustments for completion
        persona_multiplier = 1.0
        if persona in ["Stressed", "DislikesDriving"]:
            # Heavily penalize detours for completion
            detour_penalty = detour * 50.0
            detour_score -= detour_penalty
            persona_multiplier = 1.2  # Prefer fast charging
        elif persona == "EcoConscious":
            persona_multiplier = 0.9  # Green energy matters but completion is key
        elif persona == "CostSensitive":
            persona_multiplier = 1.0
        
        completion_score = (detour_score + speed_score + availability_score) * persona_multiplier
        
        return completion_score
    
    def calculate_revenue_score(
        self,
        station_id: str,
        station_info: dict,
        charge_amount_kwh: float,
        tick: int,
        persona: str
    ) -> float:
        """
        Calculate revenue score for a station.
        Higher score = better for revenue.
        
        Args:
            station_id: Station node ID
            station_info: Station information
            charge_amount_kwh: Amount of charge in kWh
            tick: Current tick
            persona: Customer persona
            
        Returns:
            Revenue score (higher is better)
        """
        # Base revenue (more charge = more revenue)
        base_revenue = charge_amount_kwh * 1.0
        
        # Green energy bonus
        green_bonus = 0.0
        if self.is_green_energy_station(station_id):
            green_bonus = 150.0 * (charge_amount_kwh / 50.0)
            
            # Extra bonus during daylight (solar available)
            if self.is_daylight_hours(tick):
                green_bonus *= 1.3
        
        # Charging speed bonus (faster = potentially more revenue)
        charge_speed = station_info.get("chargeSpeedPerCharger", 100)
        speed_bonus = charge_speed * 0.3 * (charge_amount_kwh / 50.0)
        
        # Station capacity (less congestion = more revenue)
        available = station_info.get("amountOfAvailableChargers", 1)
        total = station_info.get("totalAmountOfChargers", 1)
        capacity_ratio = available / max(total, 1)
        capacity_bonus = capacity_ratio * 100.0
        
        # Persona adjustments for revenue
        persona_multiplier = 1.0
        if persona == "EcoConscious":
            # Strongly prefer green energy for revenue
            if self.is_green_energy_station(station_id):
                persona_multiplier = 1.5
            else:
                persona_multiplier = 0.5  # Penalize non-green
        elif persona == "CostSensitive":
            # Green energy is cheaper, prefer for revenue
            if self.is_green_energy_station(station_id):
                persona_multiplier = 1.2
        elif persona in ["Stressed", "DislikesDriving"]:
            # Revenue is less important
            persona_multiplier = 0.7
        
        revenue_score = (base_revenue + green_bonus + speed_bonus + capacity_bonus) * persona_multiplier
        
        return revenue_score
    
    def calculate_balanced_station_score(
        self,
        station_id: str,
        station_info: dict,
        detour: float,
        charge_amount_kwh: float,
        tick: int,
        persona: str
    ) -> float:
        """
        Calculate balanced score for a station (60% completion, 40% revenue).
        Higher score = better station.
        
        Args:
            station_id: Station node ID
            station_info: Station information
            detour: Detour distance in km
            charge_amount_kwh: Estimated charge amount in kWh
            tick: Current tick
            persona: Customer persona
            
        Returns:
            Balanced score (higher is better)
        """
        charge_speed = station_info.get("chargeSpeedPerCharger", 100)
        
        # Calculate completion and revenue scores
        completion_score = self.calculate_completion_score(
            station_id, station_info, detour, charge_speed, persona
        )
        revenue_score = self.calculate_revenue_score(
            station_id, station_info, charge_amount_kwh, tick, persona
        )
        
        # Get persona-specific weights
        completion_weight, revenue_weight = self.get_persona_weights(persona)
        
        # Balanced score
        balanced_score = (completion_score * completion_weight) + (revenue_score * revenue_weight)
        
        return balanced_score
    
    def get_persona_weights(self, persona: str) -> tuple:
        """
        Get completion and revenue weights for a persona.
        
        Returns:
            Tuple of (completion_weight, revenue_weight)
        """
        if persona in ["Stressed", "DislikesDriving"]:
            return (0.8, 0.2)  # 80% completion, 20% revenue
        elif persona == "EcoConscious":
            return (0.5, 0.5)  # 50% completion, 50% revenue
        elif persona == "CostSensitive":
            return (0.6, 0.4)  # 60% completion, 40% revenue
        else:  # Neutral
            return (0.6, 0.4)  # 60% completion, 40% revenue
    
    def find_best_charging_station(self, customer: dict, current_tick: int) -> tuple:
        """
        Find the best charging station for a customer using balanced scoring.
        
        Args:
            customer: Customer object
            current_tick: Current game tick
            
        Returns:
            Tuple of (best_station_id, estimated_charge_amount_kwh) or (None, 0)
        """
        from_node = customer.get("fromNode")
        to_node = customer.get("toNode")
        persona = customer.get("persona", "Neutral")
        current_charge_fraction = customer.get("chargeRemaining", 0)
        max_charge_kwh = customer.get("maxCharge", 50)
        consumption_per_km = customer.get("energyConsumptionPerKm", 0.2)
        current_charge_kwh = current_charge_fraction * max_charge_kwh
        
        best_station = None
        best_score = float('-inf')
        best_charge_amount = 0.0
        
        # Calculate direct distance for detour calculation
        direct_distance = self.get_shortest_path_distance(from_node, to_node)
        if direct_distance is None:
            direct_distance = float('inf')
        
        # Evaluate all reachable stations
        for station_id, station_info in self.charging_stations.items():
            # Validate station exists and has valid info
            if not station_id or not station_info:
                continue
            
            # Check if station has available chargers
            available = station_info.get("amountOfAvailableChargers", 0)
            if available is None or available <= 0:
                continue
            
            # Calculate distances
            dist_from_start = self.get_shortest_path_distance(from_node, station_id)
            dist_to_destination = self.get_shortest_path_distance(station_id, to_node)
            
            if dist_from_start is None or dist_to_destination is None:
                continue
            
            # Check if customer can reach station
            energy_to_station = dist_from_start * consumption_per_km
            if current_charge_kwh < energy_to_station:
                continue  # Can't reach station
            
            # Calculate detour
            detour = (dist_from_start + dist_to_destination) - direct_distance
            
            # Estimate charge amount at station
            charge_at_arrival = current_charge_kwh - energy_to_station
            if charge_at_arrival < 0:
                continue
            
            # Estimate charge amount needed
            energy_needed = dist_to_destination * consumption_per_km
            charge_needed = max(0, energy_needed - charge_at_arrival)
            
            # Calculate optimal charge amount (will be refined later)
            charge_amount_kwh = self.calculate_optimal_charge_amount(
                customer, station_id, charge_at_arrival, energy_needed
            )
            
            # Calculate balanced score
            score = self.calculate_balanced_station_score(
                station_id, station_info, detour, charge_amount_kwh, current_tick, persona
            )
            
            if score > best_score:
                best_score = score
                best_station = station_id
                best_charge_amount = charge_amount_kwh
        
        return (best_station, best_charge_amount) if best_station else (None, 0.0)
    
    def calculate_optimal_charge_amount(
        self,
        customer: dict,
        station_id: str,
        charge_at_arrival: float,
        energy_needed: float
    ) -> float:
        """
        Calculate optimal charge amount based on completion and revenue.
        
        Args:
            customer: Customer object
            station_id: Station node ID
            charge_at_arrival: Charge level when arriving at station (kWh)
            energy_needed: Energy needed to reach destination (kWh)
            
        Returns:
            Optimal charge amount in kWh
        """
        max_charge_kwh = customer.get("maxCharge", 50)
        persona = customer.get("persona", "Neutral")
        
        # Validate inputs
        if max_charge_kwh <= 0:
            return 0.0
        
        if charge_at_arrival < 0:
            charge_at_arrival = 0.0
        
        if energy_needed < 0:
            energy_needed = 0.0
        
        # Minimum charge: enough to reach destination + 10% safety margin
        min_charge_kwh = charge_at_arrival + (energy_needed * 1.1)
        min_charge_kwh = min(min_charge_kwh, max_charge_kwh)
        min_charge_kwh = max(0, min_charge_kwh)  # Ensure non-negative
        
        # Persona-based charge targets
        if persona in ["Stressed", "DislikesDriving"]:
            # Minimize charging time - charge to minimum needed
            target_charge_kwh = min_charge_kwh
        elif persona == "EcoConscious":
            # Charge more at green stations for revenue
            if self.is_green_energy_station(station_id):
                target_charge_kwh = max(min_charge_kwh, max_charge_kwh * 0.85)
            else:
                target_charge_kwh = min_charge_kwh
        elif persona == "CostSensitive":
            # Moderate charge (balance cost/completion)
            target_charge_kwh = max(min_charge_kwh, max_charge_kwh * 0.75)
        else:  # Neutral
            # Balanced charge
            target_charge_kwh = max(min_charge_kwh, max_charge_kwh * 0.80)
        
        # Revenue boost: charge more if green energy station
        if self.is_green_energy_station(station_id) and persona != "Stressed":
            # Charge more for revenue, but not if Stressed
            target_charge_kwh = max(target_charge_kwh, max_charge_kwh * 0.82)
        
        # Cap at 95% (avoid edge cases per Discord info)
        target_charge_kwh = min(target_charge_kwh, max_charge_kwh * 0.95)
        
        # Calculate charge amount needed
        charge_amount_kwh = max(0, target_charge_kwh - charge_at_arrival)
        
        return charge_amount_kwh
    
    def needs_charging(self, customer: dict, current_tick: int) -> bool:
        """
        Determine if a customer should charge (improved logic).
        Charges when needed OR when revenue opportunity exists.
        
        Args:
            customer: Customer object
            current_tick: Current game tick
            
        Returns:
            Boolean indicating if charging is recommended
        """
        from_node = customer.get("fromNode")
        to_node = customer.get("toNode")
        current_charge_fraction = customer.get("chargeRemaining", 0)
        max_charge_kwh = customer.get("maxCharge", 50)
        consumption_per_km = customer.get("energyConsumptionPerKm", 0.2)
        persona = customer.get("persona", "Neutral")
        
        current_charge_kwh = current_charge_fraction * max_charge_kwh
        
        # Find shortest path distance
        distance = self.get_shortest_path_distance(from_node, to_node)
        
        if distance is None:
            # Can't find path, safer to recommend charging
            return True
        
        # Calculate energy needed
        energy_needed = distance * consumption_per_km
        
        # Always charge if customer can't reach destination
        if current_charge_kwh < energy_needed:
            return True
        
        # Charge if customer has low charge (< 30%) for safety
        if current_charge_fraction < 0.30:
            return True
        
        # Charge if journey is long (> 100km) and charge is low (< 60%)
        if distance > 100 and current_charge_fraction < 0.60:
            return True
        
        # Revenue-aware charging: charge if green energy station is on route
        # Check if any green station is on or near route
        for station_id in self.charging_stations.keys():
            if not self.is_green_energy_station(station_id):
                continue
            
            # Check if station is reachable and on/near route
            dist_to_station = self.get_shortest_path_distance(from_node, station_id)
            dist_from_station = self.get_shortest_path_distance(station_id, to_node)
            
            if dist_to_station is not None and dist_from_station is not None:
                total_via_station = dist_to_station + dist_from_station
                detour = total_via_station - distance
                
                # If station is on route (small detour) or customer is EcoConscious/CostSensitive
                if detour < 10 or persona in ["EcoConscious", "CostSensitive"]:
                    energy_to_station = dist_to_station * consumption_per_km
                    if current_charge_kwh >= energy_to_station:
                        # Can reach station, consider charging for revenue
                        if persona in ["EcoConscious", "CostSensitive"]:
                            return True  # Always charge at green stations
                        elif detour < 5:  # Very small detour
                            return True  # Charge for revenue
        
        # Charge if customer has less than 110% of needed energy (safety margin)
        if current_charge_kwh < (energy_needed * 1.1):
            return True
        
        return False
    
    def get_active_customers(self, current_tick: int) -> list:
        """
        Get customers that are active at the current tick.
        
        Args:
            current_tick: Current game tick
            
        Returns:
            List of active customers
        """
        active = []
        for customer in self.customers:
            # Validate customer has required fields
            if not customer or not isinstance(customer, dict):
                continue
            
            customer_id = customer.get("id")
            departure_tick = customer.get("departureTick", -1)
            
            # Validate customer ID
            if not customer_id:
                continue
            
            # Only recommend for customers departing at the CURRENT tick
            if departure_tick != current_tick:
                continue
            
            # Ensure customer_id is string
            customer_id = str(customer_id)
            
            # Check if already recommended
            if customer_id in self.customer_states:
                if self.customer_states[customer_id].get("recommended", False):
                    continue
            else:
                # Initialize state if not exists
                self.customer_states[customer_id] = {
                    "recommended": False,
                    "state": customer.get("state", "Home"),
                    "charging_stops": []
                }
            
            # Validate customer has required fields
            if not customer.get("fromNode") or not customer.get("toNode"):
                continue
            if customer.get("maxCharge", 0) <= 0:
                continue
            
            active.append(customer)
        
        return active
    
    def plan_multi_stop_charging(self, customer: dict, current_tick: int) -> list:
        """
        Plan multiple charging stops for long journeys.
        
        Args:
            customer: Customer object
            current_tick: Current game tick
            
        Returns:
            List of charging stop dictionaries: [{"nodeId": str, "chargeTo": float}, ...]
        """
        from_node = customer.get("fromNode")
        to_node = customer.get("toNode")
        current_charge_fraction = customer.get("chargeRemaining", 0)
        max_charge_kwh = customer.get("maxCharge", 50)
        consumption_per_km = customer.get("energyConsumptionPerKm", 0.2)
        current_charge_kwh = current_charge_fraction * max_charge_kwh
        persona = customer.get("persona", "Neutral")
        
        # Calculate journey distance
        journey_distance = self.get_shortest_path_distance(from_node, to_node)
        if journey_distance is None:
            return []
        
        # Only plan multiple stops for long journeys
        if journey_distance < 150:
            return []  # Single stop is sufficient
        
        charging_stops = []
        current_position = from_node
        current_charge = current_charge_kwh
        stations_visited = set()
        
        # Plan first stop
        best_station, _ = self.find_best_charging_station(customer, current_tick)
        if best_station:
            dist_to_station = self.get_shortest_path_distance(current_position, best_station)
            if dist_to_station is not None:
                energy_to_station = dist_to_station * consumption_per_km
                if current_charge >= energy_to_station:
                    charge_at_arrival = current_charge - energy_to_station
                    dist_from_station = self.get_shortest_path_distance(best_station, to_node) or 0
                    energy_from_station = dist_from_station * consumption_per_km
                    
                    # Calculate charge amount for first stop
                    optimal_charge_kwh = self.calculate_optimal_charge_amount(
                        customer, best_station, charge_at_arrival, energy_from_station
                    )
                    target_charge_kwh = charge_at_arrival + optimal_charge_kwh
                    target_charge_kwh = min(target_charge_kwh, max_charge_kwh)
                    if max_charge_kwh > 0:
                        target_charge_fraction = target_charge_kwh / max_charge_kwh
                        target_charge_fraction = max(0.01, min(0.95, target_charge_fraction))
                        
                        # Validate before adding
                        if not math.isnan(target_charge_fraction) and not math.isinf(target_charge_fraction):
                            charging_stops.append({
                                "nodeId": str(best_station),
                                "chargeTo": round(float(target_charge_fraction), 3)
                            })
                    stations_visited.add(best_station)
                    
                    # Update state after first charge
                    current_position = best_station
                    current_charge = target_charge_kwh
                    
                    # Check if we need a second stop for very long journeys
                    if journey_distance > 250:
                        remaining_dist = self.get_shortest_path_distance(current_position, to_node) or 0
                        
                        if remaining_dist > 100:  # Still a long way to go
                            # Find intermediate station for second stop
                            best_second_station = None
                            best_second_score = float('-inf')
                            best_second_charge = 0.0
                            
                            for station_id, station_info in self.charging_stations.items():
                                if station_id in stations_visited:
                                    continue
                                
                                available = station_info.get("amountOfAvailableChargers", 0)
                                if available <= 0:
                                    continue
                                
                                dist_to_second = self.get_shortest_path_distance(current_position, station_id)
                                dist_from_second = self.get_shortest_path_distance(station_id, to_node)
                                
                                if dist_to_second is None or dist_from_second is None:
                                    continue
                                
                                # Check if we can reach second station
                                energy_to_second = dist_to_second * consumption_per_km
                                if current_charge < energy_to_second:
                                    continue
                                
                                # Check if second station is beneficial (within reasonable detour)
                                direct_dist = remaining_dist
                                detour = (dist_to_second + dist_from_second) - direct_dist
                                
                                if detour > 30:  # Too much detour
                                    continue
                                
                                # Calculate charge amount for second stop
                                charge_at_second = current_charge - energy_to_second
                                if charge_at_second < 0:
                                    continue
                                
                                energy_from_second = dist_from_second * consumption_per_km
                                charge_amount_kwh = self.calculate_optimal_charge_amount(
                                    customer, station_id, charge_at_second, energy_from_second
                                )
                                
                                # Calculate score for second station
                                score = self.calculate_balanced_station_score(
                                    station_id, station_info, detour, charge_amount_kwh, current_tick, persona
                                )
                                
                                if score > best_second_score:
                                    best_second_score = score
                                    best_second_station = station_id
                                    best_second_charge = charge_amount_kwh
                            
                            # Add second stop if beneficial
                            if best_second_station and best_second_score > 100:
                                dist_to_second = self.get_shortest_path_distance(current_position, best_second_station)
                                if dist_to_second is not None:
                                    energy_to_second = dist_to_second * consumption_per_km
                                    charge_at_second = current_charge - energy_to_second
                                    dist_from_second = self.get_shortest_path_distance(best_second_station, to_node) or 0
                                    energy_from_second = dist_from_second * consumption_per_km
                                    
                                    optimal_charge_kwh = self.calculate_optimal_charge_amount(
                                        customer, best_second_station, charge_at_second, energy_from_second
                                    )
                                    target_charge_kwh = charge_at_second + optimal_charge_kwh
                                    target_charge_kwh = min(target_charge_kwh, max_charge_kwh)
                                    if max_charge_kwh > 0:
                                        target_charge_fraction = target_charge_kwh / max_charge_kwh
                                        target_charge_fraction = max(0.01, min(0.95, target_charge_fraction))
                                        
                                        # Validate before adding
                                        if not math.isnan(target_charge_fraction) and not math.isinf(target_charge_fraction):
                                            charging_stops.append({
                                                "nodeId": str(best_second_station),
                                                "chargeTo": round(float(target_charge_fraction), 3)
                                            })
        
        return charging_stops
    
    def create_charging_recommendation(self, customer: dict, current_tick: int) -> dict:
        """
        Create a charging recommendation for a customer.
        Supports single or multi-stop charging for long journeys.
        
        Args:
            customer: Customer object
            current_tick: Current game tick
            
        Returns:
            Recommendation dictionary or None
        """
        # Validate customer
        if not customer or not isinstance(customer, dict):
            return None
        
        customer_id = customer.get("id")
        from_node = customer.get("fromNode")
        to_node = customer.get("toNode")
        
        # Validate required fields
        if not customer_id:
            return None
        if not from_node or not to_node:
            return None
        
        # Ensure customer_id is string
        customer_id = str(customer_id)
        
        # Get customer battery info
        current_charge_fraction = customer.get("chargeRemaining", 0)
        max_charge_kwh = customer.get("maxCharge", 50)
        consumption_per_km = customer.get("energyConsumptionPerKm", 0.2)
        current_charge_kwh = current_charge_fraction * max_charge_kwh
        
        # Calculate journey distance
        journey_distance = self.get_shortest_path_distance(from_node, to_node)
        
        # Plan multi-stop charging for long journeys
        if journey_distance and journey_distance > 150:
            charging_stops = self.plan_multi_stop_charging(customer, current_tick)
            if charging_stops:
                # Validate all stops
                valid_stops = []
                for stop in charging_stops:
                    node_id = stop.get("nodeId")
                    charge_to = stop.get("chargeTo")
                    
                    # Validate stop
                    if not node_id or node_id not in self.charging_stations:
                        continue
                    if charge_to is None or math.isnan(charge_to) or math.isinf(charge_to):
                        continue
                    if not (0.01 <= charge_to <= 0.95):
                        continue
                    
                    valid_stops.append({
                        "nodeId": str(node_id),
                        "chargeTo": round(float(charge_to), 3)
                    })
                
                if valid_stops:
                    # Ensure customer state exists
                    if customer_id not in self.customer_states:
                        self.customer_states[customer_id] = {
                            "recommended": False,
                            "state": customer.get("state", "Home"),
                            "charging_stops": []
                        }
                    
                    # Mark customer as recommended
                    self.customer_states[customer_id]["recommended"] = True
                    
                    return {
                        "customerId": str(customer_id),
                        "chargingRecommendations": valid_stops
                    }
        
        # Single stop for shorter journeys or if multi-stop planning failed
        best_station, estimated_charge_amount = self.find_best_charging_station(
            customer, current_tick
        )
        
        if best_station is None:
            return None
        
        # Validate customer can reach the station
        dist_to_station = self.get_shortest_path_distance(from_node, best_station)
        if dist_to_station is None:
            return None
        
        energy_to_reach = dist_to_station * consumption_per_km
        if current_charge_kwh < energy_to_reach:
            return None
        
        # Calculate optimal charge level
        dist_from_station = self.get_shortest_path_distance(best_station, to_node) or 0
        energy_to_station = dist_to_station * consumption_per_km
        charge_at_arrival = current_charge_kwh - energy_to_station
        energy_from_station = dist_from_station * consumption_per_km
        
        # Calculate optimal charge amount
        optimal_charge_kwh = self.calculate_optimal_charge_amount(
            customer, best_station, charge_at_arrival, energy_from_station
        )
        
        # Validate values before creating recommendation
        if max_charge_kwh <= 0:
            return None
        
        # Validate optimal charge amount
        if math.isnan(optimal_charge_kwh) or math.isinf(optimal_charge_kwh) or optimal_charge_kwh < 0:
            optimal_charge_kwh = 0.0
        
        # Validate charge at arrival
        if math.isnan(charge_at_arrival) or math.isinf(charge_at_arrival) or charge_at_arrival < 0:
            charge_at_arrival = 0.0
        
        # Calculate target charge level
        target_charge_kwh = charge_at_arrival + optimal_charge_kwh
        target_charge_kwh = min(target_charge_kwh, max_charge_kwh)
        target_charge_kwh = max(0, target_charge_kwh)  # Ensure non-negative
        
        # Convert to fraction (0-1)
        target_charge_fraction = target_charge_kwh / max_charge_kwh
        
        # Validate fraction is valid number
        if math.isnan(target_charge_fraction) or math.isinf(target_charge_fraction):
            # Fallback to safe default
            target_charge_fraction = 0.80
        elif not (0 <= target_charge_fraction <= 1):
            # Clamp to valid range
            target_charge_fraction = max(0.01, min(0.95, target_charge_fraction))
        
        # Ensure between 0.01 and 0.95 (avoid edge cases per Discord info)
        target_charge_fraction = max(0.01, min(0.95, target_charge_fraction))
        
        # Validate station ID is valid and exists
        if not best_station:
            return None
        if best_station not in self.charging_stations:
            return None
        if best_station not in self.nodes:
            return None
        
        # Validate customer ID is valid
        if not customer_id:
            return None
        customer_id = str(customer_id)
        
        # Ensure customer state exists before marking as recommended
        if customer_id not in self.customer_states:
            self.customer_states[customer_id] = {
                "recommended": False,
                "state": customer.get("state", "Home"),
                "charging_stops": []
            }
        
        # Mark customer as recommended
        self.customer_states[customer_id]["recommended"] = True
        
        # Create recommendation with validation
        try:
            recommendation = {
                "customerId": str(customer_id),
                "chargingRecommendations": [
                    {
                        "nodeId": str(best_station),
                        "chargeTo": round(float(target_charge_fraction), 3)
                    }
                ]
            }
            
            # Final validation - comprehensive checks
            charge_to = recommendation["chargingRecommendations"][0].get("chargeTo")
            node_id = recommendation["chargingRecommendations"][0].get("nodeId")
            
            # Validate chargeTo
            if charge_to is None:
                return None
            try:
                charge_to = float(charge_to)
                if math.isnan(charge_to) or math.isinf(charge_to):
                    return None
                if not (0.01 <= charge_to <= 0.95):
                    return None
            except (ValueError, TypeError):
                return None
            
            # Validate nodeId
            if not node_id:
                return None
            if node_id not in self.charging_stations:
                return None
            if node_id not in self.nodes:
                return None
            
            # Update recommendation with validated values
            recommendation["chargingRecommendations"][0]["chargeTo"] = round(charge_to, 3)
            recommendation["chargingRecommendations"][0]["nodeId"] = str(node_id)
                
            return recommendation
        except (ValueError, TypeError, KeyError, IndexError, AttributeError) as e:
            # Invalid values, skip this recommendation
            return None
    
    def generate_recommendations(self, current_tick: int) -> list:
        """
        Generate customer charging recommendations for the current tick.
        
        Args:
            current_tick: Current game tick number
            
        Returns:
            List of customer recommendations
        """
        recommendations = []
        recommended_customer_ids = set()  # Track to avoid duplicates
        
        # Get customers departing at current tick
        active_customers = self.get_active_customers(current_tick)
        
        for customer in active_customers:
            customer_id = customer.get("id")
            if not customer_id:
                continue
            
            customer_id = str(customer_id)
            
            # Skip if already recommended (avoid duplicates)
            if customer_id in recommended_customer_ids:
                continue
            
            # Verify customer exists in current map
            customer_exists = False
            for c in self.customers:
                if str(c.get("id")) == customer_id:
                    customer_exists = True
                    break
            
            if not customer_exists:
                continue
            
            # Check if customer should charge
            if self.needs_charging(customer, current_tick):
                recommendation = self.create_charging_recommendation(customer, current_tick)
                if recommendation:
                    # Validate recommendation before adding
                    rec_customer_id = recommendation.get("customerId")
                    charging_stops = recommendation.get("chargingRecommendations", [])
                    
                    if not rec_customer_id or not charging_stops:
                        continue
                    
                    # Check for duplicate customer IDs
                    if rec_customer_id in recommended_customer_ids:
                        continue
                    
                    # Validate all charging stops
                    valid_stops = []
                    for stop in charging_stops:
                        node_id = stop.get("nodeId")
                        charge_to = stop.get("chargeTo")
                        
                        if not node_id:
                            continue
                        if charge_to is None:
                            continue
                        
                        try:
                            charge_to = float(charge_to)
                            if math.isnan(charge_to) or math.isinf(charge_to):
                                continue
                            if not (0.01 <= charge_to <= 0.95):
                                continue
                        except (ValueError, TypeError):
                            continue
                        
                        # Verify node exists and is a charging station
                        if node_id not in self.charging_stations:
                            continue
                        if node_id not in self.nodes:
                            continue
                        
                        valid_stops.append({
                            "nodeId": str(node_id),
                            "chargeTo": round(float(charge_to), 3)
                        })
                    
                    # Only add if has valid stops
                    if valid_stops:
                        recommendation["chargingRecommendations"] = valid_stops
                        recommendations.append(recommendation)
                        recommended_customer_ids.add(rec_customer_id)
        
        return recommendations
    
    def update_state(self, game_response: dict):
        """
        Update internal state based on game response.
        
        Args:
            game_response: Response from the game API
        """
        updated_map = game_response.get("map")
        if updated_map:
            # Reinitialize with updated map
            self.map_obj = updated_map
            self.initialize_game_state()


def generate_customer_recommendations(map_obj: dict, current_tick: int) -> list:
    """
    Main entry point for generating customer recommendations.
    This function is called from app.py.
    
    Args:
        map_obj: The current map state
        current_tick: The current tick number
        
    Returns:
        List of customer recommendations
    """
    # Create or update algorithm instance
    # Initialize recommended customers set if not exists
    if not hasattr(generate_customer_recommendations, 'recommended_customers'):
        generate_customer_recommendations.recommended_customers = set()
    
    if not hasattr(generate_customer_recommendations, 'algorithm'):
        # First time - create algorithm
        generate_customer_recommendations.algorithm = ConsiditionAlgorithm(map_obj)
    else:
        # Update map - preserve recommended customers
        prev_recommended = generate_customer_recommendations.recommended_customers.copy()
        
        # Update map and reinitialize
        generate_customer_recommendations.algorithm.map_obj = map_obj
        generate_customer_recommendations.algorithm.initialize_game_state()
        
        # Restore recommended customers state (only for customers that still exist)
        for customer_id in prev_recommended:
            if customer_id in generate_customer_recommendations.algorithm.customer_states:
                generate_customer_recommendations.algorithm.customer_states[customer_id]["recommended"] = True
    
    # Generate recommendations
    recommendations = generate_customer_recommendations.algorithm.generate_recommendations(
        current_tick
    )
    
    # Update recommended customers set with new recommendations
    for rec in recommendations:
        customer_id = rec.get("customerId")
        if customer_id:
            generate_customer_recommendations.recommended_customers.add(str(customer_id))
    
    return recommendations
