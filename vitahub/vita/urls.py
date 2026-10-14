from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views


from . import views


urlpatterns = [
    path('', views.home, name='home'),

    path(
        'register/',
        views.register_view,
        name='register'
    ),

    path(
        'login/',
        views.login_view,
        name='login'
    ),

    path(
        'logout/',
        views.logout_view,
        name='logout'
    ),


    path(
        'profile/',
        views.profile_view,
        name='profile'
    ),

    path(
        'profile/edit/',
        views.profile_edit_view,
        name='profile_edit'
    ),


    path(
        'articles/',
        views.articles_view,
        name='articles'
    ),

    path(
        'articles/<int:article_id>/',
        views.article_detail_view,
        name='article_detail'
    ),

    path(
        'specialists/',
         views.specialists_view,
         name='specialists'
    ),

    path(
        'specialists/<int:specialist_id>/',
         views.specialist_detail_view,
         name='specialist_detail'
    ),

    path(
        'forum/',
         views.forum_view,
         name='forum'
    ),

    path(
        'forum/topic/<int:topic_id>/',
         views.forum_topic_view,
         name='forum_topic'
    ),

    path(
        'forum/create/',
        views.forum_create_view,
        name='forum_create'
    ),

    path(
        'shop/',
        views.shop_view,
        name='shop'
    ),

    path(
        'shop/<int:product_id>/',
        views.product_detail_view,
        name='product_detail'
    ),

    path(
        'cart/',
        views.cart_view,
        name='cart'
    ),

    path(
        'cart/add/<int:product_id>/',
        views.cart_add_view,
        name='cart_add'
    ),

    path(
        'cart/update/<int:product_id>/',
        views.cart_update_view,
        name='cart_update'
    ),

    path(
        'cart/remove/<int:product_id>/',
        views.cart_remove_view,
        name='cart_remove'
    ),

    path(
        'checkout/',
        views.checkout_view,
        name='checkout'
    ),

    path(
        'orders/',
        views.orders_view,
        name='orders'
    ),

    path(
        'consultations/',
        views.consultations_view,
        name='consultations'
    ),

    path(
        'consultations/<int:consultation_id>/cancel/',
        views.cancel_consultation_view,
        name='cancel_consultation'
    ),

    path(
        'lab-results/',
        views.lab_results_view,
        name='lab_results'
    ),

    path(
        'lab-results/<int:result_id>/download/',
        views.lab_result_download_view,
        name='lab_result_download'
    ),

    path(
        'points/',
        views.points_view,
        name='points'
    ),

    path(
        'activate/<uidb64>/<token>/',
        views.activate_account,
        name='activate_account'
    ),


    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='vita/password_reset.html',
            email_template_name='vita/password_reset_email.html',
            subject_template_name='vita/password_reset_subject.txt',
            success_url=reverse_lazy('password_reset_done'),
        ),
        name='password_reset',
    ),

    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='vita/password_reset_done.html',
        ),
        name='password_reset_done',
    ),

    path(
        'password-reset-confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='vita/password_reset_confirm.html',
            success_url=reverse_lazy('password_reset_complete'),
        ),
        name='password_reset_confirm',
    ),

    path(
        'password-reset-complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='vita/password_reset_complete.html',
        ),
        name='password_reset_complete',
    ),

    path(
        'contacts/',
        views.contacts_view,
        name='contacts',
    ),

    path(
        'terms/',
        views.terms_view,
        name='terms'
    ),

]