import pandas as pd
from sklearn.naive_bayes import GaussianNB
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
from imblearn.over_sampling import SMOTE
from collections import Counter
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
import pylab
import pickle


data = pd.read_csv("asset/paysim.csv")
df = pd.DataFrame(data)

n_by_payment = df.groupby("paymentMode").count()

print(n_by_payment)

df_new = df.drop_duplicates()
print(df_new.count())



mapping = {"CASH_IN": 1, "CASH_OUT": 2, "DEBIT": 3, "PAYMENT": 4, "TRANSFER": 5}
df["paymentMode"] = df['paymentMode'].map(mapping)


X = df.drop(["isFraud", "isFlaggedFraud"], axis=1)
y = df["isFraud"]

"""print(X)
X_one = X.fillna(X.median())
print(X_one.count())"""

counter = Counter(y)
print(counter)
oversample = SMOTE()
X, y = oversample.fit_resample(X, y)
counterOne = Counter(y)
print(counterOne)

standard_scale = StandardScaler()
X_transformed = standard_scale.fit_transform(X)

pca = PCA(n_components=0.99, whiten=True)
pca.fit_transform(X_transformed)
print("Original number of features:", X.shape[1])
print("Reduced number of features:", X_transformed.shape[1])



X_transformed_train,  X_transformed_test, y_train, y_test = train_test_split(X_transformed, y, test_size=0.30, random_state=30)

"""df_actual_test = pd.DataFrame(X_test)
#test_result = pd.DataFrame(y_pred)
df_actual_test.to_csv("test_data.csv")
#df_actual_test.to_excel("test_data.xlsx", sheet_name='Sheet_name_1')"""


gnb = GaussianNB(var_smoothing=1e3)

model = gnb.fit(X_transformed_train, y_train)


with open('fraudDetection.pkl', 'wb') as f:
    pickle.dump(model, f)

y_pred = gnb.predict(X_transformed_test)

score = accuracy_score(y_test, y_pred)
print(f"'GuassianNB:' {score}")


labels = [0, 1]
gnb_cm = confusion_matrix(y_test, y_pred, labels)
print(gnb_cm)

sns.heatmap(gnb_cm, annot=True, cmap='Blues', fmt='')
plt.show()

sns.heatmap(gnb_cm/np.sum(gnb_cm), annot=True,
            fmt='.2%', cmap='Blues')
plt.show()

target_names = ['class 0', 'class 1']
print(classification_report(y_test, y_pred, target_names=target_names))

result = gnb.predict([[71, 2, 430022.9755, 134353577, 430022.9755, 0, 968610352, 0, 377926.1406]])
print(result)