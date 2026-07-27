import h5py
import numpy as np
import os
import time
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
from utils import extract_lean_305_features

H5_PATH = "morse_dataset.h5"

def audit_dataset():
    print("==========================================================================")
    print("     MORSE — HDF5 DATASET CLUSTERING & QUALITY AUDIT TOOL                ")
    print("==========================================================================")
    
    if not os.path.exists(H5_PATH):
        print(f"❌ Error: {H5_PATH} not found!")
        return

    print(f"📂 Loading HDF5 dataset from {H5_PATH}...")
    t0 = time.time()
    
    X_features = []
    y_labels = []
    categories = []
    
    with h5py.File(H5_PATH, "r") as h5f:
        categories = list(h5f.keys())
        for label_idx, cat in enumerate(categories):
            samples = h5f[cat][:]
            print(f"  • Extracting 305 features for '{cat}' ({len(samples)} samples)...")
            for sample in samples:
                feat = extract_lean_305_features(sample)
                X_features.append(feat)
                y_labels.append(label_idx)
                
    X = np.array(X_features, dtype=np.float32)
    y = np.array(y_labels, dtype=np.int32)
    
    print(f"\n✅ Extracted {X.shape[0]} feature vectors of dimension {X.shape[1]} in {time.time() - t0:.2f}s.")
    
    # 1. Silhouette Score Analysis
    print("\n--------------------------------------------------------------------------")
    print(" 📐 1. CLUSTER SEPARATION & SILHOUETTE SCORE ANALYSIS")
    print("--------------------------------------------------------------------------")
    
    score = silhouette_score(X, y)
    print(f"  • Overall Dataset Silhouette Score: {score:.4f}")
    if score > 0.40:
        print("  🟢 EXCELLENT: Clusters are sharply separated in 305D feature space!")
    elif score > 0.20:
        print("  🟡 GOOD: Clusters are distinct, but have moderate boundary overlap.")
    else:
        print("  🔴 WARNING: High cluster overlap detected. More feature engineering or data needed.")
        
    # 2. Unsupervised K-Means Alignment Test
    print("\n--------------------------------------------------------------------------")
    print(" 🤖 2. UNSUPERVISED K-MEANS ALIGNMENT TEST (k=3)")
    print("--------------------------------------------------------------------------")
    kmeans = KMeans(n_clusters=len(categories), random_state=42, n_init=10)
    cluster_preds = kmeans.fit_predict(X)
    
    for i, cat in enumerate(categories):
        cat_mask = (y == i)
        cat_clusters = cluster_preds[cat_mask]
        counts = np.bincount(cat_clusters, minlength=len(categories))
        dominant_cluster = np.argmax(counts)
        purity = (counts[dominant_cluster] / np.sum(counts)) * 100.0
        print(f"  • '{cat:20s}': Dominant Cluster {dominant_cluster} Purity = {purity:5.1f}% ({counts[dominant_cluster]}/{np.sum(counts)})")

    # 3. PCA Variance Explanation
    print("\n--------------------------------------------------------------------------")
    print(" 📉 3. PRINCIPAL COMPONENT ANALYSIS (PCA)")
    print("--------------------------------------------------------------------------")
    pca = PCA(n_components=3)
    pca.fit(X)
    var_exp = pca.explained_variance_ratio_ * 100.0
    print(f"  • Top 3 Principal Components explain {np.sum(var_exp):.2f}% of total variance:")
    for idx, ve in enumerate(var_exp):
        print(f"    - PC{idx+1}: {ve:.2f}% variance")

    # 4. Outlier & Misclassification Detection
    print("\n--------------------------------------------------------------------------")
    print(" 🔍 4. AMBIGUOUS & OUTLIER SAMPLE IDENTIFICATION")
    print("--------------------------------------------------------------------------")
    # Distance of each sample to its category centroid
    outliers_found = 0
    for i, cat in enumerate(categories):
        cat_mask = (y == i)
        cat_X = X[cat_mask]
        centroid = np.mean(cat_X, axis=0)
        distances = np.linalg.norm(cat_X - centroid, axis=1)
        mean_dist = np.mean(distances)
        std_dist = np.std(distances)
        
        # Outliers defined as > 3.0 standard deviations from centroid
        far_outliers = np.where(distances > (mean_dist + 3.0 * std_dist))[0]
        if len(far_outliers) > 0:
            print(f"  ⚠️ '{cat}' has {len(far_outliers)} outlier samples (>3.0 StdDev from centroid).")
            outliers_found += len(far_outliers)
        else:
            print(f"  ✅ '{cat}' has 0 extreme outlier samples.")

    print("\n==========================================================================")
    print(" 🏁 AUDIT COMPLETE")
    print("==========================================================================")

if __name__ == "__main__":
    audit_dataset()
