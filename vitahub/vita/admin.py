from django.contrib import admin
from .models import Profile, ArticleCategory, Article, Specialist, ForumTopic, ForumPost, ProductCategory, Product, Order, OrderItem, Consultation, LabResult, PointTransaction

# Register your models here.


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'nickname', 'phone', 'points')

    search_fields = ('user__username', 'user__email', 'nickname')


@admin.register(ArticleCategory)
class ArticleCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_published', 'created_at')
    list_filter = ('is_published', 'category', 'created_at')
    search_fields = ('title', 'short_description', 'content')


@admin.register(Specialist)
class SpecialistAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'experience_years', 'consultation_price', 'is_available')
    list_filter = ('is_available', 'specialization')
    search_fields = ('user__username', 'specialization', 'bio')



@admin.register(ForumTopic)
class ForumTopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_closed', 'created_at')
    list_filter = ('is_closed', 'created_at')
    search_fields = ('title', 'content', 'author__username')



@admin.register(ForumPost)
class ForumPostAdmin(admin.ModelAdmin):
    list_display = ('topic', 'author', 'created_at')
    search_fields = ('content', 'author__username', 'topic__title')


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'is_active')
    list_filter = ('is_active', 'category')
    search_fields = ('name', 'description')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'created_at', 'total')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone')
    inlines = (OrderItemInline,)


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialist', 'scheduled_at', 'consultation_format', 'status')
    list_filter = ('consultation_format', 'status', 'scheduled_at')
    search_fields = ('user__username', 'specialist__user__username', 'specialist__specialization')



@admin.register(LabResult)
class LabResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'result_date', 'uploaded_at')
    search_fields = ('title', 'user__username', 'user__email')


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'reason', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'reason')