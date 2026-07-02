FUEL_PRICE_PER_LITRE = 1100

VEHICLE_CONSUMPTION = {
    "motorcycle": {"normal": 35, "heavy":25},
    "van":{"normal":10, "heavy":7}
}
BASE_FARE = 600
RATE_PER_KM = 250
ISLAND_SURCHARGE = 300

TRAFFIC_LEVELS = ["low", "moderate", "heavy"]

ZONES = {
    "island": ["Victoria Island", "Lekki Phase 1", "Lekki Phase 2",
        "Ikoyi", "Eko Atlantic", "Ajah", "Sangotedo", "Badore",
        "Chevron", "Jakande"],

    "mainland_central": ["Yaba", "Surulere", "Mushin", "Ojuelegba", "Ebute Metta",
        "Costain", "Alaka", "Bode Thomas"],

    "mainland_north":["Ikeja", "Maryland", "Ogba", "Ojodu", "Berger", "Agege",
        "Abule Egba", "Iyana Ipaja", "Meiran", "Ifako", "Gbagada"],

    "mainland_east":["Oshodi", "Isolo", "Ago Palace", "Okota", "Ilasamaja",
        "Ijesha", "Satellite Town", "Festac", "Amuwo Odofin", "Mile 2"],

    "outskirts":["Badagry","Ikorodu","Epe","Igando","Ipaja",
        "Alimosho","Egbeda","Idimu","Igba","Igbogbo"]
}

ALL_ZONES  = [zone for group in ZONES.values() for zone in group]

ISLAND_ZONES = ZONES["island"]

ZONE_DISTANCES = {
    "Victoria Island" : 18, "Lekki Phase 1" :24, "Lekki Phase 2": 30,
    "Ikoyi":16, "Eko Atlantic":20, "Ajah" :35, "Sangotedo" :38, "Badore":36,
    "Chevron":28, "Jakande":32,

    "Yaba": 12, "Surulere" :14, "Mushin":10, "Ojuelegba":13, "Ebute Metta":11,
    "Costain":15, "Alaka":14, "Bode Thomas":13,

    "Ikeja" :0, "Maryland":5, "Ogba":6, "Ojodu":8, "Berger":10, "Agege":7,
    "Abule Egba":12, "Iyana Ipaja":14, "Meiran":13, "Ifako":6, "Gbagada":9,

    "Oshodi":8, "Isolo":11, "Ago Palace":16, "Okota":13, "Ilasamaja":10,
    "Ijesha":12, "Satellite Town":22, "Festac":18, "Amuwo Odofin":16, "Mile 2":15,

    "Badagry" : 55,"Ikorodu":35,"Epe":60,"Igando":18,"Ipaja":15,
    "Alimosho":16,"Egbeda":17,"Idimu":19,"Igba":22,"Igbogbo":38


}