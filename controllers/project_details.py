class ProjectDetails:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ProjectDetails, cls).__new__(cls)
            cls._instance.project_details = cls._instance.get_default_project_details()
        return cls._instance.project_details


    def get_default_project_details(self):
        return {"rev": 0,
                "project_info": {"rev": 1,
                                 "project_m_voltage":6300,
                                 "project_l_voltage":400,
                                 "voltage_variation":10,
                                 "project_voltage_frequency":50,
                                 "project_voltage_frequency_variation":2},
                "bagfilter": {"type": "",
                              "order": "",
                              "plc_series": "",
                              "plc_protocol": "",
                              "touch_panel": "",
                              "olm": False,
                              "ee": False,
                              "me": False,
                              "cable_supply": False,
                              "cable_dimension": 0,
                              "instruments": {
                                          "delta_pressure_transmitter": {"qty": 0, "brand": ""},
                                          "delta_pressure_switch": {"qty": 0, "brand": ""},
                                          "pressure_transmitter": {"qty": 0, "brand": ""},
                                          "pressure_switch": {"qty": 0, "brand": ""},
                                          "pressure_gauge": {"qty": 0, "brand": ""},
                                          "inlet_temperature_transmitter": {"qty": 0, "brand": ""},
                                          "outlet_temperature_transmitter": {"qty": 0, "brand": ""}
                                           }},
                "damper": {"status": False,
                           "motors": {
                               "damper": {"qty": 0, "power": 0, "brand": "", "start_type": ""}
                           },
                           "instruments": {
                               "proximity_switch": {"qty": 0, "brand": ""},
                           }},
                "fan": {"status": False,
                        "motors": {
                            "fan": {
                                "qty": 0,
                                "power": 0,
                                "rpm": "",
                                "brand": "",
                                "starting_method": "",
                                "cooling_method": "",
                                "ip_rating": "",
                                "efficiency_class": "",
                                "voltage_type": "",
                                "painting_ral": "",
                                "thermal_protection": "",
                                "space_heater": False
                            }
                        },
                        "instruments": {
                            "bearing_temperature_transmitter": {"qty": 0, "brand": ""},
                            "bearing_vibration_transmitter": {"qty": 0, "brand": ""},
                            "pressure_transmitter": {"qty": 0, "brand": ""},
                            "temperature_transmitter": {"qty": 0, "brand": ""}
                        }},
                "vibration": {"status": False,
                              "motors": {
                                  "vibration": {"qty": 0, "power": 0}
                              },
                              "instruments": {},
                              },
                "transport": {"status": False,
                              "motors": {
                                  "rotary": {"qty": 0, "power": 0},
                                  "telescopic_chute": {"qty": 0, "power": 0},
                                  "slide_gate": {"qty": 0, "power": 0},
                                  "screw1": {"qty": 0, "power": 0},
                                  "screw2": {"qty": 0, "power": 0}
                              },
                              "instruments": {
                                  "proximity_switch": {"qty": 0, "brand": ""},
                                  "speed_detector": {"qty": 0, "brand": ""},
                                  "level_switch": {"qty": 0, "brand": ""},
                                  "level_transmitter": {"qty": 0, "brand": ""}
                              }},
                "fresh_air": {"status": False,
                              "motors": {
                                  "freshair_motor": {"qty": 0, "power": 0, "start_type": ""},
                                  "fresh_air_flap": {"qty": 0, "power": 0, "start_type": ""},
                                  "emergency_flap": {"qty": 0, "power": 0, "start_type": ""}
                              },
                              "instruments": {
                                  "proximity_switch": {"qty": 0, "brand": ""},
                                  "temperature_transmitter": {"qty": 0, "brand": ""}
                              }},
                "hopper_heater": {
                    "status": False,
                    "motors": {"elements": {"qty": 0, "power": 0}},
                    "instruments": {"ptc": {"qty": 0, "brand": ""}}
                },
                }

