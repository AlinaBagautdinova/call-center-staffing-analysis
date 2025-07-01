import pandas as pd
import numpy as np
import uuid
from datetime import datetime, timedelta
import os

def generate_data():
    '''
    Основная функция для генерации и сохранения CSV-файлов
    '''
    # Настройки генерации
    TOTAL_EMPLOYEES = 25
    NEW_EMPLOYEES_COUNT = 8
    DISMISSED_EMPLOYEES_COUNT = 9
    AVG_CALLS_PER_DAY = 100
    START_DATE = datetime(2024, 1, 1)
    END_DATE = datetime(2024, 12, 31)

    # Списки имен
    MODERN_FEMALE_NAMES = [
        'София', 'Мария', 'Анна', 'Алиса', 'Виктория', 'Полина', 'Анастасия',
        'Александра', 'Елизавета', 'Екатерина', 'Дарья', 'Ксения'
    ]
    MODERN_MALE_NAMES = [
        'Александр', 'Артём', 'Михаил', 'Максим', 'Дмитрий', 'Иван',
        'Андрей', 'Никита', 'Сергей', 'Роман', 'Егор', 'Владимир'
    ]
    COMMON_LAST_NAMES = [
        'Смирнов', 'Иванов', 'Кузнецов', 'Соколов', 'Попов', 'Лебедев',
        'Новиков', 'Морозов', 'Петров', 'Волков', 'Соловьёв',
        'Васильев', 'Зайцев', 'Павлов', 'Семёнов', 'Голубев', 'Виноградов'
    ]
    
    # Списки для генерации данных по звонкам
    CALL_TYPES = ['Исходящий', 'Входящий']
    CRM_RESULTS = [
        'Должник. Обещание оплаты', 'Должник. Просьба перезвонить', 'Должник. Отказ от взаимодействия', 'Должник',
        'Автоответчик', 'Отказ от идентификации', 'Некорректное соединение', 'Недозвон', 
        'Третье лицо. Отказ от взаимодействия', 'Третье лицо'
    ]
    CRM_RESULTS_PROBABILITY = [        
        0.04, 0.05, 0.06, 0.08, 0.20, 
        0.15, 0.23, 0.11, 0.03, 0.05
    ]
    
    VALID_INCOMING_RESULTS = [res for res in CRM_RESULTS if res not in ['Недозвон', 'Некорректное соединение', 'Автоответчик']]

    # 1. Генерация сотрудников
    print('Шаг 1: Создание списка сотрудников')
    employees_list = []
    used_names = set()
    
    while len(employees_list) < TOTAL_EMPLOYEES:
        gender = np.random.choice(['male', 'female'])
        last_name_base = np.random.choice(COMMON_LAST_NAMES)
        if gender == 'female':
            first_name = np.random.choice(MODERN_FEMALE_NAMES)
            full_name = f'{first_name} {last_name_base}а'
        else:
            first_name = np.random.choice(MODERN_MALE_NAMES)
            full_name = f'{first_name} {last_name_base}'
        
        if full_name in used_names:
            continue
        used_names.add(full_name)

        i = len(employees_list)
        STABLE_EMPLOYEES_COUNT = TOTAL_EMPLOYEES - NEW_EMPLOYEES_COUNT - DISMISSED_EMPLOYEES_COUNT
        
        if i < DISMISSED_EMPLOYEES_COUNT:
            hire_date = START_DATE - timedelta(days=np.random.randint(90, 365))
            dismissal_date = START_DATE + timedelta(days=np.random.randint(120, 300))
        elif i < DISMISSED_EMPLOYEES_COUNT + NEW_EMPLOYEES_COUNT:
            hire_date = END_DATE - timedelta(days=np.random.randint(30, 90))
            dismissal_date = pd.NaT
        else:
            hire_date = START_DATE - timedelta(days=np.random.randint(60, 365))
            dismissal_date = pd.NaT

        employee = {
            'uuid': str(uuid.uuid4()),
            'name': full_name,
            'hire_date': hire_date.date(),
            'dismissal_date': pd.to_datetime(dismissal_date).date() if pd.notna(dismissal_date) else pd.NaT
        }
        employees_list.append(employee)

    employees_df = pd.DataFrame(employees_list)
    print(f'Создано {len(employees_df)} уникальных сотрудников.')

    # 2. Генерация таблицы рабочих часов
    print('Шаг 2: Генерация отчета по рабочим часам (employees.csv)')
    hours_records = []
    date_range = pd.date_range(start=START_DATE, end=END_DATE, freq='MS')

    for _, employee in employees_df.iterrows():
        for month_start in date_range:
            is_active = (employee['hire_date'] <= (month_start + pd.offsets.MonthEnd(0)).date()) and \
                        (pd.isna(employee['dismissal_date']) or employee['dismissal_date'] >= month_start.date())
            if is_active:
                hours_records.append({
                    'name': employee['name'],
                    'period': month_start.strftime('%Y-%m-01'),
                    'hours': np.random.randint(140, 166),
                    'uuid': employee['uuid'],
                    'hire_date': employee['hire_date'],
                    'dismissal_date': employee['dismissal_date'] if pd.notna(employee['dismissal_date']) else ''
                })

    hours_df = pd.DataFrame(hours_records)
    hours_df.to_csv('employees.csv', index=False, encoding='utf-8-sig')
    print(f"Файл 'employees.csv' успешно создан. Записей: {len(hours_df)}")

    # 3. Генерация отчета по звонкам
    print('Шаг 3: Генерация детального отчета по звонкам (dayler_report.csv)')
    calls_records = []
    business_days = pd.to_datetime(pd.bdate_range(start=START_DATE, end=END_DATE))

    for current_date in business_days:
        for _, employee in employees_df.iterrows():
            is_active = (employee['hire_date'] <= current_date.date()) and \
                        (pd.isna(employee['dismissal_date']) or employee['dismissal_date'] > current_date.date())
            if is_active:
                time_since_hire = (current_date.date() - employee['hire_date']).days
                num_calls = np.random.randint(int(AVG_CALLS_PER_DAY * 0.5), int(AVG_CALLS_PER_DAY * 0.8)) if time_since_hire < 90 else np.random.randint(int(AVG_CALLS_PER_DAY * 0.9), int(AVG_CALLS_PER_DAY * 1.2))

                for _ in range(num_calls):
                    
                    call_type = np.random.choice(CALL_TYPES, p=[0.8, 0.2])
                    talk_time = 0
                    
                    if call_type == 'Входящий':
                        crm_result = np.random.choice(VALID_INCOMING_RESULTS)
                        # У входящего звонка всегда есть время разговора
                        talk_time = np.random.randint(20, 120) if time_since_hire < 90 else np.random.randint(10, 90)
                    else: # Исходящий
                        crm_result = np.random.choice(CRM_RESULTS, p=CRM_RESULTS_PROBABILITY)
                        if crm_result not in ['Недозвон', 'Некорректное соединение', 'Автоответчик']:
                            talk_time = np.random.randint(20, 120) if time_since_hire < 90 else np.random.randint(10, 90)
                    
                    calls_records.append({
                        'uuid': employee['uuid'],
                        'call_type': call_type,
                        'total': talk_time + np.random.randint(5, 30),
                        'talk': talk_time,
                        'call_date': current_date.strftime('%Y-%m-%d'),
                        'crm_result': crm_result
                    })

    calls_df = pd.DataFrame(calls_records)
    calls_df.to_csv('dayler_report.csv', index=False, encoding='utf-8-sig')
    print(f"Файл 'dayler_report.csv' успешно создан. Всего звонков: {len(calls_df)}")
    print('\nГенерация завершена')

generate_data()