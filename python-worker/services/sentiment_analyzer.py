# python-worker/services/sentiment_analyzer.py
"""
Real-time sentiment analysis with:
- Twitter/Reddit API integration
- VADER + custom ML model ensemble
- Emotion classification
"""
import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline
from typing import List, Dict

class SentimentAnalyzer:
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
        self.roberta = pipeline(
            "sentiment-analysis",
            model="finiteautomata/bertweet-base-sentiment-analysis"
        )
        self.emotion = pipeline(
            "text-classification",
            model="bhadresh-savani/distilbert-base-uncased-emotion"
        )

    def analyze(self, texts: List[str]) -> Dict[str, float]:
        """Combines multiple sentiment analysis approaches"""
        vader_scores = [self.vader.polarity_scores(t)['compound'] for t in texts]
        roberta_results = self.roberta(texts)
        emotion_results = self.emotion(texts)
        
        # Weighted average (VADER 30%, RoBERTa 50%, Emotion 20%)
        compound_scores = []
        for i in range(len(texts)):
            roberta_score = 1 if roberta_results[i]['label'] == 'POS' else -1
            emotion_weight = 0.5 if emotion_results[i]['label'] in ['joy', 'love'] else -0.5
            combined = (
                0.3 * vader_scores[i] + 
                0.5 * roberta_score * roberta_results[i]['score'] +
                0.2 * emotion_weight
            )
            compound_scores.append(combined)
        
        return {
            'average': np.mean(compound_scores),
            'positive': np.sum(np.array(compound_scores) > 0.5),
            'negative': np.sum(np.array(compound_scores) < -0.5),
            'scores': compound_scores
        }

    def stream_analysis(self, source: str = 'twitter'):
        """Real-time sentiment stream processor"""
        # Implementation would connect to streaming APIs
        pass