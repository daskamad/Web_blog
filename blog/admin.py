from django.contrib import admin
from . import models


# Register your models here.
@admin.register(models.Post)
class CustomPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publish', 'status')  # Вывод информации о записи в бд
    list_filter = ('status', 'publish', 'author',)  # Боковая панель для выбора записи по кретериям
    search_fields = ('title', 'body',)  # Поля по которым происходит поиск записи по словам
    prepopulated_fields = {"slug": ('title',)}  # Для автоматического создания слагфиелд
    raw_id_fields = ('author',)  # Меняет выбор автора со список на поиск (по номеру?)
    date_hierarchy = 'publish'  # Создает меню для выбора записи по году месяцу дню
    ordering = ('status', 'publish')  # Для сортировки записей в админ панели


@admin.register(models.Comment)
class CustomCommentsAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'post', 'created', 'active')
    list_filter = ('active', 'created', 'updated')
    search_fields = ('name', 'email', 'body')
