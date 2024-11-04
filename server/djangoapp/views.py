# server/djangoapp/views.py
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .populate import initiate
from .models import CarMake, CarModel
from .restapis import get_request, analyze_review_sentiments, post_review


# Get an instance of a logger
logger = logging.getLogger(__name__)

@csrf_exempt
def login_user(request):
    logger.debug("Login request received.")
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    logger.debug(f"Attempting login for user: {username}")
    user = authenticate(username=username, password=password)
    
    if user is not None:
        login(request, user)
        logger.info(f"User {username} authenticated successfully.")
        data = {"userName": username, "status": "Authenticated"}
    else:
        logger.warning(f"Authentication failed for user: {username}")
        data = {"userName": username, "status": "Failed"}
    
    return JsonResponse(data)

def logout_request(request):
    logger.debug("Logout request received.")
    logout(request)
    data = {"userName": ""}
    logger.info("User logged out successfully.")
    return JsonResponse(data)

@csrf_exempt
def registration(request):
    logger.debug("Registration request received.")
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']

    logger.debug(f"Registering new user: {username}")
    try:
        User.objects.get(username=username)
        logger.warning(f"Username {username} already exists.")
        return JsonResponse({"userName": username, "error": "Already Registered"})
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=username, first_name=first_name, last_name=last_name, password=password, email=email
        )
        login(request, user)
        logger.info(f"User {username} registered and logged in successfully.")
        return JsonResponse({"userName": username, "status": "Authenticated"})

def get_cars(request):
    logger.debug("Fetching car models and makes.")
    if CarMake.objects.filter().count() == 0:
        logger.debug("No car makes found; initiating database population.")
        initiate()
    
    car_models = CarModel.objects.select_related('car_make')
    cars = [{"CarModel": model.name, "CarMake": model.car_make.name} for model in car_models]
    logger.info("Car models and makes fetched successfully.")
    return JsonResponse({"CarModels": cars})

import logging
logger = logging.getLogger(__name__)

def get_dealerships(request, state="All"):
    logger.info("Cassiano Medeiros")
    logger.info("Received request to /get_dealers with state: %s", state)
    
    # Adjust the base URL as needed
    base_url = "https://cassianomede-3030.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai"
    if state == "All":
        endpoint = f"{base_url}/fetchDealers"
    else:
        endpoint = f"{base_url}/fetchDealers/{state}"
    
    dealerships = get_request(endpoint)
    
    # Check for a None response from get_request
    if dealerships is None:
        logger.error("Failed to fetch dealerships data.")
        return JsonResponse({"status": 500, "message": "Error fetching dealership data"})
    
    logger.debug("Dealerships fetched: %s", dealerships)
    return JsonResponse({"status": 200, "dealers": dealerships})

def get_dealer_reviews(request, dealer_id):
    logger.debug(f"Fetching reviews for dealer ID: {dealer_id}")
    base_url = "https://cassianomede-3030.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai"
    if dealer_id:
        endpoint = f"{base_url}/fetchReviews/dealer/{dealer_id}"
        reviews = get_request(endpoint)
        if reviews:
            for review in reviews:
                sentiment = analyze_review_sentiments(review['review'])
                review['sentiment'] = sentiment.get('sentiment', 'neutral')
            logger.info(f"Reviews fetched and analyzed for dealer ID: {dealer_id}")
            return JsonResponse({"status": 200, "reviews": reviews})
        else:
            logger.error("No reviews found or failed to fetch reviews.")
            return JsonResponse({"status": 500, "message": "Error fetching reviews"})
    else:
        logger.warning("Bad Request: dealer_id not provided.")
        return JsonResponse({"status": 400, "message": "Bad Request"})

def get_dealer_details(request, dealer_id):
    logger.debug(f"Fetching details for dealer ID: {dealer_id}")
    base_url = "https://cassianomede-3030.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai"
    if dealer_id:
        endpoint = f"{base_url}/fetchDealer/{dealer_id}"
        dealership = get_request(endpoint)
        if dealership:
            return JsonResponse({"status": 200, "dealer": dealership})
        else:
            logger.error("Failed to fetch dealership details.")
            return JsonResponse({"status": 500, "message": "Error fetching dealership details"})
    else:
        logger.warning("Bad Request: dealer_id not provided.")
        return JsonResponse({"status": 400, "message": "Bad Request"})

def add_review(request):
    if not request.user.is_anonymous:
        logger.debug(f"Adding review by user: {request.user.username}")
        data = json.loads(request.body)
        try:
            post_review(data)
            logger.info("Review posted successfully.")
            return JsonResponse({"status": 200})
        except Exception as e:
            logger.error(f"Error posting review: {str(e)}")
            return JsonResponse({"status": 401, "message": "Error in posting review"})
    else:
        logger.warning("Unauthorized review submission attempt.")
        return JsonResponse({"status": 403, "message": "Unauthorized"})
