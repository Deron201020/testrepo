import threading
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.core.image import Image as CoreImage
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.stacklayout import MDStackLayout
from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText, MDListItemLeadingIcon, MDListItemSupportingText, MDListItemTertiaryText, MDListItemTrailingSupportingText, MDListItemTrailingCheckbox
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.fitimage.fitimage import FitImage
from kivymd.uix.swiper import MDSwiper, MDSwiperItem
from kivymd.uix.card import MDCard
from kivymd.uix.chip  import MDChip, MDChipText, MDChipLeadingIcon
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.font_definitions import theme_font_styles
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.button import MDIconButton, MDButton, MDButtonIcon, MDButtonText
from kivymd.uix.progressindicator import MDCircularProgressIndicator, MDLinearProgressIndicator
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivymd.uix.divider import MDDivider
from kivymd.uix.screenmanager import MDScreenManager
from kivy.uix.screenmanager import WipeTransition, CardTransition as ScreenTransition
from kivy.core.clipboard import Clipboard
from kivy_garden.mapview import MapView, MapMarker, MapSource
from kivy.uix.label import Label, CoreLabel
from kivy.uix.floatlayout import FloatLayout
from kivy_garden.frostedglass import FrostedGlass
from kivy.core.text import LabelBase
from kivy.utils import get_color_from_hex
from kivy_gradient import Gradient
from kivy.clock import mainthread, Clock
from kivy.uix.carousel import Carousel as CAROUSEL
from kivymd.uix.textfield import (
    MDTextField,
    MDTextFieldLeadingIcon,
    MDTextFieldHintText,
    MDTextFieldHelperText,
    MDTextFieldTrailingIcon,
    MDTextFieldMaxLengthText,
)
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogIcon,
    MDDialogHeadlineText,
    MDDialogSupportingText,
    MDDialogButtonContainer,
    MDDialogContentContainer,
)
from kivymd.uix.pickers import MDModalDatePicker, MDModalInputDatePicker
from kivymd.uix.screen import MDScreen
from kivy.core.window import Window
from kivy.graphics import StencilPush, StencilUse, StencilUnUse, StencilPop, Rectangle, RoundedRectangle, Ellipse, Color, Translate, PushMatrix, PopMatrix
from kivy.uix.stencilview import StencilView
from kivymd.uix.behaviors import RectangularRippleBehavior, TouchBehavior
from kivy.properties import ObjectProperty, BooleanProperty, StringProperty
from kivy.animation import Animation
from kivy.metrics import dp, sp
from kivy.uix.effectwidget import EffectWidget, HorizontalBlurEffect, VerticalBlurEffect
import requests
from requests_html import AsyncHTMLSession, HTMLSession
from bs4 import BeautifulSoup
import asyncio
import nest_asyncio
import math
import geocoder
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from unidecode import unidecode
import pandas
import datetime
from gomaps import maps_search
import webbrowser
import random
from PIL import Image, ImageFilter, ImagePalette
from io import BytesIO
import time
from plyer import call as call_phone
import pyperclip

#Get Current Location
latitude, longitude = geocoder.ip('me').latlng
coord = str(latitude) + ", " + str(longitude)
geolocator = Nominatim(user_agent=str(random.random()), timeout=5)
location = geolocator.reverse(coord, exactly_one=True)
address = location.raw['address']

#Download Databases

#Cities
City = address.get('city', '')
#city_df = pandas.read_csv('Databases/Cities/worldcities_with_images.csv')
city_df = pandas.read_csv('worldcities.csv')
city_names = city_df['city'].dropna().tolist()
city_names = [unidecode(str(city)) for city in city_names if isinstance(city, str) or isinstance(city, float)]
city_images = city_df['Image'].dropna().tolist()
city_images_dict = {}
for i in range(0,len(city_names), 1):
    if i >= len(city_images):
        break
    else:
        city_images_dict[city_names[i]] = city_images[i]

#print(city_images_dict)

#Images
if 1 == 1:
    urls = []
    for city in city_names:
        url = rf"https://www.bing.com/images/search?q={city}+city&form=HDRSC3&first=1"
        urls.append(url)

    def function(url, i, *args):
        response = requests.get(url)
        image = BeautifulSoup(response.text, 'html.parser').find("div", class_="dg_b isvctrl").find("img")["src"]
        city_df.loc[i, 'Image'] = image

    limit = 2500
    start = 7500
    #STOPPED AT: 7500
    for i in range(start, start + limit, 1):
        url = urls[:start + limit][i]
        print("URL:", url)
        thread = threading.Thread(target = function, args = (url, i))
        thread.start()

    city_df.to_csv("worldcities.csv", index=False)

#Propositions
Can_Propose = True

#Threading
threading.stack_size((1024 * 1024) * 16)

#Sentiment Analysis
Folder = "Databases/Sentiment Analysis/"
Positive = ["clean", "simple", "easy", "free", "new", "accurate", "great"]
Negative = []
with open(Folder + "positive-words.txt", "r") as f:
    text = f.read()
    text = text.lower().splitlines()
    for word in text:
        Positive.append(word)
    f.close()

with open(Folder + "negative-words.txt", "r") as f:
    text = f.read()
    text = text.lower().splitlines()
    for word in text:
        Negative.append(word)
    f.close()

Words = {"Positive" : Positive, "Negative" : Negative}
#print(Words)


#Get Current Date
TodayDate = str(datetime.date.today())
TomorrowDate = str(datetime.date.today() + datetime.timedelta(days = 1))


#Download Image From Link
def download_image(url, save_as):
    response = requests.get(url)
    with open(save_as, 'wb') as file:
        file.write(response.content)

    img = Image.open(save_as)
    radius, diameter = 20, 40
    img = img.resize((img.size[0] + diameter, img.size[1] + diameter))
    # Paste image on white background
    background_size = (img.size[0] + diameter , img.size[1] + diameter)
    background = Image.new('RGBA', background_size, (0, 0, 0, 0))

    # create new images with white and black
    mask_size = (img.size[0], img.size[1])
    mask = Image.new('L', mask_size, 0)

    black_size = (img.size[0] - diameter, img.size[1] - diameter)
    black = Image.new('L', black_size, 255)

    # create blur mask
    mask.paste(black, (int(diameter / 2), int(diameter / 2)))

    # Blur image and paste blurred edge according to mask
    mask = mask.filter(ImageFilter.GaussianBlur(radius / 2))
    background.paste(img, mask=mask)
    background.save(save_as, quality=100)

def GetPaletteFromImage(url):
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    image = image.convert("RGB")
    palette_image = image.quantize(colors=1, method=2)
    
    # Get the palette and count of each color
    palette = palette_image.getpalette()  # RGB triplets
    palette = [palette[0] / 255, palette[1] / 255, palette[2] / 255, 1]
    return palette

#Get Recommended Locations
RecommendedPlaces = []

def FindRecommendedPlaces():
    global RecommendedPlaces
    RecommendedLocation = {}
    RecommendedLocations = []
    url = 'https://www.housebeautiful.com/lifestyle/g4500/most-beautiful-places-world/?utm_source=google&utm_medium=cpc&utm_campaign=mgu_ga_hbl_md_dsa_hybd_mix_ca_20257706636&gad_source=1&gclid=Cj0KCQjw3bm3BhDJARIsAKnHoVV1vsifM4PnvOBCaDLBcgioA9JCTm4myEDY76YP1bodSyFEXtsolbAaAv4gEALw_wcB'
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Mobile/15E148 Safari/604.1'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    for place in soup.find_all("div", {'class': 'css-1l3nada e16kmapv6'}):
            Image = place.find("div",{'class': 'css-7jdyxr e1nfup6f1'}).find("img")["src"]
            Name = place.find("h2", {'class': ['css-akimb8', 'e16kmapv5']}).text.strip()
            Description = place.find("p", {'class': 'css-auya5i emevuu60'}).text.strip()
            Loc = {"Name": Name, "Description": Description, "ImageUrl": Image}
            RecommendedLocations.append(Loc)

    RecommendedPlaces = RecommendedLocations
    RecommendedLocation = RecommendedLocations[random.randint(0,len(RecommendedLocations) - 1)]
    print(RecommendedLocation)
    #download_image(RecommendedLocation["ImageUrl"], "ChosenPlace.png")
    return RecommendedLocation
# Extract hotel data
hotelfiltdict = {"Type" : {"Hotel": "nflt=ht_id%3D204", "Apartment": "nflt=ht_id%3D201"}, "Stars": {"5 Star": "nflt=class%3D5"}}
Filters = {"Hotel": {"Date1": "", "Date2": "","Adult" : 2, "Children" : 0, "Rooms" : 1, "TypeFilters": ["Hotel"], "StarsFilter": []}}
def FindHotels(Num = 5, Location = "Paris"):
    hotels = []
    def Function():
        Filter = Filters["Hotel"]
        if Filter["Date1"] == "":
            Filter["Date1"] = TodayDate
        if Filter["Date2"] == "":
            Filter["Date2"] = TomorrowDate
        url = 'https://www.booking.com/searchresults.html?ss=' + Location + '&ssne=Montreal&ssne_untouched=Montreal&label=gen173nr-1FCAQoggJCDWNpdHlfbW9udHJlYWxIM1gEaCeIAQGYATG4ARfIAQzYAQHoAQH4AQOIAgGoAgO4Aoa0k7YGwAIB0gIkZTk3ZWFhNzUtZWViNy00YjhiLTliZjctZDVkZjI1YTI3MmJi2AIF4AIB&aid=304142&lang=en-us&sb=1&src_elem=sb&src=searchresults&checkin=' + Filter["Date1"] + '&checkout=' + Filter["Date2"] + '&group_adults=' + str(Filter["Adult"]) + '&no_rooms=' + str(Filter["Rooms"]) + '&group_children=' + str(Filter["Children"])
        
        for filt in Filters["Hotel"]["TypeFilters"]:
            url += ";" + hotelfiltdict["Type"][filt]

        for filt in Filters["Hotel"]["StarsFilter"]:
            url += ";" + hotelfiltdict["Stars"][filt]

        #webbrowser.open(url)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Accept': 'text/html',
            'Cache-Control': 'public, immutable'
        }

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        Threads = []
        for i in range(0,len(soup.find_all("div", {'data-testid': 'property-card'})),1):
            if i < Num:
                hotel = soup.find_all("div", {'data-testid': 'property-card'})[i]
                try:
                    # Extract the hotel name
                    name_element = hotel.find('div', {'data-testid': 'title'})
                    name = name_element.text.strip()

                    # Extract the hotel location
                    location_element = hotel.find('span', {'data-testid': 'address'})
                    location = location_element.text.strip()

                    # Extract the hotel price
                    price_element = hotel.find('span', {'data-testid': 'price-and-discounted-price'})
                    price = price_element.text.strip()

                    # Extract the hotel rating
                    rating_element = hotel.find('div', {'data-testid': 'review-score'})
                    rating = rating_element.text.strip()
                    rating = str(round((float(rating.split(" ")[1]) / 10) * 5,1))

                    # Extract the hotel rating
                    ratingnumber_element = hotel.find('div', {'class': 'abf093bdfe f45d8e4c32 d935416c47'})
                    ratingnumber = ratingnumber_element.text.strip()

                    #Extract the hotel image
                    image = hotel.find('img')["src"]
                    MainPage = hotel.find("a", {'data-testid': 'property-card-desktop-single-image'}, href=True)
                    MainPage = MainPage['href']
                    """
                    def Finish(image, name, rating, ratingnumber, location, price):
                        images = [image]
                        response  = requests.get(MainPage)
                        soup2 = BeautifulSoup(response.text, 'html.parser')
                        Gallery = soup2.find('div', {"class": "k2-hp--gallery-header bui-grid__column bui-grid__column-9"})
                        for image in Gallery.findAll('img', {"class": "hide"}):
                            images.append(image["src"])
                        Top = soup2.find("div", {"class": "wrap-hotelpage-top"})
                        location_element = Top.find('span', {'data-node_tt_id': 'location_score_tooltip'})
                        location = location_element.text.strip()
                        hotels.append({
                        'Name': name,
                        'Location': location,
                        'Rating': rating,
                        'RatingNumber': ratingnumber,
                        'Price': price,
                        'Class': "Hotel",
                        'Images': images
                        })
                    Thread = threading.Thread(target = Finish, args = (image, name, rating, ratingnumber, location, price))
                    Thread.start()
                    Threads.append(Thread)
                    #Finish(image, name, rating, ratingnumber, location, price)
                    """
                    hotels.append({
                        'Name': name,
                        'Location': location,
                        "Coordinates" : None,
                        'Rating': rating,
                        'RatingNumber': ratingnumber,
                        'RatingDetails' : None,
                        'Price': price,
                        'Class': "Hotel",
                        'Images': [image],
                        'Link': MainPage,
                        'What': "Hotel",
                        "Comments": None,
                        "Additions": None,
                        "Rooms": None,
                        "Attraction": None,
                        "Open": None,
                        "Closes": None,
                        "Phone": None,
                        "Business": None
                        })
                except:
                    pass
            else:
                break
        for thread in Threads:
            thread.join()
    MainThread = threading.Thread(target = Function)
    MainThread.start()
    MainThread.join()
    #Function()
    return hotels

# Extract restaurants data
"""
session = HTMLSession()
session.browser
asession = AsyncHTMLSession()
nest_asyncio.apply()
def find_places(Target = "Restaurant", Num = 5):
    global coord, session, asession
    placesresult = []
    url = "https://www.google.com/maps/search/" + Target + "/@" + coord + ",13z/data=!3m1!4b1?entry=ttu&g_ep=EgoyMDI0MDgyOC4wIKXMDSoASAFQAw%3D%3D"
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Mobile/15E148 Safari/604.1'
    }
    r = session.get(url, headers=headers)
    r.html.render(timeout=20)
    soup = BeautifulSoup(r.html.raw_html, "html.parser")
    places = soup.findAll("div", class_="Nv2PK THOPZb CpccDe")
    Links = []
    for i in range(0,len(places),1):
        if i < Num:
            place = places[i]
            try:
                #Name
                name_element = place.find("div", class_="qBF1Pd fontHeadlineSmall")
                name = name_element.text.strip()
                #Rating
                rating_element = place.find("span", class_="MW4etd")
                rating = rating_element.text.strip()
                ratingnumber_element = place.find("span", class_="UY7F9")
                ratingnumber = ratingnumber_element.text.strip()
                ratingnumber = ratingnumber.split("(",1)[1].split(")",1)[0] + " reviews"
                #Link
                link = place.find("a", class_="hfpxzc", href=True)
                link = link['href']
                Links.append({"Name": name, "Rating": rating, "RatingNumber": ratingnumber, "Link": link})

            except:
                pass
        else:
            break
    async def blocking_render(url, headers):
                    session = HTMLSession()
                    r = await session.get(url, headers=headers)
                    await r.html.arender(timeout=20)  # Use synchronous render instead of async
                    soup2 = BeautifulSoup(r, "html.parser")
                    print("Hello!")
                    info = soup2.find("div", class_="k7jAl miFGmb lJ3Kh")
                    address = info.find("div", class_="Io6YTe fontBodyMedium kR99db fdkmkc").text.strip()
                    placetype = info.find("button", class_="DkEaL").text.strip()
                    image = place.find('img')["src"]
                    images = [image]
                    placesresult.append({
                        'Name': name,
                        'Rating': rating,
                        'RatingNumber' : ratingnumber,
                        "Location" : address,
                        "Class" : placetype,
                        "Images" : images
                    })
                    return r.html.raw_html
    async def Finish(name, rating, ratingnumber, link):
                    # Proceed with parsing as usual
                    loop = asyncio.get_event_loop()
                    r2 = await loop.run_in_executor(None, blocking_render, url, headers)

    async def RunTasks():
        Tasks = [Finish(link["Name"], link["Rating"], link["RatingNumber"], link["Link"]) for link in Links]
        await asyncio.gather(*Tasks)
    asyncio.run(RunTasks())
    return placesresult
"""
session = HTMLSession()
session.browser
session.cookies.clear()

async def again2(url, headers, Num):
            session2 = HTMLSession()
            #session2.browser
            session2.cookies.clear()
            r = session2.get(url, headers=headers, allow_redirects=False, verify=False)
            scrolldown = Num - 5
            #loop = asyncio.new_event_loop()
            #asyncio.set_event_loop(loop)
            await r.html.arender(wait=0, sleep = 0, timeout=10, scrolldown = scrolldown, keep_page=False)
            soup = BeautifulSoup(r.html.raw_html, "html.parser")
            places = soup.findAll("div", class_="Nv2PK THOPZb CpccDe")
            return places

def find_places(Target = "Restaurant", Num = 5):
    global coord, session
    placesresult = []
    url = "https://www.google.com/maps/search/" + Target + "/@" + coord + ",13z/data=!3m1!4b1?entry=ttu&g_ep=EgoyMDI0MDgyOC4wIKXMDSoASAFQAw%3D%3D"
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Keep-Alive': 'timeout=2, max=100',
        'Accept': 'text/html, image/jpg',
        'Cache-Control': 'public, immutable',
    }
    places = []
    try:
        r = session.get(url, headers=headers, allow_redirects=False, verify=False)
        scrolldown = Num - 5
        r.html.render(wait=0, sleep = 0, timeout=10, scrolldown = scrolldown, keep_page=False)
        soup = BeautifulSoup(r.html.raw_html, "html.parser")
        places = soup.findAll("div", class_="Nv2PK THOPZb CpccDe")
    except:
        def again():
            session2 = HTMLSession()
            #session.browser
            session2.cookies.clear()
            r = session2.get(url, headers=headers, allow_redirects=False, verify=False)
            scrolldown = Num - 5
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            r.html.arender(wait=0, sleep = 0, timeout=10, scrolldown = scrolldown, keep_page=False)
            soup = BeautifulSoup(r.html.raw_html, "html.parser")
            places = soup.findAll("div", class_="Nv2PK THOPZb CpccDe")

        #thr = threading.Thread(target = again)
        #thr.start()
        #thr.join()
        #again()
        #asyncio.run(again2(url, headers, Num))
        #loop = asyncio.get_event_loop()
        #places = loop.run_until_complete(again2(url, headers, Num))
        pass

    for i in range(0,len(places),1):
        if i < Num:
            place = places[i]
            try:
                #Name
                name_element = place.find("div", class_="qBF1Pd fontHeadlineSmall")
                name = name_element.text.strip()
                #Rating
                rating_element = place.find("span", class_="MW4etd")
                rating = rating_element.text.strip()
                ratingnumber_element = place.find("span", class_="UY7F9")
                ratingnumber = ratingnumber_element.text.strip()
                ratingnumber = ratingnumber.split("(",1)[1].split(")",1)[0] + " reviews"
                #Price
                price_element = place.find("div", class_="AJB7ye").findAll("span", recursive=False)[2].findAll("span")[1]
                price = price_element.text.strip()
                #Link
                link = place.find("a", class_="hfpxzc", href=True)
                link = link['href']
                """
                def Finish():
                    r2 = session.get(link, headers=headers)
                    r2.html.render(timeout=20)  # Use synchronous render instead of async
                    soup2 = BeautifulSoup(r2.html.raw_html, "html.parser")
                    info = soup2.find("div", class_="k7jAl miFGmb lJ3Kh")
                    address = info.find("div", class_="Io6YTe fontBodyMedium kR99db fdkmkc").text.strip()
                    placetype = info.find("button", class_="DkEaL").text.strip()
                    image = place.find('img')["src"]
                    images = [image]
                    menu = None
                    try:
                        menu = info.find("a", class_="CsEnBe", href=True)["href"].split("q=",1)[1].split("&opi",1)[0]
                    except:
                        pass
                    placesresult.append({
                        'Name': name,
                        'Rating': rating,
                        'RatingNumber' : ratingnumber,
                        "Location" : address,
                        "Class" : placetype,
                        "Images" : images,
                        "Menu": menu,
                        "Link": ""
                    })
                Finish()
                """
                images = [place.find('img')["src"]]
                infopan = place.findAll("div", class_="W4Efsd")[1]
                infos = infopan.find("div", class_="W4Efsd").findAll("span")
                placetype = infos[0].text.strip()
                address = infos[len(infos) - 1].text.strip()
                infos2 = infopan.findAll("span")
                ifopen = infos2[len(infos2) - 2].text.strip()
                closes = infos2[len(infos2) - 1].text.strip()
                closes = closes.replace("\u202f", "")
                closes = closes.replace("Closes ", "")
                closes = closes[1:]
                placesresult.append({
                        'Name': name,
                        'Rating': rating,
                        'RatingNumber' : ratingnumber,
                        'RatingDetails' : None,
                        'Price' : price,
                        "Location" : address,
                        "Coordinates" : None,
                        "Class" : placetype,
                        "Images" : images,
                        "Menu": None,
                        "Link": link,
                        "What": "Restaurant",
                        "Comments" : None,
                        "Additions": None,
                        "Rooms": None,
                        "Attraction": None,
                        "Open": ifopen,
                        "Closes": closes,
                        "Phone": None,
                        "Business": None
                })
            except:
                pass
        else:
            break

    return placesresult

def AnalyseComment(text = "I really like this restaurant"):
    global Words
    Opinion = "Neutral"
    SplittedText = text.lower().split(" ")
    PositivesNum = 0
    PositiveWords = []
    NegativesNum = 0
    NegativeWords = []
    CountedWords = []
    for i in range(0, len(SplittedText),1):
        Word = SplittedText[i]
        if len(Word) > 1:
            for c in range(0, len(Word), 1):
                Sign = Word[c]
                if Sign == "." or Sign == "!" or Sign == "?" or Sign == "," or Sign == ":" or Sign == ";":
                    Word = Word[:c]
                    break
        PreviousWord = ""
        Negation_Words = ["don't", "not"]
        if i > 0:
            PreviousWord = SplittedText[i - 1]
        if Word in Words["Positive"]:
            if not Word in CountedWords:
                if not PreviousWord in Negation_Words:
                    PositivesNum += 1
                    PositiveWords.append(Word)
                    CountedWords.append(i)
                    #print("POSITIVE:", Word)
                else:
                    NegativesNum += 1
                    NegativeWords.append(PreviousWord + " " + Word)
                    CountedWords.append(i - 1)
                    #print("NEGATIVE:", Word)
        if Word in Words["Negative"]:
            if not Word in CountedWords:
                NegativesNum += 1
                NegativeWords.append(Word)
                CountedWords.append(i)
                #print("NEGATIVE:", Word)

    if PositivesNum > NegativesNum:
        Opinion = "Positive Opinion"
    if PositivesNum < NegativesNum:
        Opinion = "Negative Opinion"
    if PositivesNum == NegativesNum:
        Opinion = "Neutral Opinion"
    #print(Opinion)
    return {"Opinion" : Opinion, "Positive Words" : PositiveWords, "Negative Words" : NegativeWords}

class Scroller(StencilView, MDBoxLayout):
    DontBlockWidgets = BooleanProperty(False)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(pos=self.update_rect, size=self.update_rect)
        self.touch_start_y = None
        self.touch_start_x = None
        self.limits = [5,3.5]
        self.overme = True
        #Clock.schedule_interval(self._update_clipself, 0)
        self.ScrollWindow = MDBoxLayout(pos_hint = {"center_x": 0.5, "center_y": 0.6})
        self.add_widget(self.ScrollWindow)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def add_widget(self, widget, *args, **kwargs):
        """Override add_widget to dynamically move widgets to ScrollWindow."""
        if self.ScrollWindow and widget != self.ScrollWindow:
            self.ScrollWindow.add_widget(widget, *args, **kwargs)
        else:
            super().add_widget(widget, *args, **kwargs)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.touch_start_y = touch.y
            self.touch_start_x = touch.x

        return super().on_touch_down(touch) 

    def on_touch_move(self, touch):
        if self.touch_start_y is not None:
            delta_y = touch.y - self.touch_start_y
            delta_x = touch.x - self.touch_start_x
            delta_y_ver = abs(delta_y)
            delta_x_ver = abs(delta_x)
            if delta_y_ver > delta_x_ver:
                self.ScrollWindow.y += delta_y
                self.touch_start_y = touch.y
                if self.ScrollWindow.y < -self.height / self.limits[0]:
                    self.ScrollWindow.y = -self.height / self.limits[0]
                if self.ScrollWindow.y > self.height / self.limits[1]:
                    self.ScrollWindow.y = self.height / self.limits[1]
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        self.touch_start_y = None
        self.touch_start_x = None
        self.overme = True
        return super().on_touch_up(touch)

class CustomCarousel(StencilView, MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(pos=self.update_rect, size=self.update_rect)

        self.touch_start_y = None
        self.touch_start_x = None
        self.limits = [2,2]
        self.can_move = True
        self.velocity_x = 0
        self.child_num = 0
        #self.adaptive_width = True
        #Clock.schedule_interval(self._update_clipself, 0)
        Clock.schedule_interval(self.ResizeWidgets, 0)
        self.ScrollWindow = MDGridLayout(orientation = "lr-tb", rows = 1, spacing = 15, adaptive_size = False, pos_hint = {"center_x": 0.5, "center_y": 0.0})
        #self.md_bg_color = "white"
        self.add_widget(self.ScrollWindow)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def add_widget(self, widget, *args, **kwargs):
        """Override add_widget to dynamically move widgets to ScrollWindow."""
        if self.ScrollWindow and widget != self.ScrollWindow:
            self.ScrollWindow.add_widget(widget, *args, **kwargs)

            self.child_num = len(self.ScrollWindow.children)
            if self.child_num - 3 > 0:
                self.child_num -= 3
            self.ScrollWindow.size_hint_x = self.child_num

            for child in self.ScrollWindow.children:
                child.size_hint = [None,None]
                child.height = self.height / self.child_num
                child.width = self.width / self.child_num
            self.ScrollWindow.size = self.ScrollWindow.minimum_size
        else:
            super().add_widget(widget, *args, **kwargs)

    def on_size(self, *args):
        if hasattr(self, "ScrollWindow"):
            self.child_num = len(self.ScrollWindow.children)
            if self.child_num - 3 > 0:
                self.child_num -= 3
            self.ScrollWindow.size_hint_x = self.child_num

            for child in self.ScrollWindow.children:
                child.size_hint = [None,None]
                child.height = self.height / self.child_num
            self.ScrollWindow.size = self.ScrollWindow.minimum_size

    def remove_widget(self, widget, *args, **kwargs):
        """Override add_widget to dynamically move widgets to ScrollWindow."""
        if self.ScrollWindow and widget != self.ScrollWindow:
            self.ScrollWindow.remove_widget(widget, *args, **kwargs)
            self.ScrollWindow.size = self.ScrollWindow.minimum_size
        else:
            super().remove_widget(widget, *args, **kwargs)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.touch_start_y = touch.y
            self.touch_start_x = touch.x
        if not any(child.collide_point(*touch.pos) for child in self.ScrollWindow.children):
            self.can_move = True
        else:
            self.can_move = False
        return super().on_touch_down(touch) 

    def on_touch_move(self, touch):
        if self.touch_start_x is not None and self.can_move:
            delta_y = touch.y - self.touch_start_y
            delta_x = touch.x - self.touch_start_x
            delta_y_ver = delta_y
            if delta_y_ver < 0:
                delta_y_ver *= -1
            delta_x_ver = delta_x
            if delta_x_ver < 0:
                delta_x_ver *= -1
            if delta_x_ver > delta_y_ver:
                self.ScrollWindow.x += delta_x * 0.5
                self.touch_start_x = touch.x
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        self.touch_start_y = None
        self.touch_start_x = None
        return super().on_touch_up(touch)

    def ResizeWidgets(self, *args):
        Top3 = [10000,10000,10000]
        Top3Widgets = [None, None, None]
        RelPoses = [0,0,0]
        childs = []
        for i in range(0, len(self.ScrollWindow.children), 1):
            child = self.ScrollWindow.children[i]
            relative_position = self.to_widget(*child.pos)
            if relative_position[0] > -10 or i == 0:
                childs.append(child)

        for i in range(0, len(Top3), 1):
            chosen = None
            for i2 in range(0, len(childs), 1):
                child = childs[i2]
                relative_position = self.to_widget(*child.pos)
                #Main Widget
                if abs(relative_position[0]) <= Top3[i]:
                    if relative_position[0] > -10 or i2 == 0:
                        Top3[i] = abs(relative_position[0])
                        Top3Widgets[i] = child
                        chosen = child
                        RelPoses[i] = relative_position

            if chosen in childs:
                childs.remove(chosen)

        for child in self.ScrollWindow.children:
            #Main Widget
            if child == Top3Widgets[0]:
                width = self.width / self.child_num
                vector = width - child.width
                child.width += (vector) * 0.1
                self.ScrollWindow.x -= (RelPoses[0][0] - 5) * 0.005
                self.ControlText(widget=child,appear = True)
            else:
                self.ControlText(widget=child,appear = False)

            #Secondary Widget
            if child == Top3Widgets[1]:
                width = self.width / self.child_num / 2
                vector = width - child.width
                child.width += (vector) * 0.1

            #Tertiary Widget
            if child == Top3Widgets[2]:
                width = self.width / self.child_num / 4
                vector = width - child.width
                child.width += (vector) * 0.1

            #Other Widgets
            if not child in Top3Widgets:
                width = 0
                vector = width - child.width
                child.width += (vector) * 0.1
                child.opacity += (0 - child.opacity) * 0.1
            else:
                child.opacity += (1 - child.opacity) * 0.1

    def ControlText(self, widget, appear):
        for child in widget.children[0].children:
            if isinstance(child, MDBoxLayout):
                if child.id == "InfoCont":
                    if appear:
                        child.opacity += (1 - child.opacity) * 0.1
                    else:
                        child.opacity += (0 - child.opacity) * 0.1
            if isinstance(child, MDLabel):
                    if appear:
                        child.opacity += (1 - child.opacity) * 0.1
                    else:
                        child.opacity += (0 - child.opacity) * 0.1

class RippleBoxLayout(RectangularRippleBehavior, MDBoxLayout):
    on_release = ObjectProperty(None)
    initialclickpos = [0,0]
    ripple = BooleanProperty(True)
    def on_touch_down(self, touch):
        self.initialclickpos = touch.pos
        if self.ripple:
            return super().on_touch_down(touch)
    def on_touch_up(self, touch):
        # Trigger the ripple effect and handle touch release logic
        if self.collide_point(touch.x, touch.y):
            movemagnitude = (abs(touch.x - self.initialclickpos[0]) + abs(touch.y - self.initialclickpos[1]))
            if self.on_release and movemagnitude < 20:
                self.on_release(self)  # Trigger the on_release event
            self.finish_ripple()
            return True
        return super().on_touch_up(touch)

    def on_md_bg_color(self, instance, value):
        self.md_bg_color = self.theme_cls.backgroundColor

class MyCarousel(CAROUSEL):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_focused = False
        Clock.schedule_interval(self.check_focus, 1)

    def check_focus(self, *args):
        if self.collide_point(*Window.mouse_pos):
            self.is_focused = True
        else:
            self.is_focused = False

class ClippedCarousel(CAROUSEL):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class NoHoverMDCard(MDCard):
    def on_enter(self, *args):
        # Disable hover effect (do nothing)
        pass

    def on_leave(self, *args):
        # Disable hover effect (do nothing)
        pass

    def on_press(self, *args):
        # Disable hover effect (do nothing)
        pass

    def on_release(self, *args):
        # Disable hover effect (do nothing)
        pass

class LabeledMapMarker(MapMarker):
    place_name = StringProperty()
    place_type = StringProperty()
    distance = StringProperty()
    source = StringProperty()
    disappear = BooleanProperty(False)

    def __init__(self, lat, lon, place_name, place_type, distance, source, **kwargs):
        super().__init__(lat=lat, lon=lon, **kwargs)
        self.place_name = place_name
        self.place_type = place_type
        self.distance = distance
        self.source = source
        self.zoom = 13
        self.Draw()

    def Draw(self, *args):
        try:
            self.canvas.before.clear()
            with self.canvas.before:
                # Draw the image as the marker
                texture = CoreImage(self.source).texture
                Rectangle(texture=texture, pos=(self.center_x - texture.width / 2, self.center_y - texture.height / 2), 
                          size=(texture.width, texture.height))
            
                # Draw the text background
                #Color(0, 0, 0, 0.3)  # Semi-transparent black
                #text_width = 100
                #text_height = 30
                #Rectangle(pos=(self.center_x - text_width / 2, self.center_y + 10),
                          #size=(text_width, text_height))
            
                # Draw the text (place name and distance)
                if self.zoom > 14:
                    self.draw_text(self.place_type, self.center_x, self.center_y + 40, color = (0, 0.2, 0.395, 1))
                    self.draw_text(self.place_name, self.center_x, self.center_y + 30)
                    self.draw_text(self.distance, self.center_x, self.center_y + 20)
        except:
            pass

    def on_zoom_changed(self):
        if not self.disappear:
            if self.parent != None:
                #print(self.parent.parent.zoom)
                self.zoom = self.parent.parent.zoom
                if self.parent.parent.zoom > 10 and self.parent.parent.zoom < 16:
                    if self.disabled:
                        self.disabled = False
                        Animation(opacity = 1, d=1).start(self)
                else:
                    if not self.disabled:
                        self.disabled = True
                        Animation(opacity = 0, d=1).start(self)
        else:
            if not self.disabled:
                self.disabled = True
                Animation(opacity = 0, d=1).start(self)

    def on_pos(self, *args):
        self.on_zoom_changed()
        self.Draw()

    def on_size(self, *args):
        self.Draw()

    def draw_text(self, text, x, y, color = (0, 0.4, 0.6980392156862745, 1)):
        with self.canvas.before:
            PushMatrix()
            Translate(x, y)
            Color(*color)
            label = CoreLabel(text=text, font_size=10)
            label.refresh()
            text_texture = label.texture
            Rectangle(texture=text_texture, size=text_texture.size, pos=(-text_texture.size[0] / 2, -text_texture.size[1] / 2))
            PopMatrix()

class GradientBox(MDBoxLayout):
    texture = ObjectProperty()
    dis = BooleanProperty()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas:
            # Define the rectangle shape with position and size
            Color(1,1,1,1)
            self.rect = Rectangle(pos=self.pos, size=self.size, texture=self.texture)

    def on_size(self, *args):
        # Update the rectangle size and position if the widget size changes
        self.rect.size = self.size
        self.rect.pos = self.pos

    def on_pos(self, *args):
        # Update the rectangle position if the widget position changes
        self.rect.pos = self.pos

class GradientBoxAnimated(MDBoxLayout):
    speed = 1
    steps = 10
    currentstep = 0

    def __init__(self, *args,**kwargs):
        super().__init__(*args,**kwargs)

        self.colors = [self.theme_cls.surfaceContainerHighColor, self.theme_cls.inverseOnSurfaceColor]
        self.texture = Gradient.vertical(self.colors[1], self.colors[0])

        self.texturecolors = [self.colors[1]]
        for i in range(0, self.steps, 1):
            self.texturecolors.append(self.colors[0])

        Clock.schedule_interval(self.animate_gradient, self.speed / self.steps)

    def animate_gradient(self, *args):
        for i in range(0, len(self.texturecolors), 1):
            if i != self.currentstep:
                self.texturecolors[len(self.texturecolors) - i - 1] = self.colors[0]
            else:
                self.texturecolors[len(self.texturecolors) - self.currentstep - 1] = self.colors[1]


        if self.currentstep < self.steps - 1:
            self.currentstep += 1
        else:
            self.currentstep = 0

        self.texture = Gradient.vertical(*self.texturecolors)
        with self.canvas:
            self.canvas.clear()
            Color(1,1,1,1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, texture=self.texture, radius = [20,])

    def on_size(self, *args):
        # Update the rectangle size and position if the widget size changes
        try:
            self.rect.size = self.size
            self.rect.pos = self.pos
        except:
            pass

    def on_pos(self, *args):
        # Update the rectangle position if the widget position changes
        try:
            self.rect.pos = self.pos
        except:
            pass

KV = '''
#:import get_color_from_hex kivy.utils.get_color_from_hex
#:import Gradient kivy_gradient.Gradient
MDScreen:
    MDNavigationLayout:
        ScreenManager:
            id: ScreenManager
            MDScreen:
                name: "Home Screen"
                MDRelativeLayout:
                    id: MainBox
                    pos_hint: {"center_x": 0.5, "center_y": 0.5}
                    size_hint: 1, 1
                    layout: False
                    MDBoxLayout:
                        pos_hint: {"center_x": 0.5, "center_y": 0.5}
                        size_hint: 1, 1
                        md_bg_color: self.theme_cls.backgroundColor

                    Scroller:
                        id: Background
                        direction: "top"
                        pos_hint: {"center_x": 0.5, "center_y": 0.25}
                        limits: [5,3.5]
                        
                        MDBoxLayout:
                            pos_hint: {"center_x": 0.5, "center_y": 0.55}
                            MDRelativeLayout:
                                CustomCarousel:
                                    id: Destinations
                                    pos_hint: {"center_x": 0.5, "center_y": 0.8}
                                    size_hint: 1, 0.5

                                MDSwiper:
                                    id: Hotels
                                    pos_hint: {"center_x": 0.5, "center_y": 0.4}
                                    size_hint: 1, 0.5
                                    size_duration: 0.5
                                    scroll_friction: 0.001
                                    swipe_distance: 140


                                MDSwiper:
                                    id: Restaurants
                                    pos_hint: {"center_x": 0.5, "center_y": 0}
                                    size_hint: 1, 0.5
                                    size_duration: 0.5
                                    scroll_friction: 0.001
                                    swipe_distance: 140

                    MDCard:
                        id: RecommendedPlaceImage
                        pos_hint: {"center_x": 0.5, "center_y": 0.875}
                        size_hint: 1, 0.25
                        radius: [0,]
                        style: "elevated"
                        elevation: 2
                        theme_shadow_color: "Custom"
                        shadow_color: self.theme_cls.primaryColor

                    MDTextField:
                        id: SearchBar
                        pos_hint: {"center_x": 0.5, "center_y": 0.83}
                        size_hint: 0.5, 0.1
                        max_height: "45dp"
                        mode: "outlined"
                        MDTextFieldHintText:
                            text: "Search"
                            text_color_normal: "white"
                            text_color_focus: "white"
                        MDTextFieldTrailingIcon:
                            icon: "magnify"
                            theme_icon_color: "Custom"
                            icon_color_normal: "white"
                            icon_color_focus: "white"
                                
                    MDBoxLayout:
                        orientation: "horizontal"
                        spacing: "2dp"
                        size_hint: 0.5, 0.1
                        pos_hint: {"center_x": 0.5, "center_y": 0.8}


                    MDBoxLayout:
                        id: SearchBarExpansionPanelBlur
                        pos_hint: {"center_x": 0.5, "center_y": 0.375}
                        size_hint: 1, 0.75
                        theme_bg_color: "Custom"
                        md_bg_color: 0,0,0,0.4
                        opacity: 0


                    MDCard:
                        id: SearchBarPropositions
                        pos_hint: {"center_x": 0.5, "center_y": 0.7}
                        size_hint: 0.7, 0.2
                        theme_bg_color: "Custom"
                        md_bg_color: [0,0,0,0]
                        radius: [0,]
                        opacity: 0
                        disabled: True
                        MDScrollView:
                            MDList:
                                spacing: 7

                    MDCard:
                        id: SearchBarExpansionPanel
                        style: "outlined"
                        pos_hint: {"center_x": 0.5, "center_y": 0.7}
                        size_hint: 0.7, None
                        adaptive_height: True
                        theme_bg_color: "Custom"
                        md_bg_color: [0,0,0,0]
                        opacity: 0
                        disabled: True

                        MDStackLayout:
                            padding: 12
                            spacing: 5
                            adaptive_height: True
                            MDChip:
                                id: HotelChip
                                type: "filter"
                                MDChipLeadingIcon:
                                    icon: "bed"
                                MDChipText:
                                    text: "Stays"

                            MDChip:
                                id: RestaurantChip
                                type: "filter"
                                MDChipLeadingIcon:
                                    icon: "food"
                                MDChipText:
                                    text: "Restaurants"

                            MDChip:
                                id: DestinationChip
                                type: "filter"
                                MDChipLeadingIcon:
                                    icon: "map"
                                MDChipText:
                                    text: "Destinations"
                            

            MDScreen:
                name: "Tab"
                MDRelativeLayout:
                    id: TabBox

            MDScreen:
                name: "Search Screen"
                MDRelativeLayout:
                    id: SearchBox

            MDScreen:
                name: "Settings Screen"
                MDRelativeLayout:
                    md_bg_color: self.theme_cls.backgroundColor
                    MDLabel:
                        id: SettingsTitle
                        text: "Settings"
                        font_size: "25sp"
                        adaptive_height: True
                        padding: "20dp", "20dp", 0, 0
                        pos_hint: {"center_x": 0.5, "center_y": 0.95}
                    MDDivider:
                        pos_hint: {"center_x": 0.5, "center_y": 0.85}

                    ScrollView:
                        pos_hint: {"center_x": 0.5, "center_y": 0.3}
                        MDRelativeLayout:
                            MDLabel:
                                text: "Appearance Mode: Dark"
                                font_size: "15sp"
                                adaptive_height: True
                                padding: "20dp", "20dp", 0, 0
                                pos_hint: {"center_x": 0.5, "center_y": 0.95}
                            MDSwitch:
                                pos_hint: {'center_x': 0.8, 'center_y': 0.925}
                                icon_active: "check"
                                icon_active_color: "white"
                                icon_inactive: "close"
                                icon_inactive_color: "gray"
                                active: True
                                on_active: app.on_switch_appearance_modes(self, self.active)


        MDNavigationDrawer:
            id: nav_drawer
            drawer_type: "modal"
            md_bg_color: self.theme_cls.backgroundColor
            elevation: 5
            radius: [0,]
            anchor: "right"

            MDRelativeLayout:
                MDCard:
                    style: "elevated"
                    elevation: 25
                    size_hint: 1,0.25
                    pos_hint: {"center_x": 0.5, "center_y": 0.875}
                    radius: [45,]
                    theme_shadow_color: "Custom"
                    shadow_color: self.theme_cls.primaryColor
                    FitImage:
                        id: nav_image
                        radius: [45,]

                ScrollView:
                    pos_hint: {"center_x": 0.5, "center_y": 0.25}
                    MDList:
                        MDListItem:
                            id: HomeButton
                            MDListItemHeadlineText:
                                text: "Home"
                            MDListItemLeadingIcon:
                                icon: "home"

                        MDListItem:
                            MDListItemHeadlineText:
                                text: "Account"
                            MDListItemLeadingIcon:
                                icon: "account-circle-outline"

                        MDListItem:
                            id: SettingsButton
                            MDListItemHeadlineText:
                                text: "Settings"
                            MDListItemLeadingIcon:
                                icon: "cog"

'''
LabelBase.register(name='Discover', fn_regular='fonts/adelia.otf')
LabelBase.register(name='Title', fn_regular='fonts/LEMONMILK-Bold.otf')
LabelBase.register(name='Text', fn_regular='fonts/coolvetica rg.otf')
LabelBase.register(name='Emoji', fn_regular='fonts/NotoEmoji-VariableFont_wght.ttf')
RecentTabs = []
CurrentTab = 1

class MyApp(MDApp):
    def build(self):
        Window.size = (414 / 1.25, 896 / 1.25)
        Window.clearcolor = (0, 0, 0, 0)
        Window.smooth = False
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        return Builder.load_string(KV)

    def change_screen(self, screen_name):
        self.root.ids.ScreenManager.current = screen_name
        self.root.ids.TabBox.clear_widgets()
    def on_switch_appearance_modes(self, switch, value):
        #self.theme_cls.theme_style_switch_animation = True
        #self.theme_cls.theme_style_switch_animation_duration = 3
        col = self.theme_cls.backgroundColor
        if value:
            self.theme_cls.theme_style = "Dark"
        else:
            self.theme_cls.theme_style = "Light"
        

    def AnimateSwiper(self, swiper, *args):
        Items = swiper.get_items()
        CurrentItem = swiper.get_current_item()
        for item in Items:
            if item != CurrentItem:
               item.disabled = True
               anim = Animation(opacity=0.1, duration=0.5)
               anim.start(item)
            else:
               item.disabled = False
               anim = Animation(opacity=1, duration=0.5)
               anim.start(item)

    def AnimateCarousel(self, carousel, *args):
        Items = carousel.get_items()
        CurrentItem = carousel.get_current_item()
        for item in Items:
            if item != CurrentItem:
               item.disabled = True
               anim = Animation(opacity=0.1, duration=0.5)
               anim.start(item)
            else:
               item.disabled = True
               anim = Animation(opacity=1, duration=0.5)
               anim.start(item)

    #Search Bar
    def ControlSearchBar(self, instance, focused, panel, panel2, blur): 
        global Can_Propose
        if instance.text == "" or focused == True:
            print("Bye")
            anim = Animation(opacity=0, duration=0.5)
            anim.start(panel)
            anim = Animation(opacity=0, duration=0.5)
            anim.start(blur)
            panel.disabled = True
            Can_Propose = True
            
        if instance.text != "" and focused == False:
            print("Hello")
            anim = Animation(opacity=1, duration=0.5)
            anim.start(panel)
            anim = Animation(opacity=1, duration=0.5)
            anim.start(blur)
            anim = Animation(opacity=0, duration=0.25)
            anim.start(panel2)
            panel.disabled = False
            Can_Propose = False

    def DisableSearchPanel(self, instance, blur):
        instance.parent.parent.opacity = 0
        blur.opacity = 0
        instance.parent.parent.disabled = True

    def ChangeWord(self, wordtochange, wordtowhichchange, item):
            print(wordtochange)
            text = item.text
            try:
                text = text.split(wordtochange, 1)
                text = text[0] + wordtowhichchange + text[1]
                item.text = text
            except:
                item.text = wordtowhichchange
    
    def ControlSearchBarPropositions(self, instance, panel, blur):
        global Can_Propose
        
        if Can_Propose:
            wheretoput = panel.children[0].children[0]
            text = instance.text.lower()
            def Function():
                if text == "":
                    anim = Animation(opacity=0, duration=0.5)
                    anim.start(panel)
                    anim = Animation(opacity=0, duration=0.5)
                    anim.start(blur)
                    panel.disabled = True
            
                else:
                    wheretoput.clear_widgets()
                    #Find Locations

                    #Way 1
                    filtered_cities = [city for city in city_names if city.lower() in text]
                    dictcities = {}
                    longest_word = ""
                    longest_index = 0
                    for city in filtered_cities:
                        if len(city) > longest_index:
                            longest_index = len(city)
                            longest_word = city
                    filtered_cities = [longest_word]
                    if longest_word == "":
                        filtered_cities = []
                    else:
                        dictcities[longest_word] = longest_word

                    #Way 2
                    filtered_cities_dict = {}
                    for city in city_names:
                        word1 = ""
                        for c in city.lower():
                            if not word1 in text:
                                break
                            else:
                                word1 += c
                        word = word1[:len(word1) - 1]
                        if len(word) > 1:
                            filtered_cities_dict[word + "/" + str(len(filtered_cities_dict))] = city
                    max_cities = 15
                    print(filtered_cities_dict)
                    for num in range(0, max_cities, 1):
                        longest_word = ""
                        longest_index = 0
                        key = ""
                        for c in filtered_cities_dict.keys():
                            word = filtered_cities_dict[c]
                            c2 = c.split("/")[0]
                            if len(c2) > longest_index:
                               longest_index = len(c2)
                               longest_word = word
                               key = c
                        if not longest_word in filtered_cities and longest_word != "":
                            filtered_cities.append(longest_word)
                            dictcities[key] = longest_word
                        if key != "":
                            del filtered_cities_dict[key]

                    #Display
                    for city in range(0, len(filtered_cities), 1):
                        name = filtered_cities[city]
                        Img = None
                        try:
                            Img = FitImage(source = city_images_dict[name], radius = [10,])
                        except:
                            pass
                        item = MDListItem(MDListItemHeadlineText(text = name), Img, radius = [0,])
                        item.bind(on_release = lambda i, city=city: self.ChangeWord(wordtochange = list(dictcities.keys())[city], wordtowhichchange = filtered_cities[city], item = instance))
                        wheretoput.add_widget(item)

                    if len(filtered_cities) > 0:
                        if panel.opacity == 0 and Can_Propose:
                            anim = Animation(opacity=1, duration=0.5)
                            anim.start(panel)
                            anim = Animation(opacity=1, duration=0.5)
                            anim.start(blur)
                            panel.disabled = False

            def Work(*args):
                if text == instance.text.lower() and Can_Propose:
                    Function()

            Clock.schedule_once(Work, 1)

    def OpenOrCloseExpansionPanel(self, Panel, ScrollView):
        if not Panel.height == 0:
            Animation(height = 0, d=0.3).start(Panel)
            Animation(opacity = 0, d=0.3).start(Panel)
            ScrollView.do_scroll_x = False
            ScrollView.do_scroll_y = True
        else:
            Animation(height = Panel.width, d=0.3).start(Panel)
            Animation(opacity = 1, d=0.3).start(Panel)
            ScrollView.do_scroll_x = False
            ScrollView.do_scroll_y = False

    #FILTER
    def OpenOrCloseFilterPanel(self, Panel, ScrollPanel):
        if not Panel.size_hint_x == 0:
            Animation(size_hint_x = 0, d=0.3).start(Panel)
            Animation(opacity = 0, d=0.3).start(Panel)
            Animation(opacity = 1, d=0.3).start(ScrollPanel)
            ScrollPanel.do_scroll_x = False
            ScrollPanel.do_scroll_y = True
            ScrollPanel.disabled = False
            Panel.disabled = True
        else:
            Animation(size_hint_x = 1, d=0.3).start(Panel)
            Animation(opacity = 1, d=0.3).start(Panel)
            Animation(opacity = 0, d=0.3).start(ScrollPanel)
            ScrollPanel.do_scroll_x = False
            ScrollPanel.do_scroll_y = False
            ScrollPanel.disabled = True
            Panel.disabled = False

    def ChangeDates(self, instance, Type, InputCalendar):
        global TodayDate, TomorrowDate
        global Filters
        if Type == "Hotel":
            MinDate = None
            if InputCalendar:
                try:
                    MinDate = str(instance.get_date()[0])
                except:
                    pass
            else:
                MinDate = str(instance.min_date)
            if MinDate == 'None':
                MinDate = TodayDate
            MaxDate = None
            if InputCalendar:
                try:
                    MaxDate = str(instance.get_date()[1])
                except:
                    pass
            else:
                MaxDate = str(instance.max_date)
            if MaxDate == 'None':
                MaxDate = TomorrowDate
            Filters["Hotel"]["Date1"] = MinDate
            Filters["Hotel"]["Date2"] = MaxDate
            print(Filters["Hotel"])
        instance.dismiss()

    def OpenCalendarInput(self, *args,  Type):
        global TodayDate
        Calendar = MDModalInputDatePicker(
            default_input_date=True, 
            mode="range"
        )
        Calendar.bind(on_cancel = Calendar.dismiss)
        Calendar.bind(on_ok = lambda instance: self.ChangeDates(instance = instance, Type = Type, InputCalendar = True))
        Calendar.bind(on_edit = lambda instance: self.OpenCalendar(Type = Type))
        Calendar.bind(on_edit = Calendar.dismiss)
        Calendar.open()

    def OpenCalendar(self, *args, Type):
        Calendar = MDModalDatePicker(
            mode="range"
        )
        Calendar.bind(on_cancel = Calendar.dismiss)
        Calendar.bind(on_ok = lambda instance: self.ChangeDates(instance = instance, Type = Type, InputCalendar = False))
        Calendar.bind(on_edit = lambda instance: self.OpenCalendarInput(Type = Type))
        Calendar.bind(on_edit = Calendar.dismiss)
        Calendar.open()

    def ChangeFilterNumbers(self, Input, Type, Variable):
        global Filters
        print(Input)
        if Input != "":
            Filters[Type][Variable] = Input

    #TEXT
    def on_size(self, label, *args):
        Size1 = label.width / 16
        Size2 = label.height / 16
        if Size1 < Size2:
            label.font_size = Size1
        else:
            label.font_size = Size2

    def on_size2(self, label, *args):
        Size1 = label.width / 10
        Size2 = label.height / 10
        if Size1 < Size2:
            label.font_size = Size1
        else:
            label.font_size = Size2

    def on_size3(self, label, *args):
        Size1 = label.width / 20
        Size2 = label.height / 20
        if Size1 < Size2:
            label.font_size = Size1
        else:
            label.font_size = Size2

    def on_size4(self, label, *args):
        Size1 = label.width / 3
        Size2 = label.height / 3
        if Size1 < Size2:
            label.font_size = Size1
        else:
            label.font_size = Size2

    def on_size5(self, label, *args):
        Size1 = label.width / 4
        Size2 = label.height / 4
        if Size1 < Size2:
            label.font_size = Size1
        else:
            label.font_size = Size2

    def on_size6(self, label, *args):
        Size1 = label.width / 2
        Size2 = label.height / 2
        if Size1 < Size2:
            label.font_size = Size1
        else:
            label.font_size = Size2

    def on_size7(self, label, *args):
        Size1 = label.width / 17
        Size2 = label.height / 17
        if Size1 < Size2:
            label.font_size = Size1
        else:
            label.font_size = Size2

    def on_size_custom(self, label, *args, divider):
        Size1 = label.width / divider
        Size2 = label.height / divider
        if Size1 < Size2:
            label.font_size = Size1
        else:
            label.font_size = Size2

    def update_height(self, instance, value):
        instance.height = value 

    def CopyText(self, *args):
        label = MDSnackbarText(text="Copied",theme_text_color="Custom",text_color=[240,240,240,1], size_hint = (0.5,0.5), adaptive_size = True)
        #label.bind(size=self.on_size6)
        MDSnackbar(label, size_hint = (0.25,0.01),pos_hint={"center_x": 0.5, "center_y": 0.1}).open()

    def PhoneCall(self, phone, *args):

        CloseButton = MDButton(MDButtonText(text="Cancel"),style="text")
        AcceptButton = MDButton(MDButtonText(text="Accept"),style="text")
        Dialog = MDDialog(MDDialogIcon(icon="phone"), 

                #Text
                MDDialogHeadlineText(
                text="Call this number? " + phone),
                    
                #Cancel or Accept
                MDDialogButtonContainer(Widget(),CloseButton,AcceptButton, spacing="8dp")
                
        )

        Dialog.open()
        Dialog.update_width()

        def Activate(Call = False, *args):
            Dialog.dismiss()
            if Call:
                #(438) 229-3591
                try:
                    call_phone.makecall("4382293591")
                except:
                    pass

        CloseButton.bind(on_release = Activate)
        AcceptButton.bind(on_release = lambda x: Activate(True))

    def CloseTab(self, *args, OpenWindow = "Home Screen"):
        def removewidgets(*args):
            for children in self.root.ids.TabBox.children:
                self.root.ids.TabBox.remove_widget(children)
        Clock.schedule_once(removewidgets, 0.5)
        self.root.ids.ScreenManager.transition = ScreenTransition()
        self.root.ids.ScreenManager.current = OpenWindow
    def OpenSite(self, *args, Site):
        webbrowser.open(Site)
    def Search(self, Type = "Hotel", SearchBar = None):
        global Filters, Can_Propose, RecommendedPlaces
        Can_Propose = True
        def TaskToDo():
            #Get Search Request
            Text = ""
            if SearchBar == None:
                Text = self.root.ids.SearchBar.text
            else:
                Text = SearchBar.text
            print(Text)

            #Create Window
            SearchItems = []
            if Type == "Hotel":
                #Find Location
                filtered_cities = [city for city in city_names if city.lower() in Text.lower()]
                longest_city_name = ""
                longest_city_name_int = 0
                for city in filtered_cities:
                    if len(city) > longest_city_name_int:
                        longest_city_name_int = len(city)
                        longest_city_name = city
                if len(filtered_cities) > 0:
                    if longest_city_name != "":
                        Location = longest_city_name
                    else:
                        Location = City
                else:
                    filtered_cities = {}
                    for city in city_names:
                        word = ""
                        for c in city.lower():
                            word += c
                            if not word in Text.lower():
                                break
                        if word != "" and word != city.lower()[0]:
                            filtered_cities[word] = city
                    longest_city_name = ""
                    longest_city_name_int = 0
                    for city in filtered_cities.keys():
                        if len(city) > longest_city_name_int:
                            longest_city_name_int = len(city)
                            longest_city_name = filtered_cities[city]
                    if longest_city_name != "":
                        Location = longest_city_name
                    else:
                        Location = City
                Text = Location
                print("LOCATION:" + Location)

                #Find Hotels
                #SearchItems = asyncio.run(FindHotels(Num=3, Location=Location))
                SearchItems = FindHotels(Num=1000, Location=Location)
                print(SearchItems)
            if Type == "Restaurant":
                SearchItems = find_places(Num=5, Target="Restaurants: " + Text)
                print(SearchItems)

            if Type == "Destination":
                SearchItems = RecommendedPlaces
                print(SearchItems)

            @mainthread
            def CreateWindow(SearchItems):
                #SwitchScreens
                self.root.ids.ScreenManager.current = "Search Screen"
                self.root.ids.TabBox.clear_widgets()
                self.root.ids.SearchBar.text = ""
                #Clear Window
                self.root.ids.SearchBox.clear_widgets()

                #Create UI
                Layout = MDRelativeLayout()
                BG = MDBoxLayout(Layout, md_bg_color = self.theme_cls.backgroundColor)#,md_bg_color = [223 / 255, 230 / 255, 233 / 255,0])

                #Search Bar And Expansion Panels And Blur
                SearchField = MDTextField(MDTextFieldHintText(text = "Search"), MDTextFieldTrailingIcon(icon = "magnify"),pos_hint = {"center_x": 0.5, "center_y": 0.925}, size_hint = (0.5, 0.1), max_height = "45dp", mode = "outlined", text = Text)
                HotelChip = MDChip(MDChipLeadingIcon(icon = "bed"),MDChipText(text = "Stays"), id = "HotelChip", type = "filter")
                HotelChip.bind(on_release = lambda instance: self.Search(Type="Hotel", SearchBar=SearchField))
                RestaurantChip = MDChip(MDChipLeadingIcon(icon = "food"),MDChipText(text = "Restaurants"), id = "RestaurantChip", type = "filter")
                RestaurantChip.bind(on_release = lambda instance: self.Search(Type="Restaurant", SearchBar=SearchField))
                DestinationChip = MDChip(MDChipLeadingIcon(icon = "map"),MDChipText(text = "Destination"), id = "DestinationChip", type = "filter")
                DestinationChip.bind(on_release = lambda instance: self.Search(Type="Destination", SearchBar=SearchField))
                ExpansionPanel = MDCard(MDStackLayout(
                    HotelChip, 
                    RestaurantChip,
                    DestinationChip,
                    padding = 12, 
                    spacing = 5,
                    adaptive_height = True,
                    ), id = "SearchBarExpansionPanel2", pos_hint = {"center_x": 0.5, "center_y": 0.75}, size_hint = (0.7, None), adaptive_height = True, theme_bg_color = "Custom", style = "outlined", md_bg_color = [0,0,0,0], opacity = 0, disabled = True)
                
                PropositionsPanel = MDCard(MDScrollView(
                    MDList(),
                    ), id = "SearchBarExpansionPanel2", pos_hint = {"center_x": 0.5, "center_y": 0.75}, size_hint = (0.7, 0.2), theme_bg_color = "Custom", md_bg_color = [0,0,0,0], radius = [0,], opacity = 0, disabled = True)
                
                Fade = GradientBox(theme_bg_color = "Custom", texture = Gradient.vertical([0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0], self.theme_cls.backgroundColor), opacity = 0)
                def ControlFade(self, value):
                    print(value)
                    if value != 1.0:
                        if Fade.dis:
                            Fade.dis = False
                            Animation(opacity = 1, d = 0.5).start(Fade)
                    else:
                        if not Fade.dis:
                            Fade.dis = True
                            Animation(opacity = 0, d = 0.5).start(Fade)
                
                Blur = MDBoxLayout(id = "SearchBarExpansionPanelBlur2", theme_bg_color = "Custom", md_bg_color = [0,0,0,0.4], opacity = 0)
                SearchField.bind(focus=lambda instance, focused: self.ControlSearchBar(instance, focused, ExpansionPanel, PropositionsPanel, Blur))
                SearchField.bind(text=lambda instance, text: self.ControlSearchBarPropositions(instance, PropositionsPanel, Blur))
                
                #Filter
                FilterButton = MDIconButton(icon = "filter",pos_hint = {"center_x": 0.825, "center_y": 0.925}, size_hint = (0.1, 0.1))
                FilterPart = MDBoxLayout(size_hint = (0, 1), opacity = 0, theme_bg_color = "Custom", md_bg_color = self.theme_cls.backgroundColor, disabled = True)
                if Type == "Hotel":
                    FilterLayout = MDStackLayout(padding=dp(10), spacing=dp(25))
                    
                    #Type
                    def CreateTypeDialog(*args):
                        CloseButton = MDButton(MDButtonText(text="Cancel"),style="text")
                        AcceptButton = MDButton(MDButtonText(text="Accept"),style="text")

                        Content = MDList(adaptive_height = True)
                        filts = Filters["Hotel"]["TypeFilters"]
                        for filt in hotelfiltdict["Type"].keys():
                            checkbox = MDListItemTrailingCheckbox()
                            if filt in filts:
                                checkbox.active = True
                            def do_filt(chbox, filt,*args):
                                print("CLICKED")
                                if chbox.active:
                                    chbox.active = False
                                else:
                                    chbox.active = True
                                act = chbox.active
                                print(act)
                                if act:
                                    if not filt in filts:
                                        filts.append(filt)
                                else:
                                    if filt in filts:
                                        filts.remove(filt)
                            item = MDListItem(MDListItemHeadlineText(text = filt), checkbox)
                            item.bind(on_release = lambda x, ch = checkbox, f = filt: do_filt(ch, f))
                            Content.add_widget(item)

                        HotelTypeDialog = MDDialog(MDDialogIcon(icon="home"), 
                                                #Text
                                                MDDialogHeadlineText(text="Choose Stay Type"),

                                                #Choices
                                                MDDialogContentContainer(Content, orientation="vertical"),

                                                MDDialogButtonContainer(Widget(),CloseButton,AcceptButton, spacing="8dp"))

                        def Activate(Open = True, Accept = False, *args):
                                if Accept:
                                    #Add
                                    for criteria in filts:
                                            if not criteria in Filters["Hotel"]["TypeFilters"]:
                                                Filters["Hotel"]["TypeFilters"].append(criteria)
                                    
                                    #Delete
                                    for criteria in Filters["Hotel"]["TypeFilters"]:
                                            if not criteria in filts:
                                                Filters["Hotel"]["TypeFilters"].remove(criteria)

                                if not Open:
                                    HotelTypeDialog.dismiss()
                                else:
                                    HotelTypeDialog.open()

                                print(Filters)

                        CloseButton.bind(on_release = lambda x: Activate(Open = False))

                        AcceptButton.bind(on_release = lambda x: Activate(Open = False, Accept = True))

                        HotelTypeDialog.update_width()

                        HotelTypeDialog.open()

                    HotelTypeButton = MDButton(MDButtonIcon(icon = "home"), MDButtonText(text="Choose Stay Type"))
                    HotelTypeButton.bind(on_release = CreateTypeDialog)

                    #Stars
                    def CreateStarsDialog(*args):
                        CloseButton = MDButton(MDButtonText(text="Cancel"),style="text")
                        AcceptButton = MDButton(MDButtonText(text="Accept"),style="text")

                        Content = MDList(adaptive_height = True)
                        filts = Filters["Hotel"]["StarsFilter"]
                        for filt in hotelfiltdict["Stars"].keys():
                            checkbox = MDListItemTrailingCheckbox()
                            if filt in filts:
                                checkbox.active = True
                            def do_filt(chbox, filt,*args):
                                print("CLICKED")
                                if chbox.active:
                                    chbox.active = False
                                else:
                                    chbox.active = True
                                act = chbox.active
                                print(act)
                                if act:
                                    if not filt in filts:
                                        filts.append(filt)
                                else:
                                    if filt in filts:
                                        filts.remove(filt)
                            item = MDListItem(MDListItemHeadlineText(text = filt), checkbox)
                            item.bind(on_release = lambda x, ch = checkbox, f = filt: do_filt(ch, f))
                            Content.add_widget(item)

                        StarsDialog = MDDialog(MDDialogIcon(icon="star"), 
                                                #Text
                                                MDDialogHeadlineText(text="Choose the Number of Stars"),

                                                #Choices
                                                MDDialogContentContainer(Content, orientation="vertical"),

                                                MDDialogButtonContainer(Widget(),CloseButton,AcceptButton, spacing="8dp"))

                        def Activate(Open = True, Accept = False, *args):
                                if Accept:
                                    #Add
                                    for criteria in filts:
                                            if not criteria in Filters["Hotel"]["StarsFilter"]:
                                                Filters["Hotel"]["StarsFilter"].append(criteria)
                                    
                                    #Delete
                                    for criteria in Filters["Hotel"]["StarsFilter"]:
                                            if not criteria in filts:
                                                Filters["Hotel"]["StarsFilter"].remove(criteria)

                                if not Open:
                                    StarsDialog.dismiss()
                                else:
                                    StarsDialog.open()

                                print(Filters)

                        CloseButton.bind(on_release = lambda x: Activate(Open = False))

                        AcceptButton.bind(on_release = lambda x: Activate(Open = False, Accept = True))

                        StarsDialog.update_width()

                        StarsDialog.open()

                    StarsButton = MDButton(MDButtonIcon(icon = "star"), MDButtonText(text="Choose the Number of Stars"))
                    StarsButton.bind(on_release = CreateStarsDialog)

                    #Calendar
                    DateButton = MDButton(MDButtonIcon(icon = "calendar"), MDButtonText(text = "Choose Booking Dates"))
                    DateButton.bind(on_release = lambda instance: self.OpenCalendar(Type = Type))
                    
                    #Adults, Children and Room Numbers
                    Adult = MDTextField(MDTextFieldHintText(text = "Adult Number"), input_filter = "int")
                    Adult.text = str(Filters["Hotel"]["Adult"])
                    Adult.bind(on_text_validate = lambda instance: self.ChangeFilterNumbers(Input = instance.text, Type = "Hotel", Variable = "Adult"))

                    Children = MDTextField(MDTextFieldHintText(text = "Children Number"), input_filter = "int")
                    Children.text = str(Filters["Hotel"]["Children"])
                    Children.bind(on_text_validate = lambda instance: self.ChangeFilterNumbers(Input = instance.text, Type = "Hotel", Variable = "Children"))

                    Room = MDTextField(MDTextFieldHintText(text = "Rooms Number"), input_filter = "int")
                    Room.text = str(Filters["Hotel"]["Rooms"])
                    Room.bind(on_text_validate = lambda instance: self.ChangeFilterNumbers(Input = instance.text, Type = "Hotel", Variable = "Rooms"))

                    #Assemble
                    FilterLayout.add_widget(HotelTypeButton)
                    FilterLayout.add_widget(StarsButton)
                    FilterLayout.add_widget(DateButton)
                    FilterLayout.add_widget(Adult)
                    FilterLayout.add_widget(Children)
                    FilterLayout.add_widget(Room)
                    FilterPart.add_widget(FilterLayout)
                
                #Search Results
                List = None
                if Type == "Hotel" or Type == "Restaurant":
                    List = MDList()
                if Type == "Destination":
                    List = MDStackLayout(md_bg_color = self.theme_cls.backgroundColor, adaptive_height = True, spacing = 5)
                ScrollPart = MDScrollView(List)
                ScrollPart.bind(scroll_y = ControlFade)

                LoadMoreButton = None
                if Type == "Restaurant":
                    LoadMoreButton = MDButton(MDButtonText(text="Load More"),style="outlined", pos_hint = {"center_x": 0.5, "center_y": 0.05}, size_hint = (0.5, 0.2))
                    SearchItemsDone = SearchItems
                    def LoadMore(*args):
                        print("LOADING MORE!")
                        SearchItems = find_places(Num=len(List.children) + 10, Target="Restaurants: " + Text)

                        @mainthread
                        def finishloading():
                            added = 0
                            for SearchItem in SearchItems:
                                if not SearchItem in SearchItemsDone:
                                    added += 1
                                    Item = MDListItem(MDCard(FitImage(source = SearchItem["Images"][0], radius = [20,]),elevation = 10, radius = [20,]),MDListItemHeadlineText(text = SearchItem["Name"]), MDListItemSupportingText(text = SearchItem["Location"]), MDListItemTertiaryText(text = SearchItem["Rating"] + " | " + "[b]" + SearchItem["Open"] + "[/b]"), MDListItemTrailingSupportingText(text = SearchItem["Price"]))
                                    Item.bind(on_release = lambda instance, i=SearchItem: self.OpenTab(Info = i, OpenWindow = 'Search Screen'))
                                    List.add_widget(Item)

                            if added == 0:
                                buttonparent = LoadMoreButton.parent
                                buttonparent.remove_widget(LoadMoreButton)

                        finishloading()

                    def load(*args):
                        thread = threading.Thread(target = LoadMore)
                        thread.start()
                    LoadMoreButton.bind(on_release = load)

                ScrollPart = MDRelativeLayout(ScrollPart, Fade, LoadMoreButton)
                ScrollView = MDGridLayout(FilterPart, ScrollPart, pos_hint = {"center_x": 0.5, "center_y": 0.425}, size_hint = (1, 0.85), rows = 1)
                FilterButton.bind(on_release = lambda instance: self.OpenOrCloseFilterPanel(Panel = FilterPart, ScrollPanel = ScrollPart))
                
                if Type == "Hotel":
                    #Create UI
                    for SearchItem in SearchItems:
                        Item = MDListItem(MDCard(FitImage(source = SearchItem["Images"][0], radius = [20,]),elevation = 10, radius = [20,]),MDListItemHeadlineText(text = SearchItem["Name"]), MDListItemSupportingText(text = SearchItem["Location"]), MDListItemTertiaryText(text = SearchItem["Rating"]), MDListItemTrailingSupportingText(text = SearchItem["Price"]))
                        Item.bind(on_release = lambda instance, i=SearchItem: self.OpenTab(Info = i, OpenWindow = 'Search Screen'))
                        List.add_widget(Item)
                if Type == "Restaurant":
                    #Create UI
                    for SearchItem in SearchItems:
                        Item = MDListItem(MDCard(FitImage(source = SearchItem["Images"][0], radius = [20,]),elevation = 10, radius = [20,]),MDListItemHeadlineText(text = SearchItem["Name"]), MDListItemSupportingText(text = SearchItem["Location"]), MDListItemTertiaryText(text = SearchItem["Rating"] + " | " + "[b]" + SearchItem["Open"] + "[/b]"), MDListItemTrailingSupportingText(text = SearchItem["Price"]))
                        Item.bind(on_release = lambda instance, i=SearchItem: self.OpenTab(Info = i, OpenWindow = 'Search Screen'))
                        List.add_widget(Item)

                if Type == "Destination":
                    #Create UI
                    Done = 1.0
                    for SearchItem in SearchItems:
                        method = "right"
                        if Done / 2.0 == int(Done/2.0):
                            method = "left"
                        if method == "right":
                            Item = MDCard(MDBoxLayout(FitImage(source = SearchItem["ImageUrl"], radius = [0,]), MDStackLayout(MDLabel(text = SearchItem["Name"], theme_font_name = "Custom", font_name = "Title", radius = [0,], md_bg_color = self.theme_cls.backgroundColor, adaptive_height = True), MDLabel(text = SearchItem["Description"], theme_font_name = "Custom", font_name = "Text", radius = [0,], md_bg_color = self.theme_cls.backgroundColor, adaptive_height = True),adaptive_height = True), radius = [20,], adaptive_height = True, md_bg_color = self.theme_cls.backgroundColor), radius = [0,], md_bg_color = self.theme_cls.backgroundColor,adaptive_height = True, ripple_behavior = True)
                            Item.bind(on_release = lambda instance, i=SearchItem: self.OpenRecommendedPlaceTab(Info = i, OpenWindow = 'Search Screen'))
                            List.add_widget(Item)
                        else:
                            Item = MDCard(MDBoxLayout(MDStackLayout(MDLabel(text = SearchItem["Name"], theme_font_name = "Custom", font_name = "Title", radius = [0,], md_bg_color = self.theme_cls.backgroundColor, adaptive_height = True), MDLabel(text = SearchItem["Description"], theme_font_name = "Custom", font_name = "Text", radius = [0,], md_bg_color = self.theme_cls.backgroundColor, adaptive_height = True),adaptive_height = True),FitImage(source = SearchItem["ImageUrl"], radius = [0,]), radius = [20,], adaptive_height = True, md_bg_color = self.theme_cls.backgroundColor), radius = [0,], md_bg_color = self.theme_cls.backgroundColor,adaptive_height = True, ripple_behavior = True)
                            Item.bind(on_release = lambda instance, i=SearchItem: self.OpenRecommendedPlaceTab(Info = i, OpenWindow = 'Search Screen'))
                            List.add_widget(Item)
                        Done += 1


                #Add Widgets
                Layout.add_widget(ScrollView)
                Layout.add_widget(Blur)
                Layout.add_widget(SearchField)
                Layout.add_widget(PropositionsPanel)
                Layout.add_widget(ExpansionPanel)
                if Type == "Hotel" or Type == "Restaurant":
                    Layout.add_widget(FilterButton)

                self.root.ids.SearchBox.add_widget(BG)

            CreateWindow(SearchItems)
            
        threading.Thread(target = TaskToDo).start()

    def ChangeTab(self, *args, Direction, OpenWindow):
        global geolocator, latitude, longitude, RecentTabs, CurrentTab, CurrentOpenedTab
        ChangedTab = False
        if Direction == "Left":
            if len(RecentTabs) > 1:
                self.root.ids.TabBox.clear_widgets()
                ChangedTab = True
            if CurrentTab == 0:
                CurrentTab = len(RecentTabs) - 1
            else:
                CurrentTab -= 1
        if Direction == "Right":
            if len(RecentTabs) > 1:
                self.root.ids.TabBox.clear_widgets()
                ChangedTab = True
            if CurrentTab == len(RecentTabs) - 1:
                CurrentTab = 0
            else:
                CurrentTab += 1
        Info = None
        if len(RecentTabs) > 1:
            Info = RecentTabs[CurrentTab]
        else:
            Info = RecentTabs[0]
        #Update UI
        def Create():
                Button = MDIconButton(icon = "close", font_size = "2sp", pos_hint = {"center_x": 0.075,"center_y": 0.975}, size_hint = (0.1,0.1))
                Carousel = MyCarousel(pos_hint = {"center_x": 0.5,"center_y": 0.85}, size_hint = (1,0.3))
                Carousel.loop = True
                def CarouselMove(*args):
                    if not Carousel.is_focused:
                        Carousel.load_next()
                Clock.schedule_interval(CarouselMove, 3.0)
                #Create Menu
                Menu = None
                try:
                    if Info["Menu"] != "":
                        Menu = MDListItem(MDListItemLeadingIcon(icon = "food"),  MDListItemSupportingText(text = Info["Menu"][:20]))
                        Menu.bind(on_release=lambda instance: self.OpenSite(Site = Info["Menu"]))
                except:
                    pass

                #Create Map
                mapview = None
                try:
                    getLoc = geolocator.geocode(Info["Location"].split(",")[0])
                    mapview = MapView(map_source = MapSource(url="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}"),zoom=13, lat=getLoc.latitude, lon=getLoc.longitude)
                    marker = MapMarker(lon=getLoc.longitude,lat=getLoc.latitude)            
                    mapview.add_marker(marker)
                except:
                    mapview = MapView(map_source = MapSource(url="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}"),zoom=13, lat=latitude, lon=longitude)
                MapCard = MDCard(mapview, size_hint = (0.9, None), height = 0, elevation = 10, opacity = 0)
        
                #Create UI
                List = MDListItem(MDListItemHeadlineText(text = Info["Name"]), MDListItemSupportingText(text = Info["Class"] + " \u2022 " + Info["Location"]), MDListItemTertiaryText(text = Info["Rating"] + " \u2022 " + Info["RatingNumber"]), MDListItemTrailingSupportingText(text = Info["Price"]))
                Layout = MDStackLayout(List, MapCard, Menu, orientation='lr-tb', padding=dp(10), spacing=dp(2), adaptive_height = True)
                View = MDScrollView(Layout, do_scroll_x = False, pos_hint = {"center_x": 0.5, "center_y": 0.45})
                List.bind(on_release=lambda instance: self.OpenOrCloseExpansionPanel(Panel = MapCard, ScrollView = View))
                
                #Create Rating Details
                Lines = []
                if Info["RatingDetails"] != None:
                    RatingDetails = MDGridLayout(rows = 3, cols = 3, adaptive_height = True)
                    for detail in Info["RatingDetails"]:

                        #Box
                        Box = MDStackLayout(adaptive_height = True)

                        #Text
                        Text = MDLabel(text = detail[0], role = "small", theme_font_name = "Custom", font_name = "Text", adaptive_height = True)

                        #Line
                        Line = MDLinearProgressIndicator(value = 0, size_hint = (0.5, None))
                        Lines.append([Line, float(detail[1]) * 10])

                        #Assemble
                        Box.add_widget(Text)
                        Box.add_widget(Line)
                        RatingDetails.add_widget(Box)

                    Layout.add_widget(RatingDetails)
                    Space = MDLabel(text = " ", role = "small", theme_font_name = "Custom", font_name = "Text", adaptive_height = True)
                    Layout.add_widget(Space)

                
                #Create Comments
                if Info["Comments"] != None:
                    if len(Info["Comments"]) > 0:
                        
                        #Comments Analysis
                        CommentsRatio = 0
                        CommentsInfoBox = MDGridLayout(rows = 1, cols = 3, adaptive_height = True)
                        PosNum = MDLabel(text = "[font=Emoji]👍[/font]", role = "medium", theme_font_name = "Custom", adaptive_height = True, markup = True)
                        PosBox = MDCard(PosNum, theme_bg_color = "Custom", md_bg_color = [0,0,0,0], adaptive_height = True)
                        NegNum = MDLabel(text = "[font=Emoji]👎[/font]", role = "medium", theme_font_name = "Custom", adaptive_height = True, markup = True)
                        NegBox = MDCard(NegNum, theme_bg_color = "Custom", md_bg_color = [0,0,0,0], adaptive_height = True)
                        RatioText = MDLabel(text = " ", role = "medium", theme_font_name = "Custom", adaptive_height = True, markup = True)
                        RatioBox = MDCard(RatioText, theme_bg_color = "Custom", md_bg_color = [0,0,0,0], adaptive_height = True)
                        CommentsInfoBox.add_widget(PosBox)
                        CommentsInfoBox.add_widget(NegBox)
                        CommentsInfoBox.add_widget(RatioBox)
                        Layout.add_widget(CommentsInfoBox)
                        Ratio = [0,0]
                        
                        #Display Comments
                        CommentsBox = MDStackLayout(orientation='lr-tb', padding=dp(10), spacing=dp(0.5), adaptive_height = True)
                        def WriteComments(CommentType = "All"):
                            if len(CommentsBox.children) > 0:
                                CommentsBox.clear_widgets()
                            for comment in Info["Comments"]: 
                                #Comment
                                Text = MDLabel(text = comment[1], role = "small", theme_font_name = "Custom", font_name = "Text", adaptive_height = True)
                    
                                #Header
                                Image = FitImage(source = comment[0], size_hint = (0.1, None), radius = [45,])
                                Image.bind(width=self.update_height)
                                Title = MDLabel(text = comment[2], role = "small", theme_font_name = "Custom", font_name = "Text", bold = True, adaptive_height = True)
                                GivenOpinion = AnalyseComment(comment[1])
                                Opinion = None
                                if GivenOpinion == "Positive Opinion":
                                    Ratio[0] += 1
                                    Opinion = MDLabel(text = GivenOpinion, role = "small", opacity = 0.8, theme_font_name = "Custom", font_name = "Text", adaptive_height = True)
                                if GivenOpinion == "Negative Opinion":
                                    Ratio[1] += 1
                                    Opinion = MDLabel(text = GivenOpinion, role = "small", opacity = 0.8, theme_font_name = "Custom", font_name = "Text", adaptive_height = True)

                                Header = MDBoxLayout(Image, MDStackLayout(Title, Opinion, orientation='lr-tb', adaptive_height = True), spacing = 5,adaptive_height = True)
                                Space = MDLabel(text = " ", role = "small", theme_font_name = "Custom", font_name = "Text", adaptive_height = True)

                                #Assemble
                                Panel = MDBoxLayout(MDStackLayout(Header, Text, Space, orientation='lr-tb', adaptive_height = True), adaptive_height = True)
                                if CommentType == "All":
                                    CommentsBox.add_widget(Panel)
                                elif GivenOpinion == CommentType:
                                    CommentsBox.add_widget(Panel)

                        WriteComments()

                        Layout.add_widget(MDBoxLayout(CommentsBox, id = "CommentsBox", adaptive_height = True))

                        #Update Comments Analysis
                        PosNum.text += "[font=Text]" + str(Ratio[0]) + "[/font]"
                        PosBox.bind(on_release = lambda x: WriteComments("Positive Opinion"))
                        NegNum.text += "[font=Text]" + str(Ratio[1]) + "[/font]"
                        NegBox.bind(on_release = lambda x: WriteComments("Negative Opinion"))
                        percent = Ratio[0] / (Ratio[0] + Ratio[1]) * 100
                        RatioText.text = "[font=Emoji]👍[/font][font=Text]/[/font][font=Emoji]👎[/font][font=Text]" + str(percent) + "%[/font]"
                        RatioBox.bind(on_release = lambda x: WriteComments("All"))
                
                InfoCard = MDBoxLayout(MDRelativeLayout(View),pos_hint = {"center_x": 0.5, "center_y": 0.375}, size_hint = (1, 0.75), md_bg_color = self.theme_cls.backgroundColor, radius = [25,25,0,0])
                LeftButton = MDIconButton(icon="invisible-png.png",pos_hint = {"center_x": 0.1, "center_y": 0.5}, size_hint = (0.025, 1))
                LeftButton.bind(on_press = lambda instance : self.ChangeTab(Direction="Left", OpenWindow = OpenWindow))
                RightButton = MDIconButton(icon="invisible-png.png",pos_hint = {"center_x": 0.9, "center_y": 0.5}, size_hint = (0.025, 1))
                RightButton.bind(on_press = lambda instance : self.ChangeTab(Direction="Right", OpenWindow = OpenWindow))
                Card = MDBoxLayout(MDBoxLayout(MDRelativeLayout(Carousel, InfoCard, Button, LeftButton, RightButton)),pos_hint = {"center_x": 0.5, "center_y": 0.5}, size_hint = (1, 1), radius = [0,])
                for Image in Info["Images"]:
                    Carousel.add_widget(FitImage(source = Image, radius = [0,]))

                for Line in Lines:
                    anim = Animation(value = Line[1], t = "easing_decelerated", d = 1.5)
                    anim.start(Line[0])
                Button.bind(on_release = lambda instance : self.CloseTab(OpenWindow = OpenWindow))
                RecentTabs.append(Info)
                self.root.ids.TabBox.add_widget(Card)
                self.root.ids.ScreenManager.current = 'Tab'

        if ChangedTab:
            Create()

    def OpenTab(self, *args, Info, OpenWindow = 'Home Screen'):
        global geolocator, latitude, longitude, RecentTabs, CurrentTab, session
        def Func():
            time1 = datetime.datetime.now()
            soup2 = None
            threads = {}
            if Info["Link"] != "":
                if Info["What"] == "Hotel":
                    headers = {
                       'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
                       'Accept-Encoding': 'gzip, deflate',
                       'Connection': 'keep-alive',
                       'Accept': 'text/html, image/png',
                       'Cache-Control': 'public, immutable'
                    }
                    #s = requests.Session()
                    response  = requests.get(Info["Link"], headers=headers)
                    soup2 = BeautifulSoup(response.text, 'html.parser')
                if Info["What"] == "Restaurant":
                        headers = {
                           'User-Agent': 'Mozilla/5.0',
                           'Accept-Encoding': 'gzip, deflate, br',
                           'Connection': 'keep-alive',
                           'Keep-Alive': 'timeout=2, max=100',
                           'Accept': 'text/html',
                           'Cache-Control': 'public, max-age=31536000, immutable',
                        }
                        try:
                            session.cookies.clear()  # Remove all cookies before the request
                            r2 = session.get(Info["Link"], headers=headers, allow_redirects=False, verify=False)
                            r2.html.render(wait=0, sleep=0, timeout=10, scrolldown=0, keep_page=False)
                            soup2 = BeautifulSoup(r2.html.raw_html, "html.parser")
                        except:
                            pass

            #time2 = datetime.datetime.now()
            #print("TIME:", time2 - time1)

            #time1 = datetime.datetime.now()
            locinf = ""
            CriteriaIcons = {
                "Free WiFi": "wifi",  # Material icon for Wi-Fi
                "Family rooms": "account-group",  # Icon for groups/family
                "Non-smoking rooms": "smoking-off",  # Icon for no smoking
                "Room service": "bell",  # Icon for room service
                "Parking": "parking",  # Icon for parking
                "Private parking": "parking",  # Icon for parking
                "Parking on site": "parking",
                "Free parking": "parking",
                "Fitness centre": "weight-lifter",  # Icon for fitness activities
                "Facilities for disabled guests": "wheelchair-accessibility",  # Icon for accessibility
                "24-hour front desk": "clock",  # Icon for time
                "Bar": "glass-cocktail",  # Icon for drinks/bar
                "Daily housekeeping": "broom",  # Icon for cleaning
                "Elevator": "elevator", # Icon for elevator
                "Lift": "elevator",
                "Laundry service": "tumble-dryer",  # Icon for laundry services
                "Indoor swimming pool" : "pool",
                "Outdoor swimming pool" : "pool",
                "Restaurant" : "food",
                "Tea/coffee maker in all rooms" : "coffee",
                "Good breakfast" : "bread-slice",
                "Breakfast" : "bread-slice",
                "2 restaurants" : "food"
            }
            hotelattractions = []
            if Info["Link"] == "":
                locinf = Info["Location"]
            else:
                if Info["What"] == "Hotel":
                    Top = soup2.find("div", {"class": "wrap-hotelpage-top"})

                    #Location
                    location_element = Top.find('div', {'class': 'a53cbfa6de f17adf7576'})
                    locinf = location_element.text.strip()

                    #Coordinates
                    coordinates_element = Top.find('a', {'class': 'a83ed08757 f88a5204c2 a40b576ae6 b98133fb50'})
                    coordinates = coordinates_element["data-atlas-latlng"]
                    coordinates = [float(coordinates.split(",")[0]), float(coordinates.split(",")[1])]
                    Info["Coordinates"] = coordinates
                    #time2 = datetime.datetime.now()
                    #print("TIME:", time2 - time1)

                    #Comments
                    try:
                        comments = soup2.find("ul", class_="fc49408fea ba4306d436 c6d7cec60f").findAll("li", class_="b0932df2e7 e375bc2404")
                        #print("FIRST STEP")
                        print(len(comments))
                        coms = []
                        for comment in comments:
                            try:
                                #Icons
                                icon = comment.find("img", class_="e3fa9175ee d354f8f44f ed3971de08")["src"]
                                #print("STEP 2")

                                #Title
                                title = comment.find("div", class_="a3332d346a e6208ee469").text.strip()
                                #print("STEP 3")

                                #Comments
                                text = comment.find("div", class_="a53cbfa6de b5726afd0b").findAll("span")[1].text.strip()
                                #print("STEP 4")

                                #Final Comment
                                coms.append([icon, text, title])
                            except:
                               pass


                        print(coms)
                        Info["Comments"] = coms
                    except:
                        pass

                    #time2 = datetime.datetime.now()
                    #print("TIME:", time2 - time1)

                    #Rating Details
                    try:
                        details = soup2.find("div", class_="bd3bd8bd58").findAll("div", class_="c624d7469d a0e60936ad a3214e5942")
                        print("FIRST STEP", len(details))
                        ratingdetails = []
                        for detail in details:
                            try:
                                #Criteria
                                criteria = detail.find("span", class_="be887614c2").text.strip()
                                print("STEP 2")

                                #Rating
                                rating = detail.find("div", class_="ccb65902b2 bdc1ea4a28").text.strip()
                                print("STEP 3")

                                #Final Detail
                                ratingdetails.append([criteria, rating])
                            except:
                               pass


                        print(ratingdetails)
                        Info["RatingDetails"] = ratingdetails
                    except:
                        pass

                    #Additions
                    try:
                        details = soup2.findAll("div", class_="c1f85371f5 c56ea7427a")
                        print("FIRST STEP", len(details))
                        additions = []
                        for detail in details:
                            try:
                                #Criteria
                                criteria = detail.find("span", class_="a5a5a75131").text.strip()
                                print("STEP 2")

                                #Final Detail
                                if not criteria in additions:
                                    additions.append(criteria)
                            except:
                               pass


                        print(additions)
                        Info["Additions"] = additions
                    except:
                        pass

                    #Attractions
                    def FindAttractions():
                        try:
                            getLoc = None
                            lat = 0
                            lon = 0
                            if Info["Coordinates"] == None:
                                getLoc = geolocator.geocode(Info["Location"].split(",")[0])
                                lat = getLoc.latitude
                                lon = getLoc.longitude
                            else:
                                lat = Info["Coordinates"][0]
                                lon = Info["Coordinates"][1]
                            attractions = {}
                            print("Coordinates:", (lat, lon))
                            Categories = ["bus_stop", "station", "park", "mall"]
                            for categorie in Categories:
                                try:
                                    query = f"{categorie} near {lat}, {lon}"
                                    places = geolocator.geocode(query, exactly_one=False, limit=None)
                                    found = []
                                    if places:
                                        for place in places:
                                            try:
                                                place_coords = [place.latitude, place.longitude]
                                                place_name = place.address.split(",")[0]
                                                place_distance = geodesic((lat, lon), place_coords).kilometers
                                                #Make the distance easier to read
                                                if place_distance < 1:
                                                    place_distance = str(round(place_distance, 2) * 1000) + "m"
                                                else:
                                                    place_distance = str(round(place_distance, 2)) + "km"

                                                found.append([place_name, place_coords, place_distance])
                                            except:
                                                pass
                                    attractions[categorie] = found
                                except:
                                    pass


                            print(attractions)
                            Info["Attractions"] = attractions
                            hotelattractions = attractions
                        except:
                            pass

                    thread = threading.Thread(target = FindAttractions)
                    threads["Attractions"] = thread
                    

                    #Rooms
                    def FindRooms():
                        try:
                            headers = {
                               'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
                               'Accept': 'image/png',
                               'Accept-Encoding': 'gzip, deflate',
                               'Connection': 'keep-alive',
                               'Cache-Control': 'public, immutable'
                            }
                            response  = requests.get(Info["Link"], headers=headers)
                            roomsoup = BeautifulSoup(response.text, 'html.parser')

                            rb = roomsoup.find("div", {"id" : "pp-nav-room-selection"})
                            roomsboxes = rb.findAll("div", class_="room clx room_info_cta m_hp_rt_room_card__container u-clearfix js-room-card js-rt_block_view_count")
                            if len(roomsboxes) == 0:
                                print("WAY 1")
                                roomsboxes = rb.findAll("div", class_="room clx room_info_cta m_hp_rt_room_card__container u-clearfix js-room-card")
                            else:
                                print("WAY 2")
                            if len(roomsboxes) == 0:
                                roomsboxes = rb.findAll("div", class_="bui-card bui-spacer--medium js-no-date-room-rate db-card__room")
                                print("WAY 3")
                            if len(roomsboxes) == 0:
                                roomsboxes = rb.findAll("div", class_="room clx room_info_cta m_hp_rt_room_card__container u-clearfix js-room-card iteration_7")
                                print("WAY 4")

                            #if len(roomsboxes) == 0:
                                #webbrowser.open(Info["Link"])
                                #pyperclip.copy(str(roomsoup))
                        
                            print("FIRST STEP", len(roomsboxes))
                            rooms = []
                            for room in roomsboxes:
                                try:
                                    #Type
                                    Type = room.find("span", class_="room__title-text m_hp_rt_room_card__title").text.strip()
                                    print("STEP 2")

                                    #Number of Guests
                                    Guests = 1
                                    if room.find("span", class_="m_hp_rt_layout_change__max") != None:
                                        Guests = int(room.find("span", class_="m_hp_rt_layout_change__max").text.strip())
                                    else:
                                        Guests = len(room.findAll("svg", class_="bk-icon -fonticon-occupancy"))
                                    print("STEP 2.5")

                                    #Bed
                                    Bed = room.find("span", class_="m-rs-bed-display__bed-type-name").text.strip()
                                    print("STEP 3")

                                    #Additions
                                    additions = room.find("p", class_="room-highlighted-facilities u-font-size:12 u-margin-bottom:4 m_hp_rt_room_card__facilities-container").findAll("span", class_="hprt-facilities-facility")
                                    Additions = []
                                    for addition in additions:
                                        Additions.append(addition.find("span").text.strip())
                                    print("STEP 4")

                                    #Images
                                    Gallery = roomsoup.find('div', class_="bigPhoto")
                                    images = Gallery.findAll("li")
                                    print("GALLERY", len(images))
                                    Images = []
                                    for image in images:
                                         try:
                                             im = image["data-src-small"]
                                             if image.get("data-room-id"):
                                                 if image["data-room-id"] == room["data-room-id"]:
                                                     if not im in Images:
                                                         Images.append(im)
                                         except:
                                              pass

                                    print("STEP 5")

                                    #Final Detail
                                    rooms.append({"Type" : Type, "GuestsNumber" : Guests, "Bed" : Bed, "Additions" : Additions, "Images" : Images})
                                except:
                                   pass


                            print(rooms)
                            Info["Rooms"] = rooms
                        except:
                            pass

                    thread = threading.Thread(target = FindRooms)
                    threads["Rooms"] = thread
                    


                if Info["What"] == "Restaurant":
                    locinf = Info["Location"]
                    info = None
                    try:
                        info = soup2.find("div", class_="k7jAl miFGmb lJ3Kh")
                    except:
                        pass

                    #Menu
                    try:
                        #Menu
                        Info["Menu"] = info.find("a", class_="CsEnBe", href=True)["href"].split("q=",1)[1].split("&opi",1)[0]

                    except:
                        pass

                    #Phone
                    try:
                        #Phone
                        Info["Phone"] = info.find("button", {"class":"CsEnBe", "data-tooltip": 'Copy phone number'}).find("div", class_="Io6YTe fontBodyMedium kR99db fdkmkc").text.strip()
                        print("Phone:", Info["Phone"])
                    except:
                        pass

                    #Business
                    try:
                        BusinessTimes = info.find("div", class_="g2BVhd eoFzo").findAll("div", role = "img")
                        Business = {}
                        for businesstime in BusinessTimes:
                            text = businesstime["aria-label"]
                            if " at " in text:
                                btime = text.split("at ")[1]
                                btime = btime.replace("\u202f", "")
                                business = text.split(" busy")[0]
                                Business[btime] = business
                            else:
                                btime = "Currently"
                                business = text.split(" ")[1]
                                Business[btime] = business

                        Info["Business"] = Business
                        print("Business:", Business)
                    except:
                        pass

                    #Comments
                    try: 
                        #Comments
                        comments = info.findAll("div", class_="jftiEf fontBodyMedium")
                        print("FIRST STEP")
                        print(len(comments))
                        coms = []
                        for comment in comments:
                            print(comment)
                            searchplace = comment.find("div", class_="jJc9Ad")

                            #Icons
                            icon = searchplace.find("img", class_="NBa7we")["src"]
                            print("STEP 2")

                            #Title
                            title = searchplace.find("div", class_="WNxzHc qLhwHc").find("div", class_="d4r55").text.strip()
                            print("STEP 3")

                            #Comments
                            Text = searchplace.find("span", class_="wiI7pd").text.strip()
                            print("STEP 4")

                            #Final Comment
                            coms.append([icon, Text, title])


                        print(coms)
                        Info["Comments"] = coms
                    except:
                        pass

            time2 = datetime.datetime.now()
            print("TIME:", time2 - time1)

            @mainthread
            def Create():
                global CurrentOpenedTab, RecentTabs

                Button = MDIconButton(icon = "close", font_size = "2sp", pos_hint = {"center_x": 0.075,"center_y": 0.975}, size_hint = (0.1,0.1))
                Carousel = MyCarousel(pos_hint = {"center_x": 0.5,"center_y": 0.85}, size_hint = (1,0.3))
                Carousel.loop = True
                def CarouselMove(*args):
                    if not Carousel.is_focused and not Carousel.disabled:
                        Carousel.load_next()
                Clock.schedule_interval(CarouselMove, 3.0)
                #Create Menu
                Menu = None
                try:
                    if Info["Menu"] != "":
                        Menu = MDListItem(MDListItemLeadingIcon(icon = "food"),  MDListItemSupportingText(text = Info["Menu"][:20]))
                        Menu.bind(on_release=lambda instance: self.OpenSite(Site = Info["Menu"]))
                except:
                    pass

                #Create Phone
                Phone = None
                try:
                    if Info["Phone"] != "":
                        Phone = MDListItem(MDListItemLeadingIcon(icon = "phone"),  MDListItemSupportingText(text = Info["Phone"]))
                        Phone.bind(on_release=lambda instance: self.PhoneCall(phone = Info["Phone"]))
                except:
                    pass

                #Create Map
                mapview = None
                mapfilter = None
                MapCard = NoHoverMDCard(size_hint = (0.9, None), height = 0, theme_bg_color = "Custom", md_bg_color = [0,0,0,0], radius = [0,], opacity = 0)
                
                #Create Open Indicator
                OpenIndicator = None
                if Info["What"] == "Restaurant":
                    OpenIndicator = MDLabel(text = "[b]" + Info["Open"] + "[/b] \u2022" + Info["Closes"], adaptive_height = True, role = "large", padding = (30,0), markup = True)
                
                #Create Business
                BusinessTable = None
                if Info["Business"] != None:
                    VerticalLine = MDDivider(orientation = "vertical")
                    HorizontalLine = MDDivider()
                    steps = 2

                    Times = []
                    for time2 in range(0, len(Info["Business"].keys()), steps):
                        key = list(Info["Business"].keys())[time2]
                        txt = key
                        if txt == "Currently":
                            txt = "Now"
                        else:
                            txt = txt[:len(txt) - 1]
                            if "a.m." in txt:
                                txt = txt.replace("a.m.", "h")
                                if txt == "12h":
                                    txt = "24h"

                            if "p.m." in txt:
                                txt = txt.replace("p.m.", "")
                                if txt == "12":
                                    txt = "12h"
                                else:
                                    print("TXT:",txt)
                                    txt = str(int(txt) + 12) + "h"

                        text = MDLabel(text = txt, role = "small", font_style = "Label", theme_font_size = "Custom", font_size = "8sp", adaptive_height = True)
                        Times.append(text)

                    #Times = (MDLabel(text = "6am", role = "small", adaptive_height = True), MDLabel(text = "9am", role = "small", adaptive_height = True), MDLabel(text = "12pm", role = "small", adaptive_height = True), MDLabel(text = "3pm", role = "small", adaptive_height = True), MDLabel(text = "6pm", role = "small", adaptive_height = True), MDLabel(text = "9pm", role = "small", adaptive_height = True))
                    Hours = MDStackLayout(HorizontalLine, MDGridLayout(*Times, rows = 1, cols = len(Times), adaptive_height = True), pos_hint = {"center_x": 0.5,"center_y": 0.1}, size_hint_x = 0.8, adaptive_height = True)

                    size = "10sp"
                    Percents = (MDLabel(text = "100%", role = "small", font_style = "Label", theme_font_size = "Custom", font_size = size, adaptive_size = True), MDLabel(text = "75%", role = "small", font_style = "Label", theme_font_size = "Custom", font_size = size, adaptive_size = True), MDLabel(text = "50%", role = "small", font_style = "Label", theme_font_size = "Custom", font_size = size, adaptive_size = True), MDLabel(text = "25%", role = "small", font_style = "Label", theme_font_size = "Custom", font_size = size, adaptive_size = True))
                    Business = MDGridLayout(MDGridLayout(*Percents, rows = 4, cols = 1, adaptive_size = True), VerticalLine, pos_hint = {"center_x": 0.5,"center_y": 0.5}, rows = 1, cols = 2, adaptive_height = True)

                    
                    Tables = []
                    for table in range(0, len(Info["Business"].keys()), steps):
                        box = MDCard(size_hint_x = 0.9, theme_bg_color = "Custom", md_bg_color = (1, 0.65, 0, 1))
                        key = list(Info["Business"].keys())[table]
                        if key == "Currently":
                            box.md_bg_color = (0.65, 1, 0.65, 1)

                        value = Info["Business"][key].replace("%","")
                        size_y = (float(value) * 0.01)
                        box.size_hint_y = size_y
                        roundness = 0
                        if size_y != 0.0:
                            roundness = 25.0 / size_y
                        box.radius = [roundness,roundness,0,0]
                        if size_y != 0.0:
                            Tables.append(MDBoxLayout(box))
                        else:
                            Tables.append(MDBoxLayout())

                    Graphics = MDGridLayout(*Tables, rows = 1, cols = len(Tables), pos_hint = {"center_x": 0.5,"center_y": 0.5}, size_hint_x = 0.8, size_hint_y = 0.6)
                    
                    BusinessTable = MDRelativeLayout(Hours, Business, Graphics, adaptive_height = True)
                
                #Create UI
                List = MDListItem(MDListItemHeadlineText(text = Info["Name"]), MDListItemSupportingText(text = Info["Class"] + " \u2022 " + Info["Location"]), MDListItemTertiaryText(text = Info["Rating"] + " \u2022 " + Info["RatingNumber"]), MDListItemTrailingSupportingText(text = Info["Price"]), opacity = 0.5)
                Layout = MDStackLayout(OpenIndicator, List, MapCard, Menu, Phone, BusinessTable, orientation='lr-tb', padding=dp(10), spacing=dp(2), adaptive_height = True)
                View = MDScrollView(Layout, do_scroll_x = False, pos_hint = {"center_x": 0.5, "center_y": 0.45})
                try:
                    getLoc = None
                    lat = 0
                    lon = 0
                    if Info["Coordinates"] == None:
                        getLoc = geolocator.geocode(Info["Location"].split(",")[0])
                        lat = getLoc.latitude
                        lon = getLoc.longitude
                    else:
                        lat = Info["Coordinates"][0]
                        lon = Info["Coordinates"][1]
                    mapview = MapView(map_source = MapSource(url="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}"),zoom=13, lat=lat, lon=lon)
                    
                    #Map filter
                    if mapview != None:
                        colsnum = 3
                        rowsnum = 3

                        mapfilter = MDGridLayout(rows = rowsnum, cols = colsnum, adaptive_height = True)
                    
                    #Main marker
                    mainmarker = MapMarker(lon=lon,lat=lat)            
                    mapview.add_marker(mainmarker)

                    #Attractions markers
                    def FinishMap(mapfilter, mapview, MapCard, List, View):
                        threads["Attractions"].start()
                        threads["Attractions"].join()
                        def FilterMarkers(acceptable_type, markers):
                            for child in markers:
                                try:
                                    if isinstance(child, LabeledMapMarker):
                                        if acceptable_type != "All":
                                            #print(child.place_type + " : ", acceptable_type)
                                            if child.place_type == acceptable_type:
                                                child.disappear = False
                                            else:
                                                child.disappear = True
                                        else:
                                            child.disappear = False
                                except:
                                    pass
                        @mainthread
                        def ShowIt():
                            try:
                                if Info["Attractions"] != None:
                                   markers = []
                                   for attractiontype in Info["Attractions"].keys():
                                        #Markers
                                        for attraction in Info["Attractions"][attractiontype]:
                                            try:
                                                attractionmarker = LabeledMapMarker(source = "map-marker.png",lon=attraction[1][1],lat=attraction[1][0], place_name=attraction[0], place_type=attractiontype, distance=attraction[2])            
                                                mapview.add_marker(attractionmarker)
                                                markers.append(attractionmarker)
                                            except:
                                                pass

                                   if mapfilter != None:
                                       button = MDButton(MDButtonText(text = "All"))
                                       mapfilter.add_widget(button)
                                       button.bind(on_release = lambda x: FilterMarkers(acceptable_type = "All", markers = markers))

                                   for attractiontype in Info["Attractions"].keys():
                                        button = None

                                        #Filter Button
                                        if mapfilter != None:
                                            if len(Info["Attractions"][attractiontype]) > 0:
                                                button = MDButton(MDButtonText(text = attractiontype))
                                                mapfilter.add_widget(button)

                                        #Bind Filter Button
                                        if button != None:
                                            button.bind(on_release = lambda x, attractiontype=attractiontype: FilterMarkers(acceptable_type = attractiontype, markers = markers))

                                #Update Map Size
                                if mapfilter != None:
                                    numberofchildren = len(mapfilter.children)

                                    colsnum = 3
                                    rowsnum = math.ceil(numberofchildren / colsnum)

                                    mapfilter.cols = colsnum
                                    mapfilter.rows = rowsnum

                                    if mapview != None:
                                        mapview.size_hint_y = 0.9 - (0.1 * rowsnum)

                                MapCard.add_widget(MDStackLayout(mapfilter,mapview))
                                anim = Animation(opacity = 1, d = 1).start(List)
                                List.bind(on_release=lambda instance: self.OpenOrCloseExpansionPanel(Panel = MapCard, ScrollView = View))

                            except:
                                pass
                        ShowIt()
                    if Info["What"] == "Hotel":
                        thr = threading.Thread(target = FinishMap, args = (mapfilter, mapview, MapCard, List, View))
                        thr.start()
                except:
                    mapview = MapView(map_source = MapSource(url="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}"),zoom=13, lat=latitude, lon=longitude)

                #Create UI
                if Info["What"] != "Hotel":
                    List.opacity = 1
                    MapCard.add_widget(MDStackLayout(mapfilter,mapview))
                    List.bind(on_release=lambda instance: self.OpenOrCloseExpansionPanel(Panel = MapCard, ScrollView = View))
                
                #Create Rating Details
                Lines = []
                if Info["RatingDetails"] != None:
                    RatingDetails = MDGridLayout(rows = 3, cols = 3, adaptive_height = True)
                    for detail in Info["RatingDetails"]:

                        #Box
                        Box = MDStackLayout(adaptive_height = True)

                        #Text
                        Text = MDLabel(text = detail[0], role = "small", theme_font_name = "Custom", font_name = "Text", adaptive_height = True)

                        #Line
                        Line = MDLinearProgressIndicator(value = 0, size_hint = (0.5, None))
                        Lines.append([Line, float(detail[1]) * 10])

                        #Assemble
                        Box.add_widget(Text)
                        Box.add_widget(Line)
                        RatingDetails.add_widget(Box)

                    Layout.add_widget(RatingDetails)
                    Space = MDLabel(text = " ", role = "small", theme_font_name = "Custom", font_name = "Text", adaptive_height = True)
                    Layout.add_widget(Space)

                #Create Additions
                AdditionsBox = None
                if Info["Additions"] != None:
                    if len(Info["Additions"]) > 0:
                        colsnum = 2
                        rowsnum = math.ceil(len(Info["Additions"]) / colsnum)
                        AdditionsBox = MDGridLayout(rows = rowsnum, cols = colsnum, adaptive_height = True, spacing = 5)
                        for Addition in Info["Additions"]:
                            Icon = None
                            if Addition in CriteriaIcons.keys():
                                Icon = MDIcon(icon = CriteriaIcons[Addition], theme_font_size = "Custom", font_size = "20sp", size_hint=(None, None))
                            Chip = MDBoxLayout(MDGridLayout(Icon, MDLabel(text = Addition, role = "small", theme_font_name = "Custom", font_name = "Text", adaptive_size = True), rows = 1, cols = 2, adaptive_size = True), adaptive_size = True)
                            Chip.opacity = 0
                            AdditionsBox.add_widget(Chip)

                        #Assemble
                        Layout.add_widget(MDDivider()) #Divider
                    
                        Space = MDLabel(text = " ", role = "small", theme_font_name = "Custom", font_name = "Text", adaptive_height = True)
                        Layout.add_widget(Space)
                    
                        Layout.add_widget(AdditionsBox) #ADDITIONS
                    
                        Space = MDLabel(text = " ", role = "small", theme_font_name = "Custom", font_name = "Text", adaptive_height = True)
                        Layout.add_widget(Space)
                    
                        Layout.add_widget(MDDivider()) #Divider
                    
                        Space = MDLabel(text = " ", role = "small", theme_font_name = "Custom", font_name = "Text", adaptive_height = True)
                        Layout.add_widget(Space)
                
                #Create Comments
                if Info["Comments"] != None:
                    if len(Info["Comments"]) > 0:
                        
                        #Comments Analysis
                        CommentsRatio = 0
                        CommentsInfoBox = MDGridLayout(rows = 1, cols = 3, adaptive_height = True)
                        PosNum = MDLabel(text = "[font=Emoji]👍[/font]", role = "medium", theme_font_name = "Custom", adaptive_height = True, markup = True)
                        PosBox = MDCard(PosNum, theme_bg_color = "Custom", md_bg_color = [0,0,0,0], radius = [0,], ripple_behavior = True, adaptive_height = True)
                        NegNum = MDLabel(text = "[font=Emoji]👎[/font]", role = "medium", theme_font_name = "Custom", adaptive_height = True, markup = True)
                        NegBox = MDCard(NegNum, theme_bg_color = "Custom", md_bg_color = [0,0,0,0], radius = [0,], ripple_behavior = True, adaptive_height = True)
                        RatioText = MDLabel(text = " ", role = "medium", theme_font_name = "Custom", adaptive_height = True, markup = True)
                        RatioBox = MDCard(RatioText, theme_bg_color = "Custom", md_bg_color = [0,0,0,0], radius = [0,], ripple_behavior = True, adaptive_height = True)
                        CommentsInfoBox.add_widget(PosBox)
                        CommentsInfoBox.add_widget(NegBox)
                        CommentsInfoBox.add_widget(RatioBox)
                        Layout.add_widget(CommentsInfoBox)
                        Ratio = [0,0]
                        
                        #Display Comments
                        CommentsBox = MDStackLayout(orientation='lr-tb', padding=dp(10), spacing=dp(0.5), adaptive_height = True)
                        def WriteComments(CommentType = "All", Initial = True):
                            if len(CommentsBox.children) > 0:
                                CommentsBox.clear_widgets()
                            for comment in Info["Comments"]: 
                                #Comment
                                GivenOpinion = AnalyseComment(comment[1])
                                text = comment[1]
                                for PosWord in GivenOpinion["Positive Words"]:
                                    try:
                                        parts = text.lower().split(PosWord, 1)
                                        p1 = len(parts[0])

                                        wordtoput = text[p1:][:len(PosWord)]

                                        parts = text.split(wordtoput, 1)
                                        txt = parts[0] + "[u]" + wordtoput + "[/u]" + parts[1]
                                        text = txt
                                        print(txt)
                                    except:
                                        pass
                                
                                Text = MDLabel(text = text, role = "small", theme_font_name = "Custom", font_name = "Text", adaptive_height = True, markup = True)
                    
                                #Header
                                Image = FitImage(source = comment[0], size_hint = (0.1, None), radius = [45,])
                                Image.bind(width=self.update_height)
                                Title = MDLabel(text = comment[2], role = "small", theme_font_name = "Custom", font_name = "Text", bold = True, adaptive_height = True)
                                Opinion = None
                                if GivenOpinion["Opinion"] == "Positive Opinion":
                                    Ratio[0] += 1
                                    Opinion = MDLabel(text = GivenOpinion["Opinion"], role = "small", opacity = 0.8, theme_font_name = "Custom", font_name = "Text", adaptive_height = True)
                                if GivenOpinion["Opinion"] == "Negative Opinion":
                                    Ratio[1] += 1
                                    Opinion = MDLabel(text = GivenOpinion["Opinion"], role = "small", opacity = 0.8, theme_font_name = "Custom", font_name = "Text", adaptive_height = True)

                                Header = MDBoxLayout(Image, MDStackLayout(Title, Opinion, orientation='lr-tb', adaptive_height = True), spacing = 5,adaptive_height = True)
                                Space = MDLabel(text = " ", role = "small", theme_font_name = "Custom", font_name = "Text", adaptive_height = True)

                                #Assemble
                                Panel = MDBoxLayout(MDStackLayout(Header, Text, Space, orientation='lr-tb', adaptive_height = True), adaptive_height = True)
                                if not Initial:
                                    Panel.opacity = 0
                                if CommentType == "All":
                                    CommentsBox.add_widget(Panel)
                                elif GivenOpinion["Opinion"] == CommentType:
                                    CommentsBox.add_widget(Panel)

                            if not Initial:
                                def ShowItems():
                                    lenght = len(CommentsBox.children)
                                    for i in range(0, lenght, 1):
                                        children = CommentsBox.children[lenght - 1 - i]
                                        Animation(opacity = 1, d = 1.5).start(children)
                                        time.sleep(0.5)
                                animthread = threading.Thread(target=ShowItems)
                                animthread.start()

                        WriteComments()

                        Layout.add_widget(MDBoxLayout(CommentsBox, id = "CommentsBox", adaptive_height = True))

                        #Update Comments Analysis
                        PosNum.text += "[font=Text]" + str(Ratio[0]) + "[/font]"
                        PosBox.bind(on_release = lambda x: WriteComments("Positive Opinion", False))
                        NegNum.text += "[font=Text]" + str(Ratio[1]) + "[/font]"
                        NegBox.bind(on_release = lambda x: WriteComments("Negative Opinion", False))
                        percent = round(Ratio[0] / (Ratio[0] + Ratio[1]) * 100)
                        RatioText.text = "[font=Emoji]👍[/font][font=Text]/[/font][font=Emoji]👎[/font][font=Text]" + str(percent) + "%[/font]"
                        RatioBox.bind(on_release = lambda x: WriteComments("All", False))
                
                #Hotel Rooms
                HotelRoomsButton = None
                HotelRoomsBox = None
                def FinishRooms(rellayout, rellayout2, View):
                    threads["Rooms"].start()
                    threads["Rooms"].join()
                    print(Info["Rooms"])
                    if Info["Rooms"] != None:
                        if Info["What"] == "Hotel" and len(Info["Rooms"]) > 0:

                            @mainthread
                            def ShowRooms():
                                try:
                                    #UI
                                    HotelRoomsBox = NoHoverMDCard(pos_hint = {"center_x": 0.5, "center_y": 0.5}, size_hint = (1, 1), theme_bg_color = "Custom", md_bg_color = [0,0,0,0.4], radius = [0,])
                                    HotelRoomsBox.disabled = True
                                    HotelRoomsBox.opacity = 0
                                    HotelRoomsLayout = NoHoverMDCard(pos_hint = {"center_x": 0.5, "center_y": 0.5}, size_hint = (1, 1), theme_bg_color = "Custom", md_bg_color = [0,0,0,0.8], radius = [0,])
                                    HotelRoomsBox.add_widget(HotelRoomsLayout)
                                    rellayout2.add_widget(HotelRoomsBox)
                                    colsnum = 1
                                    rowsnum = math.ceil(len(Info["Additions"]) / colsnum * 1.25) 
                                    roomstableaulayout = MDRelativeLayout()
                                    HotelRoomsLayout.add_widget(roomstableaulayout)
                                    Grid = MDGridLayout(rows=rowsnum,cols=colsnum, spacing = 25, padding = 25, adaptive_height = True)
                                    #scroller = Scroller()
                                    #scroller.limits = [5,4]
                                    #scroller.add_widget(Grid)
                                    roomstableaulayout.add_widget(MDScrollView(Grid, do_scroll_x = False))#scroller)

                                    #Rooms
                                    for room in Info["Rooms"]:
                                        Room = MDBoxLayout(size_hint = (1.2 / colsnum, None), height = 250, adaptive_height = True) #MDCard(size_hint = (1.2 / colsnum, None), height = 250, style = "elevated")
                                        RoomGrid = MDStackLayout(adaptive_height = True)

                                        #Carousel
                                        RoomCarousel = None
                                        if len(room["Images"]) > 0:
                                            RoomCarousel = ClippedCarousel(pos_hint = {"center_x": 0.5, "center_y": 0.8}, size_hint = (1, 0.4), loop = True)
                                            RoomGrid.add_widget(RoomCarousel)
                                            for image in room["Images"]:
                                                RoomCarousel.add_widget(FitImage(source = image))
                                        else:
                                            RoomCarousel = MDBoxLayout(MDIcon(icon = "image-off", pos_hint = {"center_x": 1, "center_y": 0.5}, theme_font_size = "Custom", font_size = "96sp"), pos_hint = {"center_x": 0.5, "center_y": 0.8}, size_hint = (1, 0.4))
                                            RoomGrid.add_widget(RoomCarousel)
                            
                                        #Info
                                        RoomInfoBox = NoHoverMDCard(pos_hint = {"center_x": 0.5, "center_y": 0.3}, size_hint = (1, 0.6), style = "elevated", radius = [0,0,25,25], adaptive_height = True)
                                        RoomInfoGrid = MDStackLayout(adaptive_height = True)
                                        RoomInfoBox.add_widget(RoomInfoGrid)
                            
                                        #Title / Type
                                        GuestsNum = " [font=Emoji]"
                                        for i in range(0, room["GuestsNumber"], 1):
                                            GuestsNum += "👤"
                                        GuestsNum += "[/font]"
                                        Type = MDLabel(text = room["Type"] + GuestsNum, theme_font_name = "Custom", font_name = "Text", role = "medium", bold = True, adaptive_height = True, markup = True)
                                        RoomInfoGrid.add_widget(Type)

                                        #Bed
                                        Bed = MDLabel(text = room["Bed"], theme_font_name = "Custom", font_name = "Text", adaptive_height = True)
                                        RoomInfoGrid.add_widget(Bed)

                                        #Additions
                                        RoomCriteriaIcons = {
                                             "Air conditioning" : "fan",
                                             "City view" : "city",
                                             "View" : "city",
                                             "Free WiFi" : "wifi",
                                             "Ensuite bathroom" : "shower",
                                             "Private bathroom" : "shower",
                                             "Bath or shower" : "shower",
                                             "Flat-screen TV" : "television",
                                             "Entire studio" : "home",
                                             "Entire apartment" : "home",
                                             "Room" : "home",
                                             "Private suite" : "home",
                                             "Microwave" : "microwave",
                                             "Heating" : "fire",
                                             "Cleaning products" : "wipe",
                                             "Coffee machine" : "coffee",
                                             "Tea/Coffee maker" : "coffee",
                                             "Refrigerator" : "fridge",
                                             "Iron" : "iron",
                                             "Ironing facilities" : "iron",
                                             "Hairdryer" : "hair_dryer",
                                             "Electric kettle" : "kettle",
                                             "Dishwasher" : "dishwasher",
                                             "Desk" : "desk",
                                             "Seating Area" : "chair",
                                             "Wardrobe or closet" : "closet"
                                        }
                                        colsnum = 1
                                        rowsnum = math.ceil(len(room["Additions"]) / colsnum)
                                        AdditionBox = MDGridLayout(rows = rowsnum, cols = colsnum, padding = 5, adaptive_height = True)
                                        RoomInfoGrid.add_widget(AdditionBox)
                                        for Addition in room["Additions"]:
                                            AdditionText = MDLabel(text = Addition, theme_font_name = "Custom", font_name = "Text", role = "small", adaptive_height = True)
                
                                            Icon = None
                                            if Addition in RoomCriteriaIcons.keys():
                                                Icon = MDIcon(icon = RoomCriteriaIcons[Addition], theme_font_size = "Custom", font_size = "20sp", size_hint=(None, None))
                
                                            adbox = MDGridLayout(Icon, AdditionText, rows = 1, cols = 2, adaptive_height = True)
                                            AdditionBox.add_widget(adbox)

                                        #Assemble
                                        RoomGrid.add_widget(RoomInfoBox)
                                        Room.add_widget(RoomGrid)
                                        Grid.add_widget(Room)

                                    #Close Button
                                    def OpenBox(*args):
                                        if HotelRoomsBox.disabled:
                                            HotelRoomsBox.disabled = False
                                            Animation(opacity = 1, d = 0.5).start(HotelRoomsBox)
                                            HotelRoomsButton.pos_hint = {"center_x": 0.5, "center_y": -0.1}
                                            HotelRoomsButton.opacity = 0
                                            HotelRoomsButton.disabled = True
                                            Carousel.disabled = True
                                            View.disabled = True
                                        else:
                                            HotelRoomsBox.disabled = True
                                            Carousel.disabled = False
                                            View.disabled = False
                                            HotelRoomsButton.pos_hint = {"center_x": 0.5, "center_y": 0.1}
                                            HotelRoomsButton.opacity = 1
                                            HotelRoomsButton.disabled = False
                                            Animation(opacity = 0, d = 0.5).start(HotelRoomsBox)

                                    CloseButton = MDIconButton(icon = "close", font_size = "2sp", pos_hint = {"center_x": 0.075,"center_y": 0.975}, size_hint = (0.1,0.1))
                                    roomstableaulayout.add_widget(CloseButton)
                                    CloseButton.bind(on_release = OpenBox)
                        
                                    #Button
                                    HotelRoomsButton = MDButton(MDButtonIcon(icon = "bed"), MDButtonText(text = "Rooms"), pos_hint = {"center_x": 0.5, "center_y": 0.1}, size_hint = (0.8, 0.2), style = "outlined")
                                    rellayout.add_widget(HotelRoomsButton)
                                    #HotelRoomsButton.bind(on_release = lambda x: self.ShowHotelRooms(Info = Info["Rooms"]))

                                    HotelRoomsButton.bind(on_release = OpenBox)

                                    def ControlButton(self, value):
                                        duration = 0.25
                                        if HotelRoomsBox.disabled:
                                            if value == 1:
                                                if HotelRoomsButton.disabled:
                                                    HotelRoomsButton.disabled = False
                                                    Animation(opacity = 1, d = duration).start(HotelRoomsButton)
                                                    Animation(pos_hint={"center_x": 0.5, "center_y": 0.1}, d = duration).start(HotelRoomsButton)
                                            else:
                                                if not HotelRoomsButton.disabled:
                                                    HotelRoomsButton.disabled = True
                                                    Animation(opacity = 0, d = duration).start(HotelRoomsButton)
                                                    Animation(pos_hint={"center_x": 0.5, "center_y": -0.1}, d = duration).start(HotelRoomsButton)

                                    View.bind(scroll_y = ControlButton)
                                except:
                                    HotelRoomsButton = None
                                    HotelRoomsBox = None

                            ShowRooms()

                #Assemble
                rellayout = MDRelativeLayout(View)

                InfoCard = MDBoxLayout(rellayout, pos_hint = {"center_x": 0.5, "center_y": 0.375}, size_hint = (1, 0.75), md_bg_color = self.theme_cls.backgroundColor, radius = [25,25,0,0])
                LeftButton = MDIconButton(icon="invisible-png.png",pos_hint = {"center_x": 0.1, "center_y": 0.5}, size_hint = (0.025, 1))
                LeftButton.bind(on_press = lambda instance : self.ChangeTab(Direction="Left", OpenWindow = OpenWindow))
                RightButton = MDIconButton(icon="invisible-png.png",pos_hint = {"center_x": 0.9, "center_y": 0.5}, size_hint = (0.025, 1))
                RightButton.bind(on_press = lambda instance : self.ChangeTab(Direction="Right", OpenWindow = OpenWindow))

                rellayout2 = MDRelativeLayout(Carousel, InfoCard, Button, LeftButton, RightButton)

                if Info["What"] == "Hotel":
                    th = threading.Thread(target = FinishRooms, args = (rellayout, rellayout2, View))
                    th.start()

                Card = MDBoxLayout(MDBoxLayout(rellayout2),pos_hint = {"center_x": 0.5, "center_y": 0.5}, size_hint = (1, 1), radius = [0,])
                
                Inf = []
                if Info["Link"] == "":
                    Inf = Info["Images"]
                else:
                    if Info["What"] == "Hotel":
                        Gallery = soup2.find('div', class_="k2-hp--gallery-header bui-grid__column bui-grid__column-9")
                        for image in Gallery.findAll('img', class_="e3fa9175ee d354f8f44f ba6d792fd4 b1a5e281e7"):
                            Inf.append(image["src"])
                    if Info["What"] == "Restaurant":
                        info = soup2.find("div", class_="k7jAl miFGmb lJ3Kh")
                        Gallery = info.find("div", class_="dryRY")
                        for image in Gallery.findAll('img', class_="DaSXdd"):
                            Inf.append(image["src"])
                Info["Images"] = Inf
                for Image in Inf:
                    Carousel.add_widget(FitImage(source = Image, radius = [0,]))

                Button.bind(on_release = lambda instance : self.CloseTab(OpenWindow = OpenWindow))
                
                #Animate
                for Line in Lines:
                    anim = Animation(value = Line[1], t = "easing_decelerated", d = 1.5)
                    anim.start(Line[0])

                if AdditionsBox != None:
                    def ShowItems():
                        lenght = len(AdditionsBox.children)
                        for i in range(0, lenght, 1):
                            children = AdditionsBox.children[lenght - 1 - i]
                            Animation(opacity = 1, d = 1.5).start(children)
                            time.sleep(0.5)
                    animthread = threading.Thread(target=ShowItems)
                    animthread.start()

                #Tabs
                if not Info in RecentTabs:
                    RecentTabs.append(Info)
                else:
                    RecentTabs.remove(Info)
                    RecentTabs.append(Info)
                self.root.ids.TabBox.add_widget(Card)
                CurrentTab = 1
                self.root.ids.ScreenManager.current = 'Tab'

            Create()

        thread5 = threading.Thread(target=Func)
        thread5.start()

    def OpenRecommendedPlaceTab(self, *args, Info, OpenWindow = 'Home Screen'):
        Button = MDIconButton(icon = "close", font_size = "2sp", pos_hint = {"center_x": 0.075,"center_y": 0.975}, size_hint = (0.1,0.1))
        Image = FitImage(source = Info["ImageUrl"],pos_hint = {"center_x": 0.5,"center_y": 0.85}, size_hint = (1,0.3))
        Name = MDLabel(text = Info["Name"], theme_font_name = "Custom", font_name = "Title", size_hint = (0.9,None), adaptive_height = True, pos_hint = {"center_x": None,"center_y": None})
        Description = MDLabel(text = Info["Description"], theme_font_name = "Custom", font_name = "Text", size_hint = (0.9,None), adaptive_height = True, pos_hint = {"center_x": None,"center_y": None})
        InfoCard = MDBoxLayout(MDScrollView(MDBoxLayout(MDStackLayout(Name,Description, orientation='lr-tb', padding=dp(10), spacing=dp(5),adaptive_height = True),adaptive_height = True)),pos_hint = {"center_x": 0.5, "center_y": 0.375}, size_hint = (1, 0.75), md_bg_color = self.theme_cls.backgroundColor, radius = [25,25,0,0])
        Card = MDBoxLayout(MDBoxLayout(MDRelativeLayout(Image, Button, InfoCard)),pos_hint = {"center_x": 0.5, "center_y": 0.5}, size_hint = (1, 1), radius = [0,], id = "Tab")
        Button.bind(on_press = lambda instance : self.CloseTab(OpenWindow = OpenWindow))
        self.root.ids.TabBox.add_widget(Card)
        self.root.ids.ScreenManager.current = 'Tab'
    def Startup(self, *args):
        self.root.ids.ScreenManager.transition = ScreenTransition(direction='left')
        self.root.ids.ScreenManager.current = 'Home Screen'
        ToDelete = {}
        RecommendedPlace = FindRecommendedPlaces()
        @mainthread
        def CreateLoading():
            #Assign Functions
            self.root.ids.HomeButton.bind(on_release = lambda instance: self.change_screen("Home Screen"))
            self.root.ids.SettingsButton.bind(on_release = lambda instance: self.change_screen("Settings Screen"))
            panel = self.root.ids.SearchBarExpansionPanel
            panel2 = self.root.ids.SearchBarPropositions
            blur = self.root.ids.SearchBarExpansionPanelBlur
            self.root.ids.SearchBar.bind(text = lambda x, y: self.ControlSearchBarPropositions(instance=x,panel=panel2,blur=blur))
            self.root.ids.SearchBar.bind(focus = lambda x, y: self.ControlSearchBar(instance=x,focused=y,panel=panel,panel2=panel2,blur=blur))
            self.root.ids.HotelChip.bind(on_release = lambda instance: self.Search("Hotel"))
            self.root.ids.HotelChip.bind(on_release = lambda instance: self.DisableSearchPanel(instance = instance, blur = blur))
            self.root.ids.RestaurantChip.bind(on_release = lambda instance: self.Search("Restaurant"))
            self.root.ids.RestaurantChip.bind(on_release = lambda instance: self.DisableSearchPanel(instance = instance, blur = blur))
            self.root.ids.DestinationChip.bind(on_release = lambda instance: self.Search("Destination"))
            self.root.ids.DestinationChip.bind(on_release = lambda instance: self.DisableSearchPanel(instance = instance, blur = blur))

            #Create Header
            Image = self.root.ids.RecommendedPlaceImage
            ImageUrl = RecommendedPlace["ImageUrl"]
            Palette = GetPaletteFromImage(ImageUrl)
            print("PALETTE:", Palette)
            img = FitImage(source = ImageUrl)
            Image2 = self.root.ids.nav_image
            Image2.parent.shadow_color = Palette
            Image.shadow_color = Palette
            Image2.source = ImageUrl
            Layout = MDRelativeLayout()
            Title1 = MDLabel(text = "Visit " + RecommendedPlace["Name"], theme_font_name = "Custom", font_name = 'Discover', size_hint = (0.9,0.175), pos_hint = {"center_x": 0.51,"center_y": 0.79}, halign = "center", theme_text_color = "Custom", text_color = [223 / 255, 230 / 255, 233 / 255,1])
            Title1.bind(size=self.on_size6)
            Title = MDLabel(text = "Visit " + RecommendedPlace["Name"], theme_font_name = "Custom", font_name = 'Discover', size_hint = (0.9,0.175), pos_hint = {"center_x": 0.5,"center_y": 0.8}, halign = "center", theme_text_color = "Custom", text_color = [45 / 255, 52 / 255, 54 / 255, 1])
            Title.bind(size=self.on_size6)
            Blackout = MDCard(theme_bg_color = "Custom",md_bg_color = [0,0,0,0.5], radius = [0,], size_hint = (1,1),pos_hint = {"center_x": 0.5,"center_y": 0.5}, ripple_behavior = True)
            Blackout.bind(on_release = lambda instance: self.OpenRecommendedPlaceTab(Info = RecommendedPlace))
            Layout.add_widget(img)
            Layout.add_widget(Blackout)
            Layout.add_widget(Title)
            Layout.add_widget(Title1)
            Image.add_widget(Layout)

            #Swipe Effect
            self.root.ids.Hotels.bind(on_swipe = lambda instance: self.AnimateSwiper(swiper = self.root.ids.Hotels))
            self.root.ids.Restaurants.bind(on_swipe = lambda instance: self.AnimateSwiper(swiper = self.root.ids.Restaurants))
            
            """
            self.root.ids.SegmentedButton.add_widget(MDBoxLayout(
                MDSegmentedButton(
                            MDSegmentedButtonItem(
                                padding=(dp(12), dp(0)),
                                MDSegmentButtonIcon(
                                    icon = "language-swift")),

                            MDSegmentedButtonItem(
                                padding=(dp(12), dp(0)),
                                MDSegmentButtonIcon(
                                    icon = "food"))),
                            type="small"
            ))
            """

            #Create Cards
            Swipers = [self.root.ids.Hotels, self.root.ids.Restaurants, self.root.ids.Destinations]
            Carousels = [self.root.ids.Destinations]
            for Swiper in Swipers:
                for i in range(0,5,1):
                    Spinner = MDCircularProgressIndicator(
                        size_hint=(0.25, 0.5),
                        pos_hint={'center_x': .5, 'center_y': .5},
                    )
                    Card = GradientBoxAnimated(MDRelativeLayout(Spinner), radius = [20,20,20,20], size_hint_y = 0.6)
                    if not Swiper in Carousels:
                        Obj = MDSwiperItem(Card)
                        ToDelete[Obj] = Swiper
                        Swiper.add_widget(Obj)
                        self.AnimateSwiper(swiper = Swiper)
                    else:
                        Obj = Card
                        ToDelete[Obj] = Swiper
                        Swiper.add_widget(Obj)
        CreateLoading()

        #Create Destinations
        @mainthread
        def CreateDestinations():
            for todel in ToDelete.keys():
                swiper = ToDelete[todel]
                if swiper == self.root.ids.Destinations:
                    swiper.remove_widget(todel)

            for i in range(0,5,1):
                if i < len(RecommendedPlaces):
                    #Extract words from name
                    name = RecommendedPlaces[i]["Name"].split()
                    Name = ""
                    WordNum = 3
                    LettersNum = 25 - 3
                    for w in range(0,WordNum,1):
                        if w < len(name):
                            n = Name + name[w] + " "
                            if len(n) > LettersNum:
                                Name = n[:LettersNum]
                            else:
                                Name = n
                    if WordNum < len(name) or len(Name) > LettersNum - 3:
                        Name += "..."

                    #Extract words from address
                    AddressNum = 3
                    address = RecommendedPlaces[i]["Description"].split()
                    Address = ""
                    for w in range(0,AddressNum,1):
                        if w < len(address):
                            Address += address[w] + " "
                    if AddressNum < len(address):
                        Address += "..."

                    #Create UI
                    Label = MDLabel(text = Name, size = (1,0.4), pos_hint = {"center_x": 0.55,"center_y": 0.1})
                    Label.bind(size=self.on_size)
                    Footer = MDBoxLayout(radius = [0,0,20,20], size_hint = [1, 0.2], md_bg_color = self.theme_cls.backgroundColor, pos_hint = {"center_x": 0.5,"center_y": 0.1}, id = "InfoCont")
                    Card = RippleBoxLayout(MDRelativeLayout(FitImage(source = RecommendedPlaces[i]["ImageUrl"], radius = [20,], pos_hint = {"center_x": 0.5,"center_y": 0.5}, size_hint = (0.99,0.99)), Footer, Label),radius = [20,20,20,20], size_hint = [None, None])
                    Card.on_release = lambda instance, i=i: self.OpenRecommendedPlaceTab(Info = RecommendedPlaces[i])
                    self.root.ids.Destinations.add_widget(Card)
                else:
                    break

        CreateDestinations()

        #Create Hotels
        Colors = {0: [214 / 255, 48 / 255, 49 / 255,1],1: [214 / 255, 48 / 255, 49 / 255,1],2:[255 / 255, 118 / 255, 117 / 255,1],3:[253 / 255, 203 / 255, 110 / 255,1],4: [0 / 255, 184 / 255, 148 / 255,1],5:[85 / 255, 239 / 255, 196 / 255, 1]}
        hotels = FindHotels(Num=5,Location=City)
        @mainthread
        def CreateHotels():
            for todel in ToDelete.keys():
                swiper = ToDelete[todel]
                if swiper == self.root.ids.Hotels:
                    swiper.remove_widget(todel)

            for i in range(0,5,1):
                if i < len(hotels):
                    #Extract words from name
                    name = hotels[i]["Name"].split()
                    Name = ""
                    WordNum = 2
                    LettersNum = 15 - 3
                    for w in range(0,WordNum,1):
                        if w < len(name):
                            n = Name + name[w] + " "
                            if len(n) > LettersNum:
                                Name = n[:LettersNum]
                            else:
                                Name = n
                    if WordNum < len(name) or len(Name) > LettersNum - 3:
                        Name += "..."

                    #Extract words from address
                    AddressNum = 2
                    address = hotels[i]["Location"].split()
                    Address = ""
                    for w in range(0,AddressNum,1):
                        if w < len(address):
                            Address += address[w] + " "
                    if AddressNum < len(address):
                        Address += "..."

                    #Create UI
                    Label = MDLabel(text = Name, size = (0.2,0.1), pos_hint = {"center_x": 0.55,"center_y": 0.15})
                    Label.bind(size=self.on_size)
                    AddressLabel = MDLabel(text = Address, size = (0.1,0.05), pos_hint = {"center_x": 0.55,"center_y": 0.1}, opacity = 0.5)
                    AddressLabel.bind(size=self.on_size)
                    PriceLabel = MDLabel(text = hotels[i]["Price"], size = (1,1), pos_hint = {"center_x": 1.1,"center_y": 0.15})
                    PriceLabel.bind(size=self.on_size3)
                    rating = round(float(hotels[i]["Rating"]),1)
                    Rating = str(rating)
                    Color = Colors[math.ceil(rating)]#[1 - (math.ceil(rating) / 10), math.ceil(rating) / 5,0,1]
                    RatingLabel = MDLabel(text = Rating, theme_text_color = "Custom", text_color = [0.5,0.5,0.5,1], size = (1,1), pos_hint = {"center_x": 1.35,"center_y": 0.125})
                    RatingLabel.bind(size=self.on_size2)
                    RatingCard = MDBoxLayout(size_hint = (0.2,0.2), pos_hint = {"center_x": 0.9,"center_y": 0.1}, radius = [0,0,20,0], md_bg_color = Color)
                    Card = RippleBoxLayout(MDRelativeLayout(FitImage(source = hotels[i]["Images"][0], radius = [20,20,0,0], pos_hint = {"center_x": 0.5,"center_y": 0.6}, size_hint = (1,0.8)),Label, AddressLabel, PriceLabel, RatingCard, RatingLabel),radius = [20,20,20,20], size_hint_y = 0.6)
                    Card.on_release = lambda instance, i=i: self.OpenTab(Info = hotels[i])
                    self.root.ids.Hotels.add_widget(MDSwiperItem(Card))
                else:
                    break

            self.AnimateSwiper(swiper = self.root.ids.Hotels)

        print(hotels)
        CreateHotels()

        #Create Restaurants
        restaurants = find_places("Restaurant near me")
        print(restaurants)
        @mainthread
        def CreateRestaurants():
            for todel in ToDelete.keys():
                swiper = ToDelete[todel]
                if swiper == self.root.ids.Restaurants:
                    swiper.remove_widget(todel)

            for i in range(0,5,1):
                if i < len(restaurants):
                    #Extract words from name
                    name = restaurants[i]["Name"].split()
                    Name = ""
                    WordNum = 2
                    LettersNum = 15 - 3
                    for w in range(0,WordNum,1):
                        if w < len(name):
                            n = Name + name[w] + " "
                            if len(n) > LettersNum:
                                Name = n[:LettersNum]
                            else:
                                Name = n
                    if WordNum < len(name) or len(Name) > LettersNum - 3:
                        Name += "..."

                    #Extract words from address
                    AddressNum = 2
                    address = restaurants[i]["Location"].split()
                    Address = ""
                    for w in range(0,AddressNum,1):
                        if w < len(address):
                            Address += address[w] + " "
                    if AddressNum < len(address):
                        Address += "..."

                    #Create UI
                    Label = MDLabel(text = Name, size = (0.2,0.1), pos_hint = {"center_x": 0.55,"center_y": 0.15})
                    Label.bind(size=self.on_size)
                    AddressLabel = MDLabel(text = Address, size = (0.1,0.05), pos_hint = {"center_x": 0.55,"center_y": 0.1}, opacity = 0.5)
                    AddressLabel.bind(size=self.on_size)
                    PriceLabel = MDLabel(text = restaurants[i]["Price"], size = (1,1), pos_hint = {"center_x": 1.1,"center_y": 0.15})
                    PriceLabel.bind(size=self.on_size3)
                    rating = float(restaurants[i]["Rating"])
                    Rating = restaurants[i]["Rating"]
                    Color = Colors[math.ceil(rating)]#[1 - (math.ceil(rating) / 10), math.ceil(rating) / 5,0,1]
                    RatingLabel = MDLabel(text = Rating, theme_text_color = "Custom", text_color = [0.5,0.5,0.5,1], size = (1,1), pos_hint = {"center_x": 1.35,"center_y": 0.125})
                    RatingLabel.bind(size=self.on_size2)
                    RatingCard = MDBoxLayout(size_hint = (0.2,0.2), pos_hint = {"center_x": 0.9,"center_y": 0.1}, radius = [0,0,20,0], md_bg_color = Color)
                    OpenCloseLabel = MDLabel(text = "[b]" + restaurants[i]["Open"] + "[/b] \u2022" + restaurants[i]["Closes"], size = (1,1), pos_hint = {"center_x": 0.55,"center_y": 0.05}, markup = True)
                    OpenCloseLabel.bind(size=self.on_size7)
                    Card = RippleBoxLayout(MDRelativeLayout(FitImage(source = restaurants[i]["Images"][0], radius = [20,20,0,0], pos_hint = {"center_x": 0.5,"center_y": 0.6}, size_hint = (1,0.8)),Label, AddressLabel, OpenCloseLabel, PriceLabel, RatingCard, RatingLabel),radius = [20,20,20,20], size_hint_y = 0.6)
                    Card.on_release = lambda instance, i=i: self.OpenTab(Info = restaurants[i])
                    self.root.ids.Restaurants.add_widget(MDSwiperItem(Card))
                else:
                    break

            self.AnimateSwiper(swiper = self.root.ids.Restaurants)

        CreateRestaurants()
    def on_start(self):
        MDScreenManager.current = "Home Screen"
        threading.Thread(target = self.Startup).start()

MyApp().run()

inp = input("Start it")
time1 = datetime.datetime.now()
hotels = FindHotels(Num=5,Location=City)
time2 = datetime.datetime.now()
print("DONE", time2 - time1)