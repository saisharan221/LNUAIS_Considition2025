"""
Considition 2025 Algorithm
--------------------------
This module implements the core algorithm for managing electric vehicles,
customers, and charging decisions.
"""

class ConsiditionAlgorithm:
    def __init__(self, map_obj):
        """
        Initialize the algorithm with map data.
        
        Args:
            map_obj: The map object containing all game state information
        """
        self.map_obj = map_obj
        self.initialize_game_state()
    
    def initialize_game_state(self):
        """Extract and initialize game state from map object."""
        # TODO: Extract EVs, charging stations, customers, locations
        self.evs = self.map_obj.get("evs", [])
        self.charging_stations = self.map_obj.get("chargingStations", [])
        self.customers = self.map_obj.get("customers", [])
        self.locations = self.map_obj.get("locations", [])
        
        # Track EV states
        self.ev_states = {}
        for ev in self.evs:
            self.ev_states[ev.get("id")] = {
                "current_location": ev.get("startLocation"),
                "battery": ev.get("batteryCapacity", 100),
                "assigned_customer": None,
                "route": []
            }
    
    def generate_recommendations(self, current_tick):
        """
        Generate customer recommendations for the current tick.
        
        Args:
            current_tick: The current game tick number
            
        Returns:
            List of customer recommendations
        """
        recommendations = []
        
        # TODO: Implement main algorithm logic
        # 1. Identify available customers
        available_customers = self.get_available_customers(current_tick)
        
        # 2. Match customers with available EVs
        for customer in available_customers:
            best_ev = self.find_best_ev_for_customer(customer, current_tick)
            if best_ev:
                recommendation = self.create_recommendation(customer, best_ev, current_tick)
                recommendations.append(recommendation)
        
        return recommendations
    
    def get_available_customers(self, current_tick):
        """
        Get customers that are available at the current tick.
        
        Args:
            current_tick: The current game tick
            
        Returns:
            List of available customers
        """
        available = []
        # TODO: Filter customers based on spawn time and assignment status
        for customer in self.customers:
            spawn_tick = customer.get("spawnTick", 0)
            if spawn_tick <= current_tick:
                # Check if not already assigned
                if not self.is_customer_assigned(customer):
                    available.append(customer)
        return available
    
    def is_customer_assigned(self, customer):
        """Check if a customer is already assigned to an EV."""
        customer_id = customer.get("id")
        for ev_id, state in self.ev_states.items():
            if state["assigned_customer"] == customer_id:
                return True
        return False
    
    def find_best_ev_for_customer(self, customer, current_tick):
        """
        Find the best EV to assign to a customer.
        
        Args:
            customer: The customer object
            current_tick: The current game tick
            
        Returns:
            Best EV ID or None
        """
        # TODO: Implement EV selection logic
        # Consider:
        # - Distance to customer
        # - Battery level
        # - Current availability
        # - Charging needs
        
        best_ev = None
        best_score = float('inf')
        
        for ev_id, state in self.ev_states.items():
            if state["assigned_customer"] is None:
                # Calculate suitability score
                score = self.calculate_ev_suitability(ev_id, customer, current_tick)
                if score < best_score:
                    best_score = score
                    best_ev = ev_id
        
        return best_ev
    
    def calculate_ev_suitability(self, ev_id, customer, current_tick):
        """
        Calculate how suitable an EV is for a customer.
        Lower score is better.
        
        Args:
            ev_id: The EV identifier
            customer: The customer object
            current_tick: The current game tick
            
        Returns:
            Suitability score (lower is better)
        """
        state = self.ev_states[ev_id]
        
        # TODO: Implement proper distance calculation
        # For now, use a simple heuristic
        pickup_location = customer.get("pickupLocation")
        current_location = state["current_location"]
        
        # Distance heuristic (placeholder)
        distance = self.calculate_distance(current_location, pickup_location)
        
        # Battery consideration
        battery_penalty = 0 if state["battery"] > 50 else 100
        
        return distance + battery_penalty
    
    def calculate_distance(self, location_a, location_b):
        """
        Calculate distance between two locations.
        
        Args:
            location_a: Start location ID
            location_b: End location ID
            
        Returns:
            Distance value
        """
        # TODO: Implement actual distance calculation based on map
        # This is a placeholder
        if location_a == location_b:
            return 0
        return 10  # Placeholder value
    
    def create_recommendation(self, customer, ev_id, current_tick):
        """
        Create a customer recommendation object.
        
        Args:
            customer: The customer object
            ev_id: The EV identifier
            current_tick: The current game tick
            
        Returns:
            Recommendation dictionary
        """
        customer_id = customer.get("id")
        
        # Update EV state
        self.ev_states[ev_id]["assigned_customer"] = customer_id
        
        # TODO: Calculate optimal route including charging stops
        route = self.calculate_route(
            ev_id,
            customer.get("pickupLocation"),
            customer.get("destination")
        )
        
        recommendation = {
            "customerId": customer_id,
            "evId": ev_id,
            "route": route
        }
        
        return recommendation
    
    def calculate_route(self, ev_id, pickup_location, destination):
        """
        Calculate the optimal route for an EV to pickup and deliver a customer.
        
        Args:
            ev_id: The EV identifier
            pickup_location: Customer pickup location
            destination: Customer destination
            
        Returns:
            List of location IDs forming the route
        """
        state = self.ev_states[ev_id]
        current_location = state["current_location"]
        
        # TODO: Implement proper routing algorithm with charging stations
        # For now, use simple direct route
        route = []
        
        # If not at pickup location, go there first
        if current_location != pickup_location:
            route.append(pickup_location)
        
        # Then go to destination
        if pickup_location != destination:
            route.append(destination)
        
        return route
    
    def update_state(self, game_response):
        """
        Update internal state based on game response.
        
        Args:
            game_response: Response from the game API
        """
        # TODO: Update EV states, battery levels, locations based on game response
        updated_map = game_response.get("map")
        if updated_map:
            self.map_obj = updated_map
            # Update EV states from the response
            # This will be implemented once we know the response structure
            pass


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
        generate_customer_recommendations.algorithm = ConsiditionAlgorithm(map_obj)
    else:
        # Update with new map state
        generate_customer_recommendations.algorithm.map_obj = map_obj
    
    # Generate recommendations
    recommendations = generate_customer_recommendations.algorithm.generate_recommendations(current_tick)
    
    return recommendations

