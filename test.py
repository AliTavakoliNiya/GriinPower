
o1 = "6.96x16.(3.6m).20"


parts = o1.replace("x", ".")
parts = parts.split(".")

parts[3] = parts[3].replace("(", "").replace("m)", "") if "(" in parts[3] else parts[3]

print

