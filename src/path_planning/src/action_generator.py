import math

class RobotActionSetGenerator():

    """
    Robot Action Set Generator Class
    
    Args: NA
    
    This class generates action sets for the path planning algorithms. 
        3 Types: 
            * discrete           -> Robot moves move_amt in cardinal directions and if diagnol=True, moves in move_amt*sqrt(2) diagnolly
            * rt (radius-theta)  -> Robot first turns a number of degrees and then traverses along a fixed radius
            * differential drive -> Robot has a differential driving system
    """

    # Discrete action set
    @staticmethod
    def gen_robot_discrete_action_set(diagnol=True, move_amt=1):
        action_set = {}
        if diagnol:
            action_set = {
                "action_set" : {
                    "up"         : {"move": (        0, -move_amt), "cost": move_amt},
                    "up_right"   : {"move": ( move_amt, -move_amt), "cost": math.sqrt(2*move_amt**2)},
                    "right"      : {"move": ( move_amt,         0), "cost": move_amt},
                    "down_right" : {"move": ( move_amt,  move_amt), "cost": math.sqrt(2*move_amt**2)},
                    "down"       : {"move": (        0,  move_amt), "cost": move_amt},
                    "down_left"  : {"move": (-move_amt,  move_amt), "cost": math.sqrt(2*move_amt**2)},
                    "left"       : {"move": (-move_amt,         0), "cost": move_amt},
                    "up_left"    : {"move": (-move_amt, -move_amt), "cost": math.sqrt(2*move_amt**2)},
                },
                "move_type"      : "discrete"
            }
    
        else:
            action_set = {
                "action_set" : {
                    "up"         : {"move": (        0, -move_amt), "cost": move_amt},
                    "right"      : {"move": ( move_amt,         0), "cost": move_amt},
                    "down"       : {"move": (        0,  move_amt), "cost": move_amt},
                    "left"       : {"move": (-move_amt,         0), "cost": move_amt},
                },
                "move_type"      : "discrete"
            } 
        return action_set

    
    # RT action set
    @staticmethod      
    def gen_robot_rt_action_set(node_threshold_xy=0.5, node_threshold_theta=30, goal_threshold_xy=1.5, goal_threshold_theta=30, max_add_turn_cost=0):
        print("\n=====================================================================================\n")
        
        dist_def = 5
        dist_bounds = (1, 10)
        
        theta_def = 30
        theta_bounds = (1, 179)
        
        n_branches_def = 5
        n_branch_bounds = (1, 10)
        
        # Query user for positions
        def get_user_input(pos_string, default, bounds):
            prompt = None
            if pos_string == "dist":
                prompt = f"Enter step size distance ({bounds[0]} <= step size <= {bounds[1]}) or leave blank to apply the default value: "
            elif pos_string == "theta":
                prompt = f"Enter angle theta ({bounds[0]} < theta < {bounds[1]}) or leave blank to apply the default value: "
            else:
                prompt = f"Enter number of possible branches (should be odd) or leave blank to apply the default value: "
                        
            # Query until user has input legal values     
            while True:
                start_str = input(prompt)
                start_str_nw = start_str.replace(" ", "")
                
                # If empty string, set values to default
                if start_str_nw == '':
                    print("Selecting default value: ", default)
                    return default              
                                    
                # Check for incorrect input
                try:
                    val = int(start_str_nw)
                except:
                    print("Please type a single integer.\n")
                    continue    
                
                # Check if position out of bounds
                if val < bounds[0] or val > bounds[1]:
                    print("Numbers out of bounds. Please select new value.\n")
                    continue

                # User chose correct inputs
                return val
        
        # Define start/goal positions
        dist = get_user_input("dist", dist_def, dist_bounds)
        print("")
        theta = get_user_input("theta", theta_def, theta_bounds)        
        print("")
        n_branches = get_user_input("branches", n_branches_def, n_branch_bounds)            
        print("\n=====================================================================================")
        
        # Init dict
        action_set = {
            "move_type" : "rt",
            "node_threshold" : (node_threshold_xy, node_threshold_theta),
            "goal_threshold" : (goal_threshold_xy, goal_threshold_theta),
            "action_set" : {}
        }
        # Apply action set
        even = False
        if n_branches%2 == 0:
            even = True
              
        dist /= node_threshold_xy
        max_turn = None
        turn_defined = False
        for i in range(n_branches):
            t = None
            if even:
                t = (n_branches//2 - i)*theta - theta//2
            else:
                t = (n_branches//2 - i)*theta 
            if not turn_defined:
                turn_defined = True
                max_turn = t
            action_set["action_set"][i] = {'move' : (dist, t), "cost" : dist+abs(max_add_turn_cost*t/max_turn)}
        return action_set

    # Differential drive action set
    @staticmethod
    def gen_robot_diff_drive_action_set(node_threshold_xy=0.5, node_threshold_theta=30, goal_threshold_xy=1.5, goal_threshold_theta=30):
        print("\n=====================================================================================\n")
                
        # Query user for positions
        def get_user_input():
            prompt = f"Enter the two wheel RPM's as left_RPM,right_RPM (0 <= RPM) or leave blank to apply the default value: "

            # Query until user has input legal values     
            while True:
                start_str = input(prompt)
                start_str_nw = start_str.replace(" ", "")
                
                # If empty string, set values to default
                if start_str_nw == '':
                    def_vals = (5, 10)
                    # def_vals = (45, 50)
                    # def_vals = (50, 100)
                    print("Selecting default values: ", f"{def_vals[0]}, {def_vals[1]}")
                    return def_vals             
                                    
                # Check for incorrect input
                try:
                    val0 = int(start_str_nw[0])
                    val1 = int(start_str_nw[1])
                except:
                    print("Please type two integers seperated by a comma.\n")
                    continue    
                
                # Check if position out of bounds
                if val0 < 0 or val1 < 0:
                    print("Numbers out of bounds. Please select new value.\n")
                    continue

                # User chose correct inputs
                return (val0 , val1)
        
        # Define user inputs
        rpm0 = 0
        rpm1, rpm2 = get_user_input()          
        print("\n=====================================================================================")
        
        # Init dict
        action_set = {
            "move_type" : "diff drive",
            "node_threshold" : (node_threshold_xy, node_threshold_theta),
            "goal_threshold" : (goal_threshold_xy, goal_threshold_theta),
            "action_set" : {}
        }
        # Apply action set 
        rpms = [rpm0, rpm1, rpm2]

        i = 0
        for rpm_l in rpms:
            for rpm_r in rpms:
                action_set["action_set"][i] = {"move": (rpm_l, rpm_r), "cost":0}
                i += 1
        return action_set