from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Tender, User, Bid, Favorite
from .forms import TenderForm, RegistrationForm, BidForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.db.models import Sum, Q
from django.core.paginator import Paginator

def index(request):
    latest_tenders = Tender.objects.filter(status='active').order_by('-created_at')[:5]
    favorited_ids = []
    if request.user.is_authenticated:
        favorited_ids = request.user.favorites.values_list('tender_id', flat=True)
    
    # Calculate active tenders count
    active_tenders_count = Tender.objects.filter(status='active').count()
    
    # Calculate total tenders value
    total_value = Tender.objects.aggregate(total=Sum('budget'))['total'] or 0
    
    if total_value >= 10000000:
        formatted_total_value = f"₹{total_value / 10000000:.1f} Cr"
    elif total_value >= 100000:
        formatted_total_value = f"₹{total_value / 100000:.1f} L"
    elif total_value >= 1000:
        formatted_total_value = f"₹{total_value / 1000:.1f} K"
    else:
        formatted_total_value = f"₹{total_value}"
        
    # Calculate category counts
    category_counts = {}
    for cat_id, cat_name in Tender.CATEGORY_CHOICES:
        category_counts[cat_id] = Tender.objects.filter(status='active', category=cat_id).count()
    
    return render(request, 'index.html', {
        'tenders': latest_tenders,
        'favorited_ids': favorited_ids,
        'active_tenders_count': active_tenders_count,
        'formatted_total_value': formatted_total_value,
        'category_counts': category_counts
    })


def listing(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    location = request.GET.get('location', '')
    min_budget = request.GET.get('min_budget')
    max_budget = request.GET.get('max_budget')
    
    tenders_list = Tender.objects.filter(status='active').order_by('-created_at')
    
    if query:
        tenders_list = tenders_list.filter(Q(title__icontains=query) | Q(description__icontains=query))
    
    if category and category != 'All Categories':
        tenders_list = tenders_list.filter(category__iexact=category)
        
    if location and location != 'All Region':
        tenders_list = tenders_list.filter(location__icontains=location)
        
    if min_budget and min_budget.strip():
        tenders_list = tenders_list.filter(budget__gte=min_budget)
        
    if max_budget and max_budget.strip():
        tenders_list = tenders_list.filter(budget__lte=max_budget)

    # Pagination: 6 tenders per page
    paginator = Paginator(tenders_list, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    favorited_ids = []
    if request.user.is_authenticated:
        favorited_ids = request.user.favorites.values_list('tender_id', flat=True)
        
    return render(request, 'all_tenders.html', {
        'tenders': page_obj,
        'query': query,
        'selected_category': category,
        'min_budget': min_budget,
        'max_budget': max_budget,
        'favorited_ids': favorited_ids,
        'page_obj': page_obj
    })

@login_required
def dashboard(request):
    user_role = request.user.role.lower()
    
    if request.user.is_superuser or user_role in ['super_admin', 'admin']:
        # Super Admin: Global site analytics
        total_tenders = Tender.objects.count()
        total_bids = Bid.objects.count()
        total_value = Tender.objects.aggregate(total=Sum('budget'))['total'] or 0
        total_users = User.objects.count()
        
        context = {
            'total_tenders': total_tenders,
            'total_bids': total_bids,
            'total_value': total_value,
            'total_users': total_users,
            'role_name': 'Super Admin',
            'total_value_str': f"₹{(total_value/10000000):.2f} Cr" # Added formatted value
        }
        return render(request, 'super-admin-dashboard.html', context)
    
    elif user_role in ['partner_admin', 'partner']:
        # Partner Admin: My Tenders and Create Tender
        tenders = Tender.objects.filter(posted_by=request.user).order_by('-created_at')
        
        # Calculate Stats
        active_tenders_count = tenders.filter(status='active').count()
        total_bids_received = Bid.objects.filter(tender__posted_by=request.user).count()
        
        return render(request, 'partner-dashboard.html', {
            'tenders': tenders, 
            'role_name': 'Partner Admin',
            'active_tenders_count': active_tenders_count,
            'total_bids_received': total_bids_received,
            'total_views': 0 # For now, as we don't track views yet
        })
    
    elif user_role == 'contractor':
        return redirect('contractor_dashboard')
    
    return redirect('index')

@login_required
def partner_applications(request):
    user_role = request.user.role.lower()
    if user_role not in ['partner_admin', 'partner']:
        return redirect('index')
    
    # Filter tenders posted by the user that have at least one bid
    tenders_with_bids = Tender.objects.filter(posted_by=request.user, bid_set__isnull=False).distinct().order_by('-created_at')
    
    # Calculate Stats (could refactor this but for now keep it simple)
    active_tenders_count = Tender.objects.filter(posted_by=request.user, status='active').count()
    total_bids_received = Bid.objects.filter(tender__posted_by=request.user).count()
    
    return render(request, 'partner-applications.html', {
        'tenders': tenders_with_bids,
        'role_name': 'Partner Admin',
        'active_tenders_count': active_tenders_count,
        'total_bids_received': total_bids_received,
        'total_views': 0
    })


@login_required
def post_tender(request):
    if request.user.role.lower() not in ['partner_admin', 'partner']:
        messages.error(request, "Only partners can post tenders.")
        return redirect('index')
    if request.method == 'POST':
        form = TenderForm(request.POST, request.FILES)
        if form.is_valid():
            tender = form.save(commit=False)
            tender.posted_by = request.user
            tender.status = 'active'
            tender.save()
            return redirect('partner_dashboard')
    else:
        form = TenderForm()
    
    return render(request, 'post-tender.html', {'form': form})

def signin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            username = None
            
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid email or password.")
    
    return render(request, 'signin.html')

@login_required
def contractor_dashboard(request):
    # Ensure only contractors access this
    if request.user.role != 'contractor':
        return redirect('index')
        
    bids = Bid.objects.filter(bidder=request.user).order_by('-submitted_at')
    
    context = {
        'bids': bids,
        'bids_count': bids.count(),
        'won_count': bids.filter(status='accepted').count(),
        'pending_count': bids.filter(status='pending').count(),
    }
    return render(request, 'contractor-dashboard.html', context)

def tender_detail(request, pk):
    tender = get_object_or_404(Tender, pk=pk)
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(user=request.user, tender=tender).exists()
    
    if request.method == 'POST':
        # Only logged in contractors can bid
        if not request.user.is_authenticated or request.user.role != 'contractor':
            messages.error(request, "You must be logged in as a Contractor to bid.")
            return redirect('login')
            
        form = BidForm(request.POST, request.FILES)
        if form.is_valid():
            bid = form.save(commit=False)
            bid.tender = tender
            bid.bidder = request.user
            bid.status = 'pending'
            bid.save()
            messages.success(request, "Bid submitted successfully!")
            return redirect('tender_detail', pk=pk)
    else:
        form = BidForm()
        
    return render(request, 'tender-detail.html', {
        'tender': tender, 
        'form': form,
        'is_favorited': is_favorited
    })

def signup(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data['email']  # Use email as username
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Auto login
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegistrationForm()
        
    return render(request, 'signup.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    return redirect('index')

@login_required
def accept_bid(request, bid_id):
    bid = get_object_or_404(Bid, id=bid_id)
    tender = bid.tender
    
    # Ensure current user is the owner of the tender
    if request.user != tender.posted_by:
        messages.error(request, "You are not authorized to perform this action.")
        return redirect('index')
        
    # Update Bid Status
    bid.status = 'accepted'
    bid.save()
    
    # Update Tender Status
    tender.status = 'closed'  # Or 'awarded'
    tender.save()
    
    # Reject other bids (optional but recommended)
    tender.bid_set.exclude(id=bid_id).update(status='rejected')
    
    messages.success(request, f"Bid from {bid.bidder.company_name} accepted! Tender is now closed.")
    return redirect('tender_detail', pk=tender.id)


@login_required
def delete_tender(request, pk):
    tender = get_object_or_404(Tender, pk=pk, posted_by=request.user)

    if request.user.role.lower() not in ['partner_admin', 'partner']:
        messages.error(request, "You are not authorized to perform this action.")
        return redirect('index')

    if request.method == 'POST':
        tender.delete()
        messages.success(request, "Tender deleted successfully.")

    return redirect('partner_dashboard')

@login_required
def toggle_favorite(request, tender_id):
    tender = get_object_or_404(Tender, id=tender_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, tender=tender)
    
    if not created:
        favorite.delete()
        action = "removed"
    else:
        action = "added"
        
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax'):
        from django.http import JsonResponse
        return JsonResponse({'status': 'success', 'action': action})
        
    return redirect(request.META.get('HTTP_REFERER', 'index'))

def terms_view(request):
    return render(request, 'terms.html')

def privacy_view(request):
    return render(request, 'privacy.html')

def bid_format_view(request):
    return render(request, 'resources/bid_format.html')

def regulations_view(request):
    return render(request, 'resources/regulations.html')

@login_required
def archive_view(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('tender')
    return render(request, 'archive.html', {'favorites': favorites})
