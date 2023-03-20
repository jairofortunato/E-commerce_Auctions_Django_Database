from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required 
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .forms import ListingForm, CommentForm
from .models import User, Listing, Bid, Comment, Category


def index(request):
    listings = Listing.objects.filter(is_active=True)
    allCategories = Category.objects.all()
    return render(request, "auctions/index.html", {
        "listings": listings,
        "categories": allCategories,
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    

@login_required
def create_listing(request):
    if request.method == "GET":
        allCategories = Category.objects.all()
        return render(request, "auctions/create_listing.html", {
            "categories": allCategories
        })
    else:
        # get the data from the form
        title = request.POST["title"]
        description = request.POST["description"]
        image_url = request.POST["image_url"]
        starting_bid = request.POST["starting_bid"]
        category = request.POST["category"]
        # who is the user
        currentUser = request.user
        # get all content about the particular category
        categoryData = Category.objects.get(name=category)

        # create a new listing object
        newListing = Listing(
        title=title,
        description=description,
        image_url=image_url,
        starting_bid=starting_bid,
        category=categoryData,
        owner=currentUser
        )
        # insert the object in our database
        newListing.save()
        # redirect to index page
        return HttpResponseRedirect(reverse(index))

def listing(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    bids = Bid.objects.filter(listing=listing).order_by('-amount')
    comments = Comment.objects.filter(listing=listing).order_by('-created_at')
    
    
    if request.user.is_authenticated:
        watchlist = request.user.watchlist.filter(id=listing.id).exists()
    else:
        watchlist = False


    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.listing = listing
            comment.save()
            messages.success(request, 'Comment added successfully.')
            return redirect('listing', listing_id=listing.id)
    else:
        comment_form = CommentForm()

    # check if bid form is submitted
    if request.method == 'POST' and 'bid' in request.POST:
        bid_amount = float(request.POST['bid_amount'])
        if bid_amount <= listing.starting_bid:
            messages.error(request, 'Your bid must be greater than the starting bid.')
            return redirect('listing', listing_id=listing.id)

        if Bid.objects.filter(listing=listing).exists():
            highest_bid = Bid.objects.filter(listing=listing).order_by('-amount').first()
            if bid_amount <= highest_bid.amount:
                messages.error(request, 'Your bid must be greater than the highest bid.')
                return redirect('listing', listing_id=listing.id)

        new_bid = Bid(
            listing=listing,
            bidder=request.user,
            amount=bid_amount
        )
        new_bid.save()
        messages.success(request, 'Your bid was successful!')
        return redirect('listing', listing_id=listing.id)

    # get highest bid for the listing
    highest_bid = None
    if Bid.objects.filter(listing=listing).exists():
        highest_bid = Bid.objects.filter(listing=listing).order_by('-amount').first()
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "bids": bids,
        "comments": comments,
        "watchlist": watchlist,
        'comment_form': comment_form,
    })

def addComment(request, listing_id):
    currentUser = request.user
    listingData = Listing.objects.get(pk=listing_id)
    message = request.POST['newComment']
    

    newComment = Comment(
        commenter=currentUser,
        listing=listingData,
        text=message
    )
    newComment.save()

    return HttpResponseRedirect(reverse("listing",args={listing_id, }))

def watchlist(request):
    listings = request.user.watchlist.all()
    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })

@login_required
def add_to_watchlist(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    user = request.user

    if user not in listing.users_watching.all():
        listing.users_watching.add(user)
        messages.success(request, "Listing added to watchlist.")
    else:
        messages.error(request, "Listing already in watchlist.")

    return redirect('watchlist')

@login_required
def remove_from_watchlist(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    user = request.user

    if user in listing.users_watching.all():
        listing.users_watching.remove(user)
        messages.success(request, "Listing removed from watchlist.")
    else:
        messages.error(request, "Listing not found in watchlist.")

    return redirect('watchlist')


def categories(request):
    if request.method == "POST":
        categoryFromForm = request.POST['category']
        category = Category.objects.get(name=categoryFromForm)
        activeListings = Listing.objects.filter(is_active=True, category=category)
        allCategories = Category.objects.all()
        return render(request, "auctions/index.html",{
            "listings": activeListings,
            "categories": allCategories,
        })
   
    listings = Listing.objects.filter(category=category)
    return render(request, "auctions/categories.html", {
        "listings": listings
    })


@login_required
def bid(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    if request.method == 'POST':
        bid_amount = float(request.POST['bid_amount'])

        if bid_amount <= listing.starting_bid:
            messages.error(request, 'Your bid must be greater than the starting bid.')
            return redirect('listing', listing_id=listing.id)

        if Bid.objects.filter(listing=listing).exists():
            highest_bid = Bid.objects.filter(listing=listing).order_by('-amount').first()
            if bid_amount <= highest_bid.amount:
                messages.error(request, 'Your bid must be greater than the highest bid.')
                return redirect('listing', listing_id=listing.id)

        new_bid = Bid(
            listing=listing,
            bidder=request.user,
            amount=bid_amount
        )
        new_bid.save()

        # Add the following line to update the listing's current price
        listing.current_price = bid_amount
        listing.save()

        messages.success(request, 'Your bid was successful!')
        return redirect('listing', listing_id=listing.id)

    return redirect('listing', listing_id=listing.id)

  

@login_required
def close_listing(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)

    if request.user != listing.seller:
        messages.error(request, "You do not have permission to close this listing.")
        return redirect('listing', listing_id=listing.id)

    if listing.closed:
        messages.error(request, "This listing is already closed.")
        return redirect('listing', listing_id=listing.id)

    listing.closed = True
    listing.save()

    # Notify the highest bidder if there is one
    if listing.bids.count() > 0:
        highest_bid = listing.bids.order_by('-amount').first()
        if highest_bid.user != listing.seller:
            highest_bid.user.notifications.create(
                message=f"Your bid of ${highest_bid.amount} for '{listing.title}' was successful!",
                link=f"/auctions/{listing.id}/",
            )

    messages.success(request, "Listing closed successfully.")
    return redirect('listing_detail', listing_id=listing.id)
