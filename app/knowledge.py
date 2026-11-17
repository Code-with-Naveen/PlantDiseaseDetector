"""Plain-language disease information shown next to each prediction.

General agronomy guidance only - it is not a substitute for advice from a local
agricultural extension service or plant pathologist.
"""

PLANT_DISPLAY = {
    "Pepper bell": "Bell pepper",
}

CONDITION_DISPLAY = {
    "Cercospora leaf spot Gray leaf spot": "Cercospora / Gray leaf spot",
    "Spider mites Two-spotted spider mite": "Spider mites (two-spotted)",
    "Haunglongbing (Citrus greening)": "Citrus greening (Huanglongbing)",
    "Esca (Black Measles)": "Esca (Black measles)",
    "Leaf blight (Isariopsis Leaf Spot)": "Leaf blight (Isariopsis leaf spot)",
    "Tomato Yellow Leaf Curl Virus": "Yellow leaf curl virus",
    "Tomato mosaic virus": "Mosaic virus",
    "healthy": "Healthy",
}

HEALTHY = {
    "about": "The leaf shows no visible signs of disease. Colour and texture look normal for this crop.",
    "treatment": ["No treatment needed."],
    "prevention": [
        "Keep monitoring leaves weekly, especially after rain or humid weather.",
        "Water at the base of the plant and avoid wetting the foliage.",
        "Maintain good spacing, balanced fertiliser and clean tools to keep plants strong.",
    ],
}

GENERIC = {
    "about": "A disease was detected on this leaf. Confirm the diagnosis with a local expert before treating.",
    "treatment": [
        "Remove and destroy badly affected leaves.",
        "Ask a local agricultural extension office which approved treatment suits your region.",
    ],
    "prevention": ["Rotate crops, avoid overhead watering and keep the area free of plant debris."],
}

INFO = {
    "Apple___Apple_scab": {
        "about": "Fungal disease (Venturia inaequalis) causing olive-green to brown scabby spots on leaves and fruit.",
        "treatment": [
            "Remove and destroy fallen infected leaves.",
            "Apply a fungicide labelled for apple scab (e.g. sulfur or captan) at green-tip to petal-fall.",
            "Prune to open the canopy so leaves dry faster.",
        ],
        "prevention": ["Plant scab-resistant varieties.", "Rake and compost or bury leaf litter in autumn."],
    },
    "Apple___Black_rot": {
        "about": "Fungal disease (Botryosphaeria obtusa) producing brown leaf spots with purple margins ('frog-eye') and rotting fruit.",
        "treatment": [
            "Prune out cankers and dead wood and destroy it.",
            "Remove mummified fruit.",
            "Use a registered fungicide during the growing season if pressure is high.",
        ],
        "prevention": ["Keep trees well-pruned and not stressed.", "Clear mummified fruit and dead twigs each winter."],
    },
    "Apple___Cedar_apple_rust": {
        "about": "Fungal disease (Gymnosporangium) with bright yellow-orange leaf spots; needs nearby juniper/cedar to complete its cycle.",
        "treatment": [
            "Apply a fungicide (e.g. myclobutanil) from pink bud through early summer.",
            "Remove nearby galls on juniper where possible.",
        ],
        "prevention": ["Plant rust-resistant apple varieties.", "Avoid planting apples close to red cedar or juniper."],
    },
    "Cherry_(including_sour)___Powdery_mildew": {
        "about": "Fungal disease forming white powdery patches on leaves and shoots, causing curling and stunted growth.",
        "treatment": [
            "Spray with sulfur or a fungicide labelled for powdery mildew.",
            "Prune out infected shoots.",
        ],
        "prevention": ["Improve air circulation by pruning.", "Avoid excess nitrogen that promotes soft new growth."],
    },
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": {
        "about": "Fungal disease (Cercospora zeae-maydis) causing long rectangular grey-tan lesions between leaf veins.",
        "treatment": [
            "Apply a foliar fungicide if lesions reach the upper leaves before tasselling.",
            "Plough under infected residue after harvest.",
        ],
        "prevention": ["Rotate away from corn for a season.", "Choose tolerant hybrids and avoid dense planting."],
    },
    "Corn_(maize)___Common_rust_": {
        "about": "Fungal disease (Puccinia sorghi) producing small cinnamon-brown pustules on both leaf surfaces.",
        "treatment": [
            "Fungicide is rarely needed; apply one only on susceptible varieties with heavy early infection.",
        ],
        "prevention": ["Plant resistant hybrids.", "Plant early so the crop matures before rust builds up."],
    },
    "Corn_(maize)___Northern_Leaf_Blight": {
        "about": "Fungal disease (Exserohilum turcicum) causing long cigar-shaped grey-green lesions on leaves.",
        "treatment": [
            "Apply a foliar fungicide at early tasselling if lesions are spreading.",
            "Remove and bury infected crop residue.",
        ],
        "prevention": ["Use resistant hybrids.", "Rotate crops and manage residue."],
    },
    "Grape___Black_rot": {
        "about": "Fungal disease (Guignardia bidwellii) with tan leaf spots edged in brown and shrivelled black fruit.",
        "treatment": [
            "Remove mummified berries and infected leaves.",
            "Apply a protectant fungicide from early shoot growth until fruit set.",
        ],
        "prevention": ["Keep the canopy open with good pruning.", "Clean up fallen fruit and leaves in winter."],
    },
    "Grape___Esca_(Black_Measles)": {
        "about": "Complex wood-rot disease causing 'tiger-stripe' leaf discolouration and spotted berries.",
        "treatment": [
            "Prune out infected wood in dry weather and disinfect tools.",
            "Severely affected vines may need to be removed.",
        ],
        "prevention": ["Protect large pruning wounds.", "Avoid pruning during wet weather."],
    },
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "about": "Fungal leaf spot producing dark brown irregular spots, which can cause early leaf drop.",
        "treatment": [
            "Apply a copper-based or other labelled fungicide.",
            "Remove heavily infected leaves.",
        ],
        "prevention": ["Improve airflow and sun exposure in the canopy.", "Avoid overhead irrigation."],
    },
    "Orange___Haunglongbing_(Citrus_greening)": {
        "about": "Serious bacterial disease spread by the Asian citrus psyllid; causes blotchy yellow leaves and bitter, lopsided fruit.",
        "treatment": [
            "There is no cure - remove infected trees to protect others, following local regulations.",
            "Control psyllids with approved insecticides.",
            "Report suspected cases to your agriculture authority.",
        ],
        "prevention": ["Buy certified disease-free nursery trees.", "Monitor for psyllids and control them early."],
    },
    "Peach___Bacterial_spot": {
        "about": "Bacterial disease (Xanthomonas) causing small dark angular leaf spots, 'shot-holes' and blemished fruit.",
        "treatment": [
            "Apply copper-based bactericide at leaf fall and early spring (follow label rates).",
            "Avoid overhead watering.",
        ],
        "prevention": ["Plant tolerant varieties.", "Keep trees well-fed and not drought-stressed."],
    },
    "Pepper,_bell___Bacterial_spot": {
        "about": "Bacterial disease (Xanthomonas) causing water-soaked spots that turn brown, with yellowing and leaf drop.",
        "treatment": [
            "Remove infected plants and avoid working in wet fields.",
            "Apply copper-based sprays early to slow spread.",
        ],
        "prevention": ["Use disease-free seed and resistant varieties.", "Rotate with non-solanaceous crops for 2-3 years."],
    },
    "Potato___Early_blight": {
        "about": "Fungal disease (Alternaria solani) producing dark concentric-ringed ('target') spots on older leaves.",
        "treatment": [
            "Remove heavily infected foliage.",
            "Apply a labelled fungicide (e.g. chlorothalonil or mancozeb) at first symptoms.",
            "Keep plants well-fertilised and watered.",
        ],
        "prevention": ["Rotate crops for 2-3 years.", "Use certified seed potatoes and destroy volunteer plants."],
    },
    "Potato___Late_blight": {
        "about": "Aggressive disease (Phytophthora infestans) causing water-soaked dark blotches and white mould underneath leaves; can destroy a crop quickly.",
        "treatment": [
            "Act immediately: remove and bag infected plants.",
            "Apply a labelled late-blight fungicide and repeat as directed.",
            "Do not compost infected tubers or foliage.",
        ],
        "prevention": ["Plant certified seed and resistant varieties.", "Hill soil well and avoid overhead watering."],
    },
    "Squash___Powdery_mildew": {
        "about": "Fungal disease giving white powdery coating on leaves, leading to yellowing and reduced yield.",
        "treatment": [
            "Spray with sulfur, potassium bicarbonate or a labelled fungicide.",
            "Remove badly infected leaves.",
        ],
        "prevention": ["Give plants space for airflow.", "Choose mildew-resistant varieties."],
    },
    "Strawberry___Leaf_scorch": {
        "about": "Fungal disease (Diplocarpon earlianum) causing dark purple spots that merge and make leaves look scorched.",
        "treatment": [
            "Remove infected leaves after harvest.",
            "Apply a labelled fungicide if the disease is severe.",
        ],
        "prevention": ["Use resistant cultivars.", "Avoid overhead watering and overcrowded beds; renovate beds regularly."],
    },
    "Tomato___Bacterial_spot": {
        "about": "Bacterial disease (Xanthomonas) causing small dark greasy spots on leaves and rough scabby fruit spots.",
        "treatment": [
            "Remove infected leaves and avoid handling wet plants.",
            "Apply copper-based sprays early (follow label).",
        ],
        "prevention": ["Use clean seed and transplants.", "Rotate crops and use drip irrigation."],
    },
    "Tomato___Early_blight": {
        "about": "Fungal disease (Alternaria solani) with brown target-like spots and yellowing on lower leaves first.",
        "treatment": [
            "Remove affected lower leaves.",
            "Apply a labelled fungicide (copper or chlorothalonil) at first signs.",
            "Mulch to stop soil splashing onto leaves.",
        ],
        "prevention": ["Rotate crops for at least 2 years.", "Stake plants and water at the base."],
    },
    "Tomato___Late_blight": {
        "about": "Aggressive disease (Phytophthora infestans) causing large greasy grey-brown blotches on leaves, stems and fruit.",
        "treatment": [
            "Remove and bag infected plants immediately; do not compost them.",
            "Apply a labelled fungicide to nearby healthy plants.",
        ],
        "prevention": ["Choose resistant varieties.", "Ensure airflow and avoid overhead watering."],
    },
    "Tomato___Leaf_Mold": {
        "about": "Fungal disease (Passalora fulva) with pale yellow spots on the upper surface and olive-green mould underneath; common in humid greenhouses.",
        "treatment": [
            "Improve ventilation and reduce humidity.",
            "Remove infected leaves; apply a labelled fungicide if needed.",
        ],
        "prevention": ["Space plants widely.", "Use resistant varieties and keep leaves dry."],
    },
    "Tomato___Septoria_leaf_spot": {
        "about": "Fungal disease (Septoria lycopersici) causing many small round spots with dark borders and grey centres.",
        "treatment": [
            "Remove infected lower leaves.",
            "Apply a labelled fungicide (copper or chlorothalonil).",
        ],
        "prevention": ["Rotate crops; mulch soil.", "Water at the base and clean up debris at season end."],
    },
    "Tomato___Spider_mites Two-spotted_spider_mite": {
        "about": "Tiny sap-sucking mites causing fine yellow stippling, bronzing and fine webbing on leaves.",
        "treatment": [
            "Spray leaves (especially undersides) with water, insecticidal soap or horticultural oil.",
            "Use a labelled miticide for heavy infestations.",
        ],
        "prevention": ["Avoid dusty, hot, dry conditions and drought stress.", "Encourage natural predators such as predatory mites."],
    },
    "Tomato___Target_Spot": {
        "about": "Fungal disease (Corynespora cassiicola) causing brown spots with concentric rings on leaves and fruit.",
        "treatment": [
            "Remove infected leaves.",
            "Apply a labelled fungicide; improve airflow by staking and pruning.",
        ],
        "prevention": ["Rotate crops.", "Avoid overhead irrigation and remove plant debris."],
    },
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "about": "Virus spread by whiteflies; causes upward-curling, yellowed, stunted leaves and poor fruit set.",
        "treatment": [
            "No cure: remove and destroy infected plants.",
            "Control whiteflies with sticky traps, soap sprays or approved insecticides.",
        ],
        "prevention": ["Plant resistant varieties.", "Use insect-proof netting and control weeds that host whiteflies."],
    },
    "Tomato___Tomato_mosaic_virus": {
        "about": "Virus causing mottled light/dark green mosaic patterns and distorted leaves; spreads by touch and tools.",
        "treatment": [
            "No cure: remove and destroy infected plants.",
            "Wash hands and disinfect tools after handling plants.",
        ],
        "prevention": ["Use virus-free seed and resistant varieties.", "Do not smoke or handle tobacco before touching plants."],
    },
}


def get_info(class_name: str, healthy: bool):
    if healthy:
        return HEALTHY
    return INFO.get(class_name, GENERIC)


def display_names(plant: str, condition: str):
    return PLANT_DISPLAY.get(plant, plant), CONDITION_DISPLAY.get(condition, condition)
