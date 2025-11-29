from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.home,name="home"),
    path('contact/', views.contact_view, name="contact"),
    path('login/',views.login_view,name="login"),
    path('signup/',views.signup_view,name="signup"),
    path('logout/',views.logout_view,name="logout"),
    path('forgot-password/',views.forgot_password,name="forgot_password"),
    path('reset-password/<str:token>/',views.reset_password,name="reset_password"),
    
    # Mentor URLs
    path('mentor/profile/',views.mentor_profile,name="mentor_profile"),
    path('mentor/profile/edit/', views.mentor_profile_edit, name='mentor_profile_edit'),
    path('mentors/',views.find_mentors,name="find_mentors"),
    path('mentors/<int:mentor_id>/',views.mentor_detail,name="mentor_detail"),
    
    # User Settings
    path('change-password/', views.change_password, name='change_password'),

    # Custom Admin URLs
    path('admin/', views.admin_dashboard, name="admin_dashboard"),
    path('admin/mentors/', views.admin_mentors, name="admin_mentors"),
    path('admin/tests/', views.admin_quiz_manage, name='admin_quiz_manage'),
    path('admin/tests/add-category/', views.admin_add_category, name='admin_add_category'),
    path('admin/tests/<int:category_id>/', views.admin_category_detail, name='admin_category_detail'),
    path('admin/tests/<int:category_id>/edit/', views.admin_edit_category, name='admin_edit_category'),
    path('admin/tests/<int:category_id>/delete/', views.admin_delete_category, name='admin_delete_category'),
    path('admin/tests/<int:category_id>/add-question/', views.admin_add_question, name='admin_add_question'),
    path('admin/tests/question/<int:question_id>/edit/', views.admin_edit_question, name='admin_edit_question'),
    path('admin/tests/question/<int:question_id>/delete/', views.admin_delete_question, name='admin_delete_question'),
    path('admin/mentors/add/', views.admin_mentor_add, name="admin_mentor_add"),
    path('admin/mentors/<int:mentor_id>/edit/', views.admin_mentor_edit, name="admin_mentor_edit"),
    path('admin/mentors/<int:mentor_id>/delete/', views.admin_mentor_delete, name="admin_mentor_delete"),
    path('admin/skills/', views.admin_skills, name="admin_skills"),
    path('admin/skills/delete/<pk>', views.delete_skills, name="delete_skills"),
    path('admin/skills/edit/<pk>', views.edit_skills, name="edit_skills"),
    path('admin/mentors/mentor_view/<pk>', views.mentor_view, name="mentor_view"),
    path('admin/sessions/', views.admin_sessions, name="admin_sessions"),
    path('admin/sessions/<int:session_id>/set-status/', views.admin_session_set_status, name="admin_session_set_status"),
    path('hire-developer-data/', views.hire_developer_data_view, name="hire_developer_data"),
    path('contact-messages/',views.contact_messages_view,name="contact_messages"),
    # Removed approve/reject and skills management routes
    path('admin/users/', views.admin_users, name="admin_users"),
    path('admin/users/<int:user_id>/edit/', views.admin_user_edit, name="admin_user_edit"),
    path('admin/users/<int:user_id>/delete/', views.admin_user_delete, name="admin_user_delete"),
    
    # Session Booking URLs
    path('book-session/<int:mentor_id>/', views.book_session, name="book_session"),
    path('payment/<int:session_id>/', views.payment_page, name="payment_page"),
    path('session-confirmation/<int:session_id>/', views.session_confirmation, name="session_confirmation"),
    path('mentee-dashboard/', views.mentee_dashboard, name="mentee_dashboard"),
    path('mentor-dashboard/', views.mentor_dashboard, name="mentor_dashboard"),
    path('mentor/session/<int:session_id>/', views.mentor_session_detail, name='mentor_session_detail'),
    path('mentor/session/<int:session_id>/set-status/', views.mentor_session_set_status, name='mentor_session_set_status'),
    path('mentor/session/<int:session_id>/accept/', views.mentor_session_accept, name='mentor_session_accept'),

    # Hire a developer Page
    path('hire-developer/', views.hire_developer_view, name="hire_developer"),
    # Quiz / Test URLs
    path('quiz/', views.quiz_categories, name='quiz_categories'),
    path('quiz/<int:category_id>/', views.take_test, name='take_test'),
    path('quiz/result/<int:attempt_id>/', views.test_result, name='test_result'),
   
]
