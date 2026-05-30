from django.urls import path

from . import views

app_name = 'finanzas'

urlpatterns = [
    path('', views.InboxView.as_view(), name='inbox'),
    path("tag/create/", views.CreateTagView.as_view(), name="create_tag"),
    path("tag/<int:tag_id>/", views.TagDetailView.as_view(), name="tag_detail"),
    path('<int:pk>/clasificar/', views.ClassifyTransactionView.as_view(), name='classify_transaction'),
    path('<int:pk>/ignorar/', views.IgnoreTransactionView.as_view(), name='ignore_transaction'),
    path('transaction/manual/', views.CreateTransactionManualView.as_view(), name='create_transaction_manual'),
    path("transaction/<int:pk>/update/", views.UpdateTransactionView.as_view(), name="update_transaction"),
    path("transaction/<int:pk>/delete/", views.DeleteTransactionView.as_view(), name="delete_transaction"),
    path("email-source/create/", views.CreateEmailSourceView.as_view(), name="create_email_source"),
    path("regex-rule/list/", views.RegexRuleListView.as_view(), name="regex_rule_list"),
    path("regex-rule/create/", views.CreateRegexRuleView.as_view(), name="create_regex_rule"),
    path("regex-rule/<int:pk>/update/", views.UpdateRegexRuleView.as_view(), name="update_regex_rule"),
    #path("regex-rule/<int:pk>/delete/", views.DeleteRegexRuleView.as_view(), name="delete_regex_rule"), 

]
