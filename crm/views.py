from django.shortcuts import render, redirect, get_object_or_404
from .models import User, Lead, Client, Task
from .forms import LeadForm, TaskForm
from plotly.offline import plot
import plotly.graph_objs as go
from django.contrib import messages
def login_view(request):
    if request.method == 'POST':
        uname=request.POST['username']
        pwd=request.POST['password']
        try:
            user=User.objects.get(username=uname,password=pwd)
            request.session['user_id'] = user.id
            request.session['username'] = user.username
            request.session['role']=user.role
            return redirect ('home')
        except User.DoesNotExist:
            return render(request,'crm/login.html',{'error':'Invalid Credentials'})
    return render(request,'crm/login.html')

def logout_view(request):
    request.session.flush()
    return redirect('login')


def lead_list(request):
    if 'user_id' not in request.session:
        return redirect('login')

    if request.session['role'] not in ['admin', 'sales']:
        return redirect('home')  # deny access to other roles

    leads = Lead.objects.all().order_by('-created_at')
    return render(request, 'crm/lead_list.html', {'leads': leads})

def add_lead(request):
    if 'user_id' not in request.session or request.session['role'] not in ['admin','sales']:
        return redirect('login')
    if request.method=='POST':
        form=LeadForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lead_list')
    else:
        form=LeadForm()

    return render(request,"crm/lead_form.html",{'form':form,'title':'Add Lead'})

def edit_lead(request, lead_id):
    if 'user_id' not in request.session or request.session['role'] not in ['admin', 'sales']:
        return redirect('login')

    lead = get_object_or_404(Lead, id=lead_id)  # Fetch the lead object

    if request.method == 'POST':
        form = LeadForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            return redirect('lead_list')
    else:
        form = LeadForm(instance=lead)

    return render(request, 'crm/lead_form.html', {'form': form, 'title': 'Edit Lead'})
    
def delete_lead(request, lead_id):
    if 'user_id' not in request.session or request.session['role'] != 'admin':
        return redirect('login')

    lead = get_object_or_404(Lead, id=lead_id)
    lead.delete()
    return redirect('lead_list')

def convert_lead_to_client(request,lead_id):
    if 'user_id' not in request.session or request.session['role'] not in ['admin','sales']:
        return redirect('login')
    lead=get_object_or_404(Lead,id=lead_id)

    Client.objects.create(name=lead.name,email=lead.email,phone=lead.phone)

    lead.delete()

    return redirect('lead_list')


def add_task(request):
    if 'user_id' not in request.session or request.session['role'] not in ['admin', 'sales']:
        messages.error(request, "You don't have permission to add tasks.")
        return redirect('login')
    
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            try:
                task = form.save(commit=False)
                # Get the User instance for the current user
                assigned_by = get_object_or_404(User, id=request.session['user_id'])
                task.assigned_by = assigned_by
                task.save()
                messages.success(request, f"Task '{task.title}' has been created successfully.")
                return redirect('task_list')
            except User.DoesNotExist:
                messages.error(request, "Error: Unable to assign the task. User not found.")
            except Exception as e:
                messages.error(request, f"An error occurred while creating the task: {str(e)}")
    else:
        form = TaskForm()
    
    return render(request, 'crm/task_form.html', {'form': form, 'title': 'Add Task'})


def task_list(request):
    user_role = request.session.get('role')
    user_id = request.session.get('user_id')

    if user_role == 'admin':
        tasks = Task.objects.all()
    elif user_role == 'sales':
        tasks = Task.objects.filter(assigned_by_id=user_id)
    elif user_role == 'support':
        tasks = Task.objects.filter(assigned_to_id=user_id)
    else:
        tasks = Task.objects.none()

    return render(request, 'crm/task_list.html', {'tasks': tasks, 'user_role': user_role})
def toggle_task_status_in_list(request, task_id):
    if 'user_id' not in request.session:
        return redirect('login')
    
    task = get_object_or_404(Task, id=task_id)
    user_role = request.session.get('role')
    user_id = request.session.get('user_id')
    
    # Check if user has permission (support staff, admin, or assigned to the task)
    if user_role in ['support', 'admin'] or task.assigned_to_id == user_id:
        task.status = 'completed' if task.status == 'pending' else 'pending'
        task.save()
    
    return redirect('task_list')

def client_list(request):
    if 'user_id' not in request.session or request.session['role'] not in ['admin', 'sales', 'support']:
        return redirect('login')
    clients = Client.objects.all().order_by('-id')
    return render(request, 'crm/client_list.html', {'clients': clients})
def client_delete(request, pk):
    client = Client.objects.get(pk=pk)
    client.delete()
    return redirect('client_list')

def dashboard(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session.get('user_id')
    role = request.session.get('role')
    username = request.session.get('username')

    # Initialize variables for recent items to None
    recent_leads = None
    recent_clients = None
    recent_tasks = None

    # Get counts (global for admin/sales, user-specific for support tasks)
    total_leads = Lead.objects.count()
    total_clients = Client.objects.count()

    # Recent Items & Task Counts based on role
    if role == 'support':
        user_tasks = Task.objects.filter(assigned_to_id=user_id)
        pending_tasks = user_tasks.filter(status='pending').count()
        completed_tasks = user_tasks.filter(status='completed').count()

        # Support only sees their own recent tasks
        recent_tasks = user_tasks.order_by('-created_at')[:5]

        # Prepare pie chart (Pending vs Completed Tasks for the support user)
        pie_chart = go.Figure(data=[go.Pie(
            labels=['Pending', 'Completed'],
            values=[pending_tasks, completed_tasks],
            marker=dict(colors=['#ffc107', '#28a745'])
        )])
        pie_div = plot(pie_chart, output_type='div')

    else:  # role is admin or sales
        # Tasks assigned by the current user
        assigned_tasks = Task.objects.filter(assigned_by_id=user_id)
        pending_tasks = assigned_tasks.filter(status='pending').count()
        completed_tasks = assigned_tasks.filter(status='completed').count()

        # Admin/Sales see recent leads and clients
        recent_leads = Lead.objects.order_by('-created_at')[:5]
        recent_clients = Client.objects.order_by('-joined_at')[:5]
        # Admin/Sales see tasks they've assigned
        recent_tasks = assigned_tasks.order_by('-created_at')[:5]

        # Prepare pie chart (Leads vs Clients)
        pie_chart = go.Figure(data=[go.Pie(
            labels=['Leads', 'Clients'],
            values=[total_leads, total_clients],
            marker=dict(colors=['#ffc107', '#28a745'])
        )])
        pie_div = plot(pie_chart, output_type='div')

    context = {
        'role': role,
        'username': username,
        'total_leads': total_leads,
        'total_clients': total_clients,
        'pending_tasks': pending_tasks,
        'completed_tasks': completed_tasks,
        'pie_chart': pie_div,
        'recent_leads': recent_leads,
        'recent_clients': recent_clients,
        'recent_tasks': recent_tasks,
    }
    return render(request, 'crm/dashboard.html', context)

def toggle_task_status(request, task_id):
    if 'user_id' not in request.session:
        return redirect('login')
    
    task = get_object_or_404(Task, id=task_id)
    user_role = request.session.get('role')
    
    # Check if user has permission (support staff, admin, or the client)
    if user_role in ['support', 'admin'] or request.user == task.client:
        task.status = 'completed' if task.status == 'pending' else 'pending'
        task.save()
    
    return redirect('dashboard')
def edit_task(request, task_id):
    if 'user_id' not in request.session or request.session['role'] not in ['admin', 'sales']:
        messages.error(request, "You don't have permission to edit tasks.")
        return redirect('task_list')

    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Task updated successfully.")
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)

    return render(request, 'crm/task_form.html', {'form': form, 'title': 'Edit Task'})

def delete_task(request, task_id):
    if 'user_id' not in request.session or request.session['role'] not in ['admin', 'sales']:
        messages.error(request, "You don't have permission to delete tasks.")
        return redirect('task_list')

    task = get_object_or_404(Task, id=task_id)
    task.delete()
    messages.success(request, "Task deleted successfully.")
    return redirect('task_list')
    
def home(request):
    if 'user_id' not in request.session:
        return render(request, 'crm/index.html')

    return redirect('dashboard')   # ✅ Correct

