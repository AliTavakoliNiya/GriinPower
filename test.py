if abs(motor_voltage - voltage_val) < 1e-3:
    score += 1
if attr_dict.get("brand") == brand:
    score += 1
if start_type and attr_dict.get("start_type") == start_type:
    score += 1
if cooling_method and attr_dict.get("cooling_method") == cooling_method:
    score += 1
if ip_rating and attr_dict.get("ip_rating") == ip_rating:
    score += 1
if efficiency_class and attr_dict.get("efficiency_class") == efficiency_class:
    score += 1
if painting_ral and attr_dict.get("painting_ral") == painting_ral:
    score += 1
if thermal_protection and attr_dict.get("thermal_protection") == thermal_protection:
    score += 1
if is_official and attr_dict.get("is_official") == is_official:
    score += 1
if is_routine and attr_dict.get("is_routine") == is_routine:
    score += 1