# services/packing.py
import ollama
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from typing import Dict, Any
import re

# Initialize the embedder and index (these will be loaded once when the service starts)
embedder = SentenceTransformer('all-MiniLM-L6-v2')

# Define your corpus of documents (same as in your packing.py)
documents = [
    # Beach Destinations
    "For a beach trip with hot weather and good air quality, pack: sunscreen, swimsuit, sunglasses, hat, beach towel, flip-flops, reusable water bottle, waterproof phone case.",
    "For a beach trip with hot weather and moderate air quality, pack: sunscreen, swimsuit, sunglasses, hat, beach towel, flip-flops, reusable water bottle, N95 mask (for dust).",
    "For a beach trip with hot weather and unhealthy air quality, pack: sunscreen, swimsuit, sunglasses, hat, beach towel, flip-flops, reusable water bottle, N95 mask (for smoke/dust), portable air purifier.",
    "For a beach trip with mild weather and good air quality, pack: light jacket, swimsuit, sunscreen, sunglasses, beach towel, sneakers, reusable water bottle.",
    "For a beach trip with mild weather and moderate air quality, pack: light jacket, swimsuit, sunscreen, sunglasses, beach towel, sneakers, reusable water bottle, N95 mask (for pollen).",
    "For a beach trip with mild weather and unhealthy air quality, pack: light jacket, swimsuit, sunscreen, sunglasses, beach towel, sneakers, reusable water bottle, N95 mask (for pollution), portable air purifier.",
    "For a beach trip with cold weather and good air quality, pack: warm jacket, swimsuit (for hot springs), sunscreen, beanie, gloves, thermal socks, reusable water bottle.",
    "For a beach trip with cold weather and moderate air quality, pack: warm jacket, swimsuit (for hot springs), sunscreen, beanie, gloves, thermal socks, reusable water bottle, N95 mask (for windborne dust).",
    "For a beach trip with cold weather and unhealthy air quality, pack: warm jacket, swimsuit (for hot springs), sunscreen, beanie, gloves, thermal socks, reusable water bottle, N95 mask (for pollution), portable air purifier.",

    # City Destinations
    "For a city trip with hot weather and good air quality, pack: light clothing, comfortable walking shoes, sunglasses, hat, reusable water bottle, portable fan, power bank.",
    "For a city trip with hot weather and moderate air quality, pack: light clothing, comfortable walking shoes, sunglasses, hat, reusable water bottle, N95 mask (for traffic fumes), portable fan.",
    "For a city trip with hot weather and unhealthy air quality, pack: light clothing, comfortable walking shoes, sunglasses, hat, reusable water bottle, N95 mask (for smog), portable air purifier, electrolyte tablets.",
    "For a city trip with mild weather and good air quality, pack: light layers, comfortable walking shoes, compact umbrella, reusable water bottle, power bank, city guidebook.",
    "For a city trip with mild weather and moderate air quality, pack: light layers, comfortable walking shoes, compact umbrella, reusable water bottle, N95 mask (for pollen), power bank.",
    "For a city trip with mild weather and unhealthy air quality, pack: light layers, comfortable walking shoes, compact umbrella, reusable water bottle, N95 mask (for pollution), portable air purifier.",
    "For a city trip with cold weather and good air quality, pack: warm coat, thermal layers, gloves, beanie, waterproof boots, reusable water bottle, hand warmers.",
    "For a city trip with cold weather and moderate air quality, pack: warm coat, thermal layers, gloves, beanie, waterproof boots, reusable water bottle, N95 mask (for cold-induced smog).",
    "For a city trip with cold weather and unhealthy air quality, pack: warm coat, thermal layers, gloves, beanie, waterproof boots, reusable water bottle, N95 mask (for pollution), portable air purifier.",

    # Mountain/Hiking Destinations
    "For a mountain trip with hot weather and good air quality, pack: hiking boots, moisture-wicking clothes, wide-brim hat, sunscreen, trekking poles, hydration bladder, insect repellent.",
    "For a mountain trip with hot weather and moderate air quality, pack: hiking boots, moisture-wicking clothes, wide-brim hat, sunscreen, trekking poles, hydration bladder, N95 mask (for dust).",
    "For a mountain trip with hot weather and unhealthy air quality, pack: hiking boots, moisture-wicking clothes, wide-brim hat, sunscreen, trekking poles, hydration bladder, N95 mask (for wildfire smoke), portable oxygen canister.",
    "For a mountain trip with mild weather and good air quality, pack: layered clothing, hiking boots, rain jacket, sunscreen, trekking poles, hydration bladder, first-aid kit.",
    "For a mountain trip with mild weather and moderate air quality, pack: layered clothing, hiking boots, rain jacket, sunscreen, trekking poles, hydration bladder, N95 mask (for pollen).",
    "For a mountain trip with mild weather and unhealthy air quality, pack: layered clothing, hiking boots, rain jacket, sunscreen, trekking poles, hydration bladder, N95 mask (for smoke), portable oxygen canister.",
    "For a mountain trip with cold weather and good air quality, pack: insulated jacket, thermal base layers, gloves, beanie, waterproof boots, hand warmers, hydration bladder (insulated).",
    "For a mountain trip with cold weather and moderate air quality, pack: insulated jacket, thermal base layers, gloves, beanie, waterproof boots, hand warmers, hydration bladder (insulated), N95 mask (for cold air).",
    "For a mountain trip with cold weather and unhealthy air quality, pack: insulated jacket, thermal base layers, gloves, beanie, waterproof boots, hand warmers, hydration bladder (insulated), N95 mask (for pollution), portable oxygen canister.",

    # Desert Destinations
    "For a desert trip with hot weather and good air quality, pack: loose, long-sleeved clothing, wide-brim hat, sunglasses, SPF 50+ sunscreen, electrolyte tablets, hydration pack, cooling towel.",
    "For a desert trip with hot weather and moderate air quality, pack: loose, long-sleeved clothing, wide-brim hat, sunglasses, SPF 50+ sunscreen, electrolyte tablets, hydration pack, N95 mask (for sandstorms).",
    "For a desert trip with hot weather and unhealthy air quality, pack: loose, long-sleeved clothing, wide-brim hat, sunglasses, SPF 50+ sunscreen, electrolyte tablets, hydration pack, N95 mask (for dust storms), portable air purifier.",
    "For a desert trip with mild weather and good air quality, pack: layered clothing, wide-brim hat, sunglasses, sunscreen, reusable water bottle, lightweight scarf (for wind).",
    "For a desert trip with mild weather and moderate air quality, pack: layered clothing, wide-brim hat, sunglasses, sunscreen, reusable water bottle, N95 mask (for dust).",
    "For a desert trip with mild weather and unhealthy air quality, pack: layered clothing, wide-brim hat, sunglasses, sunscreen, reusable water bottle, N95 mask (for pollution), portable air purifier.",
    "For a desert trip with cold weather and good air quality, pack: insulated jacket, thermal layers, gloves, beanie, sunglasses, sunscreen, reusable water bottle (insulated).",
    "For a desert trip with cold weather and moderate air quality, pack: insulated jacket, thermal layers, gloves, beanie, sunglasses, sunscreen, reusable water bottle (insulated), N95 mask (for cold wind).",
    "For a desert trip with cold weather and unhealthy air quality, pack: insulated jacket, thermal layers, gloves, beanie, sunglasses, sunscreen, reusable water bottle (insulated), N95 mask (for pollution), portable air purifier.",

    # France (Paris)
    "For a city trip to Paris with mild weather and good air quality, pack: stylish scarf (for chic looks), compact umbrella (for sudden rain), comfortable walking shoes (for cobblestones), reusable coffee cup (for café culture), Seine river cruise ticket.",
    "For a city trip to Paris with cold weather and moderate air quality, pack: trench coat, leather gloves, beret (for fashion + warmth), portable espresso maker (French coffee is strong!), anti-theft crossbody bag (for crowded metros).",

    # Japan (Tokyo)
    "For a city trip to Tokyo with hot weather and good air quality, pack: portable fan (for humid summers), coin purse (many vending machines), slip-on shoes (for temples/ryokans), pocket WiFi router, handkerchief (public restrooms often lack paper towels).",
    "For a city trip to Tokyo with cold weather and moderate air quality, pack: heat-tech innerwear (Uniqlo-style), face mask (for pollen/etiquette), IC card (Suica/Pasmo), onsen towel (for public baths), portable charger (for all-day sightseeing).",

    # Italy (Rome)
    "For a city trip to Rome with hot weather and good air quality, pack: sun hat (for no-shade ruins), refillable water bottle (for public fountains), modest clothing (for Vatican visits), gelato map (to find artisanal spots), anti-pickpocket belt bag.",
    "For a city trip to Rome with mild weather and moderate air quality, pack: light shawl (for church dress codes), comfortable sandals (for uneven streets), Italian phrasebook, wine stopper (for leftover Chianti), collapsible shopping bag (for markets).",

    # India (Delhi)
    "For a city trip to Delhi with hot weather and unhealthy air quality, pack: N99 pollution mask, hand sanitizer (street food prep), scarf (for dust/sun), electrolyte sachets (for dehydration), portable bidet (many restrooms lack TP).",
    "For a city trip to Delhi with mild weather and moderate air quality, pack: modest clothing (for cultural sites), wet wipes, power adapter (Type D), digestive tablets (for spice adjustment), cheap smartphone (to avoid theft risk).",

    # Thailand (Bangkok)
    "For a city trip to Bangkok with hot weather and moderate air quality, pack: sweat-wicking fabrics, foldable fan, reef-safe sunscreen (for island hops), Thai Baht coins (for tuk-tuks), bum bag (for night markets).",
    "For a city trip to Bangkok with mild weather and good air quality, pack: long pants (for temple visits), mosquito repellent, Grab app pre-downloaded (like Uber), quick-dry towel, portable stain remover (for street food spills).",

    # USA (New York)
    "For a city trip to New York with cold weather and moderate air quality, pack: thermal socks (for long walks), MetroCard, reusable bag (for 5¢ bag fee), Broadway ticket printouts, portable phone charger (for subway dead zones).",
    "For a city trip to New York with hot weather and good air quality, pack: sunglasses (for skyscraper glare), walking shoes (no car needed), deli sandwich map (for iconic spots), foldable tote (for impulsive shopping).",

    # Egypt (Cairo)
    "For a desert trip to Cairo with hot weather and unhealthy air quality, pack: UV-protection scarf, Egypt visa printout, USD small bills (for bribes/tips), portable fan (for pyramid climbs), wet wipes (for sand).",
    "For a city trip to Cairo with mild weather and moderate air quality, pack: conservative clothing, hieroglyphic guidebook, cheap sunglasses (for souvenir haggling), stomach meds (for ‘Pharaoh’s Revenge’), power bank (for spotty electricity).",

    # Brazil (Rio de Janeiro)
    "For a beach trip to Rio with hot weather and good air quality, pack: Havaianas flip-flops, waterproof phone pouch (for beaches), Portuguese phrasebook, anti-theft beach bag, caipirinha recipe card (to impress locals).",
    "For a city trip to Rio with mild weather and moderate air quality, pack: light rain jacket (for sudden showers), FIFA jersey (for football culture), transit card (for buses), portable speaker (for beach samba), bug spray (for dengue risk).",

    # Australia (Sydney)
    "For a beach trip to Sydney with hot weather and good air quality, pack: rash guard (for jellyfish), Opal transit card, reef-safe sunscreen (required by law), Aussie slang cheat sheet, collapsible cooler (for BYO barbies).",
    "For a city trip to Sydney with mild weather and moderate air quality, pack: layered clothing (for 4 seasons/day), VPN app (for geo-blocked content), coffee keep-cup (for flat whites), sunscreen stick (for reapplication).",

    # Morocco (Marrakech)
    "For a desert trip to Marrakech with hot weather and moderate air quality, pack: loose linen pants (for conservative areas), dirham coins (for haggling), saffron-buying guide, scarf (for sandstorms), flip-flops (for hammams).",
    "For a city trip to Marrakech with mild weather and good air quality, pack: tea set (to gift hosts), GPS offline maps (for medina maze), antihistamines (for spice dust), lantern (for romantic riads), mint leaves (for DIY tea).",

    # Spain (Barcelona)
    "For a city trip to Barcelona with hot weather and good air quality, pack: modesty cover-up (for Sagrada Família), espadrilles (local footwear), reusable water bottle (for public fountains), paella restaurant map, anti-theft backpack (for Las Ramblas).",
    "For a beach trip to Barcelona with mild weather and moderate air quality, pack: UV-protective swim shirt (for strong sun), Catalan phrasebook, tapas tour app, foldable picnic blanket (for beach paella), silicone wine pouch (for sangria).",

    # Turkey (Istanbul)
    "For a city trip to Istanbul with mild weather and moderate air quality, pack: headscarf (for mosque visits), Turkish Lira coins (for tram rides), portable tea infuser (for çay), evil eye charm (souvenir/haggle starter), stain remover pen (for kebabs).",
    "For a city trip to Istanbul with cold weather and unhealthy air quality, pack: thermal socks (for cold marble floors), VPN app (for social media bans), baklava gift box (for hosts), hammam towel, N95 mask (for winter smog).",

    # Vietnam (Hanoi)
    "For a city trip to Hanoi with hot weather and unhealthy air quality, pack: motorbike bandana (for pollution), zippered pouch (for street food dong), pho spice kit, quick-dry clothing (for humidity), portable stool (for plastic-chair cafes).",
    "For a countryside trip to Sapa with mild weather and good air quality, pack: trekking sandals (for rice terraces), ethnic textile bag (support locals), insect-repellent bracelets, rain poncho (for sudden showers), homestay gift (school supplies).",

    # Mexico (Mexico City)
    "For a city trip to Mexico City with mild weather and moderate air quality, pack: Chapulín (grasshopper) snack pack, Metro card, Lucha Libre mask (for arena nights), stomach settlers (for spicy food), Spanish slang cheat sheet.",
    "For a beach trip to Cancún with hot weather and good air quality, pack: reef-safe sunscreen (mandatory), waterproof money case (for cenotes), Mexican SIM card, tortilla warmer (for breakfast tacos), floating phone pouch (for pool parties).",

    # South Africa (Cape Town)
    "For a city trip to Cape Town with mild weather and good air quality, pack: windproof jacket (for Table Mountain), ZAR coins (for tips), braai (BBQ) spice kit, power adapter (Type D), offline maps (for spotty signal).",
    "For a safari trip to Kruger with hot weather and moderate air quality, pack: khaki clothing (no bright colors), binoculars, anti-malaria pills, wildlife checklist book, solar charger (for lodges).",

    # Indonesia (Bali)
    "For a beach trip to Bali with hot weather and good air quality, pack: sarong (for temple visits), mosquito-repellent wristbands, waterproof sandals (for waterfalls), Balinese offering kit (for ceremonies), motorbike license (for rentals).",
    "For a jungle trip to Ubud with mild weather and moderate air quality, pack: yoga mat strap, eco-friendly straw set, rice terrace map, herbal balm (for bug bites), portable bidet (for eco-toilets).",

    # Greece (Athens)
    "For a city trip to Athens with hot weather and good air quality, pack: ancient ruins guidebook, Greek coffee pot (briki), sun-protective hat (for Acropolis), olive oil shopping list, anti-slip sandals (for marble paths).",
    "For an island trip to Santorini with mild weather and moderate air quality, pack: white outfit (for photos), volcanic wine tote bag, cliffside restaurant map, selfie stick (for caldera views), seasickness pills (for ferry rides).",

    # Portugal (Lisbon)
    "For a city trip to Lisbon with mild weather and good air quality, pack: tram route map, cork products (souvenirs), pastel de nata thermal bag (for takeaway), fado music playlist, cushioned shoes (for cobblestone hills).",
    "For a beach trip to Algarve with hot weather and moderate air quality, pack: cliff-jumping water shoes, sardine can souvenirs, Algarvian citrus perfume, tide timetable (for cave tours), EU health card (for free healthcare).",

    # Argentina (Buenos Aires)
    "For a city trip to Buenos Aires with mild weather and moderate air quality, pack: mate gourd set, tango shoe protectors, USD bills (for blue market rate), steakhouse map, portable fan (for non-AC spots).",
    "For a Patagonia trip with cold weather and good air quality, pack: windproof gloves, thermal base layers, hiking gaiters, dulce de leche stash, Spanish geology guidebook.",

    # Peru (Lima)
    "For a city trip to Lima with mild weather and moderate air quality, pack: ceviche restaurant guide, altitude sickness pills (for Andes trips), alpaca wool gloves, Pisco sour kit, waterproof bag (for coastal fog).",
    "For a Machu Picchu trek with cold weather and good air quality, pack: Inca Trail permit printout, coca tea bags, hiking poles, biodegradable wet wipes, Quechua phrasebook.",

    # **United Arab Emirates (Dubai)**
    "For a city trip to Dubai with hot weather and unhealthy air quality, pack: modesty scarf (for mosques), UV-blocking sunglasses (for desert glare), gold souk bargaining guide, portable fan (for outdoor malls), Emirates ID copy (for SIM card).",
    "For a desert safari in Dubai with mild weather and moderate air quality, pack: sand-proof phone case, Arabic coffee gift set (for Bedouin hosts), cooling neck wrap, 4x4 car charger, dune-bashing motion sickness pills.",

    # **Malaysia (Kuala Lumpur)**
    "For a city trip to Kuala Lumpur with hot weather and unhealthy air quality, pack: mosquito-repellent socks (for dengue zones), MYR small bills (for street food), portable prayer mat (for mosque visits), durian breath mints, Grab app pre-downloaded.",
    "For a rainforest trip to Borneo with mild weather and good air quality, pack: leech socks, waterproof binoculars, orangutan adoption certificate (for sanctuary visits), headlamp (for night hikes), biodegradable soap.",

    # **Philippines (Palawan)**
    "For a beach trip to Palawan with hot weather and good air quality, pack: waterproof dry bag (for island hopping), Filipino phrasebook (for remote villages), reef-safe sunscreen (for coral protection), halo-halo recipe card, anti-chafing powder.",
    "For a city trip to Manila with mild weather and unhealthy air quality, pack: pollution mask (N95), Jeepney fare cheat sheet, power bank (for brownouts), sinigang soup mix, umbrella (for sudden downpours).",

    # **Netherlands (Amsterdam)**
    "For a city trip to Amsterdam with mild weather and moderate air quality, pack: bike phone mount (for rentals), canal cruise ticket printout, stroopwafel tote (for markets), portable bike lock, coffee shop etiquette guide.",
    "For a countryside trip to Keukenhof with cold weather and good air quality, pack: tulip bulb shipping kit, rainproof clogs, windmill picnic blanket, Dutch cheese knife, thermal leggings (for bike tours).",

    # **Singapore**
    "For a city trip to Singapore with hot weather and moderate air quality, pack: chewing gum (forbidden—ironic souvenir), EZ-Link transit card, hawker center wet wipes, air-conditioned mall map, portable umbrella (for sudden storms).",
    "For a Sentosa Island trip with mild weather and good air quality, pack: Universal Studios fast-pass printout, waterproof phone lanyard (for lazy river), chili crab bib, SGD coins (for vending machines), foldable water bottle.",

    # **Ireland (Dublin)**
    "For a city trip to Dublin with cold weather and moderate air quality, pack: Guinness brewery reservation, waterproof hiking boots (for Cliffs of Moher), Irish slang dictionary, wool sweater (for gift-giving), pub trivia cheat sheet.",
    "For a countryside trip to Galway with mild weather and good air quality, pack: traditional music pub map, sheep-avoiding car horn, Connemara marble souvenir guide, rainproof poncho (for ‘soft days’), thermal flask (for tea stops).",

    # **South Korea (Seoul)**
    "For a city trip to Seoul with cold weather and unhealthy air quality, pack: K-beauty sample kit (for duty-free), T-money transit card, portable oxygen canister (for pollution), Korean BBQ marinade set, smartphone selfie ring light.",
    "For a ski trip to Pyeongchang with mild weather and good air quality, pack: heated insoles, ski lift pass holder, kimchi thermos (for slopes), K-pop playlist (for apres-ski), skin moisturizer (for dry cold).",

    # **Colombia (Bogotá)**
    "For a city trip to Bogotá with mild weather and moderate air quality, pack: altitude sickness coca tea, emerald-buying guide, salsa dance shoes, arepa recipe card, theft-proof money belt (for crowded areas).",
    "For a coffee region trip with hot weather and good air quality, pack: coffee bean vacuum bags, farmstay gift (school supplies), insect-repellent bandana, waterproof journal (for humid hikes), collapsible coffee dripper.",

    # **New Zealand (Queenstown)**
    "For an adventure trip to Queenstown with cold weather and good air quality, pack: bungee-jumping GoPro mount, merino wool base layers, hobbiton tour ticket, jet boat hair ties, NZ power adapter (Type I).",
    "For a glacier hike in Franz Josef with mild weather and moderate air quality, pack: crampon-compatible boots, glacier sunscreen (high UV), Māori phrasebook, waterproof gloves, emergency locator beacon.",

    # **Croatia (Dubrovnik)**
    "For a city trip to Dubrovnik with hot weather and good air quality, pack: Game of Thrones filming map, seawater-proof sandals, Dalmatian wine tote, wall walk ticket (for sunrise), euro coins (for public toilets).",
    "For an island-hopping trip with mild weather and moderate air quality, pack: quick-dry swimwear, olive oil shopping list, waterproof speaker (for boat parties), Croatian SIM card, seasickness wristbands."


]

# Create the FAISS index (done once at startup)
index, faiss_embeddings = None, None

def initialize_packing_service():
    global index, faiss_embeddings
    if index is None:
        # Convert documents to embeddings
        embeddings = embedder.encode(documents, show_progress_bar=True)
        faiss_embeddings = np.array(embeddings).astype(np.float32)
        index = faiss.IndexFlatL2(faiss_embeddings.shape[1])
        index.add(faiss_embeddings)

def search_query(query: str) -> str:
    """Search for the most relevant packing suggestion."""
    # Encode the query
    query_embedding = embedder.encode([query])[0]
    
    # Search the FAISS index
    D, I = index.search(np.array([query_embedding]).astype(np.float32), k=1)
    
    # Get the most relevant document
    return documents[I[0][0]]

def get_packing_suggestions(city: str, temperature: float, aqi: int) -> Dict[str, Any]:
    """Get packing suggestions based on location, weather, and air quality."""
    try:
        # Initialize the service if not already done
        initialize_packing_service()
        
        # Create a query based on the input parameters
        query = (
            f"Provide packing suggestions for a trip to {city} "
            f"with a temperature of {temperature}°C "
            f"and an AQI of {aqi}. "
            "Include both a packing list and travel tips."
        )
        
        # Retrieve the most relevant document
        relevant_document = search_query(query)
        
        # Use Ollama to refine the response
        context = relevant_document + "\n\n" + "Question: " + query
        response = ollama.chat(
            model='mistral:latest',
            messages=[{"role": "user", "content": context}]
        )
        
        # Parse the response into a structured format
        # (You might need to adjust this based on how the model responds)
        return {
            "packing_list": extract_list_items(response['message']['content']),
            "travel_tips": extract_tips(response['message']['content']),
            "source": "AI-generated based on travel knowledge base"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "packing_list": [],
            "travel_tips": []
        }

def extract_list_items(text: str) -> list:
    """Extract numbered packing list items from the LLM response."""
    # Look for lines starting with a number followed by a period
    items = re.findall(r'\d+\.\s+(.*?)(?=\d+\.|Travel Tips:|$)', text, re.DOTALL)
    return [item.strip().replace('\n', ' ') for item in items]

def extract_tips(text: str) -> list:
    """Extract numbered travel tips from the LLM response."""
    match = re.search(r'Travel Tips:\s*(.+)', text, re.DOTALL)
    if match:
        tips_block = match.group(1)
        tips = re.findall(r'\d+\.\s+(.*?)(?=\d+\.|$)', tips_block, re.DOTALL)
        return [tip.strip().replace('\n', ' ') for tip in tips]
    return []
