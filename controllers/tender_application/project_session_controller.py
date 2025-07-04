from models.abs_motor import Motor


class ProjectSession:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ProjectSession, cls).__new__(cls)
            cls._instance.id = None
            cls._instance.name = None
            cls._instance.code = None
            cls._instance.unique_no = None
            cls._instance.revision = 0
            cls._instance.modified_by_id = None
            cls._instance.modified_at = None
            cls._instance.project_electrical_specs = {"project_info": {"proj_avl": [],
                                                                       "project_site_location": "",
                                                                       "owner_name": "",
                                                                       "consultant_name": "",
                                                                       "employer_name": "",
                                                                       "el_contact_name": "",
                                                                       "el_contact_position": "",
                                                                       "el_contact_phone": "",
                                                                       "me_contact_name": "",
                                                                       "me_contact_position": "",
                                                                       "me_contact_phone": "",
                                                                       "co_contact_name": "",
                                                                       "co_contact_position": "",
                                                                       "co_contact_phone": "",
                                                                       "m_voltage": 0,
                                                                       "l_voltage": 0,
                                                                       "voltage_variation": 0,
                                                                       "minimum_temprature": 0,
                                                                       "maximum_temprature": 0,
                                                                       "humidity": 0,
                                                                       "altitude_elevation": 0,
                                                                       "voltage_frequency": 0,
                                                                       "frequency_variation": 0},
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
                                                                    "spare_pins": 0,
                                                                    "instruments": {
                                                                        "delta_pressure_transmitter": {"qty": 0,
                                                                                                       "brand": None},
                                                                        "delta_pressure_switch": {"qty": 0,
                                                                                                  "brand": None},
                                                                        "pressure_transmitter": {"qty": 0,
                                                                                                 "brand": None},
                                                                        "pressure_switch": {"qty": 0, "brand": None},
                                                                        "pressure_gauge": {"qty": 0, "brand": None},
                                                                        "inlet_temperature_transmitter": {"qty": 0,
                                                                                                          "brand": None},
                                                                        "outlet_temperature_transmitter": {"qty": 0,
                                                                                                           "brand": None}
                                                                    }},
                                                      "damper": {"status": False,
                                                                 "motors": {
                                                                     "damper": {"motor": Motor(power=0), "qty": 0,
                                                                                "power": 0, "brand": None,
                                                                                "start_type": None}
                                                                 },
                                                                 "instruments": {
                                                                     "proximity_switch": {"qty": 0, "brand": None},
                                                                 }},
                                                      "fan": {"status": False,
                                                              "motors": {
                                                                  "fan": {"motor": Motor(power=0),
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
                                                                          "space_heater": False,
                                                                          "de_nde": False,
                                                                          }
                                                              },
                                                              "instruments": {
                                                                  "bearing_temperature_transmitter": {"qty": 0,
                                                                                                      "brand": None},
                                                                  "bearing_vibration_transmitter": {"qty": 0,
                                                                                                    "brand": None},
                                                                  "pressure_transmitter": {"qty": 0, "brand": None},
                                                                  "temperature_transmitter": {"qty": 0, "brand": None},
                                                                  "pt100": {"qty": 0, "brand": None}
                                                              }},
                                                      "vibration": {"status": False,
                                                                    "motors": {
                                                                        "vibration": {"motor": Motor(power=0), "qty": 0,
                                                                                      "power": 0}
                                                                    },
                                                                    "instruments": {},
                                                                    },
                                                      "transport": {"status": False,
                                                                    "motors": {
                                                                        "rotary": {"motor": Motor(power=0), "qty": 0,
                                                                                   "power": 0},
                                                                        "telescopic_chute": {"motor": Motor(power=0),
                                                                                             "qty": 0, "power": 0},
                                                                        "slide_gate": {"motor": Motor(power=0),
                                                                                       "qty": 0, "power": 0},
                                                                        "screw1": {"motor": Motor(power=0), "qty": 0,
                                                                                   "power": 0},
                                                                        "screw2": {"motor": Motor(power=0), "qty": 0,
                                                                                   "power": 0}
                                                                    },
                                                                    "instruments": {
                                                                        "proximity_switch": {"qty": 0, "brand": None},
                                                                        "speed_detector": {"qty": 0, "brand": None},
                                                                        "level_switch": {"qty": 0, "brand": None},
                                                                        "level_transmitter": {"qty": 0, "brand": None}
                                                                    }},
                                                      "fresh_air": {"status": False,
                                                                    "motors": {
                                                                        "freshair_motor": {"motor": Motor(power=0),
                                                                                           "qty": 0, "power": 0,
                                                                                           "start_type": None},
                                                                        "fresh_air_flap": {"motor": Motor(power=0),
                                                                                           "qty": 0, "power": 0,
                                                                                           "start_type": None},
                                                                        "emergency_flap": {"motor": Motor(power=0),
                                                                                           "qty": 0, "power": 0,
                                                                                           "start_type": None}
                                                                    },
                                                                    "instruments": {
                                                                        "proximity_switch": {"qty": 0, "brand": None},
                                                                        "temperature_transmitter": {"qty": 0,
                                                                                                    "brand": None}
                                                                    }},
                                                      "hopper_heater": {
                                                          "status": False,
                                                          "motors": {"elements": {"motor": Motor(power=0), "qty": 0,
                                                                                  "power": 0}},
                                                          "instruments": {"ptc": {"qty": 0, "brand": None}}
                                                      },
                                                      "installation":{
                                                          "height":0,
                                                          "width":0,
                                                          "depth":0,
                                                          "ccr":0,
                                                      },
                                                      }
        return cls._instance
