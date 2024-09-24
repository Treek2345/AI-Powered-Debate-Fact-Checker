from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils import UNEXPECTED_ERROR

class EnhancedContextBuilder:
    def __init__(self, max_context_size=5, topic_threshold=0.8):
        self.statements = []
        self.speakers = []
        self.max_context_size = max_context_size
        self.topic_threshold = topic_threshold
        self.tfidf_vectorizer = TfidfVectorizer()
        self.tfidf_matrix = None

    def add_statement(self, statement, speaker):
        try:
            self.statements.append(statement)
            self.speakers.append(speaker)
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.statements)
        except Exception as e:
            print(UNEXPECTED_ERROR.format(str(e)))

    def get_relevant_context(self, statement):
        try:
            if not self.statements:
                return ""

            statement_vector = self.tfidf_vectorizer.transform([statement])
            similarities = cosine_similarity(statement_vector, self.tfidf_matrix).flatten()

            top_indices = similarities.argsort()[:-2:-1]

            context = []
            for i in top_indices:
                if similarities[i] > self.topic_threshold:
                    context.append(self.statements[i])

            return " ".join(context[-self.max_context_size:])
        except Exception as e:
            print(UNEXPECTED_ERROR.format(str(e)))
            return ""

    def get_current_topics(self, top_n=3):
        try:
            if not self.statements:
                return []

            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            tfidf_scores = self.tfidf_matrix.sum(axis=0).A1

            keywords_with_scores = list(zip(feature_names, tfidf_scores))
            keywords_with_scores.sort(key=lambda item: item[1], reverse=True)

            return [keyword for keyword, score in keywords_with_scores[:top_n]]
        except Exception as e:
            print(UNEXPECTED_ERROR.format(str(e)))
            return []