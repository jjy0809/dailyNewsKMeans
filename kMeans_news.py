import os
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from tqdm import tqdm

data = r'C:\Users\happy\Desktop\학교\고등학교\2학년\일일 뉴스 헤드라인\data'
input = os.path.join(data, 'news.json')
output = os.path.join(data, 'res.json')
graph = os.path.join(data, 'graph')

if not os.path.exists(graph):
    os.makedirs(graph)

def load_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_graph(fig, graph_type, date):
    filename = f"{date}_{graph_type}.png"
    filepath = os.path.join(graph, filename)
    fig.savefig(filepath)
    plt.close(fig)

def elbow(tf_mat, date):
    distortions = []
    k_values = range(2, 31)
    for k in k_values:
        kmeans = KMeans(n_clusters=k, init="k-means++", n_init=20, max_iter=300, tol=1e-04, random_state=42)
        kmeans.fit(tf_mat)
        distortions.append(kmeans.inertia_)
    fig = plt.figure()
    plt.plot(k_values, distortions, marker='o')
    plt.title(f"Elbow - {date}")
    plt.xlabel("Clusters Num")
    plt.ylabel("Distortion")
    save_graph(fig, "elbow", date)

def extract_key_headlines(news_data, k=10):
    result = {}
    for date, headlines in tqdm(news_data.items(), desc="Processing"):
        if not headlines:
            continue
        vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 2), max_features=1000)
        tf_mat = vectorizer.fit_transform(headlines)
        elbow(tf_mat, date) 
        kmeans = KMeans(n_clusters=k, init="k-means++", n_init=20, max_iter=300, tol=1e-04, random_state=42)
        kmeans.fit(tf_mat)
        labs = kmeans.labels_
        clst_cnt = np.bincount(labs)
        top_clusters = clst_cnt.argsort()[-5:][::-1]
        key_head = []
        for cluster in top_clusters:
            cluster_indices = np.where(labs == cluster)[0]
            cluster_center = kmeans.cluster_centers_[cluster]
            dense_matrix = tf_mat[cluster_indices].toarray()
            distances = np.linalg.norm(dense_matrix - cluster_center, axis=1)
            closest_index = cluster_indices[np.argmin(distances)]
            key_head.append(headlines[closest_index])
        result[date] = key_head
    return result

def save_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    news_data = load_data(input)
    key_head = extract_key_headlines(news_data, k=10)
    save_json(key_head, output)