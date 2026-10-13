from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Article, ArticleCategory, Specialist, Profile, ForumTopic, ForumPost, Product, ProductCategory, Order, OrderItem, Consultation, LabResult, PointTransaction
from decimal import Decimal
from django.contrib import messages
from django.utils import timezone
from django.utils.dateparse import parse_datetime, parse_date
from django.db import transaction
from .forms import RegisterForm, ProfileForm
from django.http import FileResponse, Http404
from pathlib import Path
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings

from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.urls import reverse



def home(request):
    articles = (Article.objects.filter(is_published=True).select_related('category', 'author').order_by('-created_at')[:3])

    forum_topics = (ForumTopic.objects.select_related('author').prefetch_related('posts').order_by('-created_at')[:3])

    products = (Product.objects.filter(is_active=True, stock__gt=0).select_related('category').order_by('-created_at')[:3])

    return render(request, 'vita/home.html', {'articles': articles, 'forum_topics': forum_topics,'products': products})



def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save(commit=False)
                    user.is_active = False
                    user.save()

                    Profile.objects.get_or_create(user=user)

                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    token = default_token_generator.make_token(user)

                    activation_url = request.build_absolute_uri(
                        reverse(
                            'activate_account',
                            kwargs={
                                'uidb64': uid,
                                'token': token,
                            },
                        )
                    )

                    send_mail(
                        subject='Подтверждение регистрации VitaHub',
                        message=(
                            f"Здравствуйте, {user.first_name or 'пользователь'}!\n\n"
                            "Спасибо за регистрацию на VitaHub!\n"
                            "Для подтверждения адреса электронной почты "
                            "перейдите по ссылке:\n\n"
                            f"{activation_url}\n\n"
                            "Если вы не регистрировались на VitaHub, "
                            "просто проигнорируйте это письмо."
                        ),
                        from_email=None,
                        recipient_list=[user.email],
                        fail_silently=False,
                    )

                messages.success(
                    request,
                    'Регистрация почти завершена! '
                    'Проверьте почту и перейдите по ссылке из письма.',
                )
                return redirect('login')

            except Exception:
                messages.error(
                    request,
                    'Не удалось отправить письмо. '
                    'Попробуйте зарегистрироваться еще раз позже.',
                )
    else:
        form = RegisterForm()

    return render(request, 'vita/register.html', {'form': form})


def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if user.is_active:
            messages.info(request, 'Ваш аккаунт уже подтвержден.')
        else:
            user.is_active = True
            user.save(update_fields=['is_active'])
            messages.success(
                request,
                'Email подтверждён! Теперь вы можете войти в VitaHub.',
            )
    else:
        messages.error(
            request,
            'Ссылка подтверждения недействительна.',
        )

    return redirect('login')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=email,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('home')

        return render(
            request,
            'vita/login.html',
            {
                'error': 'Неверный email или пароль.'
            }
        )

    return render(request, 'vita/login.html')


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def profile_view(request):
    return render(request, 'vita/profile.html')

@login_required
def profile_edit_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save(request.user)

            return redirect('profile')

    else:
        form = ProfileForm(instance=profile, user=request.user)

    return render(request, 'vita/profile_edit.html', {'form': form})




def articles_view(request):
    articles = Article.objects.filter(is_published=True).select_related('category', 'author')
    categories = ArticleCategory.objects.all()
    category_id = request.GET.get('category')

    if category_id and category_id.isdigit():
        articles = articles.filter(category_id=int(category_id))

    return render(request, 'vita/articles.html', {'articles': articles, 'categories': categories,})


def article_detail_view(request, article_id):
    article = get_object_or_404(Article, pk=article_id, is_published=True)

    other_articles = (Article.objects.filter(is_published=True).exclude(pk=article.pk).order_by('-created_at')[:3])

    return render(request, 'vita/article_detail.html', {'article': article, 'other_articles': other_articles})


def specialists_view(request):
    specialists = Specialist.objects.filter(is_available=True).select_related('user')

    return render(request, 'vita/specialists.html', {'specialists': specialists})



@login_required
def specialist_detail_view(request, specialist_id):
    specialist = get_object_or_404(Specialist.objects.select_related('user'), pk=specialist_id)

    if request.method == 'POST':
        if not specialist.is_available:
            messages.error(request, 'Этот специалист сейчас не принимает записи.')
            return redirect('specialist_detail', specialist_id=specialist.id)

        scheduled_at = parse_datetime(request.POST.get('scheduled_at', ''))
        consultation_format = request.POST.get('consultation_format', 'chat')
        notes = request.POST.get('notes', '').strip()

        if scheduled_at and timezone.is_naive(scheduled_at):
            scheduled_at = timezone.make_aware(scheduled_at, timezone.get_current_timezone())

        if not scheduled_at:
            messages.error(request, 'Укажите корректные дату и время консультации.')
        elif scheduled_at <= timezone.now():
            messages.error(request, 'Дата и время консультации должны быть в будущем.')
        elif consultation_format not in dict(Consultation.Format.choices):
            messages.error(request, 'Выберите корректный формат консультации.')
        else:
            is_time_taken = Consultation.objects.filter(specialist=specialist, scheduled_at=scheduled_at).exclude(status=Consultation.Status.CANCELLED).exists()

            if is_time_taken:
                messages.error(request, 'Это время уже занято. Пожалуйста, выберите другое.')

            else:
                Consultation.objects.create(
                    user=request.user,
                    specialist=specialist,
                    scheduled_at=scheduled_at,
                    consultation_format=consultation_format,
                    notes=notes,
                    status=Consultation.Status.REQUESTED,
                )
                messages.success(request, 'Вы записались на консультацию. Ожидайте подтверждения.')
                return redirect('consultations')

    return render(request, 'vita/specialist_detail_page.html', {'specialist': specialist})


def forum_view(request):
    topics = ForumTopic.objects.select_related('author').all()

    return render(request, 'vita/forum.html', {'topics': topics})


def forum_topic_view(request, topic_id):
    topic = get_object_or_404(ForumTopic.objects.select_related('author'), pk=topic_id)


    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')

        if topic.is_closed:
            error = 'Эта тема закрыта для ответов'
        else:
            content = request.POST.get('content', '').strip()

            if content:
                ForumPost.objects.create(topic=topic, author=request.user, content=content)
                return redirect('forum_topic', topic_id=topic_id)

            error = 'Напишите текст сообщения'

    else:
        error = ''


    posts = topic.posts.select_related('author').order_by('created_at')

    return render(request, 'vita/forum_topic.html', {'topic': topic, 'posts': posts, 'error': error})


@login_required
def forum_create_view(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()

        if title and content:
            ForumTopic.objects.create(author=request.user, title=title, content=content)

            return redirect('forum')

        error = 'Заполните название темы и текст сообщения'

    else:
        error = ''

    return render(request, 'vita/forum_create.html', {'error': error})



def shop_view(request):
    products = Product.objects.filter(is_active=True).select_related('category').order_by('name')

    categories = ProductCategory.objects.all().order_by('name')

    category_id = request.GET.get('category')
    if category_id and category_id.isdigit():
        products = products.filter(category_id=int(category_id))

    return render(request, 'vita/shop.html', {'products': products, 'categories': categories, 'selected_category': category_id})




def product_detail_view(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)

    return render(request, 'vita/product_detail.html', {'product': product})




def cart_view(request):
    cart = request.session.get('cart', {})
    product_ids = [int(product_id) for product_id in cart.keys() if product_id.isdigit()]

    products = Product.objects.filter(
        id__in=product_ids,
        is_active=True
    ).select_related('category')

    cart_items = []
    total_price = 0
    total_quantity = 0

    for product in products:
        quantity = int(cart.get(str(product.id), 0))

        if quantity < 1:
            continue

        quantity = min(quantity, product.stock)

        if quantity < 1:
            continue

        item_total = product.price * quantity
        total_price += item_total
        total_quantity += quantity

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'total': item_total,
        })

    # Сохраняем исправленные количества, если остатки на складе изменились.
    request.session['cart'] = {
        str(item['product'].id): item['quantity']
        for item in cart_items
    }

    return render(request, 'vita/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_quantity': total_quantity,
        'total_products': len(cart_items),
    })


@require_POST
def cart_add_view(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True
    )

    if product.stock < 1:
        return redirect('product_detail', product_id=product.id)

    cart = request.session.get('cart', {})
    key = str(product.id)
    current_quantity = int(cart.get(key, 0))

    cart[key] = min(current_quantity + 1, product.stock)

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart')


@require_POST
def cart_update_view(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True
    )

    cart = request.session.get('cart', {})
    key = str(product.id)

    if key in cart:
        action = request.POST.get('action')

        try:
            quantity = int(cart[key])
        except (TypeError, ValueError):
            quantity = 1

        if action == 'increase':
            quantity = min(quantity + 1, product.stock)
        elif action == 'decrease':
            quantity -= 1

        if quantity < 1 or product.stock < 1:
            cart.pop(key, None)
        else:
            cart[key] = min(quantity, product.stock)

        request.session['cart'] = cart
        request.session.modified = True

    return redirect('cart')


@require_POST
def cart_remove_view(request, product_id):
    cart = request.session.get('cart', {})
    cart.pop(str(product_id), None)

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart')






@login_required
def checkout_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    cart = request.session.get('cart', {})
    product_ids = [
        int(product_id)
        for product_id in cart
        if str(product_id).isdigit()
    ]

    products = Product.objects.filter(
        id__in=product_ids,
        is_active=True
    ).select_related('category')

    cart_items = []
    total_price = Decimal('0.00')

    for product in products:
        try:
            quantity = int(cart.get(str(product.id), 0))
        except (TypeError, ValueError):
            quantity = 0

        if quantity < 1:
            continue

        item_total = product.price * quantity
        total_price += item_total

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'total': item_total,
        })


    points_to_use = 0

    if request.method == 'POST':
        try:
            points_to_use = int(request.POST.get('points_to_use', '0'))
        except (TypeError, ValueError):
            points_to_use = 0


    discount_preview = min (max(points_to_use, 0), int(total_price))

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'profile_points': profile.points,
        'points_to_use': points_to_use,
        'discount_preview': discount_preview,
        'discounted_total': max(total_price - Decimal(discount_preview), Decimal('0.00')),
        'error': '',
        'form_data': request.POST if request.method == 'POST' else {},
    }

    if points_to_use < 0:
        context['error'] = 'Количество баллов не может быть отрицательным.'
        return render(request, 'vita/checkout.html', context)

    if points_to_use > profile.points:
        context['error'] = 'У вас недостаточно баллов для этой скидки.'
        return render(request, 'vita/checkout.html', context)

    if Decimal(points_to_use) > total_price:
        context['error'] = 'Скидка не может превышать стоимость товаров.'
        return render(request, 'vita/checkout.html', context)

    if not cart_items:
        return redirect('cart')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        delivery_method = request.POST.get('delivery', 'delivery')
        payment_method = request.POST.get('payment', 'on_delivery')
        address = request.POST.get('address', '').strip()
        comment = request.POST.get('comment', '').strip()

        if not first_name or not last_name or not phone or not email:
            context['error'] = 'Заполните имя, фамилию, телефон и email.'
            return render(request, 'vita/checkout.html', context)

        if delivery_method not in ('delivery', 'pickup'):
            context['error'] = 'Выберите способ получения заказа.'
            return render(request, 'vita/checkout.html', context)

        if payment_method not in ('online', 'on_delivery'):
            context['error'] = 'Выберите способ оплаты.'
            return render(request, 'vita/checkout.html', context)

        if delivery_method == 'delivery' and not address:
            context['error'] = 'Укажите адрес доставки.'
            return render(request, 'vita/checkout.html', context)

        if delivery_method == 'pickup':
            address = 'Самовывоз'

        try:
            with transaction.atomic():
                locked_products = {
                    product.id: product
                    for product in Product.objects.select_for_update().filter(
                        id__in=product_ids,
                        is_active=True)
                }

                order_lines = []
                actual_total = Decimal('0.00')

                for item in cart_items:
                    product_id = item['product'].id
                    product = locked_products.get(product_id)

                    if product is None:
                        raise ValueError('Один из товаров больше недоступен.')

                    quantity = item['quantity']

                    if product.stock < quantity:
                        raise ValueError(
                            f'Недостаточно товара «{product.name}» на складе. '
                            f'Доступно: {product.stock} шт.'
                        )

                    line_total = product.price * quantity
                    actual_total += line_total
                    order_lines.append((product, quantity))

                locked_profile = Profile.objects.select_for_update().get(user=request.user)

                if points_to_use > locked_profile.points:
                    raise ValueError('Баланс баллов изменился. Обновите страницу и попробуйте снова.')

                if Decimal(points_to_use) > actual_total:
                    raise ValueError('Скидка не может превышать стоимость товаров.')

                final_total = actual_total - Decimal(points_to_use)

                request.user.first_name = first_name
                request.user.last_name = last_name
                request.user.email = email
                request.user.save(update_fields=['first_name', 'last_name', 'email'])

                order = Order.objects.create(user=request.user, total=final_total, points_spent=points_to_use, phone=phone, address=address, delivery_method=delivery_method, payment_method=payment_method, comment=comment)

                for product, quantity in order_lines:
                    OrderItem.objects.create(user=order, product=product, quantity=quantity, price=product.price)

                    product.stock -= quantity
                    product.save(update_fields=['stock'])

                if points_to_use > 0:
                    locked_profile.points -= points_to_use
                    locked_profile.save(update_fields=['points'])

                    PointTransaction.objects.create(user=request.user, amount=-points_to_use, reason=f'Списание баллов за заказ №{order.pk}')

        except ValueError as exc:
            context['error'] = str(exc)
            context['profile_points'] = Profile.objects.get(user=request.user).points
            return render(request, 'vita/checkout.html', context)

        request.session['cart'] = {}
        request.session.modified = True

        return redirect('orders')

    return render(request, 'vita/checkout.html', context)


@login_required
def orders_view(request):
    orders = (Order.objects.filter(user=request.user).prefetch_related('items__product').order_by('-created_at'))

    for order in orders:
        items = list(order.items.all())
        order.item_count = sum(item.quantity for item in items)
        order.order_items = items

    return render(request, 'vita/orders.html', {'orders': orders})



@login_required
def consultations_view(request):
    now = timezone.now()

    consultations = (Consultation.objects.filter(user=request.user).select_related('specialist', 'specialist__user').order_by('-scheduled_at'))

    selected_filter = request.GET.get('filter', 'all')

    if selected_filter == 'upcoming':
        consultations = consultations.filter(scheduled_at__gte=now).exclude(status=Consultation.Status.CANCELLED)

    elif selected_filter == 'past':
        consultations = consultations.filter(scheduled_at__lt=now)

    return render(request, 'vita/consultations.html', {'consultations': consultations, 'selected_filter': selected_filter, 'now': now})





@login_required
@require_POST
def cancel_consultation_view(request, consultation_id):
    consultation = get_object_or_404(Consultation, pk=consultation_id, user=request.user)

    if consultation.status not in (
        Consultation.Status.REQUESTED,
        Consultation.Status.CONFIRMED,
    ):
        messages.error(request, 'Эту консультацию нельзя отменить.')
    elif consultation.scheduled_at <= timezone.now():
        messages.error(request, 'Нельзя отменить консультацию, время которой уже наступило.')
    else:
        consultation.status = Consultation.Status.CANCELLED
        consultation.save(update_fields=['status'])
        messages.success(request, 'Запись на консультацию отменена.')

    return redirect('consultations')





@login_required
def lab_results_view(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        result_date_value = request.POST.get('result_date', '').strip()
        comment = request.POST.get('comment', '').strip()
        uploaded_file = request.FILES.get('file')

        error = None
        result_date = None

        if not title:
            error = 'Укажите название анализа.'

        elif not uploaded_file:
            error = 'Выберите файл для загрузки.'

        elif uploaded_file.size > 10 * 1024 * 1024:
            error = 'Размер файла не должен превышать 10 МБ.'

        if not error and result_date_value:
            result_date = parse_date(result_date_value)

            if result_date is None:
                error = 'Укажите корректную дату анализа.'

        if not error:
            extension = Path(uploaded_file.name).suffix.lower()
            allowed_extensions = {'.pdf', '.jpg', '.jpeg', '.png'}

            if extension not in allowed_extensions:
                error = 'Допустимые форматы: PDF, JPG, JPEG и PNG.'

        if not error:
            uploaded_file.seek(0)
            signature = uploaded_file.read(8)
            uploaded_file.seek(0)

            valid_signatures = {'.pdf': signature.startswith(b'%PDF-'), '.jpg': signature.startswith(b'\xff\xd8\xff'), '.jpeg': signature.startswith(b'\xff\xd8\xff'), '.png': signature.startswith(b'\x89PNG\r\n\x1a\n')}

            if not valid_signatures.get(extension, False):
                error = 'Содержимое файла не соответствует выбранному формату.'

        if error:
            results = LabResult.objects.filter(user=request.user).order_by('-uploaded_at')

            return render(request, 'vita/lab_results.html', {'results': results, 'error': error})

        LabResult.objects.create(user=request.user, title=title, file=uploaded_file, result_date=result_date, comment=comment)

        messages.success(request, 'Результат анализа успешно загружен.')
        return redirect('lab_results')

    results = LabResult.objects.filter(user=request.user).order_by('-uploaded_at')

    return render(request, 'vita/lab_results.html', {'results': results})


@login_required
def lab_result_download_view(request, result_id):
    result = get_object_or_404(LabResult, pk=result_id, user=request.user)

    try:
        file_handle = result.file.open('rb')
    except (FileNotFoundError, OSError, ValueError):
        raise Http404('Файл не найден.')

    return FileResponse(file_handle, as_attachment=True, filename=Path(result.file.name).name)




@login_required
def points_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    transactions = PointTransaction.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'vita/points.html', {'profile': profile, 'transactions': transactions})





def contacts_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        message = request.POST.get('message', '').strip()

        if not name or not email or not message:
            messages.error(request, 'Заполните все поля формы.')
            return render(request, 'vita/contacts.html')

        if len(name) > 100 or len(email) > 254 or len(message) > 5000:
            messages.error(request, 'Одно из полей превышает допустимую длину.')
            return render(request, 'vita/contacts.html')

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Введите корректный адрес электронной почты.')
            return render(request, 'vita/contacts.html')

        try:
            send_mail(
                subject=f'Новое сообщение с сайта VitaHub от {name}',
                message=(
                    f'Имя: {name}\n'
                    f'Email отправителя: {email}\n\n'
                    f'Сообщение:\n{message}'
                ),
                from_email=None,
                recipient_list=[settings.CONTACT_EMAIL],
                fail_silently=False,
            )
        except Exception:
            messages.error(
                request,
                'Не удалось отправить сообщение. Попробуйте позже.',
            )
        else:
            messages.success(
                request,
                'Ваше сообщение отправлено! Спасибо за обращение.',
            )
            return redirect('contacts')

    return render(request, 'vita/contacts.html')
