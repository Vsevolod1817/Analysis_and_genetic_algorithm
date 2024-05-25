import mysql.connector
import pandas as pd
import random
from deap import base, creator, tools, algorithms
import time
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans


# Подключение к базе данных MySQL
def get_connection():
    return mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='1234',
        database='mydb'
    )


connection = get_connection()


# Выполнение SQL-запроса и получение данных
def get_data(query):
    cursor = connection.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    cursor.close()
    return pd.DataFrame(rows, columns=columns)


# Определение функции приспособленности для оценки производительности SQL-запроса
def evaluate_query(queries):
    total_time = 0
    for query in queries:
        start_time = time.time()
        cursor = connection.cursor()
        cursor.execute(query)
        cursor.fetchall()
        execution_time = time.time() - start_time
        cursor.close()
        total_time += execution_time
    return (total_time,)


# Создание структуры для генетического алгоритма
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()
toolbox.register("attr_query", random.choice, [
    "SELECT * FROM student WHERE age > 20",
    "SELECT * FROM student WHERE name LIKE 'A%'",
    "SELECT * FROM student WHERE email LIKE '%@gmail.com'"
])
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_query,
                 n=3)  # Увеличиваем количество атрибутов до 3
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

toolbox.register("mate", tools.cxOnePoint)  # Используем кроссовер одной точки
toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.5)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("evaluate", evaluate_query)

# Создадим списки для хранения лучших времен выполнения и средних времен выполнения на каждой итерации
best_times = []
avg_times = []
all_best_times = []


def optimize_sql():
    global best_times, avg_times, all_best_times

    # Создание начальной популяции
    population = toolbox.population(n=10)

    # Настройки генетического алгоритма
    NGEN = 20
    CXPB = 0.5
    MUTPB = 0.2

    # Сохранение лучшего индивида и его время выполнения за все итерации
    best_individual = None
    best_time_overall = float('inf')

    # Запуск генетического алгоритма
    for gen in range(NGEN):
        offspring = algorithms.varAnd(population, toolbox, cxpb=CXPB, mutpb=MUTPB)
        fits = map(toolbox.evaluate, offspring)

        for fit, ind in zip(fits, offspring):
            ind.fitness.values = fit

        population = toolbox.select(offspring, k=len(population))

        # Сохраняем лучшее время выполнения на текущей итерации
        best_time = min(population, key=lambda ind: ind.fitness.values[0]).fitness.values[0]
        best_times.append(best_time)

        # Сохраняем среднее время выполнения на текущей итерации
        avg_time = sum(ind.fitness.values[0] for ind in population) / len(population)
        avg_times.append(avg_time)

        # Сохраняем лучшего индивида за все итерации
        if best_time < best_time_overall:
            best_time_overall = best_time
            best_individual = tools.selBest(population, k=1)[0]
            # Сохраняем лучшее время выполнения за все итерации
            all_best_times.append(min(best_times))
    # Выводим лучший запрос за все итерации
    best_query = best_individual[0]
    print(f"Лучший запрос за все итерации: {best_query}, общее время выполнения: {best_time_overall}")


# Вызываем функцию оптимизации SQL
optimize_sql()

# Визуализация времени выполнения запросов по итерациям генетического алгоритма
plt.plot(range(1, len(best_times) + 1), best_times, label='Лучшее время выполнения')
plt.plot(range(1, len(avg_times) + 1), avg_times, label='Среднее время выполнения')
plt.plot(range(1, len(all_best_times) + 1), all_best_times, label='Лучшее время выполнения за все итерации', linestyle='--')
plt.axhline(min(all_best_times), color='r', linestyle='--', label='Лучшее время выполнения за все итерации (минимум)')
plt.xlabel('Итерация')
plt.ylabel('Время выполнения (сек)')
plt.title('Время выполнения запросов по итерациям')
plt.legend()
plt.grid(True)
plt.show()