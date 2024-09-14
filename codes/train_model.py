import numpy as np
from sklearn.cluster import KMeans
import pickle

# Данные о местах (пример)
places_data = np.array([
    [55.797518, 49.107169],  # Казанский Кремль
    [55.800564, 48.974726],  # Храм всех религий
    [55.800551, 49.105114],  # Башня Сеюмбике
    [55.798591, 49.105183],  # Кул Шариф
    [55.799039, 49.113750],  # Казанско-Богородицкий монастырь
])

# Инициализируем KMeans и обучаем модель
kmeans = KMeans(n_clusters=3)
kmeans.fit(places_data)

# Сохраняем обученную модель в файл
with open('kmeans_model.pkl', 'wb') as f:
    pickle.dump(kmeans, f)

print("Модель успешно сохранена в 'kmeans_model.pkl'")
