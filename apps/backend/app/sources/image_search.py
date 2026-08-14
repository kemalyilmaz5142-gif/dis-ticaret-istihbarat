from app.schemas.search import SearchRequest
from app.services.image_service import get_image_metadata
from app.sources.base import LeadSourceAdapter, SourceLead


class ImageSearchAdapter(LeadSourceAdapter):
    source_name = "image-signature"
    source_type = "image_search"

    def collect(self, request: SearchRequest) -> list[SourceLead]:
        if not request.product_image_id:
            return []

        metadata = get_image_metadata(request.product_image_id)
        if not metadata:
            return []

        digest = metadata.get("sha256", "")[:12]
        visual_signature = metadata.get("visual_signature") or digest
        image_size = f"{metadata.get('width')}x{metadata.get('height')}" if metadata.get("width") and metadata.get("height") else "unknown-size"
        average_color = metadata.get("average_color") or "unknown-color"
        filename = metadata.get("filename", "product image")
        keyword = request.product_name_en or request.product_name_tr or filename

        return [
            SourceLead(
                company_name=f"Visual Match Candidate {index}",
                country=request.target_country,
                city=None,
                address=None,
                website=f"https://visual-match-{index}.example.com/{visual_signature}",
                email=None,
                phone=None,
                source=self.source_name,
                source_type=self.source_type,
                matched_keyword=keyword,
                confidence=70 - index,
                notes=(
                    f"Image analysis signature {visual_signature}; size {image_size}; average color {average_color}. "
                    "Reverse image API or vector similarity index can replace this adapter."
                ),
            )
            for index in range(1, 4)
        ]
