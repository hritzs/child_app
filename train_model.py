import os
import pickle
import requests
import json

import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.neighbors import KNeighborsClassifier


def get_train_data(submitted_by: str):
    URL = "http://localhost:8000/get_training_data?submitted_by="+submitted_by+"&status=NF"
    try:
        result = requests.get(URL)
        if result.status_code == 200:
            result = json.loads(result.text)
            d1 = pd.DataFrame(result, columns=['label', 'face_encoding'])
            d2 = (pd.DataFrame(d1.pop('face_encoding').values.tolist(), index=d1.index).rename(columns = lambda x: 'fe_{}'.format(x+1)))
            df = d1.join(d2)
            return df['label'], df.drop('label', axis=1)
    except Exception as e:
        raise e

def train(submitted_by: str):
    
    model_name = 'classifier.pkl'
    if os.path.isfile(model_name):
        os.remove(model_name)

    try:
        labels, key_pts = get_train_data(submitted_by)
        if len(labels) == 0:
            return {"status": False, "message": "No cases submmited by this user"}
        le = LabelEncoder()
        encoded_labels = le.fit_transform(labels)
        classifier = KNeighborsClassifier(n_neighbors=len(labels),
                                          algorithm='ball_tree',
                                          weights='distance')
        classifier.fit(key_pts, encoded_labels)

        with open(model_name, 'wb') as file:
            pickle.dump((le, classifier), file)
        return {"status": True, "message": "Model Refreshed"}
    except Exception as e:
        print(str(e))
        return {"status": False, "message": str(e)}

if __name__ == "__main__":
    result = train('admin')
