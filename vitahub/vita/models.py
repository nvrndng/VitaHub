
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    nickname = models.CharField(max_length=100, blank=True)
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True)
    about = models.TextField(blank=True)
    points = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.user.username


class ArticleCategory(models.Model):
    name = models.CharField('Название', max_length=100)
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Категория статей'
        verbose_name_plural = 'Категории статей'

    def __str__(self):
        return self.name


class Article(models.Model):
    category = models.ForeignKey(ArticleCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='articles')
    title = models.CharField('Заголовок', max_length=200)
    short_description = models.TextField('Краткое описание', max_length=300)
    content = models.CharField('Текст статьи')
    image = models.ImageField(upload_to='articles/', blank=True, null=True)
    is_published = models.BooleanField('Опубликована', default=False)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата изменения', auto_now=True)

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
        ordering = ['-created_at']

    def __str__(self):
        return self.title





class Specialist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='specialist_profile')
    specialization = models.CharField('Специализация', max_length=150)
    bio = models.TextField('О специалисте')
    education = models.TextField('Образование', blank=True)
    experience_years = models.PositiveIntegerField('Опыт работы, лет', default=0)
    photo = models.ImageField(upload_to='specialists/', blank=True, null=True)
    consultation_price = models.DecimalField('Цена консультации', max_digits=10, decimal_places=2, default=0)
    is_available = models.BooleanField('Принимает записи', default=True)

    class Meta:
        verbose_name = 'Специалист'
        verbose_name_plural = 'Специалисты'

    def __str__(self):
        return f'{self.user.get_full_name()} - {self.specialization}'




class ForumTopic(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_topics')
    title = models.CharField('Заголовок темы', max_length=200)
    content = models.TextField('Текст темы')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата изменения', auto_now=True)
    is_closed = models.BooleanField('Тема закрыта', default=False)

    class Meta:
        verbose_name = 'Тема форума'
        verbose_name_plural = 'Темы форума'
        ordering = ['-created_at']

    def __str__(self):
        return self.title




class ForumPost(models.Model):
    topic = models.ForeignKey(ForumTopic, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_posts')
    content = models.TextField('Сообщение')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Сообщение форума'
        verbose_name_plural = 'Сообщения форума'
        ordering = ['-created_at']

    def __str__(self):
        return f'Ответ к теме <<{self.topic.title}>>'





class ProductCategory(models.Model):
    name = models.CharField('Название', max_length=100)
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Категория товаров'
        verbose_name_plural = 'Категории товаров'

    def __str__(self):
        return self.name




class Product(models.Model):
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    name = models.CharField('Название товара', max_length=200)
    description = models.TextField('Описание')
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    stock = models.PositiveIntegerField('Количество на складе', default=0)
    is_active = models.BooleanField('Доступен для продажи', default=True)
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['name']

    def __str__(self):
        return self.name




class Order(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', 'Новый'
        PROCESSING = 'processing', 'В обработке'
        SHIPPED = 'shipped', 'Отправлен'
        DELIVERED = 'delivered', 'Доставлен'
        CANCELLED = 'cancelled', 'Отменен'


    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='orders')
    status = models.CharField('Статус', choices=Status.choices, default=Status.NEW, max_length=20)
    total = models.DecimalField('Сумма заказа', max_digits=10, decimal_places=2, default=0)
    phone = models.CharField('Телефон для связи', max_length=30)
    address = models.CharField('Адрес доставки', max_length=300)
    created_at = models.DateTimeField('Дата заказа', auto_now_add=True)
    updated_at = models.DateTimeField('Дата изменения', auto_now=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заказ №{self.pk} - {self.user.username}'




class OrderItem(models.Model):
    user = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items')
    quantity = models.PositiveIntegerField('Количество', default=1)
    price = models.DecimalField('Цена на момент заказа', max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказе'

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'





class Consultation(models.Model):
    class Status(models.TextChoices):
        REQUESTED = 'requested', 'Ожидает подтверждения'
        CONFIRMED = 'confirmed', 'Подтверждена'
        COMPLETED = 'completed', 'Завершена'
        CANCELLED = 'cancelled', 'Отменена'

    class Format(models.TextChoices):
        CHAT = 'chat', 'Чат'
        VIDEO = 'video', 'Видеозвонок'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consultations')
    specialist = models.ForeignKey(Specialist, on_delete=models.CASCADE, related_name='consultations')
    scheduled_at = models.DateTimeField('Дата и время консультации')
    consultation_format = models.CharField('Формат', max_length=10, choices=Format.choices, default=Format.CHAT)
    status = models.CharField('Статус', max_length=20, choices=Status.choices, default=Status.REQUESTED)
    notes = models.TextField('Комментарий пользователя', blank=True)
    created_at = models.DateTimeField('Дата записи', auto_now_add=True)

    class Meta:
        verbose_name = 'Консультация'
        verbose_name_plural = 'Консультации'
        ordering = ['-scheduled_at']

    def __str__(self):
        return f'{self.user.username} - {self.specialist}'



class LabResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lab_results')
    title = models.CharField('Название анализа', max_length=200)
    file = models.FileField(upload_to='lab_results/')
    result_date = models.DateField('Дата анализа', null=True, blank=True)
    uploaded_at = models.DateTimeField('Дата загрузки', auto_now_add=True)
    comment = models.TextField('Комментарий', blank=True)

    class Meta:
        verbose_name = 'Результат анализа'
        verbose_name_plural = 'Результаты анализов'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'{self.title} - {self.user.username}'




class PointTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='point_transactions')
    amount = models.IntegerField('Изменение баллов')
    reason = models.CharField('Причина начисления', max_length=250)
    created_at = models.DateTimeField('Дата операции', auto_now_add=True)

    class Meta:
        verbose_name = 'Операция с баллами'
        verbose_name_plural = 'История баллов'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username}: {self.amount:+} баллов'