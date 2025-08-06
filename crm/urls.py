from django.urls import path
from . import views
from .views import (
    login_view,
    logout_view,
    lead_list,
    add_lead,
    edit_lead,
    delete_lead,
    convert_lead_to_client,
    client_list,
    task_list,
    add_task,
    dashboard,
    toggle_task_status
)
urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('leads/', lead_list, name='lead_list'),
    path('leads/add/', add_lead, name='add_lead'),
    path('leads/edit/<int:lead_id>/', edit_lead, name='edit_lead'),
    path('leads/delete/<int:lead_id>/', delete_lead, name='delete_lead'),
    path('leads/convert/<int:lead_id>/', convert_lead_to_client, name='convert_lead'),
    path('clients/', client_list, name='client_list'),
    path('tasks/', task_list, name='task_list'),
    path('tasks/add/', add_task, name='add_task'),
    path('', dashboard, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('task/<int:task_id>/toggle-status/', toggle_task_status, name='toggle_task_status'),
    path('tasks/edit/<int:task_id>/', views.edit_task, name='edit_task'),
    path('tasks/delete/<int:task_id>/', views.delete_task, name='delete_task'),
    # path('toggle-task-status-in-list/<int:task_id>/', views.toggle_task_status_in_list, name='toggle_task_status_in_list'),
]