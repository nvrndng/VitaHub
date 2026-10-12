from django.contrib import admin
from django.db import transaction
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

    def save_model(self, request, obj, form, change):
        old_status = None

        if change and obj.pk:
            old_status = (Order.objects.filter(pk=obj.pk).values_list('status', flat=True).first())

        with transaction.atomic():
            super().save_model(request, obj, form, change)

            if (
                obj.status == Order.Status.DELIVERED
                and old_status != Order.Status.DELIVERED
            ):
                reason = f'Бонус за доставленный заказ №{obj.pk}'

                already_awarded = PointTransaction.objects.filter(user=obj.user, reason=reason).exists()

                if not already_awarded:
                    points_to_add = int(obj.total // 100)

                    if points_to_add > 0:
                        profile, created = Profile.objects.get_or_create(user=obj.user)

                        profile = Profile.objects.select_for_update().get(pk=profile.pk)

                        profile.points += points_to_add
                        profile.save(update_fields=['points'])

                        PointTransaction.objects.create(user=obj.user, reason=reason, amount=points_to_add)

            if (
                    obj.status == Order.Status.CANCELLED
                    and old_status != Order.Status.CANCELLED
                    and obj.points_spent > 0
            ):
                reason = f'Возврат баллов за отмену заказа №{obj.pk}'

                already_refunded = PointTransaction.objects.filter(user=obj.user, reason=reason).exists()

                if not already_refunded:
                    profile, created = Profile.objects.get_or_create(user=obj.user)

                    profile = Profile.objects.select_for_update().get(pk=profile.pk)

                    profile.points += obj.points_spent
                    profile.save(update_fields=['points'])

                    PointTransaction.objects.create(user=obj.user, amount=obj.points_spent, reason=reason)


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