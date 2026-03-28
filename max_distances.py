# Note: Values cames from Gemini AI query:
# What is the maximum distance (miles) between any 2 points in {City Name}?
# Answer was padded about 10 miles to be conservative (doubled for universities)

MAX_DISTANCES = {
    'Carlsbad':25,
    'Chula Vista':25,
    'Coronado':20,
    'Del Mar':15,
    'El Cajon':15,
    'Encinitas':20,
    'Escondido':25,
    'Imperial Beach':15,
    'La Mesa':15,
    'Lemon Grove':15,
    'National City':15,
    'Oceanside':25,
    'Poway':20,
    'San Diego':50,
    'San Marcos':20,
    'Santee':15,
    'Solana Beach':15,
    'Vista':15,
    'San Diego Harbor':20,
    'San Diego State Univ':5,
    'Uc San Diego':5,
    'Unincorporated':120
}

def get_max_distance(city):
    return float(MAX_DISTANCES[city])

