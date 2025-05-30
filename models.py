import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
import joblib
import os
import sqlite3
import json
from datetime import datetime

class TBResistancePredictor:
    """
    Class for predicting TB resistance patterns and treatment outcomes
    """
    
    def __init__(self, model_path=None):
        """
        Initialize the TB resistance predictor
        
        Parameters:
        model_path (str): Path to a saved model file (optional)
        """
        self.model = None
        self.feature_names = None
        self.target_name = None
        self.categorical_features = None
        self.numerical_features = None
        self.label_encoders = {}
        self.required_columns = None
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def preprocess_data(self, df, target_column=None, for_training=True):
        """
        Preprocess data for model training or prediction
        
        Parameters:
        df (pandas.DataFrame): DataFrame to preprocess
        target_column (str): Target column name (required for training)
        for_training (bool): Whether preprocessing is for training
        
        Returns:
        X, y (tuple): Preprocessed features and target (if for_training=True)
        X (array): Preprocessed features (if for_training=False)
        """
        # Make a copy to avoid modifying the original
        df_processed = df.copy()
        
        # Identify feature types if not already set
        if for_training and (self.categorical_features is None or self.numerical_features is None):
            self.categorical_features = [col for col in df.columns if col != target_column 
                                        and df[col].dtype == 'object']
            self.numerical_features = [col for col in df.columns if col != target_column 
                                      and df[col].dtype in ['int64', 'float64']]
            self.feature_names = self.categorical_features + self.numerical_features
            self.target_name = target_column
            self.required_columns = self.feature_names.copy()
            
            if target_column:
                self.required_columns.append(target_column)
        
        # Ensure all required columns exist
        if self.required_columns:
            for col in self.required_columns:
                if col not in df_processed.columns:
                    if col != target_column or for_training:
                        df_processed[col] = np.nan
        
        # Preprocess categorical features
        for feature in self.categorical_features:
            if feature in df_processed.columns:
                if for_training:
                    # For training, create new label encoders
                    le = LabelEncoder()
                    df_processed[feature] = le.fit_transform(df_processed[feature].astype(str))
                    self.label_encoders[feature] = le
                else:
                    # For prediction, use existing label encoders
                    if feature in self.label_encoders:
                        le = self.label_encoders[feature]
                        # Handle unseen categories
                        df_processed[feature] = df_processed[feature].astype(str)
                        df_processed[feature] = df_processed[feature].apply(
                            lambda x: x if x in le.classes_ else le.classes_[0]
                        )
                        df_processed[feature] = le.transform(df_processed[feature])
                    else:
                        # If encoder missing, use zeros
                        df_processed[feature] = 0
        
        # Extract features and target
        X = df_processed[self.feature_names].values
        
        if for_training and target_column:
            # Encode target for training
            if df_processed[target_column].dtype == 'object':
                target_le = LabelEncoder()
                y = target_le.fit_transform(df_processed[target_column])
                self.label_encoders['target'] = target_le
            else:
                y = df_processed[target_column].values
            
            return X, y
        else:
            return X
    
    def train(self, df, target_column, test_size=0.2, random_state=42):
        """
        Train a model to predict TB resistance or outcomes
        
        Parameters:
        df (pandas.DataFrame): Training data
        target_column (str): Target column name
        test_size (float): Proportion of data to use for testing
        random_state (int): Random seed for reproducibility
        
        Returns:
        dict: Training metrics
        """
        # Preprocess the data
        X, y = self.preprocess_data(df, target_column, for_training=True)
        
        # Split into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        # Create and train the model
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=random_state,
            n_jobs=-1
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate the model
        train_accuracy = self.model.score(X_train, y_train)
        test_accuracy = self.model.score(X_test, y_test)
        
        metrics = {
            'train_accuracy': train_accuracy,
            'test_accuracy': test_accuracy,
            'n_samples': len(X),
            'n_features': X.shape[1],
            'feature_importances': dict(zip(self.feature_names, 
                                          self.model.feature_importances_))
        }
        
        return metrics
    
    def predict(self, df):
        """
        Make predictions using the trained model
        
        Parameters:
        df (pandas.DataFrame): Data to make predictions on
        
        Returns:
        array: Predicted values
        """
        if self.model is None:
            raise ValueError("Model hasn't been trained yet.")
        
        # Preprocess the data
        X = self.preprocess_data(df, for_training=False)
        
        # Make predictions
        predictions = self.model.predict(X)
        
        # If target is categorical, convert back to original labels
        if 'target' in self.label_encoders:
            predictions = self.label_encoders['target'].inverse_transform(predictions)
        
        return predictions
    
    def predict_proba(self, df):
        """
        Make probability predictions using the trained model
        
        Parameters:
        df (pandas.DataFrame): Data to make predictions on
        
        Returns:
        array: Predicted probabilities
        """
        if self.model is None:
            raise ValueError("Model hasn't been trained yet.")
        
        # Preprocess the data
        X = self.preprocess_data(df, for_training=False)
        
        # Make probability predictions
        probabilities = self.model.predict_proba(X)
        
        return probabilities
    
    def save_model(self, model_path):
        """
        Save the trained model to a file
        
        Parameters:
        model_path (str): Path to save the model
        
        Returns:
        bool: Success status
        """
        if self.model is None:
            raise ValueError("Model hasn't been trained yet.")
        
        try:
            # Create a dictionary with all necessary components
            model_data = {
                'model': self.model,
                'feature_names': self.feature_names,
                'target_name': self.target_name,
                'categorical_features': self.categorical_features,
                'numerical_features': self.numerical_features,
                'label_encoders': self.label_encoders,
                'required_columns': self.required_columns,
                'metadata': {
                    'created_at': datetime.now().isoformat(),
                    'description': 'TB Resistance Predictor Model'
                }
            }
            
            # Save to file
            joblib.dump(model_data, model_path)
            return True
        
        except Exception as e:
            print(f"Error saving model: {e}")
            return False
    
    def load_model(self, model_path):
        """
        Load a trained model from a file
        
        Parameters:
        model_path (str): Path to the saved model
        
        Returns:
        bool: Success status
        """
        try:
            # Load the model data
            model_data = joblib.load(model_path)
            
            # Restore model components
            self.model = model_data['model']
            self.feature_names = model_data['feature_names']
            self.target_name = model_data['target_name']
            self.categorical_features = model_data['categorical_features']
            self.numerical_features = model_data['numerical_features']
            self.label_encoders = model_data['label_encoders']
            self.required_columns = model_data['required_columns']
            
            return True
        
        except Exception as e:
            print(f"Error loading model: {e}")
            return False

class TreatmentOutcomePredictor(TBResistancePredictor):
    """
    Specialized class for predicting TB treatment outcomes
    """
    
    def __init__(self, model_path=None):
        super().__init__(model_path)
    
    def prepare_patient_data(self, patient_data):
        """
        Prepare patient data for outcome prediction
        
        Parameters:
        patient_data (dict): Patient information
        
        Returns:
        pandas.DataFrame: Prepared data for prediction
        """
        # Convert patient data dictionary to DataFrame
        patient_df = pd.DataFrame([patient_data])
        
        # Ensure all required columns exist
        for col in self.required_columns:
            if col not in patient_df.columns:
                patient_df[col] = np.nan
        
        return patient_df
    
    def predict_outcome(self, patient_data):
        """
        Predict treatment outcome for a patient
        
        Parameters:
        patient_data (dict): Patient information
        
        Returns:
        dict: Predicted outcome and probabilities
        """
        # Prepare patient data
        patient_df = self.prepare_patient_data(patient_data)
        
        # Make prediction
        predicted_outcome = self.predict(patient_df)[0]
        
        # Get probabilities if available
        outcome_probs = {}
        if hasattr(self.model, 'predict_proba'):
            probabilities = self.predict_proba(patient_df)[0]
            outcome_classes = self.label_encoders['target'].classes_
            outcome_probs = dict(zip(outcome_classes, probabilities))
        
        return {
            'predicted_outcome': predicted_outcome,
            'outcome_probabilities': outcome_probs
        }

class DrugResistancePredictor(TBResistancePredictor):
    """
    Specialized class for predicting drug resistance patterns
    """
    
    def __init__(self, model_path=None):
        super().__init__(model_path)
    
    def predict_resistance(self, patient_data):
        """
        Predict drug resistance for a patient
        
        Parameters:
        patient_data (dict): Patient information
        
        Returns:
        dict: Predicted resistance pattern and probabilities
        """
        # Prepare patient data
        patient_df = pd.DataFrame([patient_data])
        
        # Make prediction
        predicted_resistance = self.predict(patient_df)[0]
        
        # Get probabilities if available
        resistance_probs = {}
        if hasattr(self.model, 'predict_proba'):
            probabilities = self.predict_proba(patient_df)[0]
            resistance_classes = self.label_encoders['target'].classes_
            resistance_probs = dict(zip(resistance_classes, probabilities))
        
        return {
            'predicted_resistance': predicted_resistance,
            'resistance_probabilities': resistance_probs
        }
