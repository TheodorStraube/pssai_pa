Parameters:
initial_temperature - Initial temperature for simulated annealing
frozen_temperature - Abort temperature for simulated annaeling
cooling_ratio - Rate of temperature decrease
iterations - Number of iterations per cooling step
initial_method - How to generate initial solution. Either "random" or "seq"
neighbor_method - How to generate neighborhood. "far" swaps any two operations on a machine,
		"near" only swaps operations that immediately follow each other
