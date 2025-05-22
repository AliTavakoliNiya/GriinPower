from models.abs_motor import Motor

class ProjectDetails:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ProjectDetails, cls).__new__(cls)
            cls._instance.project_details = cls._instance.get_default_project_details()
        return cls._instance.project_details


    def get_default_project_details(self):
        return {"project_info": {"rev": 1,
                                 "project_m_voltage":6300,
                                 "project_l_voltage":400,
                                 "voltage_variation":10,
                                 "project_voltage_frequency":50,
                                 "project_voltage_frequency_variation":2},
                "bagfilter": {"type": None,
                              "order": "",
                              "plc_series": None,
                              "plc_protocol": None,
                              "touch_panel": "",
                              "olm": False,
                              "ee": False,
                              "me": False,
                              "cable_supply": False,
                              "cable_dimension": 0,
                              "instruments": {
                                          "delta_pressure_transmitter": {"qty": 0, "brand": None},
                                          "delta_pressure_switch": {"qty": 0, "brand": None},
                                          "pressure_transmitter": {"qty": 0, "brand": None},
                                          "pressure_switch": {"qty": 0, "brand": None},
                                          "pressure_gauge": {"qty": 0, "brand": None},
                                          "inlet_temperature_transmitter": {"qty": 0, "brand": None},
                                          "outlet_temperature_transmitter": {"qty": 0, "brand": None}
                                           }},
                "damper": {"status": False,
                           "motors": {
                               "damper": {"motor":Motor(power_kw=0), "qty": 0, "power": 0, "brand": None, "start_type": None}
                                    },
                           "instruments": {
                               "proximity_switch": {"qty": 0, "brand": None},
                                          }},
                "fan": {"status": False,
                        "motors": {
                            "fan": {"motor":Motor(power_kw=0),
                                    "qty": 0,
                                    "power": 0,
                                    "rpm": None,
                                    "brand": None,
                                    "start_type": None,
                                    "cooling_method": None,
                                    "ip_rating": None,
                                    "efficiency_class": None,
                                    "voltage_type": None,
                                    "painting_ral": None,
                                    "thermal_protection": None,
                                    "space_heater": False
                                     }
                        },
                        "instruments": {
                            "bearing_temperature_transmitter": {"qty": 0, "brand": None},
                            "bearing_vibration_transmitter": {"qty": 0, "brand": None},
                            "pressure_transmitter": {"qty": 0, "brand": None},
                            "temperature_transmitter": {"qty": 0, "brand": None},
                            "pt100": {"qty": 0, "brand": None}
                        }},
                "vibration": {"status": False,
                              "motors": {
                                  "vibration": {"motor":Motor(power_kw=0),"qty": 0, "power": 0}
                              },
                              "instruments": {},
                              },
                "transport": {"status": False,
                              "motors": {
                                  "rotary": {"motor":Motor(power_kw=0),"qty": 0, "power": 0},
                                  "telescopic_chute": {"motor":Motor(power_kw=0),"qty": 0, "power": 0},
                                  "slide_gate": {"motor":Motor(power_kw=0),"qty": 0, "power": 0},
                                  "screw1": {"motor":Motor(power_kw=0),"qty": 0, "power": 0},
                                  "screw2": {"motor":Motor(power_kw=0),"qty": 0, "power": 0}
                              },
                              "instruments": {
                                  "proximity_switch": {"qty": 0, "brand": None},
                                  "speed_detector": {"qty": 0, "brand": None},
                                  "level_switch": {"qty": 0, "brand": None},
                                  "level_transmitter": {"qty": 0, "brand": None}
                              }},
                "fresh_air": {"status": False,
                              "motors": {
                                  "freshair_motor": {"motor":Motor(power_kw=0),"qty": 0, "power": 0, "start_type": None},
                                  "fresh_air_flap": {"motor":Motor(power_kw=0),"qty": 0, "power": 0, "start_type": None},
                                  "emergency_flap": {"motor":Motor(power_kw=0),"qty": 0, "power": 0, "start_type": None}
                              },
                              "instruments": {
                                  "proximity_switch": {"qty": 0, "brand": None},
                                  "temperature_transmitter": {"qty": 0, "brand": None}
                              }},
                "hopper_heater": {
                                  "status": False,
                                  "motors": {"elements": {"motor":Motor(power_kw=0), "qty": 0, "power": 0}},
                                  "instruments": {"ptc": {"qty": 0, "brand": None}}
                },
                }

