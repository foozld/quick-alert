import tensorflow as tf
from transformers import BertTokenizer, TFBertForSequenceClassification
from typing import List, Tuple, Dict, Optional
import numpy as np
import spacy
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import re

class DisasterDetector:
    def __init__(self):
        pass
    
    def predict(self, texts):
        """Dummy prediction method for sample implementation"""
        return [{"is_disaster": True, "confidence": 0.9} for _ in texts]

    def _analyze_text(self, text: str) -> Dict:
        """
        Perform detailed analysis of the text to extract relevant information
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary containing extracted information
        """
        doc = self.nlp(text)
        
        # Extract named entities
        entities = {ent.label_: ent.text for ent in doc.ents}
        
        # Extract locations
        locations = self._extract_locations(doc)
        
        # Extract disaster-related keywords and determine type
        keywords = []
        disaster_type = None
        max_keyword_matches = 0
        
        for disaster, info in self.disaster_types.items():
            # Check main disaster type
            if disaster in text.lower():
                keyword_matches = 1
                # Check related keywords
                for keyword in info['keywords']:
                    if keyword in text.lower():
                        keyword_matches += 1
                        keywords.append(keyword)
                
                if keyword_matches > max_keyword_matches:
                    max_keyword_matches = keyword_matches
                    disaster_type = disaster
                    severity = info['severity']
        
        return {
            'disaster_type': disaster_type,
            'severity': severity if disaster_type else 'unknown',
            'locations': locations,
            'keywords': keywords,
            'entities': entities
        }
    
    def _extract_locations(self, doc) -> List[Dict[str, float]]:
        """
        Extract and geocode locations from the text
        
        Args:
            doc: spaCy document
            
        Returns:
            List of dictionaries containing location information
        """
        locations = []
        for ent in doc.ents:
            if ent.label_ in ['GPE', 'LOC']:
                try:
                    location = self.geocoder.geocode(ent.text)
                    if location:
                        locations.append({
                            'name': ent.text,
                            'lat': location.latitude,
                            'lon': location.longitude
                        })
                except GeocoderTimedOut:
                    continue
        return locations
    
    def _calculate_confidence(self, 
                            disaster_prob: float, 
                            keywords: List[str], 
                            locations: List[Dict]) -> float:
        """
        Calculate overall confidence score based on multiple factors
        
        Args:
            disaster_prob: Base disaster probability from the model
            keywords: List of disaster-related keywords found
            locations: List of extracted locations
            
        Returns:
            Confidence score between 0 and 1
        """
        # Base confidence from model probability
        confidence = disaster_prob
        
        # Adjust based on keywords
        keyword_boost = min(len(keywords) * 0.1, 0.3)  # Max 0.3 boost from keywords
        
        # Adjust based on location information
        location_boost = min(len(locations) * 0.1, 0.2)  # Max 0.2 boost from locations
        
        # Combine scores (ensure it doesn't exceed 1.0)
        final_confidence = min(confidence + keyword_boost + location_boost, 1.0)
        
        return float(final_confidence)
    
    def train(self, texts: List[str], labels: List[int], epochs: int = 3):
        """
        Fine-tune the model on disaster-related data
        
        Args:
            texts: List of training texts
            labels: List of corresponding labels (0: non-disaster, 1: disaster)
            epochs: Number of training epochs
        """
        # Prepare training data
        train_encodings = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=128,
            return_tensors="tf"
        )
        
        train_dataset = tf.data.Dataset.from_tensor_slices((
            dict(train_encodings),
            labels
        )).shuffle(1000).batch(16)
        
        # Compile and train the model
        optimizer = tf.keras.optimizers.Adam(learning_rate=2e-5)
        loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
        
        self.model.compile(optimizer=optimizer, loss=loss, metrics=['accuracy'])
        self.model.fit(train_dataset, epochs=epochs)
    
    def save_model(self, path: str):
        """Save the fine-tuned model to disk"""
        self.model.save_pretrained(path)
        self.tokenizer.save_pretrained(path)
    
    def extract_keywords(self, text: str) -> List[str]:
        """
        Extract relevant keywords from the text that indicate a disaster
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of extracted keywords
        """
        disaster_keywords = {
            'earthquake', 'flood', 'hurricane', 'tornado', 'wildfire',
            'tsunami', 'landslide', 'avalanche', 'volcanic', 'storm',
            'emergency', 'evacuation', 'disaster', 'catastrophe', 'crisis'
        }
        
        # Simple keyword extraction (can be enhanced with NLP techniques)
        words = set(text.lower().split())
        return list(words.intersection(disaster_keywords)) 