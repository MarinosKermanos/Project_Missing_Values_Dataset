import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.impute import SimpleImputer

# Read the data
X_full = pd.read_csv('C:/Users/User/Desktop/GitHub/Missing_Values_Dataset/train.csv', index_col='Id') #train data
X_test_full = pd.read_csv('C:/Users/User/Desktop/GitHub/Missing_Values_Dataset/test.csv', index_col='Id') #test data

# Remove rows with missing target, separate target from predictors
X_full.dropna(axis=0, subset=['SalePrice'], inplace=True)
y = X_full.SalePrice
X_full.drop(['SalePrice'], axis=1, inplace=True)

# We'll use only numerical predictors for simplicity
X = X_full.select_dtypes(exclude=['object'])
X_test = X_test_full.select_dtypes(exclude=['object'])

# Break off validation set from training data
X_train, X_valid, y_train, y_valid = train_test_split(X, y, train_size=0.8, test_size=0.2,
                                                      random_state=0)
# Shape of training data (num_rows, num_columns)
print(X_train.shape)

# Number of missing values in each column of training data
missing_val_count_by_column = (X_train.isnull().sum())
print(missing_val_count_by_column[missing_val_count_by_column > 0])

#score_dataset Function for comparing different approaches
def score_dataset(X_train, X_valid, y_train, y_valid):
    model = RandomForestRegressor(n_estimators=100, random_state=0)
    model.fit(X_train, y_train)
    preds = model.predict(X_valid)
    return mean_absolute_error(y_valid, preds)

#First approach-->Drop the columns with missing values
#Get names of columns with missing values
cols_with_missing = [col for col in X_train.columns
                      if X_train[col].isnull().any()]
print(cols_with_missing)

#drop columns in training and validation data
reduced_X_train = X_train.drop(cols_with_missing, axis = 'columns')
reduced_X_valid = X_valid.drop(cols_with_missing, axis = 'columns')

#Get MAE for the first approach
print("MAE (Drop columns with missing values):")
print(score_dataset(reduced_X_train, reduced_X_valid, y_train, y_valid))

#Second approach --> Using Imputation
my_imputer = SimpleImputer()
imputed_X_train = pd.DataFrame(my_imputer.fit_transform(X_train))
imputed_X_valid = pd.DataFrame(my_imputer.transform(X_valid))

# imputation removed column names; put them back
imputed_X_train.columns = X_train.columns
imputed_X_valid.columns = X_train.columns

#Get MAE for the second approach
print("MAE (Imputation):")
print(score_dataset(imputed_X_train, imputed_X_valid, y_train, y_valid))

#Generate test predictions
final_imputer = SimpleImputer(strategy = 'most_frequent')
final_X_train = pd.DataFrame(final_imputer.fit_transform(X_train))
final_X_valid = pd.DataFrame(final_imputer.transform(X_valid))

#Imputation removed column names; put them back
final_X_train.columns = X_train.columns
final_X_valid.columns = X_train.columns

# Define and fit model
model = RandomForestRegressor(n_estimators=100, random_state=0)
model.fit(final_X_train, y_train)

# Get validation predictions and MAE
preds_valid = model.predict(final_X_valid)
print("MAE (Your approach):")
print(mean_absolute_error(y_valid, preds_valid))

# Preprocess test data
final_X_test = pd.DataFrame(final_imputer.transform(X_test))

#imputation removed column names; put them back
final_X_test.columns = X_train.columns


#Get test predictions
preds_test = model.predict(final_X_test)
print(preds_test)

# Save test predictions to .csv file
output = pd.DataFrame({'Id': X_test.index,
                       'SalePrice': preds_test})
output.to_csv('submission.csv', index=False)