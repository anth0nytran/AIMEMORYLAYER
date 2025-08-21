import os
from typing import Optional

from pinecone import Pinecone, ServerlessSpec, CloudProvider, AwsRegion, GcpRegion, AzureRegion, Metric, VectorType

from app.utils.settings import get_settings


_pc: Optional[Pinecone] = None
_index_host: Optional[str] = None


def _region_enum(cloud: str, region: str):
	cloud = cloud.lower()
	region = region.replace("-", "_").upper()
	if cloud == "aws":
		return CloudProvider.AWS, getattr(AwsRegion, region, AwsRegion.US_EAST_1)
	if cloud == "gcp":
		return CloudProvider.GCP, getattr(GcpRegion, region, GcpRegion.US_CENTRAL1)
	if cloud == "azure":
		return CloudProvider.AZURE, getattr(AzureRegion, region, AzureRegion.EASTUS2)
	return CloudProvider.AWS, AwsRegion.US_EAST_1


def get_pinecone() -> Pinecone:
	global _pc
	if _pc is None:
		settings = get_settings()
		api_key = settings.pinecone_api_key or os.getenv("PINECONE_API_KEY")
		_pc = Pinecone(api_key=api_key) if api_key else Pinecone()
	return _pc  # type: ignore[return-value]


def ensure_index() -> str:
	"""Create the serverless index if missing and cache host. Returns host."""
	global _index_host
	if _index_host:
		return _index_host
	settings = get_settings()
	pc = get_pinecone()
	name = settings.pinecone_index
	if not pc.has_index(name=name):
		cloud_enum, region_enum = _region_enum(settings.pinecone_cloud, settings.pinecone_region or "us-east-1")
		pc.create_index(
			name=name,
			dimension=settings.embedding_dimension,
			metric=Metric.COSINE,
			spec=ServerlessSpec(cloud=cloud_enum, region=region_enum),
			vector_type=VectorType.DENSE,
		)
	desc = pc.describe_index(name=name)
	_index_host = desc.host
	return _index_host


def get_index():
	"""Return an Index client (creates index on first call if needed)."""
	host = ensure_index()
	pc = get_pinecone()
	return pc.Index(host=host)


def upsert_vectors(vectors, namespace: str = ""):
	"""vectors: List[Tuple[id, vector, metadata]]"""
	idx = get_index()
	return idx.upsert(vectors=vectors, namespace=namespace)


def query_top_k(vector, top_k: int, namespace: str = "", metadata_filter: Optional[dict] = None, include_metadata: bool = True):
	idx = get_index()
	return idx.query(
		vector=vector,
		top_k=top_k,
		include_metadata=include_metadata,
		filter=metadata_filter or {},
	)


