from django.shortcuts import render,redirect
from .models import *
from .forms import *
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.http import JsonResponse
from .utilities import login_req
import json
# Create your views here.
def login_view(request):
    if request.method == 'POST':
        form = MemberLoginForm(request.POST)
        if form.is_valid():
            username_input = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Try to find user by email or memberID
            try:
                if '@' in username_input:
                    user_obj = CustomUser.objects.get(email=username_input)
                else:
                    user_obj = CustomUser.objects.get(memberID=username_input)
            except CustomUser.DoesNotExist:
                user_obj = None

            if user_obj:
                user = authenticate(request, email=user_obj.email, password=password)
                if user:
                    member=MemberModel.objects.filter(user_detail_id=user.id).first()
                    login(request, user)
                    # if user.is_superuser == False and member.mode_of_payment=='Online':
                    #     return redirect(f'/checkout/{member.id}')
                    # else:
                    #     return redirect('dashboard')
                    return redirect('dashboard')
                else:
                    form.add_error(None, 'Invalid credentials')
            else:
                form.add_error(None, 'No user found with this Email or Member ID')
    else:
        form = MemberLoginForm()

    return render(request, 'login_view.html', {'form': form})


def register_view(request):
    if request.method == 'POST':
        form = MemberRegistrationForm(request.POST)

        latest_member = CustomUser.objects.last()

        # if latest_member:
        #     # Assuming the format is 'TPD<Number>'
        #     split_number_part = int(latest_member.memberID[4:])  # Extract number part
        #     memberID = f"CKDNF{split_number_part + 1:06d}"  # Increment and pad with zeros
        # else:
        #     memberID = "CKDNF000001"  # Start with this if no records exist

        if form.is_valid():
            member = form.save(commit=False)

            # Determine sponsor
            senior_ID = request.POST.get('senior_ID')
            sponsor_member = MemberModel.objects.filter(user_detail__memberID=senior_ID).first()
            member_count = MemberModel.objects.count()

            if sponsor_member or member_count == 0:
                # Link sponsor
                member.sponser_member = sponsor_member if member_count != 0 else None
                member.rank = 'Not Available'
                member.registration_fee = 11000
                member.save()

                # Do distribution + referral
                # distribution_of_amount(request, member.id)
                # if memberID != "JSCT000001":
                    # member_refferal_benefits(request, member.id)
                    # DonationsModel.objects.create(
                    #     member_id       = member.id,
                    #     amount          = 1551,
                    #     slip_for        ='Registration'
                    # )
                messages.success(request, "Registration successful! You can now log in.")

                # Login the user
                user = member.user_detail
                print('User:', user)
                # user.backend = 'cmsapp.backends.CustomUserAuthenticationBackend'
                # login(request, user)
                if member.mode_of_payment=='Online':
                     return redirect(f'/checkout/{member.id}')
                else:
                    return redirect('login')

            else:
                messages.error(request, "This sponsor ID is not valid")
                print("This sponsor ID is not valid")
        else:
            print(form.errors)
    else:
        form = MemberRegistrationForm()

    return render(request, 'register_view.html', {'form': form})

def index(request):
    return render(request,'index.html')

@login_req
def dashboard(request):
    return render(request,'dashboard.html',{})

def logout_view(request):
    """
    Logs out the currently logged-in user and redirects to the homepage.
    """
    logout(request)
    return redirect('login')  # Redirect to the login page after logout



def cascade_ajax(request):
    if request.method == 'POST':
        level = request.POST.get('level')  # Get the current level (e.g., 'district', 'block', etc.)
        value = request.POST.get('value')  # Get the selected value from the previous dropdown

        if not level or not value:
            return JsonResponse([], safe=False)  # Return an empty list if parameters are missing
        if level == 'state':
            record = StateModel.objects.filter(name=value).first()
            if record:
                results = CityModel.objects.filter(state_id=record.id)
        else:
            return JsonResponse([], safe=False)  # Return empty if the level is invalid

        # Prepare the results as a list of dictionaries
        if results:
            data = [{"name": item.name} for item in results]
        else:
            data = []

        return JsonResponse(data, safe=False)

    return JsonResponse([], safe=False)  # Return empty list for non-POST requests


def get_sponser_name_ajax(request):
    if request.method == 'POST':
        sponserID= request.POST.get('sponserID')
        user= CustomUser.objects.filter(memberID=sponserID).first()
        if user:
           data={"name": user.applicant_name,"status":True}
        #    print(data)
           return JsonResponse(data, safe=False) 
    return JsonResponse([],safe=False)


@login_req
def level_data(request):
    user=request.user
    user_id=user.id
    tree= build_tree(user_id)
    # print(tree)
    return render(request,'level_data.html',{'tree':json.dumps(tree)})

def build_tree(id):
    user=CustomUser.objects.filter(id=id).first()
    member = MemberModel.objects.filter(id=id).first()
    if not member:
        return None

    # Query for children where the current member is the sponsor
    children = MemberModel.objects.filter(sponser_member_id=member.id)
    tree = {
        'member': {'name':member.applicant_name,'memberID':user.memberID,'rank':member.rank,'is_active':member.is_active},
        'children': []
    }

    # Recursively build the tree for each child
    for child in children:
        subtree = build_tree(child.id)
        if subtree:
            tree['children'].append(subtree)

    return tree




















# def build_tree(level=1, max_level=13, left_unit=1, right_unit=1):
#     if level > max_level:
#         return None

#     total_team = left_unit + right_unit
#     income = total_team * 600  # formula from table

#     node = {
#         "level": level,
#         "left_unit": left_unit,
#         "right_unit": right_unit,
#         "team": total_team,
#         "income": income,
#         "children": []
#     }

#     # Recursively build next level (double units each time)
#     child = build_tree(level + 1, max_level, left_unit * 2, right_unit * 2)
#     if child:
#         node["children"].append(child)

#     return node


# def income_tree_recursive(request):
#     tree = build_tree()
#     return render(request, "income_tree_recursive.html", {"tree": tree})