"""
Considition 2025 Algorithm
--------------------------
Electric Vehicle Charging Recommendation System

This module recommends optimal charging strategies for customers traveling
in electric vehicles, considering battery levels, charging station
availability, route optimization, and energy source preferences.
"""

import heapq


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
        self.charging_stations = {}
        self.zones = {}
        self.customers = []
        
        self.initialize_game_state()
    
    def initialize_game_state(self):
        """Extract and initialize game state from map object."""
        # Build graph from nodes and edges
        nodes_list = self.map_obj.get("nodes", [])
        edges_list = self.map_obj.get("edges", [])
        zones_list = self.map_obj.get("zones", [])
        
        # Index nodes
        for node in nodes_list:
            node_id = node.get("id")
            self.nodes[node_id] = node
            self.graph[node_id] = []
            
            # Track charging stations
            target = node.get("target", {})
            if target.get("Type") == "ChargingStation":
                self.charging_stations[node_id] = target
            
            # Collect all customers
            customers_at_node = node.get("customers", [])
            for customer in customers_at_node:
                customer["homeNode"] = node_id
                self.customers.append(customer)
        
        # Build adjacency list for graph
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
            self.customer_states[customer.get("id")] = {
                "recommended": False,
                "state": customer.get("state", "Home")
            }
    
    def generate_recommendations(self, current_tick):
        """
        Generate customer charging recommendations for the current tick.
        
        Args:
            current_tick: The current game tick number
            
        Returns:
            List of customer recommendations
        """
        recommendations = []
        
        # Get customers departing at or after current tick
        active_customers = self.get_active_customers(current_tick)
        
        for customer in active_customers:
            # ULTRA-AGGRESSIVE: Charge EVERYONE (maximize KWH revenue!)
            # Skip the needs_charging check entirely
            recommendation = self.create_charging_recommendation(
                customer, current_tick
            )
            if recommendation:
                recommendations.append(recommendation)
        
        return recommendations
    
    def get_active_customers(self, current_tick):
        """
        Get customers that are active at the current tick.
        
        Args:
            current_tick: The current game tick
            
        Returns:
            List of active customers
        """
        active = []
        for customer in self.customers:
            departure_tick = customer.get("departureTick", 0)
            customer_id = customer.get("id")
            
            # Only recommend for customers departing at the CURRENT tick
            # (not in the future)
            if (departure_tick == current_tick and
                    not self.customer_states[customer_id]["recommended"]):
                active.append(customer)
        
        return active
    
    def needs_charging(self, customer, current_tick):
        """
        Determine if a customer needs to charge before their journey.
        
        Args:
            customer: The customer object
            current_tick: The current game tick
            
        Returns:
            Boolean indicating if charging is needed
        """
        from_node = customer.get("fromNode")
        to_node = customer.get("toNode")
        current_charge_fraction = customer.get("chargeRemaining", 0)
        max_charge_kwh = customer.get("maxCharge", 50)
        consumption_per_km = customer.get("energyConsumptionPerKm", 0.2)
        
        # Calculate current charge in kWh
        current_charge_kwh = current_charge_fraction * max_charge_kwh
        
        # Find shortest path distance
        distance = self.get_shortest_path_distance(from_node, to_node)
        
        if distance is None:
            # Can't find path, safer to recommend charging
            return True
        
        # Calculate energy needed for journey
        energy_needed = distance * consumption_per_km
        
        # AGGRESSIVE MODE: Recommend if less than 200% of needed energy
        # This maximizes KWH revenue by charging more customers!
        return current_charge_kwh < (energy_needed * 2.0)
    
    def get_shortest_path_distance(self, start_node, end_node):
        """
        Calculate shortest path distance using Dijkstra's algorithm.
        
        Args:
            start_node: Starting node ID
            end_node: Ending node ID
            
        Returns:
            Shortest distance or None if no path exists
        """
        if start_node == end_node:
            return 0
        
        if start_node not in self.graph or end_node not in self.graph:
            return None
        
        # Dijkstra's algorithm
        distances = {node: float('inf') for node in self.graph}
        distances[start_node] = 0
        pq = [(0, start_node)]
        visited = set()
        
        while pq:
            current_dist, current_node = heapq.heappop(pq)
            
            if current_node in visited:
                continue
            
            visited.add(current_node)
            
            if current_node == end_node:
                return current_dist
            
            for neighbor in self.graph.get(current_node, []):
                neighbor_node = neighbor["to"]
                edge_dist = neighbor["distance"]
                new_dist = current_dist + edge_dist
                
                if new_dist < distances[neighbor_node]:
                    distances[neighbor_node] = new_dist
                    heapq.heappush(pq, (new_dist, neighbor_node))
        
        return None if distances[end_node] == float('inf') else distances[
            end_node
        ]
    
    def find_best_charging_station(self, customer, current_tick):
        """
        Find the best charging station for a customer.
        PRIORITIZES reachable stations!
        
        Args:
            customer: The customer object
            current_tick: The current game tick
            
        Returns:
            Best charging station node ID or None
        """
        from_node = customer.get("fromNode")
        to_node = customer.get("toNode")
        persona = customer.get("persona", "Neutral")
        current_charge_kwh = customer.get("chargeRemaining", 0) * customer.get("maxCharge", 50)
        consumption = customer.get("energyConsumptionPerKm", 0.2)
        
        best_station = None
        best_score = float('inf')
        
        for station_id, station_info in self.charging_stations.items():
            # Check if station has available chargers
            available = station_info.get("amountOfAvailableChargers", 0)
            if available <= 0:
                continue
            
            # Calculate distance to station
            dist_from_start = self.get_shortest_path_distance(
                from_node, station_id
            )
            if dist_from_start is None:
                continue
            
            # CHECK REACHABILITY FIRST!
            energy_to_station = dist_from_start * consumption
            if current_charge_kwh < energy_to_station:
                # Cannot reach this station - skip it
                continue
            
            # Calculate distance from station to destination
            dist_to_destination = self.get_shortest_path_distance(
                station_id, to_node
            )
            if dist_to_destination is None:
                continue
            
            # Calculate detour
            direct_distance = self.get_shortest_path_distance(
                from_node, to_node
            )
            if direct_distance is None:
                direct_distance = dist_from_start + dist_to_destination
            
            detour = (dist_from_start + dist_to_destination) - direct_distance
            
            # Calculate score based on persona
            score = self.calculate_station_score(
                station_id,
                station_info,
                detour,
                persona
            )
            
            if score < best_score:
                best_score = score
                best_station = station_id
        
        return best_station
    
    def calculate_station_score(
            self, station_id, station_info, detour, persona):
        """
        Calculate a score for a charging station based on customer persona.
        
        Args:
            station_id: The station node ID
            station_info: Station information
            detour: Extra distance to reach this station
            persona: Customer persona
            
        Returns:
            Score (lower is better)
        """
        charge_speed = station_info.get("chargeSpeedPerCharger", 100)
        
        # Get zone for energy source info
        station_node = self.nodes.get(station_id, {})
        zone_id = station_node.get("zoneId")
        zone = self.zones.get(zone_id, {})
        
        # Check if zone has green energy
        has_green_energy = self.zone_has_green_energy(zone)
        
        # AGGRESSIVE MODE: Reduce detour penalties (KWH revenue > completion)
        score = detour * 0.5  # Base score with lower penalty
        
        # Adjust based on persona (but be more liberal!)
        if persona == "Stressed" or persona == "DislikesDriving":
            # Still minimize detour, but less strict
            score += detour * 0.5  # Lower penalty (was 2x)
            score -= charge_speed * 0.2  # More favor for fast charging
        
        elif persona == "CostSensitive":
            # Favor cheaper options (green energy might be cheaper)
            if has_green_energy:
                score -= 50
            score += detour * 0.2  # Low detour penalty (was 0.5)
        
        elif persona == "EcoConscious":
            # Strongly favor green energy
            if has_green_energy:
                score -= 100
            else:
                score += 100  # Penalize non-green
            score += detour * 0.1  # Very low detour penalty (was 0.3)
        
        else:  # Neutral
            # Balanced approach, but liberal on detours
            if has_green_energy:
                score -= 20
            score += detour * 0.3  # Lower penalty (was 1.0)
        
        return score
    
    def zone_has_green_energy(self, zone):
        """
        Check if a zone has green energy sources.
        
        Args:
            zone: Zone object
            
        Returns:
            Boolean indicating if zone has green energy
        """
        green_sources = {"Hydro", "Nuclear", "Wind", "Solar"}
        energy_sources = zone.get("energySources", [])
        
        for source in energy_sources:
            if source.get("type") in green_sources:
                return True
        
        return False
    
    def calculate_charging_amount(self, customer, station_id):
        """
        Calculate how much charge a customer needs.
        
        Args:
            customer: The customer object
            station_id: The charging station node ID
            
        Returns:
            Charging amount in kWh
        """
        from_node = customer.get("fromNode")
        to_node = customer.get("toNode")
        current_charge_fraction = customer.get("chargeRemaining", 0)
        max_charge_kwh = customer.get("maxCharge", 50)
        consumption_per_km = customer.get("energyConsumptionPerKm", 0.2)
        
        # Current charge
        current_charge_kwh = current_charge_fraction * max_charge_kwh
        
        # Calculate total journey distance through charging station
        dist_to_station = self.get_shortest_path_distance(
            from_node, station_id
        )
        dist_from_station = self.get_shortest_path_distance(
            station_id, to_node
        )
        
        if dist_to_station is None or dist_from_station is None:
            # Default to full charge if path calculation fails
            return max_charge_kwh - current_charge_kwh
        
        # Energy needed to reach station
        energy_to_station = dist_to_station * consumption_per_km
        
        # Charge remaining when reaching station
        charge_at_station = current_charge_kwh - energy_to_station
        
        # Charge needed (with 10% safety margin)
        energy_needed_from_station = dist_from_station * consumption_per_km
        target_charge = energy_needed_from_station * 1.1
        
        # Amount to charge
        charge_amount = max(0, target_charge - charge_at_station)
        
        # Don't exceed battery capacity
        # charge_at_station might be negative if we can't reach station
        if charge_at_station < 0:
            # Can't reach the station with current charge
            charge_amount = max_charge_kwh
        else:
            max_possible_charge = max_charge_kwh - charge_at_station
            charge_amount = min(charge_amount, max_possible_charge)
        
        # Final safety check: never exceed battery capacity
        charge_amount = min(charge_amount, max_charge_kwh)
        
        return charge_amount
    
    def get_path_nodes(self, start_node, end_node):
        """
        Get the list of nodes in the shortest path.
        
        Args:
            start_node: Starting node ID
            end_node: Ending node ID
            
        Returns:
            List of node IDs in the path
        """
        if start_node == end_node:
            return [start_node]
        
        if start_node not in self.graph or end_node not in self.graph:
            return []
        
        # Modified Dijkstra's to track path
        distances = {node: float('inf') for node in self.graph}
        distances[start_node] = 0
        previous = {node: None for node in self.graph}
        pq = [(0, start_node)]
        visited = set()
        
        while pq:
            current_dist, current_node = heapq.heappop(pq)
            
            if current_node in visited:
                continue
            
            visited.add(current_node)
            
            if current_node == end_node:
                break
            
            for neighbor in self.graph.get(current_node, []):
                neighbor_node = neighbor["to"]
                edge_dist = neighbor["distance"]
                new_dist = current_dist + edge_dist
                
                if new_dist < distances[neighbor_node]:
                    distances[neighbor_node] = new_dist
                    previous[neighbor_node] = current_node
                    heapq.heappush(pq, (new_dist, neighbor_node))
        
        # Reconstruct path
        if distances[end_node] == float('inf'):
            return []
        
        path = []
        current = end_node
        while current is not None:
            path.append(current)
            current = previous[current]
        
        path.reverse()
        return path
    
    def create_charging_recommendation(self, customer, current_tick):
        """
        Create a charging recommendation for a customer.
        
        Args:
            customer: The customer object
            current_tick: The current game tick
            
        Returns:
            Recommendation dictionary or None
        """
        customer_id = customer.get("id")
        from_node = customer.get("fromNode")
        to_node = customer.get("toNode")
        
        # Get customer battery info
        current_charge_fraction = customer.get("chargeRemaining", 0)
        max_charge_kwh = customer.get("maxCharge", 50)
        consumption_per_km = customer.get("energyConsumptionPerKm", 0.2)
        current_charge_kwh = current_charge_fraction * max_charge_kwh
        
        # Find best charging station
        best_station = self.find_best_charging_station(customer,
                                                       current_tick)
        
        if best_station is None:
            # No suitable charging station found
            return None
        
        # Validate customer can reach the station
        dist_to_station = self.get_shortest_path_distance(
            from_node, best_station
        )
        if dist_to_station is None:
            return None
            
        energy_to_reach = dist_to_station * consumption_per_km
        if current_charge_kwh < energy_to_reach:
            # Can't reach station with current charge
            return None
        
        # Calculate charging amount (in kWh)
        charge_amount = self.calculate_charging_amount(customer,
                                                       best_station)
        
        if charge_amount <= 0:
            return None
        
        # Mark customer as recommended
        self.customer_states[customer_id]["recommended"] = True
        
        # Create recommendation
        # CORRECT FORMAT from documentation:
        # chargingRecommendations is an ARRAY of charging stops
        
        # Calculate optimal charge level
        dist_from_station = self.get_shortest_path_distance(
            best_station, to_node
        ) or 0
        
        energy_to_station = dist_to_station * consumption_per_km
        charge_at_station = current_charge_kwh - energy_to_station
        energy_from_station = dist_from_station * consumption_per_km
        
        # AGGRESSIVE: Target charge with 2x safety margin!
        target_charge_kwh = charge_at_station + (energy_from_station * 2.0)
        
        # Always charge to at least 95% if stopping (MAXIMIZE KWH!)
        # Stopping to charge has overhead, make it worth it!
        min_charge_kwh = max_charge_kwh * 0.95
        target_charge_kwh = max(min_charge_kwh, target_charge_kwh)
        
        # Cap at max battery
        target_charge_kwh = min(max_charge_kwh, target_charge_kwh)
        
        # Convert to percentage (0-1)
        target_charge_fraction = target_charge_kwh / max_charge_kwh
        
        # Charge high! Between 0.85 and 0.99 (max KWH revenue!)
        target_charge_fraction = max(0.85, min(0.99, target_charge_fraction))
        
        recommendation = {
            "customerId": customer_id,
            "chargingRecommendations": [  # Array of charging stops!
                {
                    "nodeId": best_station,  # "nodeId" not "chargingStation"
                    "chargeTo": round(target_charge_fraction, 3)
                }
            ]
        }
        
        return recommendation
    
    def update_state(self, game_response):
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


def generate_customer_recommendations(map_obj, current_tick):
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
    if not hasattr(generate_customer_recommendations, 'algorithm'):
        generate_customer_recommendations.algorithm = ConsiditionAlgorithm(
            map_obj
        )
    # Don't reinitialize - keep the state!
    # Just update the map reference
    else:
        generate_customer_recommendations.algorithm.map_obj = map_obj
    
    # Generate recommendations
    recommendations = (
        generate_customer_recommendations.algorithm.generate_recommendations(
            current_tick
        )
    )
    
    return recommendations
