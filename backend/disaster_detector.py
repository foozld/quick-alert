import tensorflow as tf
from transformers import BertTokenizer, TFBertForSequenceClassification
from typing import List, Tuple
import numpy as np

class DisasterDetector:
    def __init__(self, model_path: str = None):
        """
        Initialize the disaster detector with a pre-trained BERT model
        
        Args:
            model_path: Optional path to a fine-tuned model
        """
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        if model_path:
            self.model = TFBertForSequenceClassification.from_pretrained(model_path)
        else:
            self.model = TFBertForSequenceClassification.from_pretrained(
                'bert-base-uncased',
                num_labels=2
            )
            
    def predict(self, texts: List[str]) -> List[Tuple[float, float]]:
        """
        Predict disaster probability for a list of texts
        
        Args:
            texts: List of text strings to analyze
            
        Returns:
            List of tuples containing (non_disaster_prob, disaster_prob)
        """
        # Tokenize all texts
        inputs = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=128,
            return_tensors="tf"
        )
        
        # Get predictions
        outputs = self.model(inputs)
        probabilities = tf.nn.softmax(outputs.logits, axis=-1).numpy()
        
        return [(float(prob[0]), float(prob[1])) for prob in probabilities]
    
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