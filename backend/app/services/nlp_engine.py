from collections import defaultdict
from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.models.complaint import Complaint


@dataclass(frozen=True)
class IssueProfile:
    key: str
    title: str
    category: str
    description: str


ISSUE_PROFILES = (
    IssueProfile(
        key='water',
        title='Water Supply Disruption',
        category='Water & sanitation',
        description='no water our street has no water water supply disruption tanker did not arrive low pressure dry taps school water shortage',
    ),
    IssueProfile(
        key='garbage',
        title='Garbage Collection Failure',
        category='Sanitation',
        description='garbage waste rubbish bins overflowing missed collection pickup sanitation trash not collected',
    ),
    IssueProfile(
        key='road',
        title='Road Damage',
        category='Roads & transport',
        description='road damage pothole broken road crater traffic vehicle unsafe street surface',
    ),
    IssueProfile(
        key='light',
        title='Street Light Outage',
        category='Public safety',
        description='street light outage lamp dark lighting flickering nighttime visibility electrical fixture',
    ),
    IssueProfile(
        key='drainage',
        title='Drainage Blockage',
        category='Water & sanitation',
        description='drain drainage blockage flooding backed up water footpath inlet rain smell sewage',
    ),
)


class LocalNlpEngine:
    """Cluster complaints using local TF-IDF vectors and cosine similarity."""

    def __init__(self, similarity_threshold: float = 0.14, cluster_threshold: float = 0.28) -> None:
        self.similarity_threshold = similarity_threshold
        self.cluster_threshold = cluster_threshold

    @staticmethod
    def _text(complaint: Complaint) -> str:
        return f'{complaint.category}. {complaint.description}. Location: {complaint.location}'

    def group(self, complaints: list[Complaint]) -> dict[str, list[Complaint]]:
        if not complaints:
            return {}

        profile_texts = [profile.description for profile in ISSUE_PROFILES]
        complaint_texts = [self._text(complaint) for complaint in complaints]
        vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        vectors = vectorizer.fit_transform(profile_texts + complaint_texts)
        profile_vectors = vectors[:len(ISSUE_PROFILES)]
        complaint_vectors = vectors[len(ISSUE_PROFILES):]
        profile_scores = cosine_similarity(complaint_vectors, profile_vectors)

        grouped: dict[str, list[Complaint]] = defaultdict(list)
        unassigned: list[int] = []
        for index, scores in enumerate(profile_scores):
            best_profile_index = int(scores.argmax())
            if float(scores[best_profile_index]) >= self.similarity_threshold:
                grouped[ISSUE_PROFILES[best_profile_index].key].append(complaints[index])
            else:
                unassigned.append(index)

        for indexes in self._cluster_unassigned(complaint_vectors, unassigned):
            cluster_id = self._cluster_id(complaints, indexes)
            grouped[cluster_id] = [complaints[index] for index in indexes]
        return dict(grouped)

    def _cluster_unassigned(self, vectors, indexes: list[int]) -> list[list[int]]:
        clusters: list[list[int]] = []
        for index in indexes:
            matching_cluster = next(
                (cluster for cluster in clusters if self._similar_to_cluster(vectors, index, cluster)),
                None,
            )
            if matching_cluster is None:
                clusters.append([index])
            else:
                matching_cluster.append(index)
        return clusters

    def _similar_to_cluster(self, vectors, index: int, cluster: list[int]) -> bool:
        similarities = cosine_similarity(vectors[index], vectors[cluster]).ravel()
        return bool(similarities.max(initial=0) >= self.cluster_threshold)

    @staticmethod
    def _cluster_id(complaints: list[Complaint], indexes: list[int]) -> str:
        first_id = min(complaints[index].id for index in indexes)
        return f'emerging-{first_id[:8]}'


nlp_engine = LocalNlpEngine()