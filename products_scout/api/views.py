#=================================================DONE===================================================

from openai import OpenAI
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import json
import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import json
import logging
from openai import OpenAI  # Import OpenAI client
logger = logging.getLogger(__name__)


# Define the system and user instructions for generating responses
SYSTEM_PROMPT = """
    Respond to the user's query with detailed and specific recommendations, explanations, or ideas. The query can relate to:
    - **Products**: Features, pricing, comparisons, use cases, and types (e.g., laptops, shoes, smartphones).
    - **Brands**: Reputation, top products, comparisons (e.g., Nike, Samsung, Apple).
    - **Special Occasions**: Gift ideas, themes, and product suggestions for birthdays, anniversaries, weddings, etc.
    - **Product Types**: Features, subcategories, and best use cases for various product types (e.g., gaming laptops, trail running shoes).
    - ... etc ... but very important to always give in markdown format only

    Provide responses in **markdown format** with clear sections, lists, or tables. Ensure that the responses are structured, engaging, and user-friendly.


    NOTE (some example for Out of scope queries):-
    If someone ask for solving any type of programming related query then don't give any type of code only give some theoretical approach and explanation and suggest him the official documents with the links with a (disclaimer:- something like providing the code is against the policy of products scout) and give a information in markdown something like (below are some books related to your query).
    If the query is theory base then give him a short note on the query with disclaimer and give a information in markdown something like (below are some products or books as needed which relates to the query). 
    If the query is unrelated, politely explain that it is outside the scope of supported topics, and suggest asking about products, brands, or special occasions.
    If the query is related to any discussion but not relates to any products, ideas, brands and special occasions.
    If the query is related to past more than 50 - 100 years then give him a short note on the query with disclaimer and also provide some resources and give a information in markdown something like (below are some books otherwise products related to your query).
    If the query is related to any specific popular person but not relates any products, brands and special occasion then give him a short note on the query and give a information in markdown something like (below are some products or books as per requirement related to your query).

    IMPORTANT:- 
    Never give the first line with bold markdown only give in critical case
    The categories which are not outside of the scope (
    brands, books, biographies, clothes & fashion, beauty and personal care, 
    sport items etc something related) but always give notification for incorrect spellings may affect you result. 
    If the query is outside of the scope don't forget to give the disclaimer (eg. outside the scope of supported topics) something like this.
    If the query is related to product then give the information based on Indian e-commerce services.

    VERY IMPORTANT:-
    Never suggest any product with names in the response either describe his query in very detail if products related and give a information in markdown like (below are some products related to your query).
    Only give suggestion when someone's query about the something like (gifts, ideas, etc..) but relevant to products 
    If the products is related to ecommerce platforms like (Amazon) then give every product information in very details.
    If the user's query is product related then always give the notification for incorrect spellings may affect your result.
    If the user ask about this company then the give a detail explanation of our company i am giving you some details of the company (
        Company Name:- Products Scout
        Products Scout is an AI-driven platform designed to provide product recommendations based on user input. We use APIs, including third-party APIs such as Amazon, and artificial intelligence tools to suggest products that match your preferences.
        Products Scout, your trusted partner in finding the perfect products. We leverage cutting-edge AI and API integrations to provide you with fast, reliable, and personalized product as per your requirements.
        Experience next-level AI technology for smarter product searches
        Find top-rated products in seconds, customized just for you
        Explore a world of products with global coverage and recommendations
        also give the company link:- productsscout.com.
    ) 

    Query: {query}
    """

SYSTEM_PROMPT_1 = "You are a helpful assistant that helps users find the best products based on their queries."


# Helper function to parse extracted features JSON
# def parse_features_json(features_str):
#     """
#     Parse the extracted features JSON string into a Python dictionary.
#     """
#     try:
#         return json.loads(features_str.body)
#     except json.JSONDecodeError:
#         return {"error": "Failed to parse extracted features JSON."}

class MockRequest:
    def __init__(self, data):
        self.data = data


# (=================DONE==================)
@api_view(['POST'])
@permission_classes([AllowAny])  # Allow open access
def generate_response_view(request):
    """
    Generate a response based on the user's query using OpenAI's API.
    """
    user_query = request.data.get('query', '')

    # Step 1: Initialize OpenAI client
    api_key = settings.OPENAI_API_KEY
    client = OpenAI(api_key=api_key)
    logger.info(f"Received query: {user_query}")

    if not user_query:
        logger.warning("Empty query received.")
        return Response({"error": "Query cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Step 1: Generate a response using OpenAI

        # Step 1: Generate a response using OpenAI
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_query}
            ],
            temperature=0.7
        )
        generated_response = completion.choices[0].message.content
        logger.info(f"Generated response: {generated_response}")

        # Check if the query is product-related
        if is_product_related(user_query):
            logger.info("Query is product-related. Proceeding with feature extraction.")

            # Step 2: Extract features using GPT-4
            feature_extraction_prompt = f"""
                You are an advanced AI assistant specializing in extracting and structuring product features for e-commerce applications. 
                Your task is to analyze the provided input description and extract all explicitly mentioned features. Additionally:

                1. If the input is very short (e.g., single words like "iPhone" or "Nike"), infer relevant features based on your knowledge 
                   of common product attributes for such queries.
                2. If the input mentions a famous person (e.g., Einstein, Newton, Mahatma Gandhi), infer that the product is likely a book 
                   or biography about that person and include relevant attributes such as category ("Books"), title, and related topics.
                3. Always ensure the extracted features are relevant and presented in a well-structured JSON format.

                Input Description:
                {user_query}

                Example Outputs:
                - Input: "Nike shoes"
                  Output:
                  {{
                      "product_category": "shoes",
                      "brand": "Nike",
                      "type": "sports shoes",
                      "features": ["durable", "lightweight", "stylish"]
                  }}

                - Input: "Einstein"
                  Output:
                  {{
                      "product_category": "Books",
                      "title": "Biography of Albert Einstein",
                      "type": "biography",
                      "related_topics": ["physics", "relativity", "scientific contributions"]
                  }}

                - Input: "Recommend a good book on physics"
                  Output:
                  {{
                      "product_category": "Books",
                      "title": "Physics Fundamentals",
                      "type": "educational",
                      "topics": ["physics", "mechanics", "thermodynamics"]
                  }}

                - Input: "Camera"
                  Output:
                  {{
                      "product_category": "electronics",
                      "type": "digital camera",
                      "features": ["high resolution", "optical zoom", "lightweight", "compact"]
                  }}

                  if query contains more than 1 values for same key then extract those features like the below given example

                  Example Outputs:
                - Input: "Nike and adidas shoes"
                  Output:
                  {{
                      "product_category": "shoes",
                      "brand": ["Nike", "adidas"],
                      "type": "sports shoes",
                      "features": ["durable", "lightweight", "stylish"]
                  }}

                Analyze the input and provide a structured JSON response.
            """

            feature_extraction_response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "user", "content": feature_extraction_prompt}
                ]
            )
            extracted_features = feature_extraction_response.choices[0].message.content.strip()
            logger.info(f"Extracted features (raw): {extracted_features}")

            # Validate and parse extracted features
            if not extracted_features or extracted_features.lower().startswith("the input provided"):
                return Response({"error": "No valid features extracted from the input."}, status=400)

                # Validate and parse extracted features
            try:
                extracted_features_json = json.loads(extracted_features)
                logger.info(f"Extracted features (parsed): {extracted_features_json}")

                # Step 3: Fetch products based on extracted features
                products_response = fetch_products(extracted_features_json)
                logger.info(f"Fetched products: {products_response}")

                # Return response, extracted features, and fetched products
                return Response({
                    "response": generated_response,
                    "extracted_features": extracted_features_json,
                    "products": products_response.get("products", []),
                    "error": products_response.get("error", None)
                }, status=status.HTTP_200_OK)

            except json.JSONDecodeError:
                logger.error("Failed to parse extracted features as JSON.")
                # If parsing fails, proceed without features and products
                return Response({
                    "response": generated_response,
                    "extracted_features": None,
                    "products": None
                }, status=status.HTTP_200_OK)

        else:
            logger.info("Query is not product-related. Skipping feature extraction.")
            # If the query is not product-related, return only the generated response
            return Response({
                "response": generated_response,
                "extracted_features": None,
                "products": None
            }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Unexpected error occurred: {str(e)}")
        return Response({"error": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# (=================DONE==================)
def fetch_products(features):
    """
    Fetch relevant products from Amazon using RapidAPI based on the extracted features.
    """
    try:
        if not features:
            logger.warning("Feature extraction returned empty results.")
            return {"error": "Features are required."}

        logger.info(f"Extracted features for product search: {features}")

        # Construct a query string dynamically from features
        query_parts = []
        for key, value in features.items():
            query_parts.append(str(value))
        query = " ".join(query_parts).strip()
        logger.info(f"Constructed Query String: {query}")

        # Prepare query parameters
        headers = {
            "x-rapidapi-key": settings.RAPIDAPI_KEY,  # Securely fetch API key from settings
            "x-rapidapi-host": "real-time-amazon-data.p.rapidapi.com"
        }
        url = "https://real-time-amazon-data.p.rapidapi.com/search"

        all_products = []
        current_page = 1
        max_pages = 3  # Set a reasonable limit to prevent excessive API calls
        while current_page <= max_pages:
            logger.info(f"Fetching page {current_page}...")

            query_params = {
                "query": query,
                "page": str(current_page),
                "country": "IN",
                "sort_by": "RELEVANCE",
                "product_condition": "ALL",
                "is_prime": "false",
                "deals_and_discounts": "NONE"
            }

            # Make the API call
            try:
                response = requests.get(url, headers=headers, params=query_params, timeout=10)
                logger.info(f"API Response Status: {response.status_code}")

                if response.status_code == 200:
                    page_data = response.json().get("data", {}).get("products", [])
                    if not page_data:
                        logger.info("No more products found.")
                        break  # Stop if no products are found on the current page

                    all_products.extend(page_data)
                    current_page += 1
                else:
                    logger.error(f"Failed to fetch products on page {current_page}: {response.text}")
                    break  # Exit on API error
            except requests.RequestException as e:
                logger.error(f"Request failed for page {current_page}: {str(e)}")
                return {"error": f"Failed to fetch products: {str(e)}"}

        if not all_products:
            logger.warning("No products found for the given query.")
            return {"error": "No products found for the given query."}

        logger.info(f"Total products fetched: {len(all_products)}")
        return {"products": all_products}

    except Exception as e:
        logger.error(f"Unexpected error in fetch_products: {str(e)}")
        return {"error": f"Unexpected error in fetch_products: {str(e)}"}


# (=================DONE==================)
# @api_view(['POST'])
# @permission_classes([AllowAny])  # Allow open access
def is_product_related(query):
    """
    Check if the user's query or the generated response is related to e-commerce products.
    """
    product_keywords = [
        # General e-commerce terms
        "buy", "purchase", "price", "recommend", "review", "product", "discount",
        "ecommerce", "available on", "category", "deal", "offers", "sale", "bestseller",
        "cheap", "expensive", "affordable", "budget", "premium", "shopping", "order", "suggest",
        "cart", "checkout", "payment", "refund", "return", "exchange",

        # Electronics and gadgets
        "electronics", "smartphone", "laptop", "tablet", "desktop", "computer", "monitor",
        "headphones", "earbuds", "speakers", "camera", "dslr", "gaming", "console", "router",
        "charger", "cables", "mouse", "keyboard", "smartwatch", "wearable", "TV", "television",
        "projector", "hard drive", "SSD", "storage", "power bank", "printer", "scanner",
        "home theater", "bluetooth",
        "smartphone accessories", "screen protectors", "phone cases", "pop sockets",
        "car phone holders", "wireless chargers", "fast chargers", "charging cables",
        "USB-C cables", "lightning cables", "micro USB cables", "portable chargers",
        "solar power banks", "laptop accessories", "laptop bags", "laptop sleeves",
        "cooling pads", "external GPUs", "tablet stands", "stylus pens", "keyboard covers",
        "mouse pads", "gaming laptops", "gaming desktops", "gaming monitors",
        "gaming headsets", "gaming keyboards", "mechanical keyboards", "gaming mice",
        "RGB lighting accessories", "VR headsets", "virtual reality accessories",
        "console controllers", "console stands", "console skins", "PS5 accessories",
        "Xbox accessories", "Nintendo Switch accessories", "joysticks", "gaming chairs",
        "gaming desks", "PC components", "graphic cards", "motherboards", "processors",
        "RAM", "cooling fans", "CPU coolers", "power supplies", "cabinets",
        "webcams", "microphones", "ring lights", "studio lights", "action cameras",
        "GoPro accessories", "tripods", "camera lenses", "camera bags",
        "memory cards", "SD cards", "microSD cards", "card readers", "flash drives",
        "external hard drives", "portable SSDs", "network storage devices",
        "Wi-Fi routers", "mesh Wi-Fi systems", "range extenders", "modems",
        "internet dongles", "home automation devices", "smart plugs", "smart bulbs",
        "smart home hubs", "smart locks", "video doorbells", "security cameras",
        "baby monitors", "smart thermostats", "smart sensors", "robot vacuums",
        "wireless headphones", "noise-cancelling headphones", "over-ear headphones",
        "in-ear headphones", "true wireless earbuds", "Bluetooth speakers",
        "soundbars", "subwoofers", "portable speakers", "multi-room audio systems",
        "car speakers", "amplifiers", "record players", "home entertainment systems",
        "smart TVs", "4K TVs", "OLED TVs", "QLED TVs", "projector screens",
        "mini projectors", "pocket projectors", "AV receivers", "universal remotes",
        "printer ink", "printer cartridges", "3D printers", "3D printer filaments",
        "scanners", "document scanners", "barcode scanners", "label printers",
        "fax machines", "office electronics", "calculators", "graphic calculators",
        "portable monitors", "USB hubs", "docking stations", "data cables",
        "power strips", "surge protectors", "UPS", "voltage stabilizers",
        "home audio systems", "Bluetooth transmitters", "FM transmitters",
        "streaming devices", "Chromecast", "Fire TV Stick", "Roku",
        "satellite receivers", "set-top boxes", "digital antennas",
        "e-readers", "Kindle", "digital notepads", "fitness trackers",
        "smart glasses", "hearing aids", "portable DVD players",
        "electronic musical instruments", "keyboards", "electric guitars",
        "midi controllers", "audio interfaces", "DJ controllers", "mixers",
        "studio monitors", "podcast equipment", "soundproofing panels",
        "wearable tech", "health trackers", "sleep trackers",
        "portable fans", "portable air conditioners", "electric heaters",
        "personal humidifiers", "smart alarms", "digital clocks",
        "electronic toys", "drones", "drone accessories", "action drones",
        "dash cams", "car electronics", "car chargers", "car cameras",
        "car GPS devices", "radar detectors", "vehicle tracking devices",
        "portable generators", "solar panels", "portable power stations",
        "electric scooters", "electric bikes", "hoverboards", "electric skateboards",
        "walkie-talkies", "portable radios", "weather radios",
        "scientific calculators", "graphing calculators", "digital scales",
        "kitchen scales", "postal scales", "handheld scanners", "barcode readers",

        # Clothing and fashion
        "clothing", "shoes", "fashion", "accessories", "jewelry", "watches", "sunglasses",
        "t-shirt", "shirt", "jeans", "jacket", "coat", "sweater", "hoodie", "sneakers",
        "heels", "boots", "sandals", "formal wear", "casual wear", "activewear", "sportswear",
        "swimwear", "dresses", "skirts", "suits", "hats", "belts", "scarves", "gloves",
        "bags", "handbags", "backpacks", "wallets", "clothes",
        "blouses", "tops", "trousers", "pants", "shorts", "leggings", "capris",
        "tunic", "cardigans", "blazers", "vests", "trench coats", "overcoats",
        "raincoats", "windbreakers", "parkas", "puffer jackets", "leather jackets",
        "denim jackets", "sports bras", "bras", "underwear", "lingerie", "boxers",
        "briefs", "panties", "camisoles", "slips", "shapewear", "stockings",
        "tights", "kurtas", "kurtis", "ethnic wear", "sarees", "lehenga choli",
        "salwar kameez", "sherwanis", "dhoti", "kurta pajama", "indian wear",
        "abaya", "hijabs", "kaftans", "polo shirts", "graphic tees", "crop tops",
        "tank tops", "tube tops", "sweatpants", "tracksuits", "gym wear",
        "jumpsuits", "rompers", "co-ord sets", "nightwear", "sleepwear", "pyjamas",
        "loungewear", "robes", "bathrobes", "thermal wear", "maternity wear",
        "baby clothes", "kids clothing", "school uniforms", "party wear",
        "ball gowns", "cocktail dresses", "evening dresses", "workwear",
        "office wear", "formal suits", "wedding dresses", "bridal wear",
        "cummerbunds", "neckties", "bow ties", "pocket squares", "cufflinks",
        "bracelets", "necklaces", "earrings", "rings", "anklets", "brooches",
        "pendants", "charms", "lockets", "chains", "hair accessories", "hairbands",
        "headbands", "scrunchies", "clips", "beanies", "caps", "berets", "fedora",
        "stoles", "wraps", "shawls", "mufflers", "work boots", "rain boots",
        "flip-flops", "loafers", "oxfords", "derby shoes", "brogues", "moccasins",
        "slip-ons", "ballet flats", "platform shoes", "wedges", "clogs",
        "espadrilles", "running shoes", "training shoes", "court shoes",
        "climbing shoes", "hiking boots", "snow boots", "chukka boots",
        "chelsea boots", "riding boots", "saddle bags", "tote bags", "clutches",
        "crossbody bags", "duffel bags", "luggage bags", "messenger bags",
        "laptop bags", "gym bags", "travel pouches", "waist bags", "cosmetic bags",
        "makeup bags", "diaper bags", "school bags", "suitcases", "trunks",
        "garment bags", "workwear aprons", "fashion aprons", "holiday sweaters",
        "theme-based costumes", "seasonal clothing", "beachwear", "cover-ups",
        "sun hats", "visor hats", "fedora hats", "cowboy hats", "bucket hats",
        "ankle socks", "crew socks", "knee-high socks", "compression socks",
        "no-show socks", "slipper socks", "baby booties", "designer wear",
        "tailored suits", "custom fit shirts", "luxury clothing",

        # Home and kitchen
        "appliances", "furniture", "kitchen", "microwave", "oven", "toaster", "blender",
        "refrigerator", "washing machine", "dishwasher", "vacuum", "air purifier", "heater",
        "cooler", "coffee maker", "cookware", "utensils", "cutlery", "dining table", "chairs",
        "sofa", "bed", "mattress", "wardrobe", "lighting", "lamp", "curtains", "carpet",
        "decor", "shelving", "storage",

        # Beauty and personal care
        "beauty", "skincare", "makeup", "lipstick", "foundation", "mascara", "eyeliner",
        "hair care", "shampoo", "conditioner", "hair dryer", "straightener", "trimmer",
        "razor", "perfume", "fragrance", "soap", "body wash", "moisturizer", "sunscreen",
        "nail polish", "bath accessories",
        "lip balm", "lip gloss", "lip liner", "face primer", "concealer", "bb cream",
        "cc cream", "highlighter", "blush", "bronzer", "contour kit", "setting spray",
        "setting powder", "eyebrow pencil", "eyebrow gel", "eyeshadow palette",
        "false eyelashes", "eyelash glue", "makeup brushes", "beauty blender",
        "makeup remover", "micellar water", "cleansing balm", "face wash",
        "face scrub", "exfoliator", "face mask", "sheet mask", "peel-off mask",
        "clay mask", "toner", "serum", "face oil", "facial mist", "anti-aging cream",
        "eye cream", "eye serum", "dark circle corrector", "acne treatment",
        "pimple patches", "spot treatment", "whitening cream", "brightening serum",
        "blemish remover", "blackhead remover", "pore minimizer", "body scrub",
        "body lotion", "body butter", "body oil", "hand cream", "foot cream",
        "foot scrub", "deodorant", "antiperspirant", "body mist", "bath salts",
        "bath bombs", "bubble bath", "loofah", "bath sponge", "exfoliating gloves",
        "pedicure kit", "manicure kit", "nail art supplies", "nail glue",
        "nail polish remover", "cuticle oil", "cuticle remover", "cuticle pusher",
        "hair oil", "hair serum", "heat protectant spray", "hair mousse",
        "hair spray", "dry shampoo", "hair mask", "leave-in conditioner",
        "hair color", "hair dye", "temporary hair color", "hair extensions",
        "hair clips", "hair accessories", "hair brushes", "hair combs",
        "hair bands", "scrunchies", "hair pins", "bobby pins", "hair rollers",
        "curling iron", "hot air brush", "beard trimmer", "beard oil",
        "aftershave lotion", "shaving cream", "shaving gel", "electric shaver",
        "epilator", "wax strips", "wax heater", "threading tool",
        "tweezers", "facial razors", "blackhead extractor", "skin tag remover",
        "electric facial cleanser", "skin rejuvenation device", "jade roller",
        "gua sha", "dermaroller", "light therapy mask", "body slimming belt",
        "massager", "handheld massager", "scalp massager", "foot massager",
        "steamers", "facial steamer", "sauna blanket", "toothpaste", "toothbrush",
        "electric toothbrush", "mouthwash", "teeth whitening strips",
        "teeth whitening kit", "dental floss", "tongue cleaner", "oral care kit",
        "contact lens solution", "eye drops", "kajal", "hair removal cream",
        "talcum powder", "body powder", "face powder", "compact powder",
        "perfume gift sets", "makeup organizer", "travel beauty kits",
        "skincare travel kits", "mirror with light", "vanity mirror",
        "cosmetic bag", "toiletry bag", "personal care tools", "beauty gadgets",

        # Sports and outdoors
        "sports", "outdoors", "fitness", "gym equipment", "dumbbells", "treadmill",
        "bicycle", "mountain bike", "road bike", "electric bike", "helmet", "cycling gloves",
        "elbow guard", "knee guard", "tent", "backpacking", "hiking", "trekking poles",
        "camping", "camping stove", "sleeping bag", "camping chair", "camping table",
        "yoga mat", "water bottle", "hydration pack", "exercise band", "resistance bands",
        "protein", "whey protein", "vegan protein", "protein bars", "supplements",
        "multivitamins", "fish oil", "creatine", "bcaa", "sports shoes", "running shoes",
        "trail running shoes", "soccer ball", "basketball", "football", "tennis racket",
        "badminton racket", "shuttlecock", "cricket bat", "cricket ball", "stumps",
        "hockey stick", "golf clubs", "golf balls", "golf bag", "volleyball", "volleyball net",
        "table tennis paddle", "table tennis balls", "ping pong table", "baseball bat",
        "baseball gloves", "softball", "lacrosse stick", "lacrosse balls", "skateboard",
        "roller skates", "ice skates", "skiing equipment", "snowboarding equipment",
        "paddleboard", "kayak", "canoe", "life jacket", "swimming goggles", "swimming cap",
        "snorkeling gear", "diving equipment", "surfboard", "bodyboard", "water shoes",
        "fishing rod", "fishing reel", "fishing tackle", "bait", "fishing net",
        "hunting gear", "archery bow", "arrows", "crossbow", "paintball gun", "airsoft gun",
        "binoculars", "compass", "portable flashlight", "headlamp", "rock climbing gear",
        "carabiners", "climbing harness", "chalk bag", "pulleys", "ski poles", "snowshoes",
        "sled", "pedometer", "fitness tracker", "smartwatch", "heart rate monitor",
        "gym gloves", "weightlifting belt", "pull-up bar", "home gym system", "kettlebells",
        "medicine ball", "ab roller", "rowing machine", "stationary bike", "elliptical trainer",
        "boxing gloves", "punching bag", "hand wraps", "mma gloves", "kickboxing pads",
        "trampoline", "balance board", "exercise ball", "foam roller", "stretching strap",
        "jump rope", "parachute training gear", "agility ladder", "cones", "speed hurdles",
        "gymnastics mat", "gym rings", "parallel bars", "climbing rope", "slackline",
        "parkour equipment", "obstacle course equipment", "martial arts uniforms", "karate gi",
        "judo gi", "taekwondo gear", "fencing gear", "squash racket", "squash ball",
        "racquetball racket", "racquetball balls", "paddle tennis racket", "pickleball paddle",
        "pickleball balls", "cornhole set", "darts", "dartboard", "bocce ball", "horseshoes",
        "frisbee", "ultimate frisbee", "disk golf", "campfire accessories", "portable grill",
        "portable cooler", "hammock", "tactical gear", "camouflage gear", "outdoor knives",
        "multipurpose tools", "self-defense gear",

        # Baby and kids
        "baby", "kids", "toys", "stroller", "diapers", "feeding bottle", "cradle",
        "baby clothes", "stuffed toys", "board games", "puzzle",
        "stationery", "school bag", "lunch box",
        "baby monitor", "pacifier",

        # Books and media
        "books", "novels", "book", "ebook", "ebooks", "textbooks", "magazines", "comics", "music",
        "instruments", "guitar", "piano", "violin", "drums", "microphone", "headset",
        "audiobooks", "media", "CD", "DVD", "blu-ray",
        "fiction books", "non-fiction books", "self-help books", "motivational books",
        "mystery novels", "thriller books", "romance novels", "historical fiction",
        "sci-fi books", "fantasy books", "children's books", "young adult books",
        "educational books", "workbooks", "activity books", "reference books",
        "cookbooks", "recipe books", "travel guides", "biographies", "autobiographies",
        "graphic novels", "manga", "art books", "photography books", "coffee table books",
        "poetry books", "religious books", "spiritual books", "law books",
        "medical textbooks", "engineering textbooks", "business books", "investment guides",
        "programming books", "technology books", "ebooks readers", "Kindle devices",
        "audiobook subscriptions", "podcasts", "online courses",
        "music CDs", "movie DVDs", "series box sets", "live concert blu-rays",
        "karaoke microphones", "keyboard instruments", "acoustic guitars", "electric guitars",
        "bass guitars", "ukuleles", "harmonicas", "flutes", "saxophones", "trumpets",
        "drum sets", "cajon drums", "percussion instruments", "digital pianos",
        "music stands", "sheet music", "guitar picks", "instrument cases",
        "headphones for music", "recording microphones", "home studio equipment",
        "vinyl records", "record players", "media streaming devices",
        "music streaming subscriptions", "sound systems", "home theater speakers",
        "projectors for media", "audio mixing boards", "DJ equipment",

        # Automotive
        "car", "bike", "automotive", "tyres", "car accessories", "motorcycle",
        "helmets", "bike locks", "car seats", "dashboard camera", "gps", "battery",
        "oil", "tools", "repair kit",

        # Miscellaneous
        "gadgets", "pets", "pet food", "collar", "leash", "toys for pets", "bedding",
        "travel accessories", "luggage", "power tools", "tool kit", "garden", "plants",
        "seeds", "fertilizer", "planter", "art supplies", "craft materials",

        # Brand names
        # International Brands
        "nike", "adidas", "apple", "samsung", "sony", "microsoft", "dell", "hp", "lenovo",
        "asus", "lg", "panasonic", "canon", "nikon", "bose", "jbl", "philips", "levi's",
        "gucci", "prada", "chanel", "louis vuitton", "puma", "under armour", "reebok",
        "zara", "h&m", "forever 21", "tesla", "ferrari", "lamborghini", "rolex", "omega",
        "netflix", "amazon", "ikea", "coca-cola", "pepsi", "starbucks", "nestle",
        "google", "youtube", "facebook", "instagram", "twitter", "ford", "chevrolet",
        "honda", "toyota", "hyundai", "kia", "jaguar", "volvo", "vans", "timberland",
        "converse", "columbia", "the north face", "patagonia", "iphone",

        # Indian Brands
        "tata", "mahindra", "bajaj", "hero motocorp", "reliance", "infosys", "wipro",
        "godrej", "amul", "dabur", "parle", "britannia", "asian paints", "himalaya",
        "vicco", "bajaj electricals", "blue star", "voltas", "vip industries", "raymond",
        "aditya birla group", "hindustan unilever", "itc", "marico", "patanjali", "tvs",
        "apollo tyres", "mrf", "jk tyres", "ceat", "bata india", "woodland", "fabindia",
        "biba", "manyavar", "wildcraft", "lenskart", "zomato", "swiggy", "paytm",
        "flipkart", "ola", "byju's", "oyo", "urban clap", "bigbasket", "nykaa",
        "myntra", "ajio", "snapdeal", "shopclues", "pepperfry", "firstcry", "pharmeasy",
        "medlife", "1mg", "policybazaar", "makemytrip", "yatra", "cleartrip", "ixigo",
        "redbus", "bookmyshow", "justdial", "hdfc bank", "icici bank", "axis bank",
        "state bank of india", "bank of baroda", "punjab national bank", "canara bank",
        "indusind bank", "kotak mahindra bank", "yes bank", "idfc first bank", "rbl bank",
        "federal bank", "south indian bank", "karur vysya bank", "city union bank",
        "lakshmi vilas bank", "dcb bank", "bandhan bank", "au small finance bank",
        "equitas small finance bank", "ujjivan small finance bank", "suryoday small finance bank",
        "janalakshmi financial services", "capital small finance bank", "esaf small finance bank",
        "fincare small finance bank", "north east small finance bank", "utkarsh small finance bank",
        "shivalik small finance bank", "unity small finance bank", "paytm payments bank",
        "airtel payments bank", "jio payments bank", "nsdl payments bank", "fino payments bank",
        "india post payments bank", "aditya birla payments bank", "vodafone m-pesa",
        "idea payments bank", "bharat billpay", "bhim", "upi", "rupay", "imps", "neft",
        "rtgs", "aeps", "nfs", "cts", "nach", "apbs", "bbps", "bharat qr", "upi 2.0",

        # Famous People (Biographies or Books)
        # International figures
        "albert einstein", "isaac newton", "mahatma gandhi", "martin luther king jr.",
        "abraham lincoln", "nelson mandela", "steve jobs", "elon musk", "marie curie",
        "leonardo da vinci", "galileo galilei", "ludwig van beethoven", "wolfgang amadeus mozart",
        "william shakespeare", "j.k. rowling", "george orwell", "barack obama",
        "michelle obama", "winston churchill", "charles darwin", "sigmund freud",
        "aristotle", "plato", "cleopatra", "christopher columbus", "nikola tesla",
        "marie antoinette", "queen elizabeth ii", "albert camus", "mark twain",
        "benjamin franklin", "theodore roosevelt", "amelia earhart", "rosa parks",
        "anne frank", "vincent van gogh", "pablo picasso", "jane austen", "ernest hemingway",
        "alexander hamilton", "franklin d. roosevelt", "malala yousafzai", "greta thunberg",
        "elon musk", "thomas jefferson", "john f. kennedy", "ronald reagan", "margaret thatcher",
        "joan of arc", "george washington", "napoleon bonaparte", "walt disney", "oprah winfrey",
        "jeff bezos", "bill gates", "andrew carnegie", "henry ford", "marilyn monroe",
        "frida kahlo", "andy warhol", "jackie robinson", "babe ruth", "muhammad ali",
        "michael jordan", "kobe bryant", "serena williams", "roger federer", "cristiano ronaldo",
        "lionel messi", "usain bolt", "neil armstrong", "sally ride", "stephen hawking",
        "alan turing", "ada lovelace", "grace hopper", "james watt", "alexander graham bell",
        "thomas edison", "mark zuckerberg", "malcolm x", "harriet tubman", "frederick douglass",
        "mother teresa", "oscar wilde", "virginia woolf", "victor hugo", "leo tolstoy",
        "maya angelou", "audrey hepburn", "charlie chaplin", "diana, princess of wales",

        # Indian figures
        "mahatma gandhi", "jawaharlal nehru", "sardar vallabhbhai patel", "subhas chandra bose",
        "bhagat singh", "dr. b.r. ambedkar", "sarvepalli radhakrishnan", "apj abdul kalam",
        "indira gandhi", "lal bahadur shastri", "rajiv gandhi", "narendra modi",
        "amitabh bachchan", "lata mangeshkar", "m.s. subbulakshmi", "ratan tata",
        "j.r.d. tata", "dhirubhai ambani", "mukesh ambani", "narayana murthy",
        "azim premji", "vikram sarabhai", "homi bhabha", "satya nadella", "sundar pichai",
        "kalpana chawla", "pv sindhu", "mary kom", "virat kohli", "ms dhoni", "sachin tendulkar",
        "rahul dravid", "kapil dev", "abhinav bindra", "viswanathan anand", "amitav ghosh",
        "arundhati roy", "salman rushdie", "rabindranath tagore", "swami vivekananda",
        "ramakrishna paramahamsa", "chanakya", "guru nanak", "shirdi sai baba",
        "sri aurobindo", "rabindra nath tagore", "field marshal sam manekshaw",
        "ravi shankar", "zakir hussain", "pandit bhimsen joshi", "uday shankar",
        "mf husain", "satyajit ray", "mother teresa", "dr. verghese kurien",
        "kiran bedi", "arvind kejriwal", "anna hazare", "medha patkar", "jayaprakash narayan",

        # Popular Series and Media Franchises
        "harry potter", "game of thrones", "lord of the rings", "star wars",
        "marvel", "dc comics", "frozen", "avatar", "stranger things", "the witcher",
        "breaking bad", "friends", "the office", "sherlock holmes", "percy jackson",
        "the hunger games", "twilight", "fifty shades of grey", "the chronicles of narnia",

        # Additional popular brands available on Amazon
        "amazon basics", "solimo", "happy belly", "mountain falls", "buttoned down",
        "wickedly prime", "goodthreads", "simple joys by carter's", "daily ritual",
        "presto!", "mama bear", "amazon essentials", "the drop", "core 10",
        "hanes", "champion", "gildan", "fruit of the loom", "carhartt", "columbia",
        "disney", "lego", "cuisinart", "oxford", "samsung", "apple", "sony", "hp",
        "microsoft", "asus", "nintendo", "anker", "sandisk", "logitech", "fitbit",
        "garmin", "bose", "jbl", "beats", "dyson", "kitchenaid", "instant pot",
        "ninja", "keurig", "philips", "oral-b", "gillette", "neutrogena", "l'oreal",
        "maybelline", "nyx", "e.l.f.", "olay", "pantene", "tresemmé", "dove",
        "aveeno", "cerave", "la roche-posay", "vichy", "cosrx", "the ordinary",
        "paula's choice", "sunday riley", "tatcha", "drunk elephant", "laneige",
        "olaplex", "moroccanoil", "shea moisture", "burt's bees", "aquaphor",
        "vaseline", "nivea", "eucerin", "cetaphil", "jergens", "aveeno baby",
        "johnson's baby", "pampers", "huggies", "luv's", "gerber", "enfamil",
        "similac", "babyganics", "earth's best", "honest company", "seventh generation",
        "mrs. meyer's", "method", "lysol", "clorox", "tide", "gain", "arm & hammer",
        "persil", "all", "downy", "bounce", "snuggle", "scotch-brite", "swiffer",
        "bissell", "shark", "eureka", "hoover", "dyson", "roomba", "neato",
        "ecovacs", "eufy", "ihealth", "omron", "withings", "fitbit", "garmin",
        "apple watch", "samsung galaxy watch", "fossil", "timex", "casio", "seiko",
        "citizen", "bulova", "movado", "tissot", "tag heuer", "rolex", "omega",
        "breitling", "panerai", "cartier", "patek philippe", "audemars piguet",
        "vacheron constantin", "jaeger-lecoultre", "iwc", "hublot", "zenith",
        "blancpain", "breguet", "glashütte original", "lange & söhne", "ulysse nardin",
        "girard-perregaux", "piaget", "franck muller", "richard mille", "roger dubuis",
        "parmigiani fleurier", "greubel forsey", "laurent ferrier", "mb&f",
        "urwerk", "de bethune", "f.p. journe", "h. moser & cie.", "a. lange & söhne",
        "voutilainen", "philippe dufour", "george daniels", "daniel roth",
        "gerald genta", "jacob & co.", "chopard", "bovet", "breguet", "blancpain",
        "jaquet droz", "harry winston", "van cleef & arpels", "audemars piguet",
        "patek philippe", "vacheron constantin", "jaeger-lecoultre",

        # Other Relevant Keywords
        "new arrivals", "best sellers", "popular items", "limited edition", "discounted",
        "latest trends", "trending", "highly rated", "customer favorites", "exclusive deals",

        # Programming language
        "python", "java", "javascript", "react",
        "c", "c++", "ruby", "swift", "go", "rust",
        "typescript", "kotlin", "scala", "php", "perl",
        "html", "css", "sql", "ruby on rails", "dart",
        "lua", "shell scripting", "matlab", "r",
        "haskell", "clojure", "elixir", "f#",
        "vhdl", "fortran", "assembly", "objective-c",
        "powershell", "graphql", "flutter", "ai", "artificial intelligence",
        "machine learning", "ml", "deep learning", "data science",
        "blockchain", "robotics", "robots"
    ]

    # Check if any of the keywords appear in the query or response
    query_lower = query.lower()
    # response_lower = response.lower()
    for keyword in product_keywords:
        if keyword in query_lower:
            return True

    return False



# ====================================================================================================

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from openai import OpenAI
import openai  # For exception handling


# (=================DONE==================)
@api_view(['POST'])
@permission_classes([AllowAny])
def generate_response_view_main(request):
    user_query = request.data.get('query', '').strip()

    # Validate the presence of the query
    if not user_query:
        logger.warning("Empty query received.")
        return Response({"error": "Query cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)

    api_key = settings.OPENAI_API_KEY
    if not api_key:
        logger.error("OpenAI API key is missing.")
        return Response(
            {"error": "OpenAI API key is not configured. Please contact support."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    try:
        client = OpenAI(api_key=api_key)
        logger.info(f"OpenAI client initialized successfully for query: {user_query}")

    except openai.AuthenticationError:
        return Response(
            {"error": "Authentication with the OpenAI API failed. Check the API key."},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    except Exception as e:
        return Response(
            {"error": f"Unexpected error while initializing OpenAI client: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    try:
        # Step 1: Generate a response using OpenAI
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_query}
            ],
            temperature=0.7
        )
        generated_response = completion.choices[0].message.content
        logger.info(f"Generated response: {generated_response}")

        # Return the generated response immediately
        return Response({
            "response": generated_response,
            "status": "partial",
            "message": "Response generated. You can now fetch features and products."
        }, status=status.HTTP_200_OK)

    except openai.AuthenticationError:
        logger.error("Authentication with the OpenAI API failed.")
        return Response(
            {"error": "Authentication with the OpenAI API failed. Check the API key."},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    except openai.RateLimitError:
        logger.error("Rate limit exceeded for the OpenAI API.")
        return Response(
            {"error": "Rate limit exceeded for the OpenAI API. Please try again later."},
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )
    except openai.APIError as e:
        logger.error(f"OpenAI API error: {str(e)}")
        return Response(
            {"error": f"An error occurred with the OpenAI API: {str(e)}"},
            status=status.HTTP_502_BAD_GATEWAY,
        )
    except openai.OpenAIError as e:
        logger.error(f"Unexpected OpenAI API error: {str(e)}")
        return Response(
            {"error": f"Unexpected OpenAI API error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return Response(
            {"error": f"Unexpected error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# (=================DONE==================)
@api_view(['POST'])
@permission_classes([AllowAny])
def fetch_features_and_products_view(request):
    """
    Fetch product features from a query and relevant products based on the extracted features.
    """
    # Fetch the query directly from the request body
    user_query = request.data.get('query', '').strip()

    if not user_query:
        logger.warning("No query provided.")
        return Response({"error": "No query provided. Please provide a query."}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the query is product-related
    if not is_product_related(user_query):
        logger.info("Query is not product-related.")
        return Response({
            "response": "The query is not product-related. No features or products can be extracted.",
            "extracted_features": None,
            "products": None
        }, status=status.HTTP_200_OK)

    # Initialize OpenAI client
    api_key = settings.OPENAI_API_KEY
    if not api_key:
        logger.error("OpenAI API key is missing.")
        return Response(
            {"error": "OpenAI API key is not configured. Please contact support."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    try:
        client = OpenAI(api_key=api_key)
        logger.info("OpenAI client initialized successfully.")
    except openai.AuthenticationError:
        return Response(
            {"error": "Authentication failed. Please check your API key."},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    except Exception as e:
        return Response(
            {"error": f"Unexpected error while initializing OpenAI client: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Step 2: Extract features using GPT-4
    feature_extraction_prompt = f"""
        You are an advanced AI assistant specializing in extracting and structuring product features for e-commerce applications. 
        Your task is to analyze the provided input description and extract all explicitly mentioned features. Additionally:

        1. If the input is very short (e.g., single words like "iPhone" or "Nike"), infer relevant features based on your knowledge 
           of common product attributes for such queries.
        2. If the input mentions a famous person (e.g., Einstein, Newton, Mahatma Gandhi), infer that the product is likely a book 
           or biography about that person and include relevant attributes such as category ("Books"), title, and related topics.
        3. Always ensure the extracted features are relevant and presented in a well-structured JSON format.
        
        VERY VERY IMPORTANT:-
         Never describe about the user's query only give the well-structured JSON format of the user query.

        Input Description:
        {user_query}

        Example Outputs:
        - Input: "Nike shoes"
          Output:
          {{
              "product_category": "shoes",
              "brand": "Nike",
              "type": "sports shoes",
              "features": ["durable", "lightweight", "stylish"]
          }}

        - Input: "Einstein"
          Output:
          {{
              "product_category": "Books",
              "title": "Biography of Albert Einstein",
              "type": "biography",
              "related_topics": ["physics", "relativity", "scientific contributions"]
          }}

        - Input: "Recommend a good book on physics"
          Output:
          {{
              "product_category": "Books",
              "title": "Physics Fundamentals",
              "type": "educational",
              "topics": ["physics", "mechanics", "thermodynamics"]
          }}

        - Input: "Camera"
          Output:
          {{
              "product_category": "electronics",
              "type": "digital camera",
              "features": ["high resolution", "optical zoom", "lightweight", "compact"]
          }}

          if query contains more than 1 values for same key then extract those features like the below given example

          Example Outputs:
        - Input: "Nike and adidas shoes"
          Output:
          {{
              "product_category": "shoes",
              "brand": ["Nike", "adidas"],
              "type": "sports shoes",
              "features": ["durable", "lightweight", "stylish"]
          }}

        Analyze the input and provide a structured JSON response.
    """

    try:
        # Step 2: Extract features using GPT-4
        feature_extraction_response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": feature_extraction_prompt}]
        )
        raw_features = feature_extraction_response.choices[0].message.content.strip()
        logger.info(f"Extracted features (raw): {raw_features}")

        # Validate and parse extracted features
        try:
            extracted_features = json.loads(raw_features)
            logger.info(f"Extracted features (parsed): {extracted_features}")
        except json.JSONDecodeError:
            logger.error("Failed to parse extracted features as JSON.")
            return Response(
                {"error": "Failed to parse the extracted features as valid JSON. Please refine your input or try again."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        # Step 3: Fetch products based on extracted features
        try:
            products_response = fetch_products(extracted_features)
            logger.info(f"Fetched products: {products_response}")
        except Exception as e:
            logger.error(f"Error while fetching products: {str(e)}")
            return Response(
                {"error": f"Product fetching failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Validate product response structure
        if not isinstance(products_response, dict) or "products" not in products_response:
            return Response(
                {"error": "Invalid response from product fetching. Please try again later."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # Return extracted features and products
        return Response({
            "response": "Product-related query processed successfully.",
            "extracted_features": extracted_features,
            "products": products_response.get("products", []),
            "status": "complete"
        }, status=status.HTTP_200_OK)

    except openai.RateLimitError:
        logger.error("Rate limit exceeded for the OpenAI API.")
        return Response(
            {"error": "Rate limit exceeded. Please try again later."},
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )
    except openai.APIError as e:
        logger.error(f"OpenAI API error: {str(e)}")
        return Response(
            {"error": f"OpenAI API error: {str(e)}"},
            status=status.HTTP_502_BAD_GATEWAY,
        )
    except openai.OpenAIError as e:
        logger.error(f"Unexpected OpenAI API error: {str(e)}")
        return Response(
            {"error": f"Unexpected OpenAI API error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except Exception as e:
        logger.error(f"Unexpected error occurred: {str(e)}")
        return Response(
            {"error": f"An unexpected error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
