from django.urls import path
from .import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_update_view, name='profile_update'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('projek/', views.project_list_view, name='list_projek'),
    path('projek/create', views.create_project_view, name='create_project'),
    path('projek/<int:project_id>/edit/', views.edit_project_view, name='update_project'),
    path('projek/<int:project_id>/view/', views.project_detail_view, name='view_project'),

     # --- URL Problem Framing ---
    path('problem-framing/select-project/', views.select_problem_framings, name='select_project_for_framing'), # Pilih proyek untuk PF
    path('problem-framing/create/<int:project_id>/', views.create_problem_framing_view, name='create_problem_framing'), # Buat Problem Framing
    path('problem-framing/list/', views.problem_framing_list_view, name='problem_framing_list'), # Daftar semua Problem Framing
    path('problem-framing/edit/<int:pk>/', views.edit_problem_framing_view, name='edit_problem_framing'), # Edit Problem Framing
    path('problem-framing/view/<int:pk>/', views.problem_framing_detail_view, name='view_problem_framing'), # Edit Problem Framing
    path('problem-framing/<int:pk>/delete/', views.delete_problem_framing_view, name='delete_problem_framing'),

    # --- URL: Permintaan Dataset ---
    path('dataset-request/select-project/', views.select_project_for_dataset_request_view, name='select_project_for_dataset_request'),
    path('dataset-request/create/<int:project_id>/', views.create_dataset_request_view, name='create_dataset_request'),
    path('dataset-request/list/', views.dataset_request_list_view, name='dataset_request_list'),
    path('dataset-request/<int:request_id>/delete/', views.delete_request_dataset, name='delete_request_dataset'),

    #--api-- datasets
    path('dataset-request/api/<int:projek_id>/', views.get_request_data_api, name='get_request_data_api'),
    path('problem-framing/api<int:pk>/',views.problem_framing_api, name="get_problem_framing_api"),

    # --- URL : Permintaan Data Processing ---
    path('processing/select-project/', views.select_project_for_data_processing_view, name='select_project_for_data_processing_view'),
    path('processing/view/<int:pk>/', views.data_processing_detail_view, name='view_data_processing_view'),
    path('processing/edit/<int:pk>/', views.edit_data_processing_view, name='edit_data_processing_view'),
    path('processing/create/<int:project_id>/', views.create_data_processing_view, name='create_data_processing_view'),
    path('processing/list/', views.data_processing_list_view, name='data_processing_list_view'),
    path('processing-list/<int:pk>/delete/', views.delete_processing_data, name='delete_processing_data'),


    # --- URL : Permintaan Training Model ---
    path('training-model/list/', views.training_model_list_view, name='model_training_list'),

    path('training-model/select-project/', views.select_project_for_training_model_view, name='select_project_for_training_model'),
    path('training-model/view/<int:pk>/', views.training_model_detail_view, name='view_training_model'),
    path('training-model/edit/<int:pk>/', views.edit_training_model_view, name='edit_training_model'),
    path('training-model/create/<int:pk>/', views.create_training_model_view, name='create_training_model'),
    path('training-model/<int:pk>/delete/', views.delete_training_model, name='delete_training_model'),

    # --- URL : Dokumentasi ---
    path('documentations/', views.documentations, name='documentations'),
]
