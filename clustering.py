# import numpy as np
import pandas as pd
import os
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import joblib
from sklearn.preprocessing import StandardScaler

def cluster_data() -> pd.DataFrame:
    # Create models directory if it doesn't exist
    model_path = "models"
    os.makedirs(model_path, exist_ok=True)
    
    try:
        # Read macro nutrient data
        data_ = pd.read_csv("outputs/macros.csv")
        # Data preprocessing
        data = data_.drop(columns=["name"])

        # Try to load models or create new ones if they don't exist
        try:
            scaler_loaded = joblib.load(os.path.join(model_path, "scaler_model.pkl"))
            pca_loaded = joblib.load(os.path.join(model_path, "pca_model.pkl"))
            kmeans_loaded = joblib.load(os.path.join(model_path, "kmeans_model.pkl"))
            print("✅ Using existing models")
        except FileNotFoundError:
            print("⚠️ Model files not found, creating new ones...")
            
            # Create and save new models
            scaler_loaded = StandardScaler()
            X_scaled = scaler_loaded.fit_transform(data)
            joblib.dump(scaler_loaded, os.path.join(model_path, "scaler_model.pkl"))
            
            pca_loaded = PCA(n_components=2)
            X_pca = pca_loaded.fit_transform(X_scaled)
            joblib.dump(pca_loaded, os.path.join(model_path, "pca_model.pkl"))
            
            kmeans_loaded = KMeans(n_clusters=3, random_state=42)
            kmeans_loaded.fit(X_pca)
            joblib.dump(kmeans_loaded, os.path.join(model_path, "kmeans_model.pkl"))
            print("✅ Created and saved new models")

        # Transform data using the models
        X = scaler_loaded.transform(data)
        X = pca_loaded.transform(X)
        
        # Get KMeans cluster labels
        # Get KMeans cluster labels
        labels = kmeans_loaded.predict(X)
        print(labels)
        # Add results to the dataframe
        data_["pca1"] = X[:, 0]
        data_["pca2"] = X[:, 1]
        data_["cluster"] = labels

        # Save results
        data_.to_csv("outputs/macros_clustered.csv", index=False)
        print("✅ Kümeleme tamamlandı. `outputs/macros_clustered.csv` dosyasında görebilirsin.")
        
        return data_
    except Exception as e:
        print(f"❌ Kümeleme işlemi sırasında hata: {str(e)}")
        return pd.DataFrame()  # Return empty DataFrame on error
