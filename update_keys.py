#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для обновления VLESS ключей в файле SCRAB_PODPISKI.txt
Сохраняет шапку и добавляет ключи с 7-й строки
"""

import requests
import urllib.parse
import re
import os

def load_keys_from_url(url):
    """Загружает ключи из указанного URL"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text.strip().split('\n')
    except Exception as e:
        print(f"Ошибка загрузки ключей: {e}")
        return []

def extract_name_from_key(key):
    """Извлекает название соединения из ключа"""
    if '#' in key:
        name_part = key.split('#', 1)[1]
        # Декодируем URL-encoded название
        try:
            decoded_name = urllib.parse.unquote(name_part)
            return decoded_name
        except:
            return name_part
    return ""

def filter_keys_by_providers(keys, target_providers):
    """Фильтрует ключи по нужным провайдерам"""
    filtered_keys = []
    
    for key in keys:
        if not key.strip():
            continue
            
        name = extract_name_from_key(key)
        
        # Проверяем содержится ли название провайдера в имени соединения
        for provider in target_providers:
            if provider.lower() in name.lower():
                filtered_keys.append(key)
                break
    
    return filtered_keys

def clean_and_number_keys(keys):
    """Очищает названия ключей и добавляет порядковые номера в конец"""
    
    cleaned_keys = []
    
    for line in keys:
        line = line.strip()
        if not line:
            continue
        
        # Находим позицию символа #
        if '#' in line:
            # Отрезаем все до # включительно
            key_part = line.split('#', 1)[0]
            cleaned_keys.append(key_part)
        else:
            # Если нет #, берем всю строку
            cleaned_keys.append(line)
    
    # Добавляем порядковые номера в конец после #
    numbered_keys = []
    for i, key in enumerate(cleaned_keys, 1):
        numbered_keys.append(f"{key}#{i}")
    
    return numbered_keys

def read_header(filename):
    """Читает шапку файла (первые 6 строк)"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            header = lines[:6]  # Первые 6 строк
            return header
    except Exception as e:
        print(f"Ошибка чтения шапки файла: {e}")
        return None

def update_file_with_keys(filename, header, keys):
    """Обновляет файл, сохраняя шапку и добавляя ключи с 7-й строки"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            # Записываем шапку
            f.writelines(header)
            # Добавляем пустую строку (6-я строка)
            f.write('\n')
            # Добавляем пустую строку (7-я строка)
            f.write('\n')
            # Записываем ключи с 8-й строки
            for key in keys:
                f.write(key + '\n')
        print(f"Файл {filename} обновлен. Добавлено {len(keys)} ключей")
    except Exception as e:
        print(f"Ошибка обновления файла: {e}")

def main():
    # URL для загрузки ключей
    urls = [
        "https://raw.githubusercontent.com/zieng2/wl/main/vless_lite.txt",
        "https://gbr.mydan.online/configs",
        "https://raw.githubusercontent.com/RKPchannel/RKP_bypass_configs/refs/heads/main/configs/url_work.txt"
    ]
    
    # Нужные провайдеры (только для первой ссылки)
    target_providers = ["VK", "Yandex", "Aeza Group", "Timeweb"]
    
    # Имя выходного файла
    output_file = "SCRAB_PODPISKI.txt"
    
    print("Обновление VLESS ключей...")
    
    # Читаем существующую шапку
    header = read_header(output_file)
    if header is None:
        print("Не удалось прочитать шапку файла")
        return
    
    print("Шапка файла успешно прочитана")
    
    all_filtered_keys = []
    
    for i, url in enumerate(urls):
        print(f"\nЗагрузка ключей из: {url}")
        keys = load_keys_from_url(url)
        
        if not keys:
            print(f"Не удалось загрузить ключи из {url}")
            continue
        
        print(f"Загружено {len(keys)} ключей")
        
        # Для первой ссылки применяем фильтрацию, для второй и третьей - берем все ключи
        if i == 0:  # Первая ссылка
            print("Фильтрация ключей...")
            filtered_keys = filter_keys_by_providers(keys, target_providers)
            print(f"Найдено {len(filtered_keys)} ключей от нужных провайдеров")
        else:  # Вторая и третья ссылки
            print("Собираем все ключи без фильтрации...")
            filtered_keys = [key for key in keys if key.strip()]  # Убираем пустые строки
            print(f"Собрано {len(filtered_keys)} ключей")
        
        all_filtered_keys.extend(filtered_keys)
    
    if not all_filtered_keys:
        print("Не найдено ключей")
        return
    
    print(f"\nВсего найдено {len(all_filtered_keys)} ключей")
    
    print("Очистка и нумерация ключей...")
    numbered_keys = clean_and_number_keys(all_filtered_keys)
    
    print("Обновление файла...")
    update_file_with_keys(output_file, header, numbered_keys)
    
    # Вывод статистики по провайдерам (только для первой ссылки)
    print("\nСтатистика по провайдерам (из первой ссылки):")
    for provider in target_providers:
        provider_keys = [key for key in all_filtered_keys if provider.lower() in extract_name_from_key(key).lower()]
        print(f"{provider}: {len(provider_keys)} ключей")
    
    other_keys_count = len([k for k in all_filtered_keys if not any(p.lower() in extract_name_from_key(k).lower() for p in target_providers)])
    print(f"\nДобавлено всех ключей из второй и третьей ссылок: {other_keys_count} ключей")
    
    print(f"\nГотово! Файл {output_file} обновлен с {len(numbered_keys)} соединениями.")

if __name__ == "__main__":
    main()
